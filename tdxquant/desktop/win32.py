from __future__ import annotations

import platform
import time
import ctypes
from ctypes import wintypes

from ..exceptions import UnsupportedPlatformError

IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    import win32api
    import win32con
    import win32gui
    import win32process
else:
    win32api = None
    win32con = None
    win32gui = None
    win32process = None

if IS_WINDOWS:
    _user32 = ctypes.windll.user32
else:
    _user32 = None


if IS_WINDOWS:
    class GUITHREADINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.DWORD),
            ("flags", wintypes.DWORD),
            ("hwndActive", wintypes.HWND),
            ("hwndFocus", wintypes.HWND),
            ("hwndCapture", wintypes.HWND),
            ("hwndMenuOwner", wintypes.HWND),
            ("hwndMoveSize", wintypes.HWND),
            ("hwndCaret", wintypes.HWND),
            ("rcCaret", wintypes.RECT),
        ]
else:
    GUITHREADINFO = None


def require_windows() -> None:
    if not IS_WINDOWS:
        raise UnsupportedPlatformError("Win32 automation requires running under native Windows Python")


def set_text(hwnd: int, text: str) -> None:
    require_windows()
    win32api.SendMessage(hwnd, win32con.WM_SETTEXT, 0, text)


def type_text(hwnd: int, text: str, clear_first: bool = True) -> None:
    require_windows()
    if clear_first:
        set_text(hwnd, "")
    for ch in text:
        win32api.SendMessage(hwnd, win32con.WM_CHAR, ord(ch), 0)


def get_text(hwnd: int) -> str:
    require_windows()
    # GetWindowText is unreliable for cross-process Edit controls.
    length = int(_user32.SendMessageW(int(hwnd), win32con.WM_GETTEXTLENGTH, 0, 0))
    if length <= 0:
        return win32gui.GetWindowText(hwnd)
    buffer = ctypes.create_unicode_buffer(length + 1)
    copied = int(_user32.SendMessageW(int(hwnd), win32con.WM_GETTEXT, length + 1, ctypes.byref(buffer)))
    if copied <= 0:
        return win32gui.GetWindowText(hwnd)
    return buffer.value


def get_class_name(hwnd: int) -> str:
    require_windows()
    return win32gui.GetClassName(hwnd)


def get_rect(hwnd: int) -> tuple[int, int, int, int] | None:
    require_windows()
    try:
        return tuple(int(value) for value in win32gui.GetWindowRect(hwnd))
    except Exception:
        return None


def click(hwnd: int) -> None:
    require_windows()
    win32api.SendMessage(hwnd, win32con.BM_CLICK, 0, 0)


def get_parent(hwnd: int) -> int | None:
    require_windows()
    parent = win32gui.GetParent(hwnd)
    return int(parent) if parent else None


def enumerate_child_windows(hwnd: int) -> list[int]:
    require_windows()
    children: list[int] = []

    def _callback(child_hwnd: int, _lparam: int) -> bool:
        children.append(int(child_hwnd))
        return True

    win32gui.EnumChildWindows(int(hwnd), _callback, 0)
    return children


def enumerate_top_windows() -> list[dict[str, int | str | bool]]:
    require_windows()
    items: list[dict[str, int | str | bool]] = []

    def _callback(hwnd: int, _lparam: int) -> bool:
        try:
            items.append(
                {
                    "hwnd": int(hwnd),
                    "title": str(win32gui.GetWindowText(hwnd) or ""),
                    "class_name": str(win32gui.GetClassName(hwnd) or ""),
                    "visible": bool(win32gui.IsWindowVisible(hwnd)),
                    "enabled": bool(win32gui.IsWindowEnabled(hwnd)),
                }
            )
        except Exception:
            return True
        return True

    win32gui.EnumWindows(_callback, 0)
    return items


def get_control_id(hwnd: int) -> int | None:
    require_windows()
    control_id = win32gui.GetDlgCtrlID(hwnd)
    return int(control_id) if control_id not in (0, -1) else None


def send_wm_command(parent_hwnd: int, control_id: int, control_hwnd: int | None = None, notify_code: int | None = None) -> None:
    require_windows()
    code = win32con.BN_CLICKED if notify_code is None else notify_code
    wparam = ((code & 0xFFFF) << 16) | (control_id & 0xFFFF)
    lparam = 0 if control_hwnd is None else int(control_hwnd)
    win32api.SendMessage(parent_hwnd, win32con.WM_COMMAND, wparam, lparam)


def post_wm_command(parent_hwnd: int, control_id: int, control_hwnd: int | None = None, notify_code: int | None = None) -> None:
    require_windows()
    code = win32con.BN_CLICKED if notify_code is None else notify_code
    wparam = ((code & 0xFFFF) << 16) | (control_id & 0xFFFF)
    lparam = 0 if control_hwnd is None else int(control_hwnd)
    win32gui.PostMessage(parent_hwnd, win32con.WM_COMMAND, wparam, lparam)


def send_enter(hwnd: int) -> None:
    require_windows()
    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
    win32api.SendMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)


def send_space(hwnd: int) -> None:
    require_windows()
    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_SPACE, 0)
    win32api.SendMessage(hwnd, win32con.WM_KEYUP, win32con.VK_SPACE, 0)


