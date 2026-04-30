from __future__ import annotations

import time
from dataclasses import dataclass

from ..models import ErrorCode, Result

try:
    import serial
    from serial import SerialException
except ImportError:  # pragma: no cover - dependency may be absent outside Windows runtime
    serial = None

    class SerialException(Exception):
        pass


SUPPORTED_HID_KEYS = {
    "tab": "TAB",
    "enter": "ENTER",
    "esc": "ESC",
    "delete": "DELETE",
    "ctrl+a": "CTRL+A",
}


def normalize_hid_key(name: str) -> str:
    normalized = name.strip().lower()
    if normalized not in SUPPORTED_HID_KEYS:
        raise ValueError(f"unsupported HID key: {name}")
    return SUPPORTED_HID_KEYS[normalized]


def build_type_command(text: str, commit_key: str = "none") -> str:
    payload = text.strip()
    if not payload or not payload.isdigit():
        raise ValueError("HID TYPE text must be a non-empty numeric string")
    if commit_key == "none":
        return f"TYPE {payload}"
    return f"TYPE {payload} {normalize_hid_key(commit_key)}"


def validate_hid_wire_command(command: str) -> str:
    wire = command.strip()
    if not wire:
        raise ValueError("HID wire command must not be empty")

    parts = wire.split()
    head = parts[0].upper()
    if head == "PING":
        if len(parts) != 1:
            raise ValueError("PING does not accept additional arguments")
        return "PING"

    if head == "KEY":
        if len(parts) != 2:
            raise ValueError("KEY command must have exactly one key argument")
        return f"KEY {normalize_hid_key(parts[1])}"

    if head == "TYPE":
        if len(parts) not in {2, 3}:
            raise ValueError("TYPE command must be `TYPE <digits>` or `TYPE <digits> <TAB|ENTER>`")
        commit_key = "none" if len(parts) == 2 else parts[2]
        return build_type_command(parts[1], commit_key=commit_key)

    raise ValueError("unsupported HID wire command; bridge only allows PING, KEY, and TYPE")


@dataclass(slots=True)
class HidBridgeConfig:
    port: str
    baudrate: int = 115200
    timeout: float = 2.0
    write_timeout: float = 2.0


class HidBridgeClient:
    def __init__(self, config: HidBridgeConfig) -> None:
        self.config = config
        self._serial = None

    def __enter__(self) -> "HidBridgeClient":
        if serial is None:
            raise RuntimeError("pyserial is required for HID bridge commands")
        self._serial = serial.Serial(
            port=self.config.port,
            baudrate=self.config.baudrate,
            timeout=self.config.timeout,
            write_timeout=self.config.write_timeout,
        )
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._serial is not None:
            self._serial.close()
            self._serial = None

    def send(self, command: str) -> str:
        if self._serial is None:
            raise RuntimeError("HID bridge is not connected")
        wire = command.strip() + "\n"
        self._serial.reset_input_buffer()
        self._serial.write(wire.encode("utf-8"))
        self._serial.flush()
        response = self._serial.readline().decode("utf-8", errors="replace").strip()
        if not response:
            raise TimeoutError(f"no response for HID command: {command}")
        return response


def _serial_guard_result(action: str) -> Result | None:
    if serial is not None:
        return None
    return Result(
        ok=False,
        code=ErrorCode.EXECUTION_FAILED,
        message=f"{action} requires pyserial",
        next_action="Install pyserial in the Windows Python environment before using HID bridge commands.",
    )


def run_hid_ping(port: str, baudrate: int, timeout: float, pre_delay: float = 0.0) -> Result:
    guard = _serial_guard_result("hid-ping")
    if guard:
        return guard
    config = HidBridgeConfig(port=port, baudrate=baudrate, timeout=timeout, write_timeout=timeout)
    try:
        with HidBridgeClient(config) as client:
            if pre_delay > 0:
                time.sleep(pre_delay)
            response = client.send("PING")
    except (SerialException, OSError, TimeoutError, RuntimeError) as exc:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"hid ping failed: {exc}",
            data={"port": port, "baudrate": baudrate, "timeout": timeout, "pre_delay": pre_delay},
        )
    return Result(
        ok=response.upper().startswith("OK"),
        code=ErrorCode.OK if response.upper().startswith("OK") else ErrorCode.EXECUTION_FAILED,
        message="hid bridge ping completed" if response.upper().startswith("OK") else "hid bridge ping returned non-OK response",
        data={"port": port, "baudrate": baudrate, "timeout": timeout, "pre_delay": pre_delay, "command": "PING", "response": response},
    )


def run_hid_send(port: str, baudrate: int, timeout: float, command: str, pre_delay: float = 0.0) -> Result:
    guard = _serial_guard_result("hid-send")
    if guard:
        return guard
    config = HidBridgeConfig(port=port, baudrate=baudrate, timeout=timeout, write_timeout=timeout)
    try:
        with HidBridgeClient(config) as client:
            if pre_delay > 0:
                time.sleep(pre_delay)
            response = client.send(command)
    except (SerialException, OSError, TimeoutError, RuntimeError) as exc:
        return Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"hid send failed: {exc}",
            data={"port": port, "baudrate": baudrate, "timeout": timeout, "pre_delay": pre_delay, "command": command},
        )
    return Result(
        ok=response.upper().startswith("OK"),
        code=ErrorCode.OK if response.upper().startswith("OK") else ErrorCode.EXECUTION_FAILED,
        message="hid bridge command completed" if response.upper().startswith("OK") else "hid bridge returned non-OK response",
        data={"port": port, "baudrate": baudrate, "timeout": timeout, "pre_delay": pre_delay, "command": command, "response": response},
    )
