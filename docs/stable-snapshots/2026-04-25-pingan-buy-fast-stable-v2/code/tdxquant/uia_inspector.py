from __future__ import annotations

import re
import time
from types import SimpleNamespace
from typing import Any

from .models import ErrorCode, Result
from .win32_api import (
    IS_WINDOWS,
    click,
    click_screen_point,
    enumerate_child_windows,
    enumerate_top_windows,
    focus_window,
    get_class_name,
    get_control_id,
    get_foreground_window,
    get_parent,
    get_text,
    restore_foreground_window,
    send_enter,
    send_wm_command,
    set_text,
)
from .hid_bridge import run_hid_send

if IS_WINDOWS:
    from pywinauto import Desktop
else:
    Desktop = None


def inspect_uia_windows(title_keyword: str | None = None) -> Result:
    if not IS_WINDOWS:
        return Result(
            ok=False,
            code=ErrorCode.UNSUPPORTED_PLATFORM,
            message="UIA window enumeration is only available from native Windows Python",
            next_action="Run the UIA window command from Windows Python.",
        )

    items: list[dict[str, Any]] = []
    try:
        windows = Desktop(backend="uia").windows()
    except Exception as exc:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"failed to enumerate desktop windows: {exc}",
        )

    for window in windows:
        try:
            info = window.element_info
            name = getattr(info, "name", "") or ""
            class_name = getattr(info, "class_name", "") or ""
            if title_keyword and title_keyword not in name and title_keyword not in class_name:
                continue
            rect = getattr(info, "rectangle", None)
            items.append(
                {
                    "name": name,
                    "class_name": class_name,
                    "control_type": getattr(info, "control_type", "") or "",
                    "automation_id": getattr(info, "automation_id", "") or "",
                    "handle": getattr(info, "handle", None),
                    "rectangle": (
                        [rect.left, rect.top, rect.right, rect.bottom]
                        if rect is not None and hasattr(rect, "left")
                        else None
                    ),
                    "visible": getattr(window, "is_visible", lambda: None)(),
                    "enabled": getattr(window, "is_enabled", lambda: None)(),
                }
            )
        except Exception:
            continue

    return Result(
        ok=True,
        code=ErrorCode.OK,
        message="enumerated desktop UIA windows",
        data={"title_keyword": title_keyword, "windows": items},
    )


def inspect_uia_dialogs(
    title_keyword: str | None = None,
    max_depth: int = 4,
    include_all_windows: bool = False,
) -> Result:
    if not IS_WINDOWS:
        return Result(
            ok=False,
            code=ErrorCode.UNSUPPORTED_PLATFORM,
            message="UIA dialog inspection is only available from native Windows Python",
            next_action="Run the UIA dialog command from Windows Python.",
        )

    try:
        windows = Desktop(backend="uia").windows()
    except Exception as exc:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"failed to enumerate desktop windows: {exc}",
        )

    dialogs: list[dict[str, Any]] = []
    for window in windows:
        try:
            info = window.element_info
            name = getattr(info, "name", "") or ""
            class_name = getattr(info, "class_name", "") or ""
            control_type = getattr(info, "control_type", "") or ""
            is_visible = bool(getattr(window, "is_visible", lambda: False)())
            if not is_visible:
                continue
            if title_keyword and title_keyword not in name and title_keyword not in class_name:
                continue
            if not include_all_windows and class_name != "#32770":
                continue
            dialogs.append(_serialize_uia_subtree(window, max_depth=max_depth))
        except Exception:
            continue

    dialogs.sort(key=lambda item: _uia_dialog_score(item), reverse=True)
    return Result(
        ok=bool(dialogs),
        code=ErrorCode.OK if dialogs else ErrorCode.WINDOW_NOT_FOUND,
        message="enumerated UIA dialogs" if dialogs else "could not find matching UIA dialogs",
        data={
            "title_keyword": title_keyword,
            "max_depth": max_depth,
            "include_all_windows": include_all_windows,
            "dialogs": dialogs,
        },
        next_action=None if dialogs else "在弹窗仍然可见时重试；若它不是标准对话框，可加 --include-all-windows。",
    )


def wait_for_uia_dialog(
    title_keyword: str | None = None,
    max_depth: int = 4,
    include_all_windows: bool = False,
    timeout: float = 8.0,
    poll_interval: float = 0.25,
    exclude_handle: int | None = None,
    exclude_class_names: list[str] | None = None,
    exclude_handles: list[int] | None = None,
    baseline_handles: list[int] | None = None,
    require_new_handle: bool = False,
    foreground_only: bool = False,
) -> Result:
    if not IS_WINDOWS:
        return Result(
            ok=False,
            code=ErrorCode.UNSUPPORTED_PLATFORM,
            message="UIA dialog wait is only available from native Windows Python",
            next_action="Run the UIA dialog wait command from Windows Python.",
        )

    deadline = time.time() + timeout
    last_result: Result | None = None
    excluded = set(exclude_class_names or [])
    excluded_handles = {int(handle) for handle in (exclude_handles or [])}
    if exclude_handle is not None:
        excluded_handles.add(int(exclude_handle))
    baseline = {int(handle) for handle in (baseline_handles or [])}
    while time.time() < deadline:
        result = inspect_uia_dialogs(
            title_keyword=title_keyword,
            max_depth=max_depth,
            include_all_windows=include_all_windows,
        )
        last_result = result
        dialogs = list(result.data.get("dialogs", [])) if result.data else []
        foreground_hwnd = get_foreground_window() if foreground_only else None
        filtered = []
        for dialog in dialogs:
            root = dialog.get("root", {})
            handle = root.get("handle")
            class_name = str(root.get("class_name", "") or "")
            if handle is not None:
                handle = int(handle)
            if handle is not None and handle in excluded_handles:
                continue
            if class_name in excluded:
                continue
            if foreground_only and foreground_hwnd is not None and handle != foreground_hwnd:
                continue
            if require_new_handle and handle is not None and handle in baseline:
                continue
            filtered.append(dialog)
        if filtered:
            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="captured UIA dialog after waiting",
                data={
                    "title_keyword": title_keyword,
                    "max_depth": max_depth,
                    "include_all_windows": include_all_windows,
                    "timeout": timeout,
                    "poll_interval": poll_interval,
                    "foreground_only": foreground_only,
                    "require_new_handle": require_new_handle,
                    "baseline_handles": sorted(baseline),
                    "dialogs": filtered,
                },
            )
        time.sleep(max(0.05, poll_interval))

    if last_result is not None:
        return Result(
            ok=False,
            code=last_result.code,
            message="timed out waiting for UIA dialog",
            data={
                "title_keyword": title_keyword,
                "max_depth": max_depth,
                "include_all_windows": include_all_windows,
                "timeout": timeout,
                "poll_interval": poll_interval,
                "foreground_only": foreground_only,
                "require_new_handle": require_new_handle,
                "baseline_handles": sorted(baseline),
                "dialogs": [],
            },
            next_action="先触发目标弹窗，再增大 --timeout 重试。",
        )
    return Result(
        ok=False,
        code=ErrorCode.WINDOW_NOT_FOUND,
        message="timed out waiting for UIA dialog",
        data={
            "title_keyword": title_keyword,
            "max_depth": max_depth,
            "include_all_windows": include_all_windows,
            "timeout": timeout,
            "poll_interval": poll_interval,
            "foreground_only": foreground_only,
            "require_new_handle": require_new_handle,
            "baseline_handles": sorted(baseline),
            "dialogs": [],
        },
        next_action="先触发目标弹窗，再增大 --timeout 重试。",
    )


def run_pingan_probe(
    title_keyword: str,
    code: str,
    price: str,
    quantity: int,
    post_delay: float = 1.0,
    max_depth: int = 12,
) -> Result:
    if not IS_WINDOWS:
        return Result(
            ok=False,
            code=ErrorCode.UNSUPPORTED_PLATFORM,
            message="pingan probe is only available from native Windows Python",
            next_action="Run the pingan-probe command from Windows Python.",
        )

    steps: list[dict[str, Any]] = []

    def capture(step_name: str, result: Result) -> Result:
        steps.append({"step": step_name, "result": result.to_dict()})
        return result

    capture("windows_before", inspect_uia_windows(title_keyword))
    capture("set_code", set_uia_text(title_keyword, value=code, automation_id="12005", control_type="Edit"))
    capture("set_price", set_uia_text(title_keyword, value=price, automation_id="12006", control_type="Edit"))
    capture("set_quantity", set_uia_text(title_keyword, value=str(quantity), automation_id="12007", control_type="Edit"))
    capture("read_2021_before", read_uia_element(title_keyword, automation_id="2021", control_type="Text"))
    capture("read_2022_before", read_uia_element(title_keyword, automation_id="2022", control_type="Text"))
    capture("read_9100_before", read_uia_element(title_keyword, automation_id="9100", control_type="Text"))
    final_activation: Result | None = None
    for activation_strategy in ("invoke", "bm_click", "wm_command", "enter_key"):
        final_activation = capture(
            f"activate_buy_{activation_strategy}",
            activate_uia_element(
                title_keyword,
                automation_id="2010",
                control_type="Button",
                strategy=activation_strategy,
                post_delay=post_delay,
            ),
        )
        capture(
            f"read_2021_after_{activation_strategy}",
            read_uia_element(title_keyword, automation_id="2021", control_type="Text"),
        )
        capture(
            f"read_2022_after_{activation_strategy}",
            read_uia_element(title_keyword, automation_id="2022", control_type="Text"),
        )
        capture(
            f"read_9100_after_{activation_strategy}",
            read_uia_element(title_keyword, automation_id="9100", control_type="Text"),
        )
        capture(
            f"windows_after_{activation_strategy}",
            inspect_uia_windows(title_keyword),
        )
    capture("uia_after", inspect_uia_tree(title_keyword, max_depth=max_depth))

    ok = final_activation.ok if final_activation is not None else False
    warnings: list[str] = []
    if not ok:
        warnings.append("Non-physical activation sequence did not complete successfully; inspect the activate_buy_* steps.")
    return Result(
        ok=ok,
        code=ErrorCode.OK if ok else final_activation.code,
        message="completed pingan probe sequence" if ok else "pingan probe sequence encountered an error",
        data={
            "title_keyword": title_keyword,
            "input": {"code": code, "price": price, "quantity": quantity, "post_delay": post_delay, "max_depth": max_depth},
            "mode": "non_physical",
            "steps": steps,
        },
        warnings=warnings,
    )


