from __future__ import annotations

import importlib
import importlib.util
import os
from dataclasses import replace
from datetime import date, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from ..block_mutation import apply_block_mutation_safety
from ..block_snapshot import BlockSnapshotRequest, normalize_block_snapshot
from ..block_sync import sync_watchlist_to_block
from ..desktop.inspect import find_main_window
from ..formula_screen import build_formula_screen_payload
from ..models import ErrorCode, Result
from ..provider_discovery import build_capability_discovery_payload
from ..serialization import serialize_value
from ..desktop.win32 import IS_WINDOWS

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    pd = None

try:
    from serial.tools import list_ports
except ImportError:  # pragma: no cover
    list_ports = None

_TQCENTER_MODULE_CACHE: dict[str, Any] = {}
_TQCENTER_DLL_DIRECTORY_HANDLES: list[Any] = []


def _unsupported_result(action: str) -> Result | None:
    if IS_WINDOWS:
        return None
    return Result(
        ok=False,
        code=ErrorCode.UNSUPPORTED_PLATFORM,
        message=f"{action} is only available from native Windows Python",
        next_action="Run the command from Windows Python instead of WSL/Linux.",
    )


def _default_strategy_path() -> str:
    return str(Path(__file__).resolve())


def _list_serial_ports() -> list[dict[str, Any]]:
    if list_ports is None:
        return []
    ports = []
    for port in list_ports.comports():
        ports.append(
            {
                "device": port.device,
                "name": port.name,
                "description": port.description,
                "hwid": port.hwid,
            }
        )
    return ports


def _dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for item in values:
        normalized = item.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)
    return deduped


def _build_probe_check(
    status: str,
    summary: str,
    *,
    detail: Any | None = None,
    recommended_action: str | None = None,
    critical: bool = False,
) -> dict[str, Any]:
    payload = {
        "status": status,
        "summary": summary,
        "critical": critical,
    }
    if detail is not None:
        payload["detail"] = serialize_value(detail)
    if recommended_action:
        payload["recommended_action"] = recommended_action
    return payload


def _probe_platform() -> dict[str, Any]:
    if IS_WINDOWS:
        return _build_probe_check("ok", "native Windows Python is available", detail={"platform": "Windows"}, critical=True)
    return _build_probe_check(
        "failed",
        "native Windows Python is unavailable",
        detail={"platform": "non_windows"},
        recommended_action="Run the provider from native Windows Python instead of WSL/Linux.",
        critical=True,
    )


def _probe_tqcenter_module(strategy_path: str | None = None) -> dict[str, Any]:
    tq_class, info = _load_tqcenter(strategy_path)
    if tq_class is None:
        return _build_probe_check(
            "failed",
            "tqcenter module is unavailable",
            detail=info,
            recommended_action="Verify tqcenter, TPythClient.dll, and TongDaXin runtime dependencies are installed.",
            critical=True,
        )
    return _build_probe_check("ok", "tqcenter module is available", detail=info, critical=True)


def _probe_query_runtime(strategy_path: str | None = None) -> dict[str, Any]:
    if not IS_WINDOWS:
        return _build_probe_check(
            "failed",
            "query runtime requires native Windows Python",
            detail={"strategy_path": strategy_path or _default_strategy_path()},
            recommended_action="Run the provider from native Windows Python instead of WSL/Linux.",
            critical=True,
        )
    tq_class, info = _init_tqcenter(strategy_path)
    if tq_class is None:
        return _build_probe_check(
            "failed",
            "query runtime initialization failed",
            detail=info,
            recommended_action="Confirm TongDaXin is running and the Windows TdxQuant runtime initializes successfully.",
            critical=True,
        )
    try:
        return _build_probe_check("ok", "query runtime initialized successfully", detail=info, critical=True)
    finally:
        try:
            tq_class.close()
        except Exception:
            pass


def _probe_subscription_runtime(strategy_path: str | None = None) -> dict[str, Any]:
    session = TdxRuntimeSubscriptionSession(strategy_path=strategy_path)
    try:
        if session._initial_error is not None or session._tq_class is None:
            initial_error = session._initial_error.to_dict() if session._initial_error is not None else None
            return _build_probe_check(
                "failed",
                "subscription runtime initialization failed",
                detail={
                    "runtime_info": session._runtime_info,
                    "initial_error": initial_error,
                    "strategy_path": session.strategy_path,
                },
                recommended_action=(
                    session._initial_error.next_action
                    if session._initial_error is not None
                    else "Confirm TongDaXin runtime subscription support is available."
                ),
                critical=True,
            )
        return _build_probe_check(
            "ok",
            "subscription runtime initialized successfully",
            detail={"strategy_path": session.strategy_path, "runtime_info": session._runtime_info},
            critical=True,
        )
    finally:
        session.close()


def _probe_desktop_window(window_key: str) -> dict[str, Any]:
    if not IS_WINDOWS:
        return _build_probe_check(
            "unsupported",
            "desktop window probing is only available from native Windows Python",
            detail={"window_key": window_key},
        )
    result = find_main_window(window_key)
    if result.ok:
        return _build_probe_check("ok", "desktop window probe succeeded", detail=result.to_dict())
    return _build_probe_check(
        "failed",
        "desktop window probe failed",
        detail=result.to_dict(),
        recommended_action=result.next_action,
    )


def _probe_hid(requested_port: str | None = None) -> dict[str, Any]:
    if list_ports is None:
        return _build_probe_check(
            "unsupported",
            "serial port enumeration is unavailable",
            detail={"requested_port": requested_port},
            recommended_action="Install pyserial if HID probing is required.",
        )
    ports = _list_serial_ports()
    detail = {
        "requested_port": requested_port,
        "ports": ports,
    }
    if requested_port:
        requested_found = any(str(port.get("device", "")).lower() == requested_port.lower() for port in ports)
        detail["requested_port_found"] = requested_found
        if not requested_found:
            return _build_probe_check(
                "warning",
                f"requested HID port {requested_port} was not found",
                detail=detail,
                recommended_action=f"Connect the HID device and confirm that serial port {requested_port} is visible.",
            )
        return _build_probe_check("ok", f"requested HID port {requested_port} is available", detail=detail)
    if not ports:
        return _build_probe_check(
            "warning",
            "no serial ports are currently enumerated",
            detail=detail,
            recommended_action="Connect the HID device if desktop trade automation is needed.",
        )
    return _build_probe_check("ok", "serial ports are available", detail=detail)


def _derive_provider_overall_status(checks: dict[str, dict[str, Any]]) -> str:
    critical_failure = any(
        check.get("critical") and check.get("status") in {"failed", "unsupported"} for check in checks.values()
    )
    if critical_failure:
        return "unavailable"
    any_issue = any(check.get("status") != "ok" for check in checks.values())
    if any_issue:
        return "degraded"
    return "ok"


