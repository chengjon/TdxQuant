from __future__ import annotations

from dataclasses import asdict
from typing import Callable

from ..exceptions import UnsupportedPlatformError
from ..models import ControlInfo, ErrorCode, Result
from .win32 import IS_WINDOWS, win32gui


def _guard() -> Result | None:
    if not IS_WINDOWS:
        return Result(
            ok=False,
            code=ErrorCode.UNSUPPORTED_PLATFORM,
            message="Win32 window inspection is only available from native Windows Python",
            next_action="Run the CLI under Windows rather than inside WSL/Linux.",
        )
    return None


def find_main_window(title_keyword: str) -> Result:
    guard = _guard()
    if guard:
        return guard

    matches: list[dict[str, int | str | bool]] = []

    def enum_callback(hwnd: int, _: object) -> bool:
        title = win32gui.GetWindowText(hwnd)
        if title_keyword in title:
            matches.append(
                {
                    "hwnd": hwnd,
                    "title": title,
                    "class_name": win32gui.GetClassName(hwnd),
                    "visible": bool(win32gui.IsWindowVisible(hwnd)),
                }
            )
        return True

    win32gui.EnumWindows(enum_callback, None)
    if not matches:
        return Result(
            ok=False,
            code=ErrorCode.WINDOW_NOT_FOUND,
            message=f"could not find a top-level window containing {title_keyword!r}",
            data={"title_keyword": title_keyword},
            next_action="Open Ping An Securities, log in, and navigate to the trading page.",
        )
    matches.sort(key=_match_score, reverse=True)
    return Result(
        ok=True,
        code=ErrorCode.OK,
        message="found top-level window",
        data={"title_keyword": title_keyword, "matches": matches, "main_hwnd": matches[0]["hwnd"]},
    )


def _match_score(item: dict[str, int | str | bool]) -> tuple[int, int, int]:
    title = str(item.get("title", "") or "")
    class_name = str(item.get("class_name", "") or "")
    visible = 1 if item.get("visible") else 0
    class_score = 2 if class_name == "TdxW_MainFrame_Class" else 1 if class_name == "#32770" else 0
    title_penalty = -1 if "cmd.exe" in title.lower() else 0
    return (class_score, visible, title_penalty)


def enumerate_controls(main_hwnd: int) -> Result:
    guard = _guard()
    if guard:
        return guard

    controls: list[ControlInfo] = []

    def walk(parent_hwnd: int, parent: int | None) -> None:
        child_index = 0

        def callback(hwnd: int, _: object) -> bool:
            nonlocal child_index
            try:
                rect = win32gui.GetWindowRect(hwnd)
            except Exception:
                rect = None
            controls.append(
                ControlInfo(
                    hwnd=hwnd,
                    class_name=win32gui.GetClassName(hwnd),
                    text=win32gui.GetWindowText(hwnd),
                    parent_hwnd=parent,
                    rect=rect,
                    child_index=child_index,
                )
            )
            child_index += 1
            walk(hwnd, hwnd)
            return True

        win32gui.EnumChildWindows(parent_hwnd, callback, None)

    walk(main_hwnd, main_hwnd)
    return Result(
        ok=True,
        code=ErrorCode.OK,
        message="enumerated window controls",
        data={"main_hwnd": main_hwnd, "controls": [asdict(control) for control in controls]},
    )