def focus_uia_element(
    title_keyword: str,
    automation_id: str | None = None,
    name: str | None = None,
    control_type: str | None = None,
    timeout: float = 5.0,
    post_delay: float = 0.2,
) -> Result:
    if not IS_WINDOWS:
        return Result(
            ok=False,
            code=ErrorCode.UNSUPPORTED_PLATFORM,
            message="UIA focus is only available from native Windows Python",
            next_action="Run the UIA focus command from Windows Python.",
        )

    if not automation_id and not name:
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message="UIA focus requires --automation-id or --name",
            next_action="Provide at least one UIA selector.",
        )

    target = _find_uia_element(title_keyword, automation_id, name, control_type, timeout)
    if not target["ok"]:
        return Result(
            ok=False,
            code=ErrorCode.CONTROL_NOT_FOUND,
            message="could not find the requested UIA element to focus",
            data=target,
            next_action="Confirm the selector from a fresh uia-inspect snapshot and retry.",
        )

    element = target["element"]
    info = target["info"]
    try:
        _prepare_window(target["window"])
        element.set_focus()
        time.sleep(post_delay)
        return Result(
            ok=True,
            code=ErrorCode.OK,
            message="focused UIA element",
            data={
                "title_keyword": title_keyword,
                "automation_id": getattr(info, "automation_id", "") or "",
                "name": getattr(info, "name", "") or "",
                "control_type": getattr(info, "control_type", "") or "",
                "handle": getattr(info, "handle", None),
            },
        )
    except Exception as exc:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"failed to focus UIA element: {exc}",
            data={
                "title_keyword": title_keyword,
                "automation_id": getattr(info, "automation_id", "") or "",
                "name": getattr(info, "name", "") or "",
            },
        )


def run_pingan_hid_submit_probe(
    title_keyword: str,
    port: str,
    baudrate: int,
    timeout: float,
    code: str,
    price: str,
    quantity: int,
    submit_mode: str = "button_enter",
    post_delay: float = 1.0,
    max_depth: int = 12,
    dialog_timeout: float = 2.5,
    hid_pre_delay: float = 0.0,
) -> Result:
    if not IS_WINDOWS:
        return Result(
            ok=False,
            code=ErrorCode.UNSUPPORTED_PLATFORM,
            message="pingan HID submit probe is only available from native Windows Python",
            next_action="Run the pingan-hid-submit-probe command from Windows Python.",
        )

    if submit_mode not in {"button_enter", "quantity_tab_enter"}:
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message="invalid pingan HID submit mode",
            data={"submit_mode": submit_mode},
            next_action="Use one of: button_enter, quantity_tab_enter.",
        )

    steps: list[dict[str, Any]] = []

    def capture(step_name: str, result: Result) -> Result:
        steps.append({"step": step_name, "result": result.to_dict()})
        return result

    windows_before_result = capture("windows_before", inspect_uia_windows(title_keyword))
    baseline_handles: list[int] = []
    if windows_before_result.ok and windows_before_result.data:
        for item in windows_before_result.data.get("windows", []):
            handle = item.get("handle")
            if isinstance(handle, int):
                baseline_handles.append(handle)
    capture("set_code", set_uia_text(title_keyword, value=code, automation_id="12005", control_type="Edit"))
    capture("set_price", set_uia_text(title_keyword, value=price, automation_id="12006", control_type="Edit"))
    capture("set_quantity", set_uia_text(title_keyword, value=str(quantity), automation_id="12007", control_type="Edit"))
    capture("read_2021_before", read_uia_element(title_keyword, automation_id="2021", control_type="Text"))
    capture("read_2022_before", read_uia_element(title_keyword, automation_id="2022", control_type="Text"))
    capture("read_9100_before", read_uia_element(title_keyword, automation_id="9100", control_type="Text"))

    if submit_mode == "button_enter":
        focus_result = capture(
            "focus_submit_button",
            focus_uia_element(title_keyword, automation_id="2010", control_type="Button", post_delay=0.2),
        )
        if not focus_result.ok:
            return Result(
                ok=False,
                code=focus_result.code,
                message="pingan HID submit probe aborted before HID enter",
                data={
                    "title_keyword": title_keyword,
                    "port": port,
                    "baudrate": baudrate,
                    "timeout": timeout,
                    "input": {"code": code, "price": price, "quantity": quantity, "submit_mode": submit_mode},
                    "steps": steps,
                },
                next_action="Confirm the buy button is visible and focusable, then retry.",
            )
        hid_result = capture("hid_key_enter", run_hid_send(port=port, baudrate=baudrate, timeout=timeout, pre_delay=hid_pre_delay, command="KEY ENTER"))
    else:
        focus_result = capture(
            "focus_quantity_input",
            focus_uia_element(title_keyword, automation_id="12007", control_type="Edit", post_delay=0.2),
        )
        if not focus_result.ok:
            return Result(
                ok=False,
                code=focus_result.code,
                message="pingan HID submit probe aborted before HID tab+enter",
                data={
                    "title_keyword": title_keyword,
                    "port": port,
                    "baudrate": baudrate,
                    "timeout": timeout,
                    "input": {"code": code, "price": price, "quantity": quantity, "submit_mode": submit_mode},
                    "steps": steps,
                },
                next_action="Confirm the quantity input is visible and focusable, then retry.",
            )
        capture("hid_key_tab", run_hid_send(port=port, baudrate=baudrate, timeout=timeout, pre_delay=hid_pre_delay, command="KEY TAB"))
        hid_result = capture("hid_key_enter", run_hid_send(port=port, baudrate=baudrate, timeout=timeout, pre_delay=0.1, command="KEY ENTER"))

    if post_delay > 0:
        time.sleep(post_delay)

    capture("read_2021_after", read_uia_element(title_keyword, automation_id="2021", control_type="Text"))
    capture("read_2022_after", read_uia_element(title_keyword, automation_id="2022", control_type="Text"))
    capture("read_9100_after", read_uia_element(title_keyword, automation_id="9100", control_type="Text"))
    capture("windows_after", inspect_uia_windows(title_keyword))
    capture(
        "dialogs_after",
        wait_for_uia_dialog(
            title_keyword=None,
            max_depth=6,
            include_all_windows=True,
            timeout=dialog_timeout,
            poll_interval=0.2,
            exclude_class_names=[
                "Shell_TrayWnd",
                "Shell_SecondaryTrayWnd",
                "Progman",
                "WorkerW",
                "Notepad",
                "PX_WINDOW_CLASS",
                "CASCADIA_HOSTING_WINDOW_CLASS",
            ],
            baseline_handles=baseline_handles,
            require_new_handle=True,
            foreground_only=True,
        ),
    )
    capture("uia_after", inspect_uia_tree(title_keyword, max_depth=max_depth))

    warnings: list[str] = []
    if not hid_result.ok:
        warnings.append("HID submit step failed; inspect hid_key_* steps and the serial port configuration.")
    warnings.append("该命令只把最终提交动作切换为 HID 真实键盘输入，填单过程仍然使用现有 UIA 写值能力。")
    return Result(
        ok=hid_result.ok,
        code=ErrorCode.OK if hid_result.ok else hid_result.code,
        message="completed pingan HID submit probe" if hid_result.ok else "pingan HID submit probe encountered an error",
        data={
            "title_keyword": title_keyword,
            "input": {
                "code": code,
                "price": price,
                "quantity": quantity,
                "submit_mode": submit_mode,
                "post_delay": post_delay,
                "max_depth": max_depth,
                "dialog_timeout": dialog_timeout,
            },
            "hid": {"port": port, "baudrate": baudrate, "timeout": timeout},
            "hid_pre_delay": hid_pre_delay,
            "mode": "hid_submit_only",
            "steps": steps,
        },
        warnings=warnings,
    )


def run_pingan_buy_submit_once(
    title_keyword: str,
    port: str,
    baudrate: int,
    timeout: float,
    code: str,
    price: str,
    quantity: int,
    post_delay: float = 1.0,
    max_depth: int = 12,
    dialog_timeout: float = 2.5,
    hid_pre_delay: float = 0.0,
    confirm_timeout: float = 3.0,
    confirm_post_delay: float = 1.0,
    result_timeout: float = 3.0,
    close_result_dialog: bool = True,
    result_close_pre_delay: float = 0.0,
    capture_final_uia: bool = True,
) -> Result:
    if not IS_WINDOWS:
        return Result(
            ok=False,
            code=ErrorCode.UNSUPPORTED_PLATFORM,
            message="pingan buy submit is only available from native Windows Python",
            next_action="Run the pingan-buy-submit-once command from Windows Python.",
        )

    steps: list[dict[str, Any]] = []
    timing_steps: list[dict[str, Any]] = []

    def capture(step_name: str, result: Result) -> Result:
        steps.append({"step": step_name, "result": result.to_dict()})
        return result

    def capture_timed(step_name: str, fn: Any) -> Any:
        started_at = time.perf_counter()
        value = fn()
        timing_steps.append({"step": step_name, "duration_ms": round((time.perf_counter() - started_at) * 1000, 3)})
        return value

    probe_result = capture_timed(
        "submit_probe",
        lambda: capture(
            "submit_probe",
            run_pingan_hid_submit_probe(
                title_keyword=title_keyword,
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                code=code,
                price=price,
                quantity=quantity,
                submit_mode="quantity_tab_enter",
                post_delay=post_delay,
                max_depth=max_depth,
                dialog_timeout=dialog_timeout,
                hid_pre_delay=hid_pre_delay,
            ),
        ),
    )
    confirm_target = capture_timed("confirm_lookup", lambda: _find_pingan_confirm_button(title_keyword=title_keyword, timeout=confirm_timeout))
    if not confirm_target["ok"]:
        return Result(
            ok=False,
            code=ErrorCode.CONTROL_NOT_FOUND,
            message="could not find current pingan confirm button after submit",
            data={
                "title_keyword": title_keyword,
                "input": {"code": code, "price": price, "quantity": quantity},
                "steps": steps,
                "confirm_lookup": confirm_target,
            },
            next_action="Keep the confirm dialog visible and inspect the latest UIA tree.",
        )

    confirm_info = confirm_target["info"]
    confirm_hwnd = getattr(confirm_info, "handle", None)
    if not confirm_hwnd:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message="confirm button was found but does not expose a Win32 handle",
            data={
                "title_keyword": title_keyword,
                "input": {"code": code, "price": price, "quantity": quantity},
                "steps": steps,
                "confirm_lookup": _serialize_runtime_element(confirm_target["element"], confirm_info),
            },
        )

    confirm_click = capture_timed(
        "confirm_click_wm_command",
        lambda: capture(
            "confirm_click_wm_command",
            _click_runtime_target(confirm_target, strategy="wm_command", post_delay=confirm_post_delay),
        ),
    )
    result_dialog = capture_timed("result_dialog_lookup", lambda: _find_pingan_result_dialog(title_keyword=title_keyword, timeout=result_timeout))
    detected_result_dialog_data: dict[str, Any] = {}
    if result_dialog["ok"]:
        result_info = result_dialog["info"]
        detected_result_dialog_data = _serialize_runtime_element(result_dialog["element"], result_info) | _extract_dialog_text_payload_from_sources(
            hwnd=getattr(result_info, "handle", None),
            element=result_dialog["element"],
        )
        capture(
            "result_dialog_detected",
            Result(
                ok=True,
                code=ErrorCode.OK,
                message="detected pingan result dialog",
                data=detected_result_dialog_data,
            ),
        )
        if close_result_dialog:
            result_confirm_target = _find_pingan_result_confirm_button(title_keyword=title_keyword, timeout=1.0)
            if result_confirm_target["ok"]:
                capture(
                    "result_dialog_focus_confirm",
                    _focus_runtime_target(result_confirm_target, post_delay=max(0.1, result_close_pre_delay)),
                )
            capture(
                "result_dialog_close",
                run_hid_send(
                    port=port,
                    baudrate=baudrate,
                    timeout=timeout,
                    pre_delay=result_close_pre_delay,
                    command="KEY ENTER",
                ),
            )
    else:
        steps.append(
            {
                "step": "result_dialog_detected",
                "result": Result(
                    ok=False,
                    code=ErrorCode.WINDOW_NOT_FOUND,
                    message="did not detect pingan result dialog within timeout",
                    data={"timeout": result_timeout, "last_error": result_dialog.get("last_error")},
                ).to_dict(),
            }
        )
    if capture_final_uia:
        capture_timed("uia_after_confirm", lambda: capture("uia_after_confirm", inspect_uia_tree(title_keyword, max_depth=max_depth)))
    ok = bool(probe_result.ok and confirm_click.ok)
    return Result(
        ok=ok,
        code=ErrorCode.OK if ok else confirm_click.code,
        message="completed pingan buy submit once" if ok else "pingan buy submit once encountered an error",
        data={
            "title_keyword": title_keyword,
            "input": {"code": code, "price": price, "quantity": quantity},
            "hid": {"port": port, "baudrate": baudrate, "timeout": timeout},
            "hid_pre_delay": hid_pre_delay,
            "capture_final_uia": capture_final_uia,
            "confirm_button": _safe_serialize_runtime_element(confirm_target["element"], confirm_info),
            "result_dialog": detected_result_dialog_data if result_dialog["ok"] else {},
            "timing": {"steps": timing_steps},
            "steps": steps,
        },
        warnings=[
            "该命令会实际执行确认点击；请仅在你接受当前委托后果时使用。"
        ],
    )


