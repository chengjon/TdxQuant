from tdxquant.cli import build_parser, run_tdx_trade_hid_send, run_tdx_trade_probe
from tdxquant.hid_bridge import validate_hid_wire_command


def test_validate_hid_wire_command_supports_minimal_protocol() -> None:
    assert validate_hid_wire_command("PING") == "PING"
    assert validate_hid_wire_command("key tab") == "KEY TAB"
    assert validate_hid_wire_command("TYPE 000001 enter") == "TYPE 000001 ENTER"


def test_validate_hid_wire_command_rejects_unsupported_command() -> None:
    try:
        validate_hid_wire_command("MOUSE CLICK")
    except ValueError as exc:
        assert "unsupported HID wire command" in str(exc)
    else:
        raise AssertionError("expected ValueError for unsupported HID wire command")


def test_tdx_trade_hid_send_rejects_invalid_command_before_runtime() -> None:
    result = run_tdx_trade_hid_send(port="COM3", baudrate=115200, timeout=2.0, command="MOUSE CLICK")
    assert not result.ok
    assert result.code.value == "invalid_request"
    assert result.next_action is not None


def test_tdx_trade_probe_returns_unsupported_or_control_result() -> None:
    result = run_tdx_trade_probe(window_key="通达信金融终端", max_depth=12)
    assert result.code.value in {"unsupported_platform", "ok", "control_not_found", "window_not_found"}


def test_parser_accepts_trade_bridge_commands() -> None:
    parser = build_parser()
    args = parser.parse_args(["trade", "buy", "--port", "COM3", "--code", "000001", "--price", "10.00", "--quantity", "100"])
    assert args.command == "trade"
    assert args.trade_command == "buy"

    args = parser.parse_args(["trade", "submit-once", "--port", "COM3", "--code", "000001", "--price", "10.00", "--quantity", "100"])
    assert args.command == "trade"
    assert args.trade_command == "submit-once"

    args = parser.parse_args(["tdx-trade-probe"])
    assert args.command == "tdx-trade-probe"

    args = parser.parse_args(["tdx-trade-hid-ping", "--port", "COM3"])
    assert args.command == "tdx-trade-hid-ping"

    args = parser.parse_args(["tdx-trade-hid-send", "--port", "COM3", "--wire-command", "TYPE 000001 TAB"])
    assert args.command == "tdx-trade-hid-send"

    args = parser.parse_args(
        [
            "tdx-trade-buy-probe",
            "--port",
            "COM3",
            "--code",
            "000001",
            "--price",
            "10.00",
            "--quantity",
            "100",
        ]
    )
    assert args.command == "tdx-trade-buy-probe"
