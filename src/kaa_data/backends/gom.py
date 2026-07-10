from __future__ import annotations

import sys
from pathlib import Path

from tqdm import tqdm

from kaa_data.config import PipelineConfig
from kaa_data.extract.texture import extract_texture2d_png
from kaa_data.models import AssetTask, FetchReport, SkippedAsset, TaskManifest
from kaa_data.octo.manifest import fetch_manifest, load_revision_state, save_revision_state
from kaa_data.tasks.postprocess import apply_post_process


class GomBackend:
    name = "gom"

    def healthcheck(self, config: PipelineConfig) -> None:
        gom_root = config.gom_root.resolve()
        if not gom_root.exists():
            raise FileNotFoundError(f"GkmasObjectManager not found: {gom_root}")

    def ensure_cache(self, config: PipelineConfig, *, force: bool = False) -> int:
        base_revision = 0 if force else load_revision_state(config.output_dir / ".gom_revision")
        manifest = fetch_manifest(
            config.gom_root,
            base_revision=base_revision,
            request_timeout=config.gom_request_timeout,
        )
        save_revision_state(config.output_dir / ".gom_revision", manifest.revision)
        return manifest.revision

    def fetch(self, config: PipelineConfig, task_manifest: TaskManifest, *, force: bool = False) -> FetchReport:
        self.ensure_cache(config, force=force)
        gom = self._import_gom(config.gom_root, config.gom_request_timeout)
        manifest = gom.fetch()

        ok = 0
        failed: list[AssetTask] = []
        skipped: list[SkippedAsset] = []

        for task in tqdm(task_manifest.tasks, desc="gom sprites"):
            if self._task_already_valid(task) and not force:
                ok += 1
                continue

            try:
                if task.asset_name not in manifest:
                    skipped.append(
                        SkippedAsset(task.asset_name, task.ref_id, "not in octo manifest")
                    )
                    continue

                obj = manifest[task.asset_name]
                data = obj.get_data(image_format="png")
                png_bytes = data["bytes"]

                task.output_path.parent.mkdir(parents=True, exist_ok=True)
                task.output_path.write_bytes(png_bytes)
                apply_post_process(task.post_process, task.output_path)

                if not self._task_already_valid(task):
                    failed.append(task)
                else:
                    ok += 1
            except Exception as exc:
                skipped.append(SkippedAsset(task.asset_name, task.ref_id, str(exc)))

        return FetchReport(
            backend=self.name,
            tasks_total=len(task_manifest.tasks),
            tasks_ok=ok,
            tasks_failed=failed,
            skipped=skipped,
        )

    def _import_gom(self, gom_root: Path, request_timeout: int):
        root = gom_root.resolve()
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        import GkmasObjectManager as gom  # type: ignore

        utils = sys.modules.get("GkmasObjectManager.utils")
        if utils is not None:
            utils.REQUEST_TIMEOUT = request_timeout
        return gom

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