def run_pingan_buy_fast(
    title_keyword: str,
    port: str,
    baudrate: int,
    timeout: float,
    code: str,
    price: str,
    quantity: int,
    post_delay: float = 0.2,
    max_depth: int = 12,
    dialog_timeout: float = 2.0,
    hid_pre_delay: float = 0.0,
    confirm_timeout: float = 1.5,
    confirm_post_delay: float = 0.1,
    result_timeout: float = 1.5,
    price_quantity_input_mode: str = "uia",
    dialog_lookup_mode: str = "uia",
    close_result_dialog: bool = True,
    result_close_pre_delay: float = 0.0,
    capture_final_uia: bool = False,
) -> Result:
    if not IS_WINDOWS:
        return Result(
            ok=False,
            code=ErrorCode.UNSUPPORTED_PLATFORM,
            message="pingan buy fast is only available from native Windows Python",
            next_action="Run the pingan-buy command from Windows Python.",
        )

    steps: list[dict[str, Any]] = []
    timing_steps: list[dict[str, Any]] = []

    def capture(step_name: str, result: Result) -> Result:
        steps.append({"step": step_name, "result": result.to_dict()})
        return result

    def capture_timed(step_name: str, fn: Any) -> Any:
        started_at = time.perf_counter()
        value = fn()
        timing_steps.append({"step": step_name, "duration_ms": round((time.perf_counter() - started_at) * 1000, 3)})
        return value

    window_target = capture_timed("main_window_lookup", lambda: _find_uia_window(title_keyword, timeout=timeout))
    if not window_target["ok"]:
        return Result(
            ok=False,
            code=ErrorCode.WINDOW_NOT_FOUND,
            message="pingan buy fast could not find target window",
            data={"title_keyword": title_keyword, "input": {"code": code, "price": price, "quantity": quantity}, "timing": {"steps": timing_steps}},
        )
    target_window = window_target["window"]
    try:
        _prepare_window(target_window)
    except Exception:
        pass

    cached_targets: dict[tuple[str, str], dict[str, Any]] = {}

    def get_cached_target(automation_id: str, control_type: str) -> dict[str, Any]:
        cache_key = (automation_id, control_type)
        if cache_key in cached_targets:
            return cached_targets[cache_key]
        target = _find_uia_element_direct_in_window(target_window, automation_id=automation_id, name=None, control_type=control_type)
        if not target["ok"]:
            target = _find_uia_element_in_window(target_window, automation_id=automation_id, name=None, control_type=control_type)
        if target["ok"]:
            cached_targets[cache_key] = target
        return target

    def set_cached_text_uia(step_name: str, automation_id: str, value: str, target: dict[str, Any]) -> Result:
        element = target["element"]
        info = target["info"]
        try:
            if hasattr(element, "set_edit_text"):
                element.set_edit_text(value)
            else:
                element.set_focus()
                element.type_keys("^a{BACKSPACE}", set_foreground=False)
                element.type_keys(value, with_spaces=True, set_foreground=False)
            if post_delay > 0:
                time.sleep(post_delay)
            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="set cached UIA text",
                data={
                    "title_keyword": title_keyword,
                    "automation_id": getattr(info, "automation_id", "") or "",
                    "control_type": getattr(info, "control_type", "") or "",
                    "value": value,
                    "input_mode": "uia",
                },
            )
        except Exception as exc:
            return Result(
                ok=False,
                code=ErrorCode.EXECUTION_FAILED,
                message=f"failed to set cached UIA text: {exc}",
                data={"title_keyword": title_keyword, "automation_id": automation_id, "value": value, "input_mode": "uia"},
            )

    def set_cached_text_win32(step_name: str, automation_id: str, value: str, target: dict[str, Any]) -> Result:
        info = target["info"]
        handle = getattr(info, "handle", None)
        if not handle:
            return Result(
                ok=False,
                code=ErrorCode.CONTROL_NOT_FOUND,
                message="cached target does not expose a native handle",
                data={"title_keyword": title_keyword, "automation_id": automation_id, "value": value, "input_mode": "win32"},
            )
        try:
            set_text(int(handle), value)
            observed_value = get_text(int(handle))
        except Exception as exc:
            return Result(
                ok=False,
                code=ErrorCode.EXECUTION_FAILED,
                message=f"failed to set cached Win32 text: {exc}",
                data={"title_keyword": title_keyword, "automation_id": automation_id, "value": value, "handle": handle, "input_mode": "win32"},
            )
        if str(observed_value or "").strip() != str(value).strip():
            return Result(
                ok=False,
                code=ErrorCode.EXECUTION_FAILED,
                message="cached Win32 text verification mismatch",
                data={
                    "title_keyword": title_keyword,
                    "automation_id": automation_id,
                    "value": value,
                    "observed_value": observed_value,
                    "handle": handle,
                    "input_mode": "win32",
                },
            )
        if post_delay > 0:
            time.sleep(post_delay)
        return Result(
            ok=True,
            code=ErrorCode.OK,
            message="set cached Win32 text via handle",
            data={
                "title_keyword": title_keyword,
                "automation_id": getattr(info, "automation_id", "") or "",
                "control_type": getattr(info, "control_type", "") or "",
                "value": value,
                "observed_value": observed_value,
                "handle": handle,
                "input_mode": "win32",
            },
        )

    def set_cached_text(step_name: str, automation_id: str, value: str, input_mode: str = "uia") -> Result:
        target = get_cached_target(automation_id, "Edit")
        if not target["ok"]:
            return Result(
                ok=False,
                code=ErrorCode.CONTROL_NOT_FOUND,
                message="could not find cached UIA text target",
                data={"title_keyword": title_keyword, "automation_id": automation_id, "step": step_name, "target": target},
            )
        if input_mode == "win32":
            return set_cached_text_win32(step_name, automation_id, value, target)
        if input_mode == "hybrid_win32":
            win32_result = set_cached_text_win32(step_name, automation_id, value, target)
            if win32_result.ok:
                return win32_result
            fallback_result = set_cached_text_uia(step_name, automation_id, value, target)
            fallback_result.data.setdefault("fallback_from", win32_result.message)
            fallback_result.data.setdefault("fallback_source", win32_result.data)
            return fallback_result
        return set_cached_text_uia(step_name, automation_id, value, target)

    def focus_cached_element(step_name: str, automation_id: str, control_type: str = "Edit", focus_delay: float = 0.05) -> Result:
        target = get_cached_target(automation_id, control_type)
        if not target["ok"]:
            return Result(
                ok=False,
                code=ErrorCode.CONTROL_NOT_FOUND,
                message="could not find cached UIA focus target",
                data={"title_keyword": title_keyword, "automation_id": automation_id, "step": step_name, "target": target},
            )
        element = target["element"]
        info = target["info"]
        try:
            element.set_focus()
            if focus_delay > 0:
                time.sleep(focus_delay)
            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="focused cached UIA element",
                data={
                    "title_keyword": title_keyword,
                    "automation_id": getattr(info, "automation_id", "") or "",
                    "control_type": getattr(info, "control_type", "") or "",
                    "handle": getattr(info, "handle", None),
                },
            )
        except Exception as exc:
            return Result(
                ok=False,
                code=ErrorCode.EXECUTION_FAILED,
                message=f"failed to focus cached UIA element: {exc}",
                data={"title_keyword": title_keyword, "automation_id": automation_id},
            )

    set_code_result = capture_timed(
        "set_code",
        lambda: capture("set_code", set_cached_text("set_code", "12005", code)),
    )
    if not set_code_result.ok:
        return Result(
            ok=False,
            code=set_code_result.code,
            message="pingan buy fast aborted while setting code",
            data={"title_keyword": title_keyword, "input": {"code": code, "price": price, "quantity": quantity}, "steps": steps, "timing": {"steps": timing_steps}},
        )

    set_price_result = capture_timed(
        "set_price",
        lambda: capture("set_price", set_cached_text("set_price", "12006", price, input_mode=price_quantity_input_mode)),
    )
    if not set_price_result.ok:
        return Result(
            ok=False,
            code=set_price_result.code,
            message="pingan buy fast aborted while setting price",
            data={"title_keyword": title_keyword, "input": {"code": code, "price": price, "quantity": quantity}, "steps": steps, "timing": {"steps": timing_steps}},
        )

    set_quantity_result = capture_timed(
        "set_quantity",
        lambda: capture("set_quantity", set_cached_text("set_quantity", "12007", str(quantity), input_mode=price_quantity_input_mode)),
    )
    if not set_quantity_result.ok:
        return Result(
            ok=False,
            code=set_quantity_result.code,
            message="pingan buy fast aborted while setting quantity",
            data={"title_keyword": title_keyword, "input": {"code": code, "price": price, "quantity": quantity}, "steps": steps, "timing": {"steps": timing_steps}},
        )

    focus_result = capture_timed(
        "focus_quantity_input",
        lambda: capture("focus_quantity_input", focus_cached_element("focus_quantity_input", "12007", control_type="Edit", focus_delay=0.05)),
    )
    if not focus_result.ok:
        return Result(
            ok=False,
            code=focus_result.code,
            message="pingan buy fast aborted before HID submit",
            data={"title_keyword": title_keyword, "input": {"code": code, "price": price, "quantity": quantity}, "steps": steps, "timing": {"steps": timing_steps}},
            next_action="Confirm the quantity input is visible and focusable, then retry.",
        )

    capture_timed(
        "hid_key_tab",
        lambda: capture("hid_key_tab", run_hid_send(port=port, baudrate=baudrate, timeout=timeout, pre_delay=hid_pre_delay, command="KEY TAB")),
    )
    hid_enter_result = capture_timed(
        "hid_key_enter",
        lambda: capture("hid_key_enter", run_hid_send(port=port, baudrate=baudrate, timeout=timeout, pre_delay=0.05, command="KEY ENTER")),
    )
    if not hid_enter_result.ok:
        return Result(
            ok=False,
            code=hid_enter_result.code,
            message="pingan buy fast aborted during HID submit",
            data={"title_keyword": title_keyword, "input": {"code": code, "price": price, "quantity": quantity}, "steps": steps, "timing": {"steps": timing_steps}},
        )

    if post_delay > 0:
        time.sleep(post_delay)

    def find_confirm_target() -> dict[str, Any]:
        if dialog_lookup_mode == "win32_experimental":
            experimental = _find_pingan_confirm_button_win32(timeout=confirm_timeout)
            if experimental["ok"]:
                experimental["lookup_mode"] = "win32_experimental"
                return experimental
            fallback = _find_pingan_confirm_button(title_keyword=title_keyword, timeout=confirm_timeout)
            fallback["lookup_mode"] = "uia_fallback"
            fallback["lookup_fallback_from"] = experimental.get("last_error")
            return fallback
        target = _find_pingan_confirm_button(title_keyword=title_keyword, timeout=confirm_timeout)
        target["lookup_mode"] = "uia"
        return target

    confirm_target = capture_timed("confirm_lookup", find_confirm_target)
    if not confirm_target["ok"]:
        return Result(
            ok=False,
            code=ErrorCode.CONTROL_NOT_FOUND,
            message="could not find current pingan confirm button after fast submit",
            data={
                "title_keyword": title_keyword,
                "input": {"code": code, "price": price, "quantity": quantity},
                "steps": steps,
                "timing": {"steps": timing_steps},
                "confirm_lookup": confirm_target,
            },
            next_action="Keep the confirm dialog visible and inspect the latest UIA tree.",
        )

    confirm_info = confirm_target["info"]
    confirm_click = capture_timed(
        "confirm_click_wm_command",
        lambda: capture(
            "confirm_click_wm_command",
            _click_runtime_hwnd(confirm_target["hwnd"], strategy="wm_command", post_delay=confirm_post_delay)
            if confirm_target.get("hwnd")
            else _click_runtime_target(confirm_target, strategy="wm_command", post_delay=confirm_post_delay),
        ),
    )
    def find_result_dialog() -> dict[str, Any]:
        if dialog_lookup_mode == "win32_experimental":
            experimental = _find_pingan_result_dialog_win32(timeout=result_timeout)
            if experimental["ok"]:
                experimental["lookup_mode"] = "win32_experimental"
                return experimental
            fallback = _find_pingan_result_dialog(title_keyword=title_keyword, timeout=result_timeout)
            fallback["lookup_mode"] = "uia_fallback"
            fallback["lookup_fallback_from"] = experimental.get("last_error")
            return fallback
        target = _find_pingan_result_dialog(title_keyword=title_keyword, timeout=result_timeout)
        target["lookup_mode"] = "uia"
        return target

    result_dialog = capture_timed("result_dialog_lookup", find_result_dialog)
    detected_result_dialog_data: dict[str, Any] = {}
    if result_dialog["ok"]:
        result_info = result_dialog["info"]
        detected_result_dialog_data = _safe_serialize_runtime_element(result_dialog["element"], result_info) | _extract_dialog_text_payload_from_sources(
            hwnd=getattr(result_info, "handle", None),
            element=result_dialog.get("element_for_extract"),
        )
        detected_result_dialog_data["lookup_mode"] = result_dialog.get("lookup_mode", dialog_lookup_mode)
        if result_dialog.get("lookup_fallback_from"):
            detected_result_dialog_data["lookup_fallback_from"] = result_dialog.get("lookup_fallback_from")
        capture(
            "result_dialog_detected",
            Result(ok=True, code=ErrorCode.OK, message="detected pingan result dialog", data=detected_result_dialog_data),
        )
        if close_result_dialog:
            if dialog_lookup_mode == "win32_experimental":
                result_confirm_target = _find_pingan_result_confirm_button_win32(timeout=0.5)
                if not result_confirm_target["ok"]:
                    result_confirm_target = _find_pingan_result_confirm_button(title_keyword=title_keyword, timeout=0.5)
            else:
                result_confirm_target = _find_pingan_result_confirm_button(title_keyword=title_keyword, timeout=0.5)
            if result_confirm_target["ok"]:
                capture_timed(
                    "result_dialog_focus_confirm",
                    lambda: capture(
                        "result_dialog_focus_confirm",
                        _focus_runtime_hwnd(int(result_confirm_target["hwnd"]), post_delay=max(0.05, result_close_pre_delay))
                        if result_confirm_target.get("hwnd")
                        else _focus_runtime_target(result_confirm_target, post_delay=max(0.05, result_close_pre_delay)),
                    ),
                )
            capture_timed(
                "result_dialog_close",
                lambda: capture(
                    "result_dialog_close",
                    run_hid_send(
                        port=port,
                        baudrate=baudrate,
                        timeout=timeout,
                        pre_delay=result_close_pre_delay,
                        command="KEY ENTER",
                    ),
                ),
            )
    else:
        steps.append(
            {
                "step": "result_dialog_detected",
                "result": Result(
                    ok=False,
                    code=ErrorCode.WINDOW_NOT_FOUND,
                    message="did not detect pingan result dialog within timeout",
                    data={"timeout": result_timeout, "last_error": result_dialog.get("last_error")},
                ).to_dict(),
            }
        )

    if capture_final_uia:
        capture_timed("uia_after_confirm", lambda: capture("uia_after_confirm", inspect_uia_tree(title_keyword, max_depth=max_depth)))

    ok = bool(confirm_click.ok)
    return Result(
        ok=ok,
        code=ErrorCode.OK if ok else confirm_click.code,
        message="completed pingan buy fast" if ok else "pingan buy fast encountered an error",
        data={
            "title_keyword": title_keyword,
            "input": {"code": code, "price": price, "quantity": quantity},
            "hid": {"port": port, "baudrate": baudrate, "timeout": timeout},
            "dialog_timeout": dialog_timeout,
            "hid_pre_delay": hid_pre_delay,
            "capture_final_uia": capture_final_uia,
            "dialog_lookup_mode": dialog_lookup_mode,
            "confirm_button": _safe_serialize_runtime_element(confirm_target["element"], confirm_info),
            "result_dialog": detected_result_dialog_data if result_dialog["ok"] else {},
            "timing": {"steps": timing_steps},
            "steps": steps,
        },
        warnings=["该命令会实际执行确认点击；请仅在你接受当前委托后果时使用。"],
    )