def _collect_provider_warnings_and_actions(checks: dict[str, dict[str, Any]]) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    actions: list[str] = []
    for check_name, payload in checks.items():
        status = str(payload.get("status", ""))
        if status == "ok":
            continue
        warnings.append(f"{check_name}: {payload.get('summary', '')}")
        action = payload.get("recommended_action")
        if isinstance(action, str) and action:
            actions.append(action)
    return warnings, _dedupe_strings(actions)


def _collect_provider_probe_snapshot(window_key: str, strategy_path: str | None = None, hid_port: str | None = None) -> dict[str, Any]:
    resolved_strategy_path = strategy_path or _default_strategy_path()
    checks = {
        "platform": _probe_platform(),
        "tqcenter_module": _probe_tqcenter_module(strategy_path),
        "query_runtime": _probe_query_runtime(strategy_path),
        "subscription_runtime": _probe_subscription_runtime(strategy_path),
        "desktop_window": _probe_desktop_window(window_key),
        "hid": _probe_hid(hid_port),
    }
    warnings, recommended_actions = _collect_provider_warnings_and_actions(checks)
    return {
        "overall_status": _derive_provider_overall_status(checks),
        "context": {
            "window_key": window_key,
            "strategy_path": resolved_strategy_path,
            "requested_hid_port": hid_port,
        },
        "checks": checks,
        "recommended_actions": recommended_actions,
        "warning_count": len(warnings),
        "warnings": warnings,
    }


def _build_provider_doctor_findings(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    severity_map = {
        "ok": "info",
        "warning": "warning",
        "failed": "error",
        "unsupported": "error",
    }
    findings: list[dict[str, Any]] = []
    checks = snapshot.get("checks", {})
    if isinstance(checks, dict):
        for check_name, payload in checks.items():
            if not isinstance(payload, dict):
                continue
            status = str(payload.get("status", ""))
            if status == "ok":
                continue
            findings.append(
                {
                    "id": check_name,
                    "severity": severity_map.get(status, "error"),
                    "status": status,
                    "summary": payload.get("summary"),
                    "critical": bool(payload.get("critical", False)),
                    "recommended_action": payload.get("recommended_action"),
                }
            )
    if findings:
        return findings
    return [
        {
            "id": "provider-ready",
            "severity": "info",
            "status": "ok",
            "summary": "All provider health checks passed.",
            "critical": False,
        }
    ]


def _candidate_tqcenter_files_from_path(raw_path: str | os.PathLike[str]) -> list[Path]:
    path = Path(raw_path).expanduser()
    candidates: list[Path] = []

    if path.name.lower() == "tqcenter.py":
        candidates.append(path)
    if path.suffix.lower() == ".py":
        candidates.append(path.parent / "tqcenter.py")
        candidates.append(path.parent.parent / "sys" / "tqcenter.py")
        candidates.append(path.parent.parent / "user" / "tqcenter.py")
    else:
        candidates.append(path / "tqcenter.py")
        candidates.append(path / "sys" / "tqcenter.py")
        candidates.append(path / "user" / "tqcenter.py")

    deduped: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate)
        if key not in seen:
            seen.add(key)
            deduped.append(candidate)
    return deduped


def _candidate_tqcenter_files(strategy_path: str | None = None) -> list[Path]:
    candidates: list[Path] = []
    for env_name in ("TDXQUANT_TQCENTER_PATH", "TDXQUANT_PYPLUGINS_DIR"):
        env_value = os.environ.get(env_name)
        if env_value:
            candidates.extend(_candidate_tqcenter_files_from_path(env_value))
    if strategy_path:
        candidates.extend(_candidate_tqcenter_files_from_path(strategy_path))

    resolved: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        try:
            if not candidate.exists() or not candidate.is_file():
                continue
            key = str(candidate.resolve())
        except OSError:
            continue
        if key not in seen:
            seen.add(key)
            resolved.append(candidate)
    return resolved


def _add_tqcenter_dll_directories(tqcenter_path: Path) -> None:
    add_dll_directory = getattr(os, "add_dll_directory", None)
    if add_dll_directory is None:
        return
    for directory in (tqcenter_path.parent, tqcenter_path.parent.parent):
        try:
            if directory.exists() and directory.is_dir():
                _TQCENTER_DLL_DIRECTORY_HANDLES.append(add_dll_directory(str(directory)))
        except OSError:
            continue


def _load_external_tqcenter(tqcenter_path: Path) -> Any:
    resolved_path = tqcenter_path.resolve()
    cache_key = str(resolved_path)
    cached = _TQCENTER_MODULE_CACHE.get(cache_key)
    if cached is not None:
        return cached

    _add_tqcenter_dll_directories(resolved_path)
    module_name = f"_tdxquant_external_tqcenter_{len(_TQCENTER_MODULE_CACHE)}"
    spec = importlib.util.spec_from_file_location(module_name, str(resolved_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load tqcenter spec from {resolved_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _TQCENTER_MODULE_CACHE[cache_key] = module
    return module


def _load_tqcenter(strategy_path: str | None = None) -> tuple[Any | None, dict[str, Any]]:
    external_errors: list[str] = []
    for candidate in _candidate_tqcenter_files(strategy_path):
        try:
            module = _load_external_tqcenter(candidate)
        except Exception as exc:
            external_errors.append(f"{candidate}: {exc}")
            continue
        tq_class = getattr(module, "tq", None)
        if tq_class is None:
            external_errors.append(f"{candidate}: tqcenter.tq is unavailable")
            continue
        return tq_class, {
            "available": True,
            "module": "tqcenter",
            "module_path": str(candidate.resolve()),
            "module_source": "external",
        }

    if external_errors:
        return None, {
            "available": False,
            "error": "; ".join(external_errors),
            "module": "tqcenter",
            "module_source": "external",
        }

    try:
        module = importlib.import_module("tqcenter")
    except Exception as exc:
        return None, {"available": False, "error": str(exc), "module": "tqcenter"}
    tq_class = getattr(module, "tq", None)
    if tq_class is None:
        return None, {"available": False, "error": "tqcenter.tq is unavailable", "module": "tqcenter"}
    info = {"available": True, "module": "tqcenter"}
    module_path = getattr(module, "__file__", None)
    if module_path:
        info["module_path"] = str(module_path)
    return tq_class, info


def _init_tqcenter(strategy_path: str | None = None) -> tuple[Any | None, dict[str, Any]]:
    tq_class, info = _load_tqcenter(strategy_path)
    if tq_class is None:
        return None, info
    selected_path = strategy_path or _default_strategy_path()
    try:
        tq_class.initialize(selected_path)
    except Exception as exc:
        failed_info = dict(info)
        failed_info.update({"available": False, "error": str(exc), "strategy_path": selected_path, "module": "tqcenter"})
        return None, failed_info
    ready_info = dict(info)
    ready_info.update({"available": True, "strategy_path": selected_path, "module": "tqcenter"})
    return tq_class, ready_info


def _run_tq_call(action: str, callback, strategy_path: str | None = None) -> Result:
    guard = _unsupported_result(action)
    if guard:
        return guard
    tq_class, info = _init_tqcenter(strategy_path)
    if tq_class is None:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"{action} could not initialize TdxQuant runtime",
            data={"tdx_api": info},
            next_action="Verify the Windows TdxQuant runtime, TPythClient.dll, and TongDaXin client are installed and running.",
        )
    try:
        payload = callback(tq_class)
        return Result(
            ok=True,
            code=ErrorCode.OK,
            message=action,
            data={"tdx_api": info, "result": serialize_value(payload)},
        )
    except ValueError as exc:
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message=str(exc),
            data={"tdx_api": info},
        )
    except Exception as exc:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"{action} failed: {exc}",
            data={"tdx_api": info},
        )
    finally:
        try:
            tq_class.close()
        except Exception:
            pass


