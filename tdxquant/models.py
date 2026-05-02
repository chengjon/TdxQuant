from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

from .result_contract import (
    DEFAULT_CAPABILITY_VERSION,
    DEFAULT_SCHEMA_VERSION,
    PROVIDER_NAME,
    PROVIDER_VERSION,
    build_runtime_metadata,
)


class ErrorCode(str, Enum):
    OK = "ok"
    UNSUPPORTED_PLATFORM = "unsupported_platform"
    PATH_NOT_FOUND = "path_not_found"
    WINDOW_NOT_FOUND = "window_not_found"
    CONTROL_NOT_FOUND = "control_not_found"
    INVALID_REQUEST = "invalid_request"
    EXECUTION_FAILED = "execution_failed"


@dataclass(slots=True)
class ControlInfo:
    hwnd: int
    class_name: str
    text: str
    parent_hwnd: int | None
    rect: tuple[int, int, int, int] | None
    child_index: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DetectionResult:
    code_hwnd: int | None = None
    price_hwnd: int | None = None
    quantity_hwnd: int | None = None
    buy_button_hwnd: int | None = None
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class OrderRequest:
    code: str
    quantity: int
    price: str | None = None
    dry_run: bool = False

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.code.isdigit() or len(self.code) != 6:
            issues.append("stock code must be a 6-digit numeric string")
        if self.quantity <= 0 or self.quantity % 100 != 0:
            issues.append("quantity must be a positive multiple of 100")
        if self.price is not None:
            try:
                if float(self.price) <= 0:
                    issues.append("price must be positive")
            except ValueError:
                issues.append("price must be parseable as a number")
        return issues


@dataclass(slots=True)
class Result:
    ok: bool
    code: ErrorCode
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    next_action: str | None = None
    _provider_contract: dict[str, Any] | None = field(default=None, repr=False, compare=False)
    _provider_artifacts: list[dict[str, Any]] | None = field(default=None, repr=False, compare=False)

    def to_dict(self) -> dict[str, Any]:
        if self._provider_contract is not None:
            return self.to_provider_dict()
        return {
            "ok": self.ok,
            "code": self.code.value,
            "message": self.message,
            "data": self.data,
            "warnings": self.warnings,
            "next_action": self.next_action,
        }

    def to_provider_dict(
        self,
        *,
        capability: str | None = None,
        capability_version: str | None = None,
        schema_version: str | None = None,
        request_id: str | None = None,
        started_at: str | None = None,
        finished_at: str | None = None,
        elapsed_ms: float | int | None = None,
        runtime: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        contract = dict(self._provider_contract or {})
        payload_data = dict(self.data)
        if self.next_action is not None and "next_action" not in payload_data:
            payload_data["next_action"] = self.next_action
        artifacts = contract.get("artifacts")
        if self._provider_artifacts is not None and artifacts in (None, []):
            artifacts = list(self._provider_artifacts)
        elif artifacts is None:
            maybe_artifacts = payload_data.pop("artifacts", None)
            artifacts = list(maybe_artifacts) if isinstance(maybe_artifacts, list) else []
        warnings = contract.get("warnings")
        if warnings is None:
            warnings = list(self.warnings)
        return {
            "success": self.ok,
            "ok": self.ok,
            "code": self.code.value,
            "message": self.message,
            "capability": capability or contract.get("capability") or "unknown",
            "capability_version": capability_version or contract.get("capability_version") or DEFAULT_CAPABILITY_VERSION,
            "schema_version": schema_version or contract.get("schema_version") or DEFAULT_SCHEMA_VERSION,
            "request_id": request_id or contract.get("request_id"),
            "started_at": started_at or contract.get("started_at"),
            "finished_at": finished_at or contract.get("finished_at"),
            "elapsed_ms": elapsed_ms if elapsed_ms is not None else contract.get("elapsed_ms"),
            "runtime": runtime or contract.get("runtime") or build_runtime_metadata(mode="direct", extra={"provider": PROVIDER_NAME, "provider_version": PROVIDER_VERSION}),
            "warnings": list(warnings),
            "data": payload_data,
            "artifacts": list(artifacts),
        }