def inspect_uia_tree(title_keyword: str, max_depth: int = 6) -> Result:
    if not IS_WINDOWS:
        return Result(
            ok=False,
            code=ErrorCode.UNSUPPORTED_PLATFORM,
            message="UIA inspection is only available from native Windows Python",
            next_action="Run the UIA commands from Windows Python.",
        )

    windows = []
    for window in Desktop(backend="uia").windows():
        try:
            name = window.window_text()
        except Exception:
            name = ""
        if title_keyword in name:
            windows.append(window)

    if not windows:
        return Result(
            ok=False,
            code=ErrorCode.WINDOW_NOT_FOUND,
            message=f"could not find a UIA window containing {title_keyword!r}",
            data={"title_keyword": title_keyword},
            next_action="Open Ping An Securities and navigate to the page you want to inspect.",
        )

    windows.sort(key=_uia_window_score, reverse=True)
    root = windows[0]
    try:
        root_info = root.element_info
    except Exception as exc:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"failed to access UIA root element: {exc}",
        )

    tree = _serialize_uia_subtree(root, max_depth=max_depth)

    return Result(
        ok=True,
        code=ErrorCode.OK,
        message="enumerated UIA tree",
        data={
            "title_keyword": title_keyword,
            "root": tree["root"],
            "max_depth": max_depth,
            "nodes": tree["nodes"],
        },
    )


def _uia_window_score(window: Any) -> tuple[int, int]:
    try:
        info = window.element_info
        class_name = getattr(info, "class_name", "") or ""
        visible = 1 if getattr(window, "is_visible", lambda: False)() else 0
    except Exception:
        class_name = ""
        visible = 0
    class_score = 2 if class_name == "TdxW_MainFrame_Class" else 1 if class_name == "#32770" else 0
    return (class_score, visible)


def _uia_dialog_score(dialog: dict[str, Any]) -> tuple[int, int, int]:
    root = dialog.get("root", {})
    class_name = str(root.get("class_name", "") or "")
    name = str(root.get("name", "") or "")
    visible = 1 if root.get("visible") else 0
    class_score = 2 if class_name == "#32770" else 1
    name_score = 1 if name else 0
    return (class_score, name_score, visible)


def _serialize_uia_subtree(root: Any, max_depth: int) -> dict[str, Any]:
    try:
        root_info = root.element_info
    except Exception:
        root_info = None

    nodes: list[dict[str, Any]] = []

    def serialize_element(wrapper: Any, depth: int, parent_path: str | None, index: int) -> None:
        try:
            info = wrapper.element_info
            rect = getattr(info, "rectangle", None)
            children = wrapper.children()
        except Exception:
            return

        path = f"{parent_path}/{index}" if parent_path is not None else "0"
        node = {
            "path": path,
            "parent_path": parent_path,
            "depth": depth,
            "index": index,
            "name": getattr(info, "name", "") or "",
            "control_type": getattr(info, "control_type", "") or "",
            "automation_id": getattr(info, "automation_id", "") or "",
            "class_name": getattr(info, "class_name", "") or "",
            "handle": getattr(info, "handle", None),
            "rich_text": getattr(info, "rich_text", "") or "",
            "rectangle": (
                [rect.left, rect.top, rect.right, rect.bottom]
                if rect is not None and hasattr(rect, "left")
                else None
            ),
        }
        nodes.append(node)
        if depth >= max_depth:
            return
        for child_index, child in enumerate(children):
            serialize_element(child, depth + 1, path, child_index)

    serialize_element(root, 0, None, 0)
    return {
        "root": {
            "name": getattr(root_info, "name", "") or "",
            "class_name": getattr(root_info, "class_name", "") or "",
            "control_type": getattr(root_info, "control_type", "") or "",
            "handle": getattr(root_info, "handle", None),
            "visible": getattr(root, "is_visible", lambda: None)(),
            "enabled": getattr(root, "is_enabled", lambda: None)(),
        },
        "nodes": nodes,
    }


