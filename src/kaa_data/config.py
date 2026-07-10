from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@dataclass
class PipelineConfig:
    root: Path
    gakumasu_diff: Path
    output_dir: Path
    sprites_dir: Path
    release_dir: Path
    game_db: Path
    tasks_path: Path
    build_report_path: Path
    default_backend: str
    zstd_level: int
    campus_root: Path
    campus_binary: Path
    campus_cache: Path
    campus_assets: Path
    gom_root: Path
    gom_request_timeout: int

    @classmethod
    def load(cls, root: Path | None = None) -> PipelineConfig:
        root = (root or Path.cwd()).resolve()
        config_path = root / "pipeline.toml"
        if not config_path.exists():
            raise FileNotFoundError(f"Missing pipeline config: {config_path}")

        with config_path.open("rb") as f:
            data = tomllib.load(f)

        data_cfg = data["data"]
        output_cfg = data["output"]
        build_cfg = data["build"]
        campus_cfg = data["backends"]["campus"]
        gom_cfg = data["backends"]["gom"]

        campus_binary = root / campus_cfg["binary"]
        if os.name == "nt" and not campus_binary.suffix:
            campus_binary = campus_binary.with_suffix(".exe")

        return cls(
            root=root,
            gakumasu_diff=root / data_cfg["gakumasu_diff"],
            output_dir=root / output_cfg["dir"],
            sprites_dir=root / output_cfg["sprites"],
            release_dir=root / output_cfg["release"],
            game_db=root / output_cfg["game_db"],
            tasks_path=root / output_cfg["tasks"],
            build_report_path=root / output_cfg["build_report"],
            default_backend=build_cfg["default_backend"],
            zstd_level=build_cfg["zstd_level"],
            campus_root=root / campus_cfg["root"],
            campus_binary=campus_binary,
            campus_cache=root / campus_cfg["cache"],
            campus_assets=root / campus_cfg["assets"],
            gom_root=root / gom_cfg["root"],
            gom_request_timeout=gom_cfg["request_timeout"],
        )

    def ensure_output_dirs(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.sprites_dir.mkdir(parents=True, exist_ok=True)
        self.release_dir.mkdir(parents=True, exist_ok=True)
        for sub in ("idol_cards", "skill_cards", "drinks"):
            (self.sprites_dir / sub).mkdir(parents=True, exist_ok=True)