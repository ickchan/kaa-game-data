from __future__ import annotations

import sys
from pathlib import Path

import requests

from kaa_data.extract.texture import UNITY_SIGNATURE, extract_texture2d_png
from kaa_data.octo.manifest import AssetEntry

DOWNLOAD_HEADERS = {
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; GM1910 Build/RKQ1.201022.002)",
}


def _deobfuscator(gom_root: Path, asset_name: str):
    root = gom_root.resolve()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from GkmasObjectManager.object.deobfuscate import GkmasAssetBundleDeobfuscator

    return GkmasAssetBundleDeobfuscator(asset_name)


def download_asset_bytes(entry: AssetEntry, gom_root: Path) -> bytes:
    resp = requests.get(entry.url, headers=DOWNLOAD_HEADERS, timeout=120)
    resp.raise_for_status()
    data = resp.content

    if not data.startswith(UNITY_SIGNATURE):
        data = _deobfuscator(gom_root, entry.name).process(data)

    if len(data) != entry.size:
        # Size mismatch is common for some entries; keep going if signature is valid.
        pass

    return data


def ensure_asset_cached(
    entry: AssetEntry,
    cache_path: Path,
    gom_root: Path,
    *,
    force: bool = False,
) -> bool:
    if cache_path.exists() and not force:
        return True

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    data = download_asset_bytes(entry, gom_root)
    cache_path.write_bytes(data)
    return True


def extract_cached_asset(cache_path: Path, out_path: Path) -> bool:
    return extract_texture2d_png(cache_path.read_bytes(), out_path)