def click_uia_element(
    title_keyword: str,
    automation_id: str | None = None,
    name: str | None = None,
    control_type: str | None = None,
    timeout: float = 5.0,
    post_delay: float = 0.5,
) -> Result:
    if not IS_WINDOWS:
        return Result(
            ok=False,
            code=ErrorCode.UNSUPPORTED_PLATFORM,
            message="UIA click is only available from native Windows Python",
            next_action="Run the UIA click command from Windows Python.",
        )

    if not automation_id and not name:
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message="UIA click requires --automation-id or --name",
            next_action="Provide at least one UIA selector.",
        )

    deadline = time.time() + timeout
    last_error: str | None = None
    while time.time() < deadline:
        try:
            windows = Desktop(backend="uia").windows()
        except Exception as exc:
            last_error = str(exc)
            time.sleep(0.2)
            continue

        target_window = None
        for window in windows:
            try:
                window_name = window.window_text()
            except Exception:
                window_name = ""
            if title_keyword in window_name:
                target_window = window
                break

        if target_window is None:
            time.sleep(0.2)
            continue

        try:
            _prepare_window(target_window)
            descendants = target_window.descendants()
        except Exception as exc:
            last_error = str(exc)
            time.sleep(0.2)
            continue

        for element in descendants:
            try:
                info = element.element_info
                element_name = getattr(info, "name", "") or ""
                element_automation_id = getattr(info, "automation_id", "") or ""
                element_control_type = getattr(info, "control_type", "") or ""
            except Exception:
                continue

            if automation_id and element_automation_id != automation_id:
                continue
            if name and element_name != name:
                continue
            if control_type and element_control_type != control_type:
                continue

            try:
                element.click_input()
                time.sleep(post_delay)
                return Result(
                    ok=True,
                    code=ErrorCode.OK,
                    message="clicked UIA element",
                    data={
                        "title_keyword": title_keyword,
                        "automation_id": element_automation_id,
                        "name": element_name,
                        "control_type": element_control_type,
                    },
                )
            except Exception as exc:
                last_error = str(exc)
                break

        time.sleep(0.2)

    return Result(
        ok=False,
        code=ErrorCode.CONTROL_NOT_FOUND,
        message="could not find or click the requested UIA element",
        data={
            "title_keyword": title_keyword,
            "automation_id": automation_id,
            "name": name,
            "control_type": control_type,
            "last_error": last_error,
        },
        next_action="Confirm the UIA selectors from a fresh uia-inspect snapshot and retry.",
    )


def click_uia_path(
    title_keyword: str,
    path: str,
    timeout: float = 5.0,
    post_delay: float = 0.5,
) -> Result:
    if not IS_WINDOWS:
        return Result(
            ok=False,
            code=ErrorCode.UNSUPPORTED_PLATFORM,
            message="UIA path click is only available from native Windows Python",
            next_action="Run the UIA path click command from Windows Python.",
        )

    if not path:
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message="UIA path click requires a non-empty --path",
            next_action="Provide a path from a uia-inspect snapshot, for example 0/17/0/0/0/1/6.",
        )

    target = _find_uia_path_element(title_keyword, path, timeout)
    if not target["ok"]:
        return Result(
            ok=False,
            code=ErrorCode.CONTROL_NOT_FOUND,
            message="could not find the requested UIA path element",
            data=target,
            next_action="Confirm the path from a fresh uia-inspect snapshot and retry.",
        )

    element = target["element"]
    info = target["info"]
    try:
        _prepare_window(target["window"])
        element.click_input()
        time.sleep(post_delay)
        return Result(
            ok=True,
            code=ErrorCode.OK,
            message="clicked UIA path element",
            data={
                "title_keyword": title_keyword,
                "path": path,
                "name": getattr(info, "name", "") or "",
                "automation_id": getattr(info, "automation_id", "") or "",
                "control_type": getattr(info, "control_type", "") or "",
                "class_name": getattr(info, "class_name", "") or "",
            },
        )
    except Exception as exc:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"failed to click UIA path element: {exc}",
            data={"title_keyword": title_keyword, "path": path},
        )


def activate_uia_element(
    title_keyword: str,
    automation_id: str | None = None,
    name: str | None = None,
    control_type: str | None = None,
    strategy: str = "auto",
    timeout: float = 5.0,
    post_delay: float = 0.5,
) -> Result:
    if not IS_WINDOWS:
        return Result(
            ok=False,
            code=ErrorCode.UNSUPPORTED_PLATFORM,
            message="UIA activation is only available from native Windows Python",
            next_action="Run the UIA activate command from Windows Python.",
        )

    if not automation_id and not name:
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message="UIA activation requires --automation-id or --name",
            next_action="Provide at least one UIA selector.",
        )
    if strategy not in {"auto", "invoke", "click_input", "bm_click", "wm_command", "enter_key"}:
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message="invalid UIA activation strategy",
            data={"strategy": strategy},
            next_action="Use one of: auto, invoke, click_input, bm_click, wm_command, enter_key.",
        )

    target = _find_uia_element(title_keyword, automation_id, name, control_type, timeout)
    if not target["ok"]:
        return Result(
            ok=False,
            code=ErrorCode.CONTROL_NOT_FOUND,
            message="could not find the requested UIA element to activate",
            data=target,
            next_action="Confirm the selector from a fresh uia-inspect snapshot and retry.",
        )

    return _activate_target(title_keyword, target, post_delay, strategy)


def read_uia_element(
    title_keyword: str,
    automation_id: str | None = None,
    name: str | None = None,
    control_type: str | None = None,
    timeout: float = 5.0,
) -> Result:
    if not IS_WINDOWS:
        return Result(
            ok=False,
            code=ErrorCode.UNSUPPORTED_PLATFORM,
            message="UIA read is only available from native Windows Python",
            next_action="Run the UIA read command from Windows Python.",
        )

    if not automation_id and not name:
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message="UIA read requires --automation-id or --name",
            next_action="Provide at least one UIA selector.",
        )

    target = _find_uia_element(title_keyword, automation_id, name, control_type, timeout)
    if not target["ok"]:
        return Result(
            ok=False,
            code=ErrorCode.CONTROL_NOT_FOUND,
            message="could not find the requested UIA element to read",
            data=target,
            next_action="Confirm the selector from a fresh uia-inspect snapshot and retry.",
        )

    try:
        payload = _serialize_runtime_element(target["element"], target["info"])
        payload["title_keyword"] = title_keyword
        return Result(
            ok=True,
            code=ErrorCode.OK,
            message="read UIA element",
            data=payload,
        )
    except Exception as exc:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"failed to read UIA element: {exc}",
            data={"title_keyword": title_keyword, "automation_id": automation_id, "name": name},
        )


def click_uia_center(
    title_keyword: str,
    automation_id: str | None = None,
    name: str | None = None,
    control_type: str | None = None,
    timeout: float = 5.0,
    post_delay: float = 0.5,
) -> Result:
    if not IS_WINDOWS:
        return Result(
            ok=False,
            code=ErrorCode.UNSUPPORTED_PLATFORM,
            message="UIA center click is only available from native Windows Python",
            next_action="Run the UIA center-click command from Windows Python.",
        )

    if not automation_id and not name:
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message="UIA center click requires --automation-id or --name",
            next_action="Provide at least one UIA selector.",
        )

    target = _find_uia_element(title_keyword, automation_id, name, control_type, timeout)
    if not target["ok"]:
        return Result(
            ok=False,
            code=ErrorCode.CONTROL_NOT_FOUND,
            message="could not find the requested UIA element to center-click",
            data=target,
            next_action="Confirm the selector from a fresh uia-inspect snapshot and retry.",
        )

    element = target["element"]
    info = target["info"]
    _prepare_window(target["window"])
    rect = getattr(info, "rectangle", None)
    if rect is None or not hasattr(rect, "left"):
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message="target element does not expose a clickable rectangle",
            data={"title_keyword": title_keyword, "automation_id": getattr(info, "automation_id", "") or ""},
        )
    center_x = int((rect.left + rect.right) / 2)
    center_y = int((rect.top + rect.bottom) / 2)
    try:
        click_screen_point(center_x, center_y, settle_delay=post_delay)
        payload = _serialize_runtime_element(element, info)
        payload["title_keyword"] = title_keyword
        payload["click_point"] = [center_x, center_y]
        return Result(
            ok=True,
            code=ErrorCode.OK,
            message="clicked UIA element center point",
            data=payload,
        )
    except Exception as exc:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"failed to center-click UIA element: {exc}",
            data={"title_keyword": title_keyword, "automation_id": getattr(info, "automation_id", "") or ""},
        )


def list_uia_combobox_items(
    title_keyword: str,
    automation_id: str | None = None,
    name: str | None = None,
    timeout: float = 5.0,
    post_delay: float = 0.5,
) -> Result:
    if not IS_WINDOWS:
        return Result(
            ok=False,
            code=ErrorCode.UNSUPPORTED_PLATFORM,
            message="UIA combobox inspection is only available from native Windows Python",
            next_action="Run the UIA combobox command from Windows Python.",
        )

    if not automation_id and not name:
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message="UIA combobox inspection requires --automation-id or --name",
            next_action="Provide at least one UIA selector.",
        )

    target = _find_uia_element(title_keyword, automation_id, name, "ComboBox", timeout)
    if not target["ok"]:
        return Result(
            ok=False,
            code=ErrorCode.CONTROL_NOT_FOUND,
            message="could not find the requested UIA combobox",
            data=target,
            next_action="Confirm the combobox selectors from a fresh uia-inspect snapshot and retry.",
        )

    element = target["element"]
    info = target["info"]
    try:
        element.expand()
    except Exception:
        try:
            element.click_input()
        except Exception:
            pass
    time.sleep(post_delay)

    items: list[dict[str, Any]] = []
    try:
        descendants = target["window"].descendants()
    except Exception as exc:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"failed to enumerate combobox descendants: {exc}",
        )

    seen: set[tuple[str, str]] = set()
    for child in descendants:
        try:
            child_info = child.element_info
            child_control_type = getattr(child_info, "control_type", "") or ""
            child_name = getattr(child_info, "name", "") or ""
            child_automation_id = getattr(child_info, "automation_id", "") or ""
            child_class_name = getattr(child_info, "class_name", "") or ""
        except Exception:
            continue
        if child_control_type not in {"ListItem", "Text"}:
            continue
        if not child_name:
            continue
        key = (child_control_type, child_name)
        if key in seen:
            continue
        seen.add(key)
        items.append(
            {
                "name": child_name,
                "control_type": child_control_type,
                "automation_id": child_automation_id,
                "class_name": child_class_name,
            }
        )

    return Result(
        ok=True,
        code=ErrorCode.OK,
        message="listed UIA combobox items",
        data={
            "title_keyword": title_keyword,
            "automation_id": getattr(info, "automation_id", "") or "",
            "name": getattr(info, "name", "") or "",
            "items": items,
        },
    )