def _require_tq_method(tq_class, method_name: str):
    method = getattr(tq_class, method_name, None)
    if method is None:
        raise RuntimeError(f"TdxQuant runtime does not expose `{method_name}` in the current environment")
    return method


def _attach_runtime_hints(result: Result, **hints: Any) -> Result:
    runtime_hints = result.data.setdefault("runtime_hints", {})
    runtime_hints.update(hints)
    return result


class TdxRuntimeSubscriptionSession:
    __slots__ = ("session_id", "strategy_path", "_tq_class", "_runtime_info", "_initial_error", "closed")

    def __init__(self, strategy_path: str | None = None) -> None:
        self.session_id = uuid4().hex
        self.strategy_path = strategy_path or _default_strategy_path()
        self._tq_class = None
        self._runtime_info: dict[str, Any] = {}
        self._initial_error: Result | None = None
        self.closed = False

        guard = _unsupported_result("opened TongDaXin runtime subscription session")
        if guard is not None:
            self._initial_error = guard
            self._runtime_info = {"available": False, "strategy_path": self.strategy_path}
            return

        tq_class, info = _init_tqcenter(self.strategy_path)
        self._runtime_info = dict(info)
        if tq_class is None:
            self._initial_error = Result(
                ok=False,
                code=ErrorCode.EXECUTION_FAILED,
                message="opened TongDaXin runtime subscription session could not initialize TdxQuant runtime",
                data={"tdx_api": info},
                next_action="Verify the Windows TdxQuant runtime, TPythClient.dll, and TongDaXin client are installed and running.",
            )
            return
        self._tq_class = tq_class

    def __enter__(self) -> "TdxRuntimeSubscriptionSession":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _session_metadata(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "strategy_path": self.strategy_path,
            "closed": self.closed,
        }

    def _finalize_result(self, result: Result) -> Result:
        result.data["runtime_session"] = self._session_metadata()
        if self._runtime_info:
            result.data.setdefault("tdx_api", dict(self._runtime_info))
        return result

    def _closed_result(self, action: str) -> Result:
        return self._finalize_result(
            Result(
                ok=False,
                code=ErrorCode.INVALID_REQUEST,
                message=f"{action} failed: runtime subscription session is already closed",
            )
        )

    def _run(self, action: str, callback) -> Result:
        if self._initial_error is not None:
            return self._finalize_result(replace(self._initial_error, data=dict(self._initial_error.data)))
        if self.closed:
            return self._closed_result(action)
        try:
            payload = callback(self._tq_class)
            return self._finalize_result(
                Result(
                    ok=True,
                    code=ErrorCode.OK,
                    message=action,
                    data={"result": serialize_value(payload)},
                )
            )
        except ValueError as exc:
            return self._finalize_result(
                Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message=str(exc),
                )
            )
        except Exception as exc:
            return self._finalize_result(
                Result(
                    ok=False,
                    code=ErrorCode.EXECUTION_FAILED,
                    message=f"{action} failed: {exc}",
                )
            )

    def subscribe_hq(self, stock_list: list[str], callback) -> Result:
        def invoke(tq_class):
            method = _require_tq_method(tq_class, "subscribe_hq")
            return method(stock_list=stock_list, callback=callback)

        return self._run("subscribed TongDaXin runtime行情 updates", invoke)

    def unsubscribe_hq(self, stock_list: list[str]) -> Result:
        def invoke(tq_class):
            method = _require_tq_method(tq_class, "unsubscribe_hq")
            return method(stock_list=stock_list)

        return self._run("unsubscribed TongDaXin runtime行情 updates", invoke)

    def get_subscribe_hq_stock_list(self) -> Result:
        def invoke(tq_class):
            method = _require_tq_method(tq_class, "get_subscribe_hq_stock_list")
            return method()

        return self._run("listed TongDaXin runtime subscribed stocks", invoke)

    def close(self) -> None:
        if self.closed:
            return
        self.closed = True
        if self._tq_class is None:
            return
        try:
            self._tq_class.close()
        except Exception:
            pass


def run_tdx_open_subscription_session(strategy_path: str | None = None) -> TdxRuntimeSubscriptionSession:
    return TdxRuntimeSubscriptionSession(strategy_path=strategy_path)


def run_tdx_subscription_subscribe(stock_list: list[str], strategy_path: str | None = None) -> Result:
    with run_tdx_open_subscription_session(strategy_path=strategy_path) as session:
        result = session.subscribe_hq(stock_list=stock_list, callback=_subscription_one_shot_callback)
    return _attach_subscription_query_metadata(result, action="subscribe_hq", stock_list=stock_list)


def run_tdx_subscription_unsubscribe(stock_list: list[str], strategy_path: str | None = None) -> Result:
    with run_tdx_open_subscription_session(strategy_path=strategy_path) as session:
        result = session.unsubscribe_hq(stock_list=stock_list)
    return _attach_subscription_query_metadata(result, action="unsubscribe_hq", stock_list=stock_list)


def run_tdx_subscription_list(strategy_path: str | None = None) -> Result:
    with run_tdx_open_subscription_session(strategy_path=strategy_path) as session:
        result = session.get_subscribe_hq_stock_list()
    return _attach_subscription_query_metadata(result, action="get_subscribe_hq_stock_list", stock_list=None)


def _subscription_one_shot_callback(*args: Any, **kwargs: Any) -> None:
    return None


def _attach_subscription_query_metadata(
    result: Result,
    *,
    action: str,
    stock_list: list[str] | None,
) -> Result:
    result.data["subscription_query"] = {
        "mode": "one_shot",
        "action": action,
        "stock_list": None if stock_list is None else list(stock_list),
        "foreground_watch_started": False,
        "background_worker_started": False,
        "event_stream_started": False,
    }
    return result


def run_tdx_provider_capabilities() -> Result:
    payload = build_capability_discovery_payload()
    return Result(
        ok=True,
        code=ErrorCode.OK,
        message="listed provider capabilities",
        data=payload,
    )


