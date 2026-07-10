from __future__ import annotations

import json
import subprocess
from pathlib import Path

from kaa_data.models import BuildReport, FetchReport, FileInfo, SkippedAsset


def gakumasu_diff_sha(gakumasu_diff: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(gakumasu_diff), "rev-parse", "HEAD"],
        text=True,
    ).strip()


def needs_release(sha: str, *, force: bool = False) -> bool:
    if force:
        return True
    try:
        result = subprocess.run(
            ["gh", "release", "list", "--limit", "1", "--json", "tagName", "-q", ".[0].tagName"],
            capture_output=True,
            text=True,
            check=False,
        )
        last_tag = (result.stdout or "").strip() or "none"
        last_sha = last_tag.removeprefix("data-")
        return sha != last_sha
    except FileNotFoundError:
        return True


def write_release_notes(sha: str, skipped: list[SkippedAsset], out_path: Path) -> None:
    notes = f"gakumasu-diff commit: {sha}"
    if skipped:
        notes += f"\n\n## Skipped Assets ({len(skipped)})\n\n"
        notes += (
            "These assets are referenced in game master data but not yet available on the game CDN.\n"
            "They will be included in a future build when the CDN is updated.\n\n"
        )
        notes += "| Asset ID | Reference | Reason |\n| --- | --- | --- |\n"
        for item in skipped:
            notes += f"| {item.asset_name} | {item.ref_id} | {item.reason} |\n"
    out_path.write_text(notes, encoding="utf-8")


def write_build_report(path: Path, report: BuildReport) -> None:
    payload = {
        "gakumasu_diff_sha": report.gakumasu_diff_sha,
        "backend": report.backend,
        "tasks_total": report.tasks_total,
        "tasks_ok": report.tasks_ok,
        "tasks_failed": [t.asset_name for t in report.tasks_failed],
        "skipped": [s.to_json() for s in report.skipped],
        "output_files": {
            k: {"md5": v.md5, "size": v.size} for k, v in report.output_files.items()
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def publish_release(
    tag: str,
    sha: str,
    release_dir: Path,
    skipped: list[SkippedAsset],
    notes_path: Path,
) -> None:
    write_release_notes(sha, skipped, notes_path)
    assets = [
        release_dir / "manifest.json",
        release_dir / "game.db.zst",
        release_dir / "idol_cards.zip",
        release_dir / "skill_cards.zip",
        release_dir / "drinks.zip",
    ]
    cmd = [
        "gh",
        "release",
        "create",
        tag,
        "--title",
        f"Game Data {sha}",
        "--notes-file",
        str(notes_path),
        *[str(p) for p in assets if p.exists()],
    ]
    subprocess.run(cmd, check=True)


def make_build_report(
    sha: str,
    backend: str,
    fetch_report: FetchReport,
    output_files: dict[str, FileInfo],
) -> BuildReport:
    return BuildReport(
        gakumasu_diff_sha=sha,
        backend=backend,
        tasks_total=fetch_report.tasks_total,
        tasks_ok=fetch_report.tasks_ok,
        tasks_failed=fetch_report.tasks_failed,
        skipped=fetch_report.skipped,
        output_files=output_files,
    )