def select_uia_combobox_item(
    title_keyword: str,
    item_name: str,
    automation_id: str | None = None,
    name: str | None = None,
    timeout: float = 5.0,
    post_delay: float = 0.5,
) -> Result:
    if not IS_WINDOWS:
        return Result(
            ok=False,
            code=ErrorCode.UNSUPPORTED_PLATFORM,
            message="UIA combobox selection is only available from native Windows Python",
            next_action="Run the UIA combobox command from Windows Python.",
        )

    if not automation_id and not name:
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message="UIA combobox selection requires --automation-id or --name",
            next_action="Provide at least one UIA selector.",
        )

    target = _find_uia_element(title_keyword, automation_id, name, "ComboBox", timeout)
    if not target["ok"]:
        return Result(
            ok=False,
            code=ErrorCode.CONTROL_NOT_FOUND,
            message="could not find the requested UIA combobox",
            data=target,
            next_action="Confirm the combobox selectors from a fresh uia-inspect snapshot and retry.",
        )

    element = target["element"]
    info = target["info"]
    try:
        element.expand()
    except Exception:
        try:
            element.click_input()
        except Exception:
            pass
    time.sleep(post_delay)

    try:
        descendants = target["window"].descendants()
    except Exception as exc:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"failed to enumerate combobox descendants: {exc}",
        )

    for child in descendants:
        try:
            child_info = child.element_info
            child_control_type = getattr(child_info, "control_type", "") or ""
            child_name = getattr(child_info, "name", "") or ""
        except Exception:
            continue
        if child_control_type not in {"ListItem", "Text"}:
            continue
        if child_name != item_name:
            continue
        try:
            child.click_input()
            time.sleep(post_delay)
            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="selected UIA combobox item",
                data={
                    "title_keyword": title_keyword,
                    "combobox_automation_id": getattr(info, "automation_id", "") or "",
                    "combobox_name": getattr(info, "name", "") or "",
                    "selected_item": item_name,
                },
            )
        except Exception as exc:
            return Result(
                ok=False,
                code=ErrorCode.EXECUTION_FAILED,
                message=f"failed to click combobox item: {exc}",
            )

    return Result(
        ok=False,
        code=ErrorCode.CONTROL_NOT_FOUND,
        message="could not find the requested combobox item",
        data={
            "title_keyword": title_keyword,
            "automation_id": automation_id,
            "name": name,
            "item_name": item_name,
        },
        next_action="List the combobox items first, then retry with an exact item name.",
    )


def set_uia_text(
    title_keyword: str,
    value: str,
    automation_id: str | None = None,
    name: str | None = None,
    control_type: str | None = "Edit",
    timeout: float = 5.0,
    post_delay: float = 0.2,
) -> Result:
    if not IS_WINDOWS:
        return Result(
            ok=False,
            code=ErrorCode.UNSUPPORTED_PLATFORM,
            message="UIA text entry is only available from native Windows Python",
            next_action="Run the UIA text command from Windows Python.",
        )

    if not automation_id and not name:
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message="UIA text entry requires --automation-id or --name",
            next_action="Provide at least one UIA selector.",
        )

    target = _find_uia_element(title_keyword, automation_id, name, control_type, timeout)
    if not target["ok"]:
        return Result(
            ok=False,
            code=ErrorCode.CONTROL_NOT_FOUND,
            message="could not find the requested UIA text target",
            data=target,
            next_action="Confirm the selector from a fresh uia-inspect snapshot and retry.",
        )

    element = target["element"]
    info = target["info"]
    try:
        _prepare_window(target["window"])
        if hasattr(element, "set_edit_text"):
            element.set_edit_text(value)
        else:
            element.set_focus()
            element.type_keys("^a{BACKSPACE}", set_foreground=False)
            element.type_keys(value, with_spaces=True, set_foreground=False)
        time.sleep(post_delay)
        return Result(
            ok=True,
            code=ErrorCode.OK,
            message="set UIA text",
            data={
                "title_keyword": title_keyword,
                "automation_id": getattr(info, "automation_id", "") or "",
                "name": getattr(info, "name", "") or "",
                "control_type": getattr(info, "control_type", "") or "",
                "value": value,
            },
        )
    except Exception as exc:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"failed to set UIA text: {exc}",
            data={
                "title_keyword": title_keyword,
                "automation_id": getattr(info, "automation_id", "") or "",
                "name": getattr(info, "name", "") or "",
                "control_type": getattr(info, "control_type", "") or "",
            },
        )


def _find_uia_element(
    title_keyword: str,
    automation_id: str | None,
    name: str | None,
    control_type: str | None,
    timeout: float,
) -> dict[str, Any]:
    deadline = time.time() + timeout
    last_error: str | None = None
    while time.time() < deadline:
        try:
            windows = Desktop(backend="uia").windows()
        except Exception as exc:
            last_error = str(exc)
            time.sleep(0.2)
            continue

        target_window = None
        for window in windows:
            try:
                window_name = window.window_text()
            except Exception:
                window_name = ""
            if title_keyword in window_name:
                target_window = window
                break

        if target_window is None:
            time.sleep(0.2)
            continue

        try:
            _prepare_window(target_window)
            candidates = _walk_uia_elements(target_window)
        except Exception as exc:
            last_error = str(exc)
            time.sleep(0.2)
            continue

        for element in candidates:
            try:
                info = element.element_info
                element_name = getattr(info, "name", "") or ""
                element_automation_id = getattr(info, "automation_id", "") or ""
                element_control_type = getattr(info, "control_type", "") or ""
            except Exception:
                continue
            if automation_id and element_automation_id != automation_id:
                continue
            if name and element_name != name:
                continue
            if control_type and element_control_type != control_type:
                continue
            return {"ok": True, "window": target_window, "element": element, "info": info}

        time.sleep(0.2)

    return {"ok": False, "last_error": last_error}


def _find_uia_window(title_keyword: str, timeout: float) -> dict[str, Any]:
    deadline = time.time() + timeout
    last_error: str | None = None
    while time.time() < deadline:
        try:
            windows = Desktop(backend="uia").windows()
        except Exception as exc:
            last_error = str(exc)
            time.sleep(0.1)
            continue
        for window in windows:
            try:
                window_name = window.window_text()
            except Exception:
                window_name = ""
            if title_keyword in window_name:
                return {"ok": True, "window": window}
        time.sleep(0.1)
    return {"ok": False, "last_error": last_error or "window not found"}


def _find_uia_top_window(
    *,
    title_keyword: str | None,
    exact_name: str | None = None,
    exact_class_name: str | None = None,
    timeout: float,
) -> dict[str, Any]:
    deadline = time.time() + timeout
    last_error: str | None = None
    while time.time() < deadline:
        try:
            windows = Desktop(backend="uia").windows()
        except Exception as exc:
            last_error = str(exc)
            time.sleep(0.05)
            continue

        for window in windows:
            try:
                info = window.element_info
                window_name = getattr(info, "name", "") or ""
                class_name = getattr(info, "class_name", "") or ""
            except Exception:
                continue
            if title_keyword and not exact_name and title_keyword not in window_name and title_keyword not in class_name:
                continue
            if exact_name and window_name != exact_name:
                continue
            if exact_class_name and class_name != exact_class_name:
                continue
            return {"ok": True, "window": window, "info": info}
        time.sleep(0.05)
    return {"ok": False, "last_error": last_error or "window not found"}


def _find_uia_element_in_window(
    window: Any,
    automation_id: str | None,
    name: str | None,
    control_type: str | None,
) -> dict[str, Any]:
    try:
        candidates = _walk_uia_elements(window)
    except Exception as exc:
        return {"ok": False, "last_error": str(exc)}

    for element in candidates:
        try:
            info = element.element_info
            element_name = getattr(info, "name", "") or ""
            element_automation_id = getattr(info, "automation_id", "") or ""
            element_control_type = getattr(info, "control_type", "") or ""
        except Exception:
            continue
        if automation_id and element_automation_id != automation_id:
            continue
        if name and element_name != name:
            continue
        if control_type and element_control_type != control_type:
            continue
        return {"ok": True, "window": window, "element": element, "info": info}

    return {"ok": False, "last_error": "element not found in cached window"}


def _find_uia_element_direct_in_window(
    window: Any,
    automation_id: str | None,
    name: str | None,
    control_type: str | None,
) -> dict[str, Any]:
    try:
        kwargs: dict[str, Any] = {}
        if automation_id:
            kwargs["auto_id"] = automation_id
        if name:
            kwargs["title"] = name
        if control_type:
            kwargs["control_type"] = control_type
        if not kwargs:
            return {"ok": False, "last_error": "direct lookup requires at least one selector"}
        element = window.child_window(**kwargs).wrapper_object()
        return {"ok": True, "window": window, "element": element, "info": element.element_info}
    except Exception as exc:
        return {"ok": False, "last_error": str(exc)}


def _find_uia_child_element_direct(
    window: Any,
    *,
    automation_id: str | None = None,
    name: str | None = None,
    control_type: str | None = None,
) -> dict[str, Any]:
    try:
        kwargs: dict[str, Any] = {}
        if automation_id:
            kwargs["auto_id"] = automation_id
        if name:
            kwargs["title"] = name
        if control_type:
            kwargs["control_type"] = control_type
        if not kwargs:
            return {"ok": False, "last_error": "direct child lookup requires at least one selector"}
        element = window.child_window(**kwargs).wrapper_object()
        return {"ok": True, "element": element, "info": element.element_info}
    except Exception as exc:
        return {"ok": False, "last_error": str(exc)}


def _find_uia_path_element(title_keyword: str, path: str, timeout: float) -> dict[str, Any]:
    deadline = time.time() + timeout
    last_error: str | None = None
    if not path:
        return {"ok": False, "last_error": "path must be non-empty"}
    wanted_path = path.strip()
    if not wanted_path.startswith("0"):
        return {"ok": False, "last_error": "path must start with 0"}

    while time.time() < deadline:
        try:
            windows = Desktop(backend="uia").windows()
        except Exception as exc:
            last_error = str(exc)
            time.sleep(0.2)
            continue

        target_window = None
        for window in windows:
            try:
                window_name = window.window_text()
            except Exception:
                window_name = ""
            if title_keyword in window_name:
                target_window = window
                break

        if target_window is None:
            time.sleep(0.2)
            continue

        try:
            _prepare_window(target_window)
            for current_path, element in _walk_uia_paths(target_window):
                if current_path == wanted_path:
                    return {"ok": True, "window": target_window, "element": element, "info": element.element_info}
            raise IndexError(f"path {wanted_path} not found")
        except Exception as exc:
            last_error = str(exc)
            time.sleep(0.2)
            continue

    return {"ok": False, "last_error": last_error}


def _prepare_window(window: Any) -> None:
    try:
        handle = int(window.handle)
    except Exception:
        handle = 0
    if handle:
        restore_foreground_window(handle)