def run_tdx_provider_health(
    window_key: str,
    strategy_path: str | None = None,
    hid_port: str | None = None,
) -> Result:
    snapshot = _collect_provider_probe_snapshot(window_key=window_key, strategy_path=strategy_path, hid_port=hid_port)
    warnings = list(snapshot.get("warnings", []))
    return Result(
        ok=True,
        code=ErrorCode.OK,
        message="collected provider health diagnostics",
        data=snapshot,
        warnings=warnings,
        next_action=snapshot["recommended_actions"][0] if snapshot.get("recommended_actions") else None,
    )


def run_tdx_provider_doctor(
    window_key: str,
    strategy_path: str | None = None,
    hid_port: str | None = None,
) -> Result:
    snapshot = _collect_provider_probe_snapshot(window_key=window_key, strategy_path=strategy_path, hid_port=hid_port)
    doctor_payload = dict(snapshot)
    doctor_payload["findings"] = _build_provider_doctor_findings(snapshot)
    warnings = list(snapshot.get("warnings", []))
    return Result(
        ok=True,
        code=ErrorCode.OK,
        message="collected provider doctor diagnostics",
        data=doctor_payload,
        warnings=warnings,
        next_action=snapshot["recommended_actions"][0] if snapshot.get("recommended_actions") else None,
    )


def run_tdx_bridge_health(
    window_key: str,
    strategy_path: str | None = None,
    hid_port: str | None = None,
    main_window_result: Result | None = None,
) -> Result:
    guard = _unsupported_result("tdx-bridge-health")
    if guard:
        return guard

    tq_class, tdx_info = _init_tqcenter(strategy_path)
    tdx_runtime_ok = tq_class is not None
    if tq_class is not None:
        try:
            tq_class.close()
        except Exception:
            pass

    windows_result = main_window_result or Result(
        ok=False,
        code=ErrorCode.WINDOW_NOT_FOUND,
        message="TongDaXin main window check was not provided",
    )
    serial_ports = _list_serial_ports()
    hid_status = {
        "available": list_ports is not None,
        "ports": serial_ports,
        "requested_port": hid_port,
        "requested_port_found": any(port["device"].lower() == hid_port.lower() for port in serial_ports) if hid_port else None,
    }
    warnings: list[str] = []
    if not windows_result.ok:
        warnings.append("当前未确认 TongDaXin 主窗口可用；桌面交易与 HID 输入链路可能无法执行。")
    if hid_port and not hid_status["requested_port_found"]:
        warnings.append(f"未找到指定 HID 串口 {hid_port}。")
    if not hid_status["ports"]:
        warnings.append("当前未发现可枚举串口；如果要继续 HID 路线，请确认硬件已连接。")

    ok = tdx_runtime_ok
    return Result(
        ok=ok,
        code=ErrorCode.OK if ok else ErrorCode.EXECUTION_FAILED,
        message="checked TongDaXin bridge health" if ok else "TongDaXin bridge health check failed",
        data={
            "platform": "Windows",
            "window_key": window_key,
            "tdx_api": tdx_info,
            "desktop_window": windows_result.to_dict(),
            "hid": hid_status,
        },
        warnings=warnings,
        next_action=None if ok else "Verify TongDaXin is running and the TdxQuant Python runtime can initialize successfully.",
    )


def _filter_payload_fields(payload: Any, field_list: list[str]) -> Any:
    if not field_list or not isinstance(payload, dict):
        return payload
    requested = {str(field).lower() for field in field_list}
    identity_fields = {"code", "stock", "stock_code", "symbol"}
    return {
        key: value
        for key, value in payload.items()
        if str(key).lower() in requested or str(key).lower() in identity_fields
    }


def run_tdx_full_tick(stock_code: str, field_list: list[str], strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        full_tick = getattr(tq_class, "get_full_tick", None)
        if callable(full_tick):
            payload = full_tick(stock_code=stock_code)
            filter_method = getattr(tq_class, "filter_dict_by_fields", None)
            if field_list and callable(filter_method):
                return filter_method(payload, field_list)
            return _filter_payload_fields(payload, field_list)
        market_snapshot = _require_tq_method(tq_class, "get_market_snapshot")
        return _filter_payload_fields(market_snapshot(stock_code=stock_code, field_list=field_list), field_list)

    return _run_tq_call("fetched TongDaXin full tick data", callback, strategy_path=strategy_path)


def _query_rows_from_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict) and payload.get("type") == "dataframe" and isinstance(payload.get("records"), list):
        return [dict(item) for item in payload["records"] if isinstance(item, dict)]
    if isinstance(payload, list):
        rows: list[dict[str, Any]] = []
        for item in payload:
            if isinstance(item, dict):
                rows.append(dict(item))
            else:
                rows.append({"value": item})
        return rows
    if isinstance(payload, dict):
        return [dict(payload)]
    return []


def _returned_fields(rows: list[dict[str, Any]]) -> list[str]:
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    return fields


def _attach_query_rows(
    result: Result,
    *,
    query_kind: str,
    requested_fields: list[str],
    query_params: dict[str, Any],
    **selectors: Any,
) -> Result:
    if not result.ok:
        return result
    rows = _query_rows_from_payload(_extract_runtime_result_payload(result))
    result.data["rows"] = rows
    result.data["query_meta"] = {
        "query_kind": query_kind,
        "row_count": len(rows),
        "requested_fields": list(requested_fields or []),
        "returned_fields": _returned_fields(rows),
        **selectors,
        "query_params": dict(query_params),
    }
    return result


def run_tdx_data_snapshot(stock_code: str, field_list: list[str], strategy_path: str | None = None) -> Result:
    result = run_tdx_full_tick(stock_code=stock_code, field_list=field_list, strategy_path=strategy_path)
    return _attach_query_rows(
        result,
        query_kind="market.snapshot",
        requested_fields=field_list,
        query_params={},
        symbol=stock_code,
    )


def run_tdx_market_snapshot(stock_code: str, field_list: list[str], strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "get_market_snapshot")
        return method(stock_code=stock_code, field_list=field_list)

    return _run_tq_call("fetched TongDaXin market snapshot via get_market_snapshot", callback, strategy_path=strategy_path)


