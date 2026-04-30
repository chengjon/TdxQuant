from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

PROVIDER_NAME = "tdxquant"
PROVIDER_VERSION = "dev"
DEFAULT_CAPABILITY_VERSION = "v1"
DEFAULT_SCHEMA_VERSION = "2026-04-28"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def format_rfc3339(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def build_runtime_metadata(*, mode: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "provider": PROVIDER_NAME,
        "provider_version": PROVIDER_VERSION,
        "mode": mode,
    }
    if extra:
        metadata.update(extra)
    return metadata
