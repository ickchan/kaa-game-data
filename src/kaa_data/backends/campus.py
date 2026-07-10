from __future__ import annotations

from pathlib import Path

from tqdm import tqdm

from kaa_data.config import PipelineConfig
from kaa_data.extract.texture import extract_texture2d_from_file
from kaa_data.models import AssetTask, FetchReport, SkippedAsset, TaskManifest
from kaa_data.octo.download import ensure_asset_cached, extract_cached_asset
from kaa_data.octo.manifest import fetch_manifest, load_revision_state, save_revision_state
from kaa_data.tasks.postprocess import apply_post_process


class CampusBackend:
    name = "campus"

    def healthcheck(self, config: PipelineConfig) -> None:
        if not config.campus_root.exists():
            raise FileNotFoundError(f"campus directory not found: {config.campus_root}")

    def ensure_cache(self, config: PipelineConfig, *, force: bool = False) -> int:
        base_revision = 0 if force else load_revision_state(config.campus_cache / ".octo_revision")
        manifest = fetch_manifest(
            config.gom_root,
            base_revision=base_revision,
            request_timeout=config.gom_request_timeout,
        )
        config.campus_cache.mkdir(parents=True, exist_ok=True)
        save_revision_state(config.campus_cache / ".octo_revision", manifest.revision)
        return manifest.revision

    def fetch(self, config: PipelineConfig, task_manifest: TaskManifest, *, force: bool = False) -> FetchReport:
        manifest = fetch_manifest(
            config.gom_root,
            base_revision=0,
            request_timeout=config.gom_request_timeout,
        )

        ok = 0
        failed: list[AssetTask] = []
        skipped: list[SkippedAsset] = []

        config.campus_assets.mkdir(parents=True, exist_ok=True)

        for task in tqdm(task_manifest.tasks, desc="campus sprites"):
            if self._task_already_valid(task) and not force:
                ok += 1
                continue

            entry = manifest.get(task.asset_name)
            if entry is None:
                skipped.append(
                    SkippedAsset(task.asset_name, task.ref_id, "not in octo manifest")
                )
                continue

            cache_path = config.campus_assets / task.asset_name
            try:
                ensure_asset_cached(entry, cache_path, config.gom_root, force=force)
                if not extract_cached_asset(cache_path, task.output_path):
                    if not extract_texture2d_from_file(cache_path, task.output_path):
                        failed.append(task)
                        continue
                apply_post_process(task.post_process, task.output_path)
                if self._task_already_valid(task):
                    ok += 1
                else:
                    failed.append(task)
            except Exception as exc:
                skipped.append(SkippedAsset(task.asset_name, task.ref_id, str(exc)))

        return FetchReport(
            backend=self.name,
            tasks_total=len(task_manifest.tasks),
            tasks_ok=ok,
            tasks_failed=failed,
            skipped=skipped,
        )

    def _task_already_valid(self, task: AssetTask) -> bool:
        import cv2

        if not task.output_path.exists():
            return False
        if not task.expected_size:
            return True
        img = cv2.imread(str(task.output_path))
        if img is None:
            return False
        return (img.shape[1], img.shape[0]) == task.expected_size