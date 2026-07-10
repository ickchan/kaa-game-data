from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AssetTask:
    asset_name: str
    output_path: Path
    ref_id: str
    post_process: str | None = None
    expected_size: tuple[int, int] | None = None

    def to_json(self, sprites_dir: Path | None = None) -> dict:
        rel_path = (
            self.output_path.relative_to(sprites_dir).as_posix()
            if sprites_dir is not None
            else self.output_path.as_posix()
        )
        data: dict = {
            "assetName": self.asset_name,
            "relPath": rel_path,
            "refId": self.ref_id,
        }
        if self.post_process:
            data["postProcess"] = self.post_process
        if self.expected_size:
            data["expectedSize"] = list(self.expected_size)
        return data

    @classmethod
    def from_json(cls, sprites_dir: Path, data: dict) -> AssetTask:
        expected = data.get("expectedSize")
        return cls(
            asset_name=data["assetName"],
            output_path=sprites_dir / data["relPath"],
            ref_id=data["refId"],
            post_process=data.get("postProcess"),
            expected_size=tuple(expected) if expected else None,
        )


@dataclass
class SkippedAsset:
    asset_name: str
    ref_id: str
    reason: str

    def to_json(self) -> dict:
        return {"id": self.asset_name, "refId": self.ref_id, "reason": self.reason}


@dataclass
class TaskManifest:
    sprites_dir: Path
    tasks: list[AssetTask] = field(default_factory=list)
    skipped: list[SkippedAsset] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_json(self) -> dict:
        return {
            "spritesDir": self.sprites_dir.as_posix(),
            "tasks": [t.to_json(self.sprites_dir) for t in self.tasks],
            "skipped": [s.to_json() for s in self.skipped],
            "warnings": self.warnings,
        }

    @classmethod
    def from_json(cls, data: dict) -> TaskManifest:
        sprites_dir = Path(data["spritesDir"])
        return cls(
            sprites_dir=sprites_dir,
            tasks=[AssetTask.from_json(sprites_dir, t) for t in data["tasks"]],
            skipped=[
                SkippedAsset(s["id"], s["refId"], s.get("reason", ""))
                for s in data.get("skipped", [])
            ],
            warnings=data.get("warnings", []),
        )


@dataclass
class FileInfo:
    md5: str
    size: int


@dataclass
class FetchReport:
    backend: str
    tasks_total: int
    tasks_ok: int
    tasks_failed: list[AssetTask] = field(default_factory=list)
    skipped: list[SkippedAsset] = field(default_factory=list)


@dataclass
class BuildReport:
    gakumasu_diff_sha: str
    backend: str
    tasks_total: int
    tasks_ok: int
    tasks_failed: list[AssetTask] = field(default_factory=list)
    skipped: list[SkippedAsset] = field(default_factory=list)
    output_files: dict[str, FileInfo] = field(default_factory=dict)