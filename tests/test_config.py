from pathlib import Path

from kaa_data.config import PipelineConfig


def test_load_config():
    root = Path(__file__).resolve().parents[1]
    config = PipelineConfig.load(root)
    assert config.gakumasu_diff.name == "gakumasu-diff"
    assert config.default_backend == "gom"