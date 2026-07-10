from __future__ import annotations

import subprocess
from pathlib import Path


def _git_apply(patch_file: Path, *, cwd: Path, reverse: bool = False) -> subprocess.CompletedProcess[str]:
    cmd = ["git", "apply"]
    if reverse:
        cmd.append("--reverse")
    cmd.extend(["--check", str(patch_file)])
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def apply_patches(root: Path) -> None:
    patches_dir = root / "patches"
    if not patches_dir.exists():
        return

    for patch_file in sorted(patches_dir.rglob("*.patch")):
        # patches/campus/001-foo.patch -> campus
        vendor_name = patch_file.relative_to(patches_dir).parts[0]
        vendor_root = root / vendor_name
        if not vendor_root.exists():
            print(f"Skip patch {patch_file.name}: vendor {vendor_name} not found")
            continue

        rel = patch_file.relative_to(root)
        if _git_apply(patch_file, cwd=vendor_root).returncode == 0:
            result = subprocess.run(
                ["git", "apply", str(patch_file)],
                cwd=vendor_root,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print(f"Applied {rel}")
            else:
                print(f"Failed to apply {rel}: {result.stderr.strip()}")
        elif _git_apply(patch_file, cwd=vendor_root, reverse=True).returncode == 0:
            print(f"Already applied: {rel}")
        else:
            print(f"Patch does not apply: {rel}")


def vendor_sync(root: Path | None = None) -> None:
    root = (root or Path.cwd()).resolve()

    if (root / ".git").exists():
        subprocess.run(
            ["git", "submodule", "update", "--init", "--recursive"],
            cwd=root,
            check=False,
        )

    apply_patches(root)
    print("Vendor sync complete")