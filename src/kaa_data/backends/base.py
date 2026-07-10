from __future__ import annotations

from typing import Protocol

from kaa_data.config import PipelineConfig
from kaa_data.models import AssetTask, FetchReport, TaskManifest


class AssetBackend(Protocol):
    name: str

    def healthcheck(self, config: PipelineConfig) -> None: ...

    def ensure_cache(self, config: PipelineConfig, *, force: bool = False) -> int: ...

    def fetch(self, config: PipelineConfig, manifest: TaskManifest, *, force: bool = False) -> FetchReport: ...