def send_tab(hwnd: int) -> None:
    require_windows()
    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_TAB, 0)
    win32api.SendMessage(hwnd, win32con.WM_KEYUP, win32con.VK_TAB, 0)


def _keybd_tap(vk_code: int, delay: float = 0.02) -> None:
    require_windows()
    win32api.keybd_event(int(vk_code), 0, 0, 0)
    time.sleep(delay)
    win32api.keybd_event(int(vk_code), 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(delay)


def send_delete_key(delay: float = 0.02) -> None:
    require_windows()
    _keybd_tap(win32con.VK_DELETE, delay=delay)


def send_ctrl_a(delay: float = 0.02) -> None:
    require_windows()
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    time.sleep(delay)
    win32api.keybd_event(ord("A"), 0, 0, 0)
    time.sleep(delay)
    win32api.keybd_event(ord("A"), 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(delay)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(delay)


def type_text_keybd(text: str, key_delay: float = 0.02) -> None:
    require_windows()
    for ch in text:
        vk_code = ord(ch.upper())
        _keybd_tap(vk_code, delay=key_delay)


def send_button_mouse_click(hwnd: int) -> None:
    require_windows()
    rect = win32gui.GetClientRect(hwnd)
    x = max(1, int((rect[2] - rect[0]) / 2))
    y = max(1, int((rect[3] - rect[1]) / 2))
    lparam = (y << 16) | (x & 0xFFFF)
    win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
    win32api.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, lparam)


def get_window_style(hwnd: int) -> int:
    require_windows()
    return int(win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE))


def get_window_exstyle(hwnd: int) -> int:
    require_windows()
    return int(win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE))


def click_screen_point(x: int, y: int, settle_delay: float = 0.2) -> None:
    require_windows()
    win32api.SetCursorPos((x, y))
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.03)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    if settle_delay > 0:
        time.sleep(settle_delay)


def get_foreground_window() -> int | None:
    require_windows()
    hwnd = int(_user32.GetForegroundWindow())
    return hwnd if hwnd else None


def get_gui_thread_focus(hwnd: int | None = None) -> int | None:
    require_windows()
    target_hwnd = hwnd or get_foreground_window()
    if not target_hwnd:
        return None
    thread_id, _ = win32process.GetWindowThreadProcessId(int(target_hwnd))
    if not thread_id:
        return None
    info = GUITHREADINFO()
    info.cbSize = ctypes.sizeof(GUITHREADINFO)
    ok = _user32.GetGUIThreadInfo(int(thread_id), ctypes.byref(info))
    if not ok:
        return None
    focus_hwnd = int(info.hwndFocus)
    return focus_hwnd if focus_hwnd else None


def restore_foreground_window(hwnd: int, settle_delay: float = 0.2) -> None:
    require_windows()
    if not hwnd:
        return
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    else:
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
    try:
        foreground = win32gui.GetForegroundWindow()
    except Exception:
        foreground = None
    try:
        current_thread, _ = win32process.GetWindowThreadProcessId(foreground) if foreground else (None, None)
        target_thread, _ = win32process.GetWindowThreadProcessId(hwnd)
        if current_thread and target_thread and current_thread != target_thread:
            win32process.AttachThreadInput(current_thread, target_thread, True)
            try:
                win32gui.BringWindowToTop(hwnd)
                win32gui.SetForegroundWindow(hwnd)
                win32gui.SetActiveWindow(hwnd)
                win32gui.SetFocus(hwnd)
            finally:
                win32process.AttachThreadInput(current_thread, target_thread, False)
        else:
            win32gui.BringWindowToTop(hwnd)
            win32gui.SetForegroundWindow(hwnd)
            win32gui.SetActiveWindow(hwnd)
            win32gui.SetFocus(hwnd)
    except Exception:
        # Some desktop/session combinations refuse focus APIs. Keep the window restored at minimum.
        pass
    if settle_delay > 0:
        time.sleep(settle_delay)


def focus_window(hwnd: int, settle_delay: float = 0.1) -> None:
    require_windows()
    if not hwnd:
        return
    parent = get_parent(hwnd)
    if parent:
        restore_foreground_window(parent, settle_delay=0.05)
    try:
        foreground = win32gui.GetForegroundWindow()
    except Exception:
        foreground = None
    try:
        current_thread, _ = win32process.GetWindowThreadProcessId(foreground) if foreground else (None, None)
        target_thread, _ = win32process.GetWindowThreadProcessId(hwnd)
        if current_thread and target_thread and current_thread != target_thread:
            win32process.AttachThreadInput(current_thread, target_thread, True)
            try:
                win32gui.SetFocus(hwnd)
            finally:
                win32process.AttachThreadInput(current_thread, target_thread, False)
        else:
            win32gui.SetFocus(hwnd)
    except Exception:
        pass
    if settle_delay > 0:
        time.sleep(settle_delay)


def register_window_message(name: str) -> int:
    require_windows()
    return int(win32gui.RegisterWindowMessage(name))


def post_message(hwnd: int, message: int, wparam: int = 0, lparam: int = 0) -> None:
    require_windows()
    win32gui.PostMessage(hwnd, int(message), int(wparam), int(lparam))
