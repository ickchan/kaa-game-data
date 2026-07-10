from __future__ import annotations

from pathlib import Path

import zstandard as zstd


def compress_db(db_path: Path, out_path: Path, *, level: int = 19) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cctx = zstd.ZstdCompressor(level=level)
    with db_path.open("rb") as f_in, out_path.open("wb") as f_out:
        cctx.copy_stream(f_in, f_out)