def run_tdx_data_kline(
    stock_list: list[str],
    period: str,
    start_time: str,
    end_time: str,
    count: int,
    dividend_type: str,
    field_list: list[str],
    fill_data: bool,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        return tq_class.get_market_data(
            field_list=field_list,
            stock_list=stock_list,
            period=period,
            start_time=start_time,
            end_time=end_time,
            count=count,
            dividend_type=dividend_type,
            fill_data=fill_data,
        )

    result = _run_tq_call("fetched TongDaXin kline data", callback, strategy_path=strategy_path)
    return _attach_query_rows(
        result,
        query_kind="market.kline",
        requested_fields=field_list,
        query_params={
            "period": period,
            "count": count,
            "dividend_type": dividend_type,
            "fill_data": fill_data,
        },
        symbols=list(stock_list),
        date_range={"start": start_time, "end": end_time},
    )


def run_tdx_data_stock_info(stock_code: str, field_list: list[str], strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        return tq_class.get_stock_info(stock_code=stock_code, field_list=field_list)

    return _run_tq_call("fetched TongDaXin stock info", callback, strategy_path=strategy_path)


def run_tdx_divid_factors(
    stock_code: str,
    start_time: str,
    end_time: str,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "get_divid_factors")
        return method(stock_code=stock_code, start_time=start_time, end_time=end_time)

    return _run_tq_call("fetched TongDaXin dividend factors", callback, strategy_path=strategy_path)


def run_tdx_ipo_info(
    ipo_type: int,
    ipo_date: int,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "get_ipo_info")
        return method(ipo_type=ipo_type, ipo_date=ipo_date)

    return _run_tq_call("fetched TongDaXin IPO info", callback, strategy_path=strategy_path)


def run_tdx_stock_list(market: str | None, list_type: int, strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "get_stock_list")
        return method(market=market, list_type=list_type)

    result = _run_tq_call("fetched TongDaXin stock list", callback, strategy_path=strategy_path)
    return _attach_query_rows(
        result,
        query_kind="meta.stock_list",
        requested_fields=[],
        query_params={"list_type": list_type},
        market=market,
    )


def run_tdx_more_info(stock_code: str, field_list: list[str], strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "get_more_info")
        return method(stock_code=stock_code, field_list=field_list)

    return _run_tq_call("fetched TongDaXin more stock info", callback, strategy_path=strategy_path)


def run_tdx_cb_info(stock_code: str, field_list: list[str], strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "get_cb_info")
        return method(stock_code=stock_code, field_list=field_list)

    return _run_tq_call("fetched TongDaXin convertible bond info", callback, strategy_path=strategy_path)


def run_tdx_gb_info(stock_code: str, date_list: list[str], count: int, strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "get_gb_info")
        return method(stock_code=stock_code, date_list=date_list, count=count)

    return _run_tq_call("fetched TongDaXin equity structure info", callback, strategy_path=strategy_path)


_QUOTE_FIELD_NAMES = {
    "amount",
    "average",
    "before5minnow",
    "buyp",
    "buyv",
    "downhome",
    "high",
    "inside",
    "inoutflag",
    "itemnum",
    "jjjz",
    "lastclose",
    "low",
    "max",
    "min",
    "now",
    "nowvol",
    "open",
    "outside",
    "sellp",
    "sellv",
    "tickdiff",
    "uphome",
    "volume",
    "xsflag",
    "zafpre3",
    "zangsu",
}


def _looks_like_quote_field_list(field_list: list[str]) -> bool:
    normalized = [str(field).strip() for field in field_list if str(field).strip()]
    if not normalized:
        return False
    return all(field.lower() in _QUOTE_FIELD_NAMES for field in normalized)


def run_tdx_gp_one_data(stock_list: list[str], field_list: list[str], strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        if _looks_like_quote_field_list(field_list):
            method = _require_tq_method(tq_class, "get_market_snapshot")
            return {
                stock_code: method(stock_code=stock_code, field_list=field_list)
                for stock_code in stock_list
            }
        method = _require_tq_method(tq_class, "get_gp_one_data")
        return method(stock_list=stock_list, field_list=field_list)

    return _run_tq_call("fetched TongDaXin gp one data", callback, strategy_path=strategy_path)


def run_tdx_financial_data(
    stock_list: list[str],
    field_list: list[str],
    start_time: str,
    end_time: str,
    report_type: str,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "get_financial_data")
        return method(
            stock_list=stock_list,
            field_list=field_list,
            start_time=start_time,
            end_time=end_time,
            report_type=report_type,
        )

    return _run_tq_call("fetched TongDaXin professional financial data", callback, strategy_path=strategy_path)


def run_tdx_financial_data_by_date(
    stock_list: list[str],
    field_list: list[str],
    year: int,
    mmdd: int,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "get_financial_data_by_date")
        return method(
            stock_list=stock_list,
            field_list=field_list,
            year=year,
            mmdd=mmdd,
        )

    return _run_tq_call("fetched TongDaXin dated professional financial data", callback, strategy_path=strategy_path)


def run_tdx_stock_transaction_data(
    stock_list: list[str],
    field_list: list[str],
    start_time: str,
    end_time: str,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "get_gpjy_value")
        return method(
            stock_list=stock_list,
            field_list=field_list,
            start_time=start_time,
            end_time=end_time,
        )

    return _run_tq_call("fetched TongDaXin stock transaction data", callback, strategy_path=strategy_path)


def run_tdx_stock_transaction_data_by_date(
    stock_list: list[str],
    field_list: list[str],
    year: int,
    mmdd: int,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "get_gpjy_value_by_date")
        return method(
            stock_list=stock_list,
            field_list=field_list,
            year=year,
            mmdd=mmdd,
        )

    return _run_tq_call("fetched TongDaXin dated stock transaction data", callback, strategy_path=strategy_path)


def run_tdx_sector_transaction_data(
    stock_list: list[str],
    field_list: list[str],
    start_time: str,
    end_time: str,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "get_bkjy_value")
        return method(
            stock_list=stock_list,
            field_list=field_list,
            start_time=start_time,
            end_time=end_time,
        )

    return _run_tq_call("fetched TongDaXin sector transaction data", callback, strategy_path=strategy_path)


def run_tdx_sector_transaction_data_by_date(
    stock_list: list[str],
    field_list: list[str],
    year: int,
    mmdd: int,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "get_bkjy_value_by_date")
        return method(
            stock_list=stock_list,
            field_list=field_list,
            year=year,
            mmdd=mmdd,
        )

    return _run_tq_call("fetched TongDaXin dated sector transaction data", callback, strategy_path=strategy_path)


def run_tdx_market_transaction_data(
    field_list: list[str],
    start_time: str,
    end_time: str,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "get_scjy_value")
        return method(
            field_list=field_list,
            start_time=start_time,
            end_time=end_time,
        )

    return _run_tq_call("fetched TongDaXin market transaction data", callback, strategy_path=strategy_path)


def run_tdx_market_transaction_data_by_date(
    field_list: list[str],
    year: int,
    mmdd: int,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "get_scjy_value_by_date")
        return method(
            field_list=field_list,
            year=year,
            mmdd=mmdd,
        )

    return _run_tq_call("fetched TongDaXin dated market transaction data", callback, strategy_path=strategy_path)


def run_tdx_data_sector_list(list_type: int = 0, strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "get_sector_list")
        return method(list_type=list_type)

    return _run_tq_call("fetched TongDaXin sector list", callback, strategy_path=strategy_path)


def run_tdx_data_sector_stocks(
    block_code: str,
    block_type: int,
    list_type: int = 0,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "get_stock_list_in_sector")
        return method(block_code=block_code, block_type=block_type, list_type=list_type)

    return _run_tq_call("fetched TongDaXin sector constituents", callback, strategy_path=strategy_path)


def run_tdx_refresh_cache(market: str, force: bool, strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "refresh_cache")
        return method(market=market, force=force)

    return _run_tq_call("refreshed TongDaXin market cache", callback, strategy_path=strategy_path)


def run_tdx_get_trading_dates(
    market: str,
    start_time: str,
    end_time: str,
    count: int,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "get_trading_dates")
        return method(market=market, start_time=start_time, end_time=end_time, count=count)

    return _run_tq_call("fetched TongDaXin trading dates", callback, strategy_path=strategy_path)


def run_tdx_refresh_kline(
    stock_list: list[str],
    period: str,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "refresh_kline")
        return method(stock_list=stock_list, period=period)

    return _run_tq_call("refreshed TongDaXin historical kline cache", callback, strategy_path=strategy_path)


def run_tdx_download_file(
    stock_code: str,
    down_time: str,
    down_type: int,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "download_file")
        return method(stock_code=stock_code, down_time=down_time, down_type=down_type)

    result = _run_tq_call("downloaded TongDaXin runtime data file", callback, strategy_path=strategy_path)
    return _attach_runtime_hints(
        result,
        download_dir=r".\PYPlugins\data",
        download_dir_host="Windows TdxQuant client workspace",
    )


def run_tdx_send_warn(
    stock_list: list[str],
    time_list: list[str],
    price_list: list[str],
    close_list: list[str],
    volume_list: list[str],
    bs_flag_list: list[str],
    warn_type_list: list[str],
    reason_list: list[str],
    count: int,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "send_warn")
        return method(
            stock_list=stock_list,
            time_list=time_list,
            price_list=price_list,
            close_list=close_list,
            volum_list=volume_list,
            bs_flag_list=bs_flag_list,
            warn_type_list=warn_type_list,
            reason_list=reason_list,
            count=count,
        )

    return _run_tq_call("sent TongDaXin client warn payload", callback, strategy_path=strategy_path)


def run_tdx_send_message(msg_str: str, strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "send_message")
        return method(msg_str)

    return _run_tq_call("sent TongDaXin client message", callback, strategy_path=strategy_path)


def run_tdx_send_file(file: str, strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "send_file")
        return method(file)

    return _run_tq_call("sent TongDaXin client file", callback, strategy_path=strategy_path)


def run_tdx_send_bt_data(
    stock_code: str,
    time_list: list[str],
    data_list: list[list[str]],
    count: int,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "send_bt_data")
        return method(stock_code=stock_code, time_list=time_list, data_list=data_list, count=count)

    return _run_tq_call("sent TongDaXin client backtest data", callback, strategy_path=strategy_path)


def run_tdx_get_user_sector(strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "get_user_sector")
        return method()

    return _run_tq_call("fetched TongDaXin custom sector list", callback, strategy_path=strategy_path)


def run_tdx_block_read_watchlist_snapshot(block_code: str, strategy_path: str | None = None) -> Result:
    sectors_result = run_tdx_get_user_sector(strategy_path=strategy_path)
    if not sectors_result.ok:
        return sectors_result

    sector_entry = _extract_custom_sector_entry(_extract_runtime_result_payload(sectors_result), block_code)
    if sector_entry is None:
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message=f"block_code not found: {block_code}",
        )

    stocks_result = run_tdx_data_sector_stocks(
        block_code=block_code,
        block_type=1,
        list_type=0,
        strategy_path=strategy_path,
    )
    if not stocks_result.ok:
        return stocks_result

    snapshot_result = normalize_block_snapshot(
        BlockSnapshotRequest(
            block_code=block_code,
            sector_name=str(sector_entry.get("Name") or sector_entry.get("name") or block_code).strip(),
            member_codes=_extract_snapshot_member_codes(_extract_runtime_result_payload(stocks_result)),
        )
    )
    return replace(
        snapshot_result,
        warnings=list(sectors_result.warnings) + list(stocks_result.warnings) + list(snapshot_result.warnings),
        next_action=stocks_result.next_action or sectors_result.next_action or snapshot_result.next_action,
    )


def _extract_runtime_result_payload(result: Result) -> Any:
    return result.data.get("result")


def _extract_custom_sector_entry(entries: Any, block_code: str) -> dict[str, Any] | None:
    if not isinstance(entries, list):
        return None
    target = block_code.strip().upper()
    for item in entries:
        if not isinstance(item, dict):
            continue
        code = str(item.get("Code") or item.get("code") or item.get("block_code") or "").strip().upper()
        if code == target:
            return item
    return None


def _extract_sector_stock_codes(payload: Any) -> list[str]:
    if not isinstance(payload, list):
        return []
    stocks: list[str] = []
    for item in payload:
        if isinstance(item, str):
            normalized = item.strip()
            if normalized:
                stocks.append(normalized)
            continue
        if isinstance(item, dict):
            code = str(item.get("Code") or item.get("code") or item.get("stock_code") or "").strip()
            if code:
                stocks.append(code)
    return stocks


def _extract_snapshot_member_codes(payload: Any) -> list[str]:
    member_codes: list[str] = []
    for stock_code in _extract_sector_stock_codes(payload):
        code = str(stock_code).strip()
        if code:
            member_codes.append(code)
    return member_codes


def _probe_custom_sector_state(
    block_code: str,
    *,
    strategy_path: str | None = None,
    include_stocks: bool = False,
) -> dict[str, Any] | Result:
    sectors_result = run_tdx_get_user_sector(strategy_path=strategy_path)
    if not sectors_result.ok:
        return sectors_result
    sector_entry = _extract_custom_sector_entry(_extract_runtime_result_payload(sectors_result), block_code)
    if sector_entry is None:
        return {"block_code": block_code, "exists": False}

    observed_state: dict[str, Any] = {
        "block_code": block_code,
        "exists": True,
        "block_name": sector_entry.get("Name") or sector_entry.get("name") or "",
    }
    if not include_stocks:
        return observed_state

    stocks_result = run_tdx_data_sector_stocks(
        block_code=block_code,
        block_type=1,
        list_type=0,
        strategy_path=strategy_path,
    )
    if not stocks_result.ok:
        return stocks_result
    observed_state["stocks"] = _extract_sector_stock_codes(_extract_runtime_result_payload(stocks_result))
    return observed_state


def run_tdx_create_sector(
    block_code: str,
    block_name: str,
    mutation_key: str | None = None,
    audit_dir: str | None = None,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "create_sector")
        return method(block_code=block_code, block_name=block_name)

    return apply_block_mutation_safety(
        operation="create_sector",
        block_code=block_code,
        block_name=block_name,
        execute_write=lambda: _run_tq_call("created TongDaXin custom sector", callback, strategy_path=strategy_path),
        observed_state=lambda: _probe_custom_sector_state(block_code, strategy_path=strategy_path),
        mutation_key=mutation_key,
        audit_dir=audit_dir,
    )


def run_tdx_delete_sector(
    block_code: str,
    mutation_key: str | None = None,
    audit_dir: str | None = None,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "delete_sector")
        return method(block_code=block_code)

    return apply_block_mutation_safety(
        operation="delete_sector",
        block_code=block_code,
        execute_write=lambda: _run_tq_call("deleted TongDaXin custom sector", callback, strategy_path=strategy_path),
        observed_state=lambda: _probe_custom_sector_state(block_code, strategy_path=strategy_path),
        mutation_key=mutation_key,
        audit_dir=audit_dir,
    )


def run_tdx_rename_sector(
    block_code: str,
    block_name: str,
    mutation_key: str | None = None,
    audit_dir: str | None = None,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "rename_sector")
        return method(block_code=block_code, block_name=block_name)

    return apply_block_mutation_safety(
        operation="rename_sector",
        block_code=block_code,
        block_name=block_name,
        execute_write=lambda: _run_tq_call("renamed TongDaXin custom sector", callback, strategy_path=strategy_path),
        observed_state=lambda: _probe_custom_sector_state(block_code, strategy_path=strategy_path),
        mutation_key=mutation_key,
        audit_dir=audit_dir,
    )


def run_tdx_clear_sector(
    block_code: str,
    mutation_key: str | None = None,
    audit_dir: str | None = None,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "clear_sector")
        return method(block_code=block_code)

    return apply_block_mutation_safety(
        operation="clear_sector",
        block_code=block_code,
        execute_write=lambda: _run_tq_call("cleared TongDaXin custom sector members", callback, strategy_path=strategy_path),
        observed_state=lambda: _probe_custom_sector_state(block_code, strategy_path=strategy_path, include_stocks=True),
        mutation_key=mutation_key,
        audit_dir=audit_dir,
    )


def run_tdx_send_user_block(
    block_code: str,
    stocks: list[str],
    show: bool,
    mutation_key: str | None = None,
    audit_dir: str | None = None,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "send_user_block")
        return method(block_code=block_code, stocks=stocks, show=show)

    return apply_block_mutation_safety(
        operation="send_user_block",
        block_code=block_code,
        stocks=stocks,
        show=show,
        execute_write=lambda: _run_tq_call("updated TongDaXin user block", callback, strategy_path=strategy_path),
        observed_state=lambda: _probe_custom_sector_state(block_code, strategy_path=strategy_path, include_stocks=True),
        mutation_key=mutation_key,
        audit_dir=audit_dir,
    )


def run_tdx_block_sync(
    block_code: str,
    symbols: list[str],
    mode: str = "replace",
    create_if_missing: bool = False,
    dry_run: bool = False,
    show: bool = True,
    write_policy: str | None = None,
    mutation_key: str | None = None,
    audit_dir: str | None = None,
    strategy_path: str | None = None,
) -> Result:
    return sync_watchlist_to_block(
        block_code=block_code,
        symbols=symbols,
        mode=mode,
        create_if_missing=create_if_missing,
        dry_run=dry_run,
        show=show,
        write_policy=write_policy,
        mutation_key=mutation_key,
        observed_state=lambda: _probe_custom_sector_state(block_code, strategy_path=strategy_path, include_stocks=True),
        create_block=lambda: run_tdx_create_sector(
            block_code=block_code,
            block_name=block_code,
            audit_dir=audit_dir,
            strategy_path=strategy_path,
        ),
        sync_members=lambda requested_symbols, requested_show: run_tdx_send_user_block(
            block_code=block_code,
            stocks=requested_symbols,
            show=requested_show,
            audit_dir=audit_dir,
            strategy_path=strategy_path,
        ),
        audit_dir=audit_dir,
    )


def run_tdx_formula_format_data(kline_payload: dict[str, Any], strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "formula_format_data")
        return method(data_dict=kline_payload)

    return _run_tq_call("formatted TongDaXin formula input data", callback, strategy_path=strategy_path)


def run_tdx_formula_set_data(
    stock_code: str,
    stock_period: str,
    stock_data: list[Any],
    count: int,
    dividend_type: int,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "formula_set_data")
        return method(
            stock_code=stock_code,
            stock_period=stock_period,
            stock_data=stock_data,
            count=count,
            dividend_type=dividend_type,
        )

    return _run_tq_call("set TongDaXin formula data", callback, strategy_path=strategy_path)


def run_tdx_formula_set_data_info(
    stock_code: str,
    stock_period: str,
    start_time: str,
    end_time: str,
    count: int,
    dividend_type: int,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "formula_set_data_info")
        return method(
            stock_code=stock_code,
            stock_period=stock_period,
            start_time=start_time,
            end_time=end_time,
            count=count,
            dividend_type=dividend_type,
        )

    return _run_tq_call("set TongDaXin formula data info", callback, strategy_path=strategy_path)


def run_tdx_formula_get_data(strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "formula_get_data")
        return method()

    return _run_tq_call("fetched TongDaXin formula data", callback, strategy_path=strategy_path)


def run_tdx_formula_zb(formula_name: str, formula_arg: str, xsflag: int, strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "formula_zb")
        return method(formula_name=formula_name, formula_arg=formula_arg, xsflag=xsflag)

    return _run_tq_call("executed TongDaXin indicator formula", callback, strategy_path=strategy_path)


def run_tdx_formula_xg(formula_name: str, formula_arg: str, strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "formula_xg")
        return method(formula_name=formula_name, formula_arg=formula_arg)

    return _run_tq_call("executed TongDaXin stock-picking formula", callback, strategy_path=strategy_path)


def run_tdx_formula_exp(formula_name: str, formula_arg: str, strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "formula_exp")
        return method(formula_name=formula_name, formula_arg=formula_arg)

    return _run_tq_call("executed TongDaXin expert formula", callback, strategy_path=strategy_path)


def run_tdx_formula_process_mul_xg(
    formula_name: str,
    formula_arg: str,
    return_count: int,
    return_date: bool,
    stock_list: list[str],
    stock_period: str,
    start_time: str,
    end_time: str,
    count: int,
    dividend_type: int,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "formula_process_mul_xg")
        return method(
            formula_name=formula_name,
            formula_arg=formula_arg,
            return_count=return_count,
            return_date=return_date,
            stock_list=stock_list,
            stock_period=stock_period,
            start_time=start_time,
            end_time=end_time,
            count=count,
            dividend_type=dividend_type,
        )

    return _run_tq_call("executed TongDaXin batch stock-picking formula", callback, strategy_path=strategy_path)


def run_tdx_formula_screen(
    formula_name: str,
    stock_list: list[str],
    *,
    formula_arg: str = "",
    return_count: int = 1,
    return_date: bool = False,
    stock_period: str = "1d",
    start_time: str = "",
    end_time: str = "",
    count: int = 0,
    dividend_type: int = 0,
    strategy_path: str | None = None,
) -> Result:
    raw_result = run_tdx_formula_process_mul_xg(
        formula_name=formula_name,
        formula_arg=formula_arg,
        return_count=return_count,
        return_date=return_date,
        stock_list=stock_list,
        stock_period=stock_period,
        start_time=start_time,
        end_time=end_time,
        count=count,
        dividend_type=dividend_type,
        strategy_path=strategy_path,
    )
    if not raw_result.ok:
        return raw_result
    raw_payload = raw_result.data.get("result")
    try:
        normalized = build_formula_screen_payload(
            raw_payload,
            formula_name=formula_name,
            stock_list=stock_list,
            formula_arg=formula_arg,
            return_count=return_count,
            return_date=return_date,
            stock_period=stock_period,
            start_time=start_time,
            end_time=end_time,
            count=count,
            dividend_type=dividend_type,
        )
    except ValueError as exc:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"formula screen normalization failed: {exc}",
            data={"raw_result": raw_result.to_dict()},
            warnings=list(raw_result.warnings),
            next_action="Inspect the raw formula_process_mul_xg payload shape and refine the formula screen normalization rules.",
        )
    return Result(
        ok=True,
        code=ErrorCode.OK,
        message="executed TongDaXin formula screen",
        data=normalized,
        warnings=list(raw_result.warnings),
        next_action=raw_result.next_action,
    )


def run_tdx_formula_process_mul_zb(
    formula_name: str,
    formula_arg: str,
    xsflag: int,
    return_count: int,
    return_date: bool,
    stock_list: list[str],
    stock_period: str,
    start_time: str,
    end_time: str,
    count: int,
    dividend_type: int,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "formula_process_mul_zb")
        return method(
            formula_name=formula_name,
            formula_arg=formula_arg,
            xsflag=xsflag,
            return_count=return_count,
            return_date=return_date,
            stock_list=stock_list,
            stock_period=stock_period,
            start_time=start_time,
            end_time=end_time,
            count=count,
            dividend_type=dividend_type,
        )

    return _run_tq_call("executed TongDaXin batch indicator formula", callback, strategy_path=strategy_path)


# ---------------------------------------------------------------------------
# Group B: documented-only functions (forward-compatible via _require_tq_method)
# ---------------------------------------------------------------------------


def run_tdx_get_relation(stock_code: str, relation_type: int, strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "get_relation")
        return method(stock_code=stock_code, relation_type=relation_type)

    return _run_tq_call("fetched TongDaXin stock relation data", callback, strategy_path=strategy_path)


def run_tdx_gb_info_by_date(stock_code: str, date: str, strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "gb_info_by_date")
        return method(stock_code=stock_code, date=date)

    return _run_tq_call("fetched TongDaXin stock board info by date", callback, strategy_path=strategy_path)


def run_tdx_get_pricevol(
    stock_code: str,
    period: str,
    start_time: str,
    end_time: str,
    count: int,
    dividend_type: str,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "get_pricevol")
        return method(
            stock_code=stock_code,
            period=period,
            start_time=start_time,
            end_time=end_time,
            count=count,
            dividend_type=dividend_type,
        )

    return _run_tq_call("fetched TongDaXin price-volume data", callback, strategy_path=strategy_path)


def run_tdx_get_trackzs_etf_info(stock_code: str, strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "get_trackzs_etf_info")
        return method(stock_code=stock_code)

    return _run_tq_call("fetched TongDaXin ETF tracking index info", callback, strategy_path=strategy_path)


def run_tdx_formula_get_all(strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "formula_get_all")
        return method()

    return _run_tq_call("fetched TongDaXin all formula list", callback, strategy_path=strategy_path)


def run_tdx_formula_get_info(formula_name: str, strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "formula_get_info")
        return method(formula_name=formula_name)

    return _run_tq_call("fetched TongDaXin formula info", callback, strategy_path=strategy_path)


def run_tdx_print_to_tdx(
    df_list: list,
    sp_name: str = "",
    xml_filename: str = "",
    jsn_filenames: list[str] | None = None,
    vertical: int | None = None,
    horizontal: int | None = None,
    height: list | None = None,
    table_names: list[str] | None = None,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "print_to_tdx")
        return method(
            df_list=df_list,
            sp_name=sp_name,
            xml_filename=xml_filename,
            jsn_filenames=jsn_filenames or [],
            vertical=vertical,
            horizontal=horizontal,
            height=height or [],
            table_names=table_names or [],
        )

    return _run_tq_call("exported data to TongDaXin client", callback, strategy_path=strategy_path)


def run_tdx_exec_to_tdx(url: str, strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "exec_to_tdx")
        return method(url=url)

    return _run_tq_call("executed TongDaXin client command", callback, strategy_path=strategy_path)


# ---------------------------------------------------------------------------
# Group C: trading domain functions
# ---------------------------------------------------------------------------


def run_tdx_stock_account(account: str, account_type: str, strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "stock_account")
        return method(account=account, account_type=account_type)

    return _run_tq_call("acquired TongDaXin stock account handle", callback, strategy_path=strategy_path)


def run_tdx_order_stock(
    account_id: int,
    stock_code: str,
    order_type: int,
    order_volume: int,
    price_type: int,
    price: float,
    strategy_path: str | None = None,
) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "order_stock")
        return method(
            account_id=account_id,
            stock_code=stock_code,
            order_type=order_type,
            order_volume=order_volume,
            price_type=price_type,
            price=price,
        )

    return _run_tq_call("submitted TongDaXin stock order", callback, strategy_path=strategy_path)


def run_tdx_query_stock_orders(account_id: int, stock_code: str, strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "query_stock_orders")
        return method(account_id=account_id, stock_code=stock_code)

    return _run_tq_call("queried TongDaXin stock orders", callback, strategy_path=strategy_path)


def run_tdx_query_stock_positions(account_id: int, strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "query_stock_positions")
        return method(account_id=account_id)

    return _run_tq_call("queried TongDaXin stock positions", callback, strategy_path=strategy_path)


def run_tdx_cancel_order_stock(account_id: int, stock_code: str, order_id: str, strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "cancel_order_stock")
        return method(account_id=account_id, stock_code=stock_code, order_id=order_id)

    return _run_tq_call("cancelled TongDaXin stock order", callback, strategy_path=strategy_path)


def run_tdx_query_stock_asset(account_id: int, strategy_path: str | None = None) -> Result:
    def callback(tq_class):
        method = _require_tq_method(tq_class, "query_stock_asset")
        return method(account_id=account_id)

    return _run_tq_call("queried TongDaXin stock asset", callback, strategy_path=strategy_path)
