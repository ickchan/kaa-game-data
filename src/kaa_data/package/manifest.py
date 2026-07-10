from __future__ import annotations

import hashlib
import json
from pathlib import Path

from kaa_data.models import FileInfo


def file_md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build_manifest(sha: str, db_path: Path, sprites_dir: Path, out_path: Path) -> dict[str, FileInfo]:
    files: dict[str, FileInfo] = {}
    files["game.db"] = FileInfo(md5=file_md5(db_path), size=db_path.stat().st_size)

    for category in ("idol_cards", "skill_cards", "drinks"):
        cat_dir = sprites_dir / category
        if not cat_dir.exists():
            continue
        for png in sorted(cat_dir.glob("*.png")):
            key = f"{category}/{png.name}"
            files[key] = FileInfo(md5=file_md5(png), size=png.stat().st_size)

    payload = {
        "version": sha,
        "files": {k: {"md5": v.md5, "size": v.size} for k, v in files.items()},
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return files