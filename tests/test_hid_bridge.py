from tdxquant.hid_bridge import build_type_command, normalize_hid_key


def test_normalize_hid_key_supports_expected_names() -> None:
    assert normalize_hid_key("tab") == "TAB"
    assert normalize_hid_key("ENTER") == "ENTER"
    assert normalize_hid_key("ctrl+a") == "CTRL+A"


def test_build_type_command_without_commit_key() -> None:
    assert build_type_command("000001") == "TYPE 000001"


def test_build_type_command_with_commit_key() -> None:
    assert build_type_command("000001", commit_key="tab") == "TYPE 000001 TAB"
