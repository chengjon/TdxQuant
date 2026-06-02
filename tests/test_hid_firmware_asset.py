from __future__ import annotations

from pathlib import Path


def test_hid_firmware_asset_matches_documented_path_and_protocol() -> None:
    firmware_path = (
        Path(__file__).resolve().parents[1]
        / "firmware"
        / "arduino"
        / "tdx_hid_keyboard"
        / "tdx_hid_keyboard.ino"
    )

    source = firmware_path.read_text(encoding="utf-8")

    assert "#include <Keyboard.h>" in source
    assert 'if (line == "PING")' in source
    assert 'line.startsWith("KEY ")' in source
    assert 'line.startsWith("TYPE ")' in source
    assert "ERR TYPE_ONLY_DIGITS" in source
