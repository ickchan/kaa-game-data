import sqlite3
from pathlib import Path

from kaa_data.tasks.builder import build_tasks


def test_build_tasks_from_minimal_db(tmp_path: Path):
    db_path = tmp_path / "game.db"
    sprites_dir = tmp_path / "sprites"
    conn = sqlite3.connect(db_path)
    conn.executescript(
        """
        CREATE TABLE IdolCardSkin (id TEXT, assetId TEXT);
        CREATE TABLE ProduceCard (assetId TEXT, isCharacterAsset INTEGER);
        CREATE TABLE ProduceDrink (assetId TEXT);
        INSERT INTO IdolCardSkin VALUES ('skin-1', 'cidol-hski-3-001');
        """
    )
    conn.commit()
    conn.close()

    manifest = build_tasks(db_path, sprites_dir)
    assert len(manifest.tasks) == 2
    assert manifest.tasks[0].asset_name.endswith("-thumb-portrait")