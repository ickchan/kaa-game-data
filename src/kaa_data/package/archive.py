from __future__ import annotations

import zipfile
from pathlib import Path


def zip_directory(source_dir: Path, zip_path: Path) -> None:
    if not source_dir.exists():
        return
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(source_dir.rglob("*")):
            if file.is_file():
                zf.write(file, file.relative_to(source_dir).as_posix())