def _find_pingan_confirm_button(title_keyword: str, timeout: float) -> dict[str, Any]:
    deadline = time.time() + timeout
    last_error: str | None = None
    while time.time() < deadline:
        snapshot = inspect_uia_tree(title_keyword, max_depth=6)
        if not snapshot.ok:
            last_error = snapshot.message
            time.sleep(0.1)
            continue
        nodes = list(snapshot.data.get("nodes", []))
        confirm_pane_path = None
        for node in nodes:
            if node.get("name") == "买入交易确认" and node.get("class_name") == "#32770":
                confirm_pane_path = node.get("path")
                break
        if not confirm_pane_path:
            time.sleep(0.1)
            continue
        target = _find_uia_element(
            title_keyword=title_keyword,
            automation_id="7015",
            name="买入确认",
            control_type="Button",
            timeout=0.5,
        )
        if target["ok"]:
            parent = getattr(getattr(target["element"], "parent", lambda: None)(), "element_info", None)
            parent_name = getattr(parent, "name", "") if parent is not None else ""
            if parent_name == "买入交易确认":
                return target
        last_error = "confirm button not found in current modal subtree"
        time.sleep(0.1)
    return {"ok": False, "last_error": last_error}


def _find_pingan_result_dialog(title_keyword: str, timeout: float) -> dict[str, Any]:
    deadline = time.time() + timeout
    last_error: str | None = None
    while time.time() < deadline:
        target = _find_pingan_result_confirm_button(title_keyword=title_keyword, timeout=0.5)
        if target["ok"]:
            parent_wrapper = getattr(target["element"], "parent", lambda: None)()
            parent_info = getattr(parent_wrapper, "element_info", None)
            parent_name = getattr(parent_info, "name", "") if parent_info is not None else ""
            if parent_name == "提示":
                return {"ok": True, "window": target["window"], "element": parent_wrapper, "info": parent_info}
        last_error = target.get("last_error") or "result dialog not found"
        time.sleep(0.1)
    return {"ok": False, "last_error": last_error}


def _find_pingan_result_confirm_button(title_keyword: str, timeout: float) -> dict[str, Any]:
    deadline = time.time() + timeout
    last_error: str | None = None
    while time.time() < deadline:
        target = _find_uia_element(
            title_keyword=title_keyword,
            automation_id="7015",
            name="确认",
            control_type="Button",
            timeout=0.5,
        )
        if target["ok"]:
            parent_wrapper = getattr(target["element"], "parent", lambda: None)()
            parent_info = getattr(parent_wrapper, "element_info", None)
            parent_name = getattr(parent_info, "name", "") if parent_info is not None else ""
            if parent_name == "提示":
                return target
        last_error = target.get("last_error") or "result confirm button not found"
        time.sleep(0.1)
    return {"ok": False, "last_error": last_error}


def _match_win32_top_window(item: dict[str, Any], title: str, class_name: str = "#32770") -> bool:
    return bool(item.get("visible")) and str(item.get("title", "") or "") == title and str(item.get("class_name", "") or "") == class_name


def _build_hwnd_runtime_target(hwnd: int, *, name: str, control_type: str, class_name: str | None = None, window_hwnd: int | None = None) -> dict[str, Any]:
    resolved_class_name = class_name or str(get_class_name(hwnd) or "")
    info = SimpleNamespace(
        automation_id="",
        name=name,
        control_type=control_type,
        class_name=resolved_class_name,
        handle=int(hwnd),
        rich_text=name,
        rectangle=None,
    )
    element = SimpleNamespace(
        element_info=info,
        window_text=lambda: str(get_text(int(hwnd)) or name or ""),
        texts=lambda: [str(get_text(int(hwnd)) or name or "")] if str(get_text(int(hwnd)) or name or "").strip() else [],
        descendants=lambda: [],
        children=lambda: [],
        set_focus=lambda: focus_window(int(hwnd), settle_delay=0.02),
    )
    window_info = SimpleNamespace(handle=int(window_hwnd or hwnd))
    window = SimpleNamespace(handle=int(window_hwnd or hwnd), element_info=window_info)
    return {"ok": True, "hwnd": int(hwnd), "window": window, "element": element, "info": info}


def _find_win32_top_window_exact(title: str, class_name: str = "#32770") -> dict[str, Any]:
    try:
        items = enumerate_top_windows()
    except Exception as exc:
        return {"ok": False, "last_error": str(exc)}
    for item in items:
        if _match_win32_top_window(item, title=title, class_name=class_name):
            return {"ok": True, "hwnd": int(item["hwnd"]), "item": item}
    return {"ok": False, "last_error": "window not found"}


def _find_win32_child_window(parent_hwnd: int, *, text: str, class_name: str) -> dict[str, Any]:
    try:
        children = enumerate_child_windows(int(parent_hwnd))
    except Exception as exc:
        return {"ok": False, "last_error": str(exc)}
    for child_hwnd in children:
        try:
            child_text = str(get_text(int(child_hwnd)) or "").strip()
            child_class = str(get_class_name(int(child_hwnd)) or "")
        except Exception:
            continue
        if child_text == text and child_class == class_name:
            return {"ok": True, "hwnd": int(child_hwnd)}
    return {"ok": False, "last_error": "child window not found"}


def _find_pingan_confirm_button_win32(timeout: float) -> dict[str, Any]:
    deadline = time.time() + timeout
    last_error: str | None = None
    while time.time() < deadline:
        dialog = _find_win32_top_window_exact("买入交易确认")
        if dialog["ok"]:
            button = _find_win32_child_window(int(dialog["hwnd"]), text="买入确认", class_name="Button")
            if button["ok"]:
                return _build_hwnd_runtime_target(
                    int(button["hwnd"]),
                    name="买入确认",
                    control_type="Button",
                    class_name="Button",
                    window_hwnd=int(dialog["hwnd"]),
                )
            last_error = button.get("last_error")
        else:
            last_error = dialog.get("last_error")
        time.sleep(0.05)
    return {"ok": False, "last_error": last_error}


def _find_pingan_result_dialog_win32(timeout: float) -> dict[str, Any]:
    deadline = time.time() + timeout
    last_error: str | None = None
    while time.time() < deadline:
        dialog = _find_win32_top_window_exact("提示")
        if dialog["ok"]:
            button = _find_win32_child_window(int(dialog["hwnd"]), text="确认", class_name="Button")
            if button["ok"]:
                target = _build_hwnd_runtime_target(
                    int(dialog["hwnd"]),
                    name="提示",
                    control_type="Pane",
                    class_name="#32770",
                    window_hwnd=int(dialog["hwnd"]),
                )
                target["element_for_extract"] = None
                return target
            last_error = button.get("last_error")
        else:
            last_error = dialog.get("last_error")
        time.sleep(0.05)
    return {"ok": False, "last_error": last_error}


def _find_pingan_result_confirm_button_win32(timeout: float) -> dict[str, Any]:
    deadline = time.time() + timeout
    last_error: str | None = None
    while time.time() < deadline:
        dialog = _find_win32_top_window_exact("提示")
        if dialog["ok"]:
            button = _find_win32_child_window(int(dialog["hwnd"]), text="确认", class_name="Button")
            if button["ok"]:
                return _build_hwnd_runtime_target(
                    int(button["hwnd"]),
                    name="确认",
                    control_type="Button",
                    class_name="Button",
                    window_hwnd=int(dialog["hwnd"]),
                )
            last_error = button.get("last_error")
        else:
            last_error = dialog.get("last_error")
        time.sleep(0.05)
    return {"ok": False, "last_error": last_error}


def _click_runtime_hwnd(hwnd: int, strategy: str, post_delay: float) -> Result:
    try:
        if strategy == "bm_click":
            click(hwnd)
        elif strategy == "wm_command":
            control_id = get_control_id(int(hwnd))
            parent = get_parent(int(hwnd))
            if parent is None:
                return Result(
                    ok=False,
                    code=ErrorCode.EXECUTION_FAILED,
                    message="parent handle is unavailable",
                    data={"hwnd": hwnd, "strategy": strategy},
                )
            if control_id is None:
                return Result(
                    ok=False,
                    code=ErrorCode.EXECUTION_FAILED,
                    message="control id is unavailable",
                    data={"hwnd": hwnd, "strategy": strategy},
                )
            send_wm_command(parent, control_id, int(hwnd))
        elif strategy == "enter_key":
            send_enter(hwnd)
        else:
            return Result(
                ok=False,
                code=ErrorCode.INVALID_REQUEST,
                message="unsupported runtime click strategy",
                data={"hwnd": hwnd, "strategy": strategy},
            )
        if post_delay > 0:
            time.sleep(post_delay)
        return Result(
            ok=True,
            code=ErrorCode.OK,
            message=f"clicked runtime Win32 control via {strategy}",
            data={"hwnd": hwnd, "strategy": strategy},
        )
    except Exception as exc:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"failed to click runtime Win32 control: {exc}",
            data={"hwnd": hwnd, "strategy": strategy},
        )


def _focus_runtime_hwnd(hwnd: int, post_delay: float) -> Result:
    try:
        focus_window(int(hwnd), settle_delay=0.02)
        if post_delay > 0:
            time.sleep(post_delay)
        return Result(
            ok=True,
            code=ErrorCode.OK,
            message="focused runtime Win32 control",
            data={"hwnd": int(hwnd)},
        )
    except Exception as exc:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"failed to focus runtime Win32 control: {exc}",
            data={"hwnd": int(hwnd)},
        )


def _click_runtime_target(target: dict[str, Any], strategy: str, post_delay: float) -> Result:
    try:
        element = target["element"]
        info = target["info"]
        if strategy == "bm_click":
            _strategy_bm_click(element, info)
        elif strategy == "wm_command":
            _strategy_wm_command(element, info)
        elif strategy == "enter_key":
            _strategy_enter_key(element, info)
        else:
            return Result(
                ok=False,
                code=ErrorCode.INVALID_REQUEST,
                message="unsupported runtime target click strategy",
                data={"strategy": strategy},
            )
        if post_delay > 0:
            time.sleep(post_delay)
        payload = _safe_serialize_runtime_element(element, info)
        payload["strategy"] = strategy
        return Result(
            ok=True,
            code=ErrorCode.OK,
            message=f"clicked runtime target via {strategy}",
            data=payload,
        )
    except Exception as exc:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"failed to click runtime target: {exc}",
            data={"strategy": strategy},
        )


def _focus_runtime_target(target: dict[str, Any], post_delay: float) -> Result:
    try:
        element = target["element"]
        info = target["info"]
        _prepare_window(target["window"])
        element.set_focus()
        if post_delay > 0:
            time.sleep(post_delay)
        return Result(
            ok=True,
            code=ErrorCode.OK,
            message="focused runtime target",
            data=_safe_serialize_runtime_element(element, info),
        )
    except Exception as exc:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"failed to focus runtime target: {exc}",
        )


def _walk_uia_elements(root: Any) -> list[Any]:
    items: list[Any] = []

    def visit(node: Any) -> None:
        items.append(node)
        try:
            children = node.children()
        except Exception:
            return
        for child in children:
            visit(child)

    visit(root)
    return items


def _walk_uia_paths(root: Any) -> list[tuple[str, Any]]:
    items: list[tuple[str, Any]] = []

    def visit(node: Any, parent_path: str | None, index: int) -> None:
        path = f"{parent_path}/{index}" if parent_path is not None else "0"
        items.append((path, node))
        try:
            children = node.children()
        except Exception:
            return
        for child_index, child in enumerate(children):
            visit(child, path, child_index)

    visit(root, None, 0)
    return items


