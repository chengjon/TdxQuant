from __future__ import annotations

import os
import platform
import re
from pathlib import Path, PureWindowsPath

from .models import ErrorCode, Result

DEFAULT_WINDOWS_PATHS = [
    r"D:\ProgramData\PinganSec\TdxW.exe",
    r"C:\ProgramData\PinganSec\TdxW.exe",
]

DEFAULT_WSL_PATHS = [
    "/mnt/d/ProgramData/PinganSec/TdxW.exe",
    "/mnt/c/ProgramData/PinganSec/TdxW.exe",
]


def windows_path_to_wsl(path: str) -> str | None:
    match = re.match(r"^([A-Za-z]):[\\/](.*)$", path)
    if not match:
        return None
    drive_letter = match.group(1).lower()
    normalized = match.group(2).replace("\\", "/").lstrip("/")
    return f"/mnt/{drive_letter}/{normalized}"


def wsl_path_to_windows(path: str) -> str | None:
    if not path.startswith("/mnt/") or len(path) < 7:
        return None
    drive_letter = path[5]
    tail = path[7:].replace("/", "\\")
    return str(PureWindowsPath(f"{drive_letter.upper()}:\\{tail}"))


def _candidate_paths(explicit_path: str | None = None) -> list[tuple[str, str]]:
    candidates: list[tuple[str, str]] = []
    if explicit_path:
        candidates.append(("explicit", explicit_path))
        translated = windows_path_to_wsl(explicit_path)
        if translated:
            candidates.append(("explicit-windows->wsl", translated))
        translated = wsl_path_to_windows(explicit_path)
        if translated:
            candidates.append(("explicit-wsl->windows", translated))
    for path in DEFAULT_WINDOWS_PATHS:
        candidates.append(("default-windows", path))
        translated = windows_path_to_wsl(path)
        if translated:
            candidates.append(("default-windows->wsl", translated))
    for path in DEFAULT_WSL_PATHS:
        candidates.append(("default-wsl", path))
        translated = wsl_path_to_windows(path)
        if translated:
            candidates.append(("default-wsl->windows", translated))
    seen: set[str] = set()
    unique: list[tuple[str, str]] = []
    for source, path in candidates:
        if path not in seen:
            unique.append((source, path))
            seen.add(path)
    return unique


def resolve_runtime(explicit_path: str | None = None) -> Result:
    attempted: list[dict[str, str | bool]] = []
    for source, path in _candidate_paths(explicit_path):
        exists = Path(path).exists()
        attempted.append({"source": source, "path": path, "exists": exists})
        if exists:
            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="resolved Ping An Securities runtime path",
                data={
                    "detected_path": path,
                    "path_source": source,
                    "platform": platform.system(),
                    "windows_path": wsl_path_to_windows(path) if path.startswith("/mnt/") else path,
                    "wsl_path": windows_path_to_wsl(path) if ":" in path else path,
                    "attempted_paths": attempted,
                },
            )
    return Result(
        ok=False,
        code=ErrorCode.PATH_NOT_FOUND,
        message="could not resolve Ping An Securities runtime path",
        data={"attempted_paths": attempted},
        next_action="Provide --exe-path or install the client under a supported path.",
    )