def _activate_target(title_keyword: str, target: dict[str, Any], post_delay: float, strategy: str) -> Result:
    element = target["element"]
    info = target["info"]
    _prepare_window(target["window"])
    attempts: list[dict[str, Any]] = []
    strategies = [
        ("invoke", _strategy_invoke),
        ("click_input", _strategy_click_input),
        ("bm_click", _strategy_bm_click),
        ("wm_command", _strategy_wm_command),
        ("enter_key", _strategy_enter_key),
    ]
    if strategy != "auto":
        strategies = [item for item in strategies if item[0] == strategy]
    for label, strategy in strategies:
        try:
            strategy(element, info)
            time.sleep(post_delay)
            payload = _safe_serialize_runtime_element(element, info)
            payload["title_keyword"] = title_keyword
            payload["strategy"] = label
            payload["attempts"] = attempts + [{"strategy": label, "ok": True}]
            return Result(
                ok=True,
                code=ErrorCode.OK,
                message=f"activated UIA element via {label}",
                data=payload,
            )
        except Exception as exc:
            attempts.append({"strategy": label, "ok": False, "error": str(exc)})

    return Result(
        ok=False,
        code=ErrorCode.EXECUTION_FAILED,
        message="failed to activate UIA element with all strategies",
        data={
            "title_keyword": title_keyword,
            "automation_id": getattr(info, "automation_id", "") or "",
            "name": getattr(info, "name", "") or "",
            "control_type": getattr(info, "control_type", "") or "",
            "attempts": attempts,
        },
    )


def _serialize_runtime_element(element: Any, info: Any) -> dict[str, Any]:
    rect = getattr(info, "rectangle", None)
    payload = {
        "automation_id": getattr(info, "automation_id", "") or "",
        "name": getattr(info, "name", "") or "",
        "control_type": getattr(info, "control_type", "") or "",
        "class_name": getattr(info, "class_name", "") or "",
        "handle": getattr(info, "handle", None),
        "rich_text": getattr(info, "rich_text", "") or "",
        "rectangle": (
            [rect.left, rect.top, rect.right, rect.bottom]
            if rect is not None and hasattr(rect, "left")
            else None
        ),
    }
    for attr_name, key in (
        ("legacy_properties", "legacy_properties"),
        ("iface_legacy_iaccessible", "legacy_accessible"),
    ):
        try:
            payload[key] = str(getattr(element.element_info, attr_name))
        except Exception:
            continue
    try:
        payload["window_text"] = element.window_text()
    except Exception:
        payload["window_text"] = ""
    try:
        payload["texts"] = element.texts()
    except Exception:
        payload["texts"] = []
    try:
        payload["legacy_value"] = element.legacy_properties().get("Value")
    except Exception:
        payload["legacy_value"] = None
    try:
        payload["selected_text"] = element.selected_text()
    except Exception:
        payload["selected_text"] = None
    try:
        children = element.children()
        payload["child_texts"] = [child.window_text() for child in children if child.window_text()]
    except Exception:
        payload["child_texts"] = []
    payload["descendant_texts"] = _collect_descendant_texts(element)
    return payload


def _safe_serialize_runtime_element(element: Any, info: Any) -> dict[str, Any]:
    try:
        return _serialize_runtime_element(element, info)
    except Exception as exc:
        return {
            "automation_id": _safe_info_attr(info, "automation_id"),
            "name": _safe_info_attr(info, "name"),
            "control_type": _safe_info_attr(info, "control_type"),
            "class_name": _safe_info_attr(info, "class_name"),
            "handle": _safe_info_attr(info, "handle"),
            "rich_text": _safe_info_attr(info, "rich_text"),
            "rectangle": None,
            "window_text": "",
            "texts": [],
            "legacy_value": None,
            "selected_text": None,
            "child_texts": [],
            "descendant_texts": [],
            "serialization_warning": str(exc),
        }


def _safe_info_attr(info: Any, attr_name: str) -> Any:
    try:
        value = getattr(info, attr_name, None)
    except Exception:
        return None
    return value or ("" if attr_name in {"automation_id", "name", "control_type", "class_name", "rich_text"} else value)


def _extract_dialog_text_payload(hwnd: Any) -> dict[str, Any]:
    return _extract_dialog_text_payload_from_sources(hwnd=hwnd)


def _extract_contract_no_from_texts(texts: list[str]) -> str | None:
    for text in texts:
        match = re.search(r"合同号(?:[：: ]|是)*([0-9A-Za-z]+)", text)
        if match:
            return match.group(1)
    return None


def _append_unique_text(target: list[str], seen: set[str], value: Any) -> None:
    normalized = str(value or "").strip()
    if not normalized or normalized in seen:
        return
    seen.add(normalized)
    target.append(normalized)


def _collect_win32_descendant_texts(hwnd: int, max_depth: int = 4) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []

    def walk(current_hwnd: int, depth: int, parent_hwnd: int | None) -> None:
        if depth > max_depth:
            return
        try:
            children = enumerate_child_windows(current_hwnd)
        except Exception:
            return
        for child_hwnd in children:
            try:
                text = str(get_text(child_hwnd) or "").strip()
            except Exception:
                text = ""
            try:
                class_name = str(get_class_name(child_hwnd) or "")
            except Exception:
                class_name = ""
            items.append(
                {
                    "hwnd": int(child_hwnd),
                    "parent_hwnd": int(parent_hwnd) if parent_hwnd else int(current_hwnd),
                    "depth": depth,
                    "class_name": class_name,
                    "text": text,
                }
            )
            walk(int(child_hwnd), depth + 1, int(current_hwnd))

    walk(int(hwnd), 1, None)
    return items


def _extract_dialog_text_payload_from_sources(hwnd: Any, element: Any | None = None) -> dict[str, Any]:
    try:
        dialog_hwnd = int(hwnd)
    except Exception:
        dialog_hwnd = 0
    child_items: list[dict[str, Any]] = []
    descendant_items: list[dict[str, Any]] = []
    merged_texts: list[str] = []
    seen_texts: set[str] = set()
    if dialog_hwnd:
        try:
            for child_hwnd in enumerate_child_windows(dialog_hwnd):
                text = str(get_text(child_hwnd) or "").strip()
                class_name = str(get_class_name(child_hwnd) or "")
                _append_unique_text(merged_texts, seen_texts, text)
                child_items.append(
                    {
                        "hwnd": int(child_hwnd),
                        "class_name": class_name,
                        "text": text,
                    }
                )
        except Exception:
            child_items = []
        descendant_items = _collect_win32_descendant_texts(dialog_hwnd)
        for item in descendant_items:
            _append_unique_text(merged_texts, seen_texts, item.get("text"))

    uia_texts: list[str] = []
    uia_tree: dict[str, Any] | None = None
    if element is not None:
        for getter in (
            lambda current: current.window_text(),
            lambda current: getattr(getattr(current, "element_info", None), "name", ""),
            lambda current: getattr(getattr(current, "element_info", None), "rich_text", ""),
        ):
            try:
                _append_unique_text(uia_texts, seen_texts, getter(element))
            except Exception:
                continue
        for text in _collect_descendant_texts(element):
            _append_unique_text(uia_texts, seen_texts, text)
        try:
            uia_tree = _serialize_uia_subtree(element, max_depth=4)
        except Exception as exc:
            uia_tree = {"error": str(exc)}
    merged_texts.extend(uia_texts)

    contract_no = _extract_contract_no_from_texts(merged_texts)
    return {
        "win32_child_texts": child_items,
        "win32_descendant_texts": descendant_items,
        "uia_texts": uia_texts,
        "uia_tree": uia_tree,
        "merged_texts": merged_texts,
        "contract_no": contract_no,
    }


def _collect_descendant_texts(element: Any) -> list[str]:
    texts: list[str] = []
    seen: set[str] = set()
    try:
        descendants = element.descendants()
    except Exception:
        return texts
    for child in descendants:
        for getter in (lambda c: c.window_text(), lambda c: getattr(c.element_info, "rich_text", "") or ""):
            try:
                value = getter(child)
            except Exception:
                value = ""
            normalized = str(value or "").strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            texts.append(normalized)
    return texts


def _strategy_invoke(element: Any, info: Any) -> None:
    if hasattr(element, "invoke"):
        element.invoke()
        return
    raise RuntimeError("invoke() is unavailable")


def _strategy_click_input(element: Any, info: Any) -> None:
    element.click_input()


def _strategy_bm_click(element: Any, info: Any) -> None:
    handle = getattr(info, "handle", None)
    if not handle:
        raise RuntimeError("native handle is unavailable")
    click(int(handle))


def _strategy_enter_key(element: Any, info: Any) -> None:
    element.set_focus()
    handle = getattr(info, "handle", None)
    if handle:
        send_enter(int(handle))
        return
    element.type_keys("{ENTER}", set_foreground=False)


def _strategy_wm_command(element: Any, info: Any) -> None:
    handle = getattr(info, "handle", None)
    if not handle:
        raise RuntimeError("native handle is unavailable")
    control_id = get_control_id(int(handle))
    parent = get_parent(int(handle))
    if parent is None:
        raise RuntimeError("parent handle is unavailable")
    if control_id is None:
        raise RuntimeError("control id is unavailable")
    send_wm_command(parent, control_id, int(handle))


def analyze_uia_snapshot(snapshot: dict[str, Any]) -> Result:
    nodes = snapshot.get("nodes", [])
    keyword_tokens = ("买入", "卖出", "下单", "代码", "证券", "价格", "委托", "数量", "股数")
    editable_types = {"Edit", "Document", "Pane", "Custom"}
    actionable_types = {"Button", "Hyperlink"}

    keyword_hits = []
    editable_candidates = []
    actionable_candidates = []
    browser_like_nodes = []

    for node in nodes:
        searchable = "".join(
            str(node.get(key, "") or "") for key in ("name", "automation_id", "class_name", "rich_text", "control_type")
        )
        if any(token in searchable for token in keyword_tokens):
            keyword_hits.append(node)
        if node.get("control_type") in editable_types:
            editable_candidates.append(node)
        if node.get("control_type") in actionable_types:
            actionable_candidates.append(node)
        if any(token in searchable for token in ("Chrome", "Cef", "Browser", "Document")):
            browser_like_nodes.append(node)

    return Result(
        ok=True,
        code=ErrorCode.OK,
        message="analyzed UIA snapshot",
        data={
            "node_count": len(nodes),
            "keyword_hits": keyword_hits[:50],
            "editable_candidates": editable_candidates[:50],
            "actionable_candidates": actionable_candidates[:50],
            "browser_like_nodes": browser_like_nodes[:50],
            "summary": {
                "keyword_hit_count": len(keyword_hits),
                "editable_candidate_count": len(editable_candidates),
                "actionable_candidate_count": len(actionable_candidates),
                "browser_like_node_count": len(browser_like_nodes),
            },
        },
        warnings=[
            "UIA visibility depends on how the embedded Chromium surface exposes accessibility nodes.",
        ],
    )
