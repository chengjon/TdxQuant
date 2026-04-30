import unittest
import json
import io
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch

from tdxquant.brokers import PingAnBrokerAdapter
from tdxquant.cli import (
    _build_pingan_buy_submit_options,
    _emit_pingan_contract_log,
    _resolve_pingan_buy_profile,
    _write_pingan_last_order_state,
)
from tdxquant.models import ControlInfo, ErrorCode, Result
from tdxquant.models import OrderRequest
from tdxquant.runtime import resolve_runtime, windows_path_to_wsl, wsl_path_to_windows
from tdxquant.uia_inspector import (
    _extract_contract_no_from_texts,
    _extract_dialog_text_payload_from_sources,
    activate_uia_element,
    analyze_uia_snapshot,
    click_uia_center,
    click_uia_element,
    click_uia_path,
    inspect_uia_windows,
    list_uia_combobox_items,
    read_uia_element,
    run_pingan_hid_submit_probe,
    run_pingan_probe,
    set_uia_text,
    select_uia_combobox_item,
)


class RuntimeMappingTests(unittest.TestCase):
    def test_windows_path_to_wsl(self) -> None:
        self.assertEqual(
            windows_path_to_wsl(r"D:\ProgramData\PinganSec\TdxW.exe"),
            "/mnt/d/ProgramData/PinganSec/TdxW.exe",
        )

    def test_wsl_path_to_windows(self) -> None:
        self.assertEqual(
            wsl_path_to_windows("/mnt/d/ProgramData/PinganSec/TdxW.exe"),
            r"D:\ProgramData\PinganSec\TdxW.exe",
        )

    def test_resolve_runtime_with_explicit_wsl_path(self) -> None:
        result = resolve_runtime("/mnt/d/ProgramData/PinganSec/TdxW.exe")
        self.assertTrue(result.ok)
        self.assertEqual(result.data["wsl_path"], "/mnt/d/ProgramData/PinganSec/TdxW.exe")
        self.assertEqual(result.data["windows_path"], r"D:\ProgramData\PinganSec\TdxW.exe")


class OrderRequestValidationTests(unittest.TestCase):
    def test_valid_order_request(self) -> None:
        self.assertEqual(OrderRequest(code="000001", quantity=100, price="12.34").validate(), [])

    def test_invalid_order_request(self) -> None:
        issues = OrderRequest(code="1", quantity=10, price="-1").validate()
        self.assertIn("stock code must be a 6-digit numeric string", issues)
        self.assertIn("quantity must be a positive multiple of 100", issues)
        self.assertIn("price must be positive", issues)


class SnapshotDetectionTests(unittest.TestCase):
    def test_detect_from_snapshot(self) -> None:
        adapter = PingAnBrokerAdapter()
        controls = [
            ControlInfo(hwnd=1, class_name="Static", text="证券代码", parent_hwnd=100, rect=(10, 10, 60, 30), child_index=0),
            ControlInfo(hwnd=2, class_name="Edit", text="", parent_hwnd=100, rect=(70, 8, 160, 30), child_index=1),
            ControlInfo(hwnd=3, class_name="Static", text="委托价", parent_hwnd=100, rect=(10, 50, 60, 70), child_index=2),
            ControlInfo(hwnd=4, class_name="Edit", text="", parent_hwnd=100, rect=(70, 48, 160, 70), child_index=3),
            ControlInfo(hwnd=5, class_name="Static", text="数量", parent_hwnd=100, rect=(10, 90, 60, 110), child_index=4),
            ControlInfo(hwnd=6, class_name="Edit", text="", parent_hwnd=100, rect=(70, 88, 160, 110), child_index=5),
            ControlInfo(hwnd=7, class_name="Button", text="买入", parent_hwnd=100, rect=(200, 88, 260, 115), child_index=6),
        ]
        snapshot = {"main_hwnd": 999, "controls": [control.to_dict() for control in controls]}
        result = adapter.detect_from_snapshot(snapshot)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["detection"]["code_hwnd"], 2)
        self.assertEqual(result.data["detection"]["price_hwnd"], 4)
        self.assertEqual(result.data["detection"]["quantity_hwnd"], 6)
        self.assertEqual(result.data["detection"]["buy_button_hwnd"], 7)

    def test_detect_webview_snapshot_reports_embedded_browser(self) -> None:
        adapter = PingAnBrokerAdapter()
        snapshot_path = Path("/mnt/d/MyCode3/tdx/pingan-controls.json")
        if not snapshot_path.exists():
            self.skipTest("real exported snapshot not available in this environment")
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        payload = snapshot.get("data", snapshot)
        controls = payload.get("controls", [])
        if len(controls) > 10000:
            self.skipTest("real exported snapshot is too broad for deterministic embedded-browser detection")
        result = adapter.detect_from_snapshot(payload)
        self.assertFalse(result.ok)
        self.assertTrue(result.data["webview_summary"]["has_embedded_browser"])
        self.assertIn("embedded Chromium/WebView", result.message)

    def test_detect_from_snapshot_tolerates_none_control_text(self) -> None:
        adapter = PingAnBrokerAdapter()
        controls = [
            ControlInfo(hwnd=1, class_name="Static", text="证券代码", parent_hwnd=100, rect=(10, 10, 60, 30), child_index=0),
            ControlInfo(hwnd=2, class_name="Edit", text="", parent_hwnd=100, rect=(70, 8, 160, 30), child_index=1),
            ControlInfo(hwnd=3, class_name="Static", text=None, parent_hwnd=100, rect=(10, 50, 60, 70), child_index=2),  # type: ignore[arg-type]
            ControlInfo(hwnd=4, class_name="Edit", text="", parent_hwnd=100, rect=(70, 48, 160, 70), child_index=3),
            ControlInfo(hwnd=5, class_name="Static", text="数量", parent_hwnd=100, rect=(10, 90, 60, 110), child_index=4),
            ControlInfo(hwnd=6, class_name="Edit", text="", parent_hwnd=100, rect=(70, 88, 160, 110), child_index=5),
            ControlInfo(hwnd=7, class_name="Button", text="买入", parent_hwnd=100, rect=(200, 88, 260, 115), child_index=6),
        ]
        snapshot = {"main_hwnd": 999, "controls": [control.to_dict() for control in controls]}
        result = adapter.detect_from_snapshot(snapshot)
        self.assertTrue(result.ok)


class UIASnapshotAnalysisTests(unittest.TestCase):
    def test_analyze_uia_snapshot(self) -> None:
        snapshot = {
            "nodes": [
                {"path": "0", "name": "平安证券", "control_type": "Window", "automation_id": "", "class_name": "Chrome_WidgetWin_0", "rich_text": ""},
                {"path": "0/0", "name": "证券代码", "control_type": "Text", "automation_id": "codeLabel", "class_name": "TextBlock", "rich_text": ""},
                {"path": "0/1", "name": "", "control_type": "Edit", "automation_id": "codeInput", "class_name": "Chrome_RenderWidgetHostHWND", "rich_text": ""},
                {"path": "0/2", "name": "买入", "control_type": "Button", "automation_id": "buyButton", "class_name": "Button", "rich_text": ""},
            ]
        }
        result = analyze_uia_snapshot(snapshot)
        self.assertTrue(result.ok)
        self.assertEqual(result.data["summary"]["keyword_hit_count"], 3)
        self.assertEqual(result.data["summary"]["editable_candidate_count"], 1)
        self.assertEqual(result.data["summary"]["actionable_candidate_count"], 1)


class UIAClickValidationTests(unittest.TestCase):
    def test_click_uia_requires_selector(self) -> None:
        result = click_uia_element("平安证券")
        self.assertFalse(result.ok)
        self.assertIn(result.code.value, {"invalid_request", "unsupported_platform"})

    def test_uia_windows_unsupported_or_ok(self) -> None:
        result = inspect_uia_windows("平安证券")
        self.assertIn(result.code.value, {"ok", "unsupported_platform"})

    def test_click_uia_path_requires_path(self) -> None:
        result = click_uia_path("平安证券", path="")
        self.assertFalse(result.ok)
        self.assertIn(result.code.value, {"invalid_request", "unsupported_platform"})

    def test_click_uia_center_requires_selector(self) -> None:
        result = click_uia_center("平安证券")
        self.assertFalse(result.ok)
        self.assertIn(result.code.value, {"invalid_request", "unsupported_platform"})

    def test_activate_uia_requires_selector(self) -> None:
        result = activate_uia_element("平安证券")
        self.assertFalse(result.ok)
        self.assertIn(result.code.value, {"invalid_request", "unsupported_platform"})

    def test_activate_uia_rejects_invalid_strategy(self) -> None:
        result = activate_uia_element("平安证券", automation_id="2010", strategy="bad")
        self.assertFalse(result.ok)
        self.assertIn(result.code.value, {"invalid_request", "unsupported_platform"})

    def test_list_combobox_requires_selector(self) -> None:
        result = list_uia_combobox_items("平安证券")
        self.assertFalse(result.ok)
        self.assertIn(result.code.value, {"invalid_request", "unsupported_platform"})

    def test_read_uia_requires_selector(self) -> None:
        result = read_uia_element("平安证券")
        self.assertFalse(result.ok)
        self.assertIn(result.code.value, {"invalid_request", "unsupported_platform"})

    def test_set_uia_text_requires_selector(self) -> None:
        result = set_uia_text("平安证券", value="000001")
        self.assertFalse(result.ok)
        self.assertIn(result.code.value, {"invalid_request", "unsupported_platform"})

    def test_pingan_probe_unsupported_or_ok(self) -> None:
        result = run_pingan_probe("平安证券", code="000001", price="10.00", quantity=100)
        self.assertIn(result.code.value, {"ok", "unsupported_platform"})

    def test_pingan_hid_submit_probe_unsupported_or_ok(self) -> None:
        result = run_pingan_hid_submit_probe(
            "平安证券",
            port="COM3",
            baudrate=115200,
            timeout=2.0,
            code="000001",
            price="10.00",
            quantity=100,
        )
        self.assertIn(result.code.value, {"ok", "unsupported_platform"})

    def test_select_combobox_requires_selector(self) -> None:
        result = select_uia_combobox_item("平安证券", item_name="示例")
        self.assertFalse(result.ok)
        self.assertIn(result.code.value, {"invalid_request", "unsupported_platform"})


class UIAContractExtractionTests(unittest.TestCase):
    def test_extract_contract_no_prefers_merged_dialog_texts(self) -> None:
        contract_no = _extract_contract_no_from_texts(
            [
                "提示",
                "委托已提交，",
                "合同号：B202604250001",
            ]
        )
        self.assertEqual(contract_no, "B202604250001")

    def test_extract_contract_no_supports_he_tong_hao_shi_pattern(self) -> None:
        contract_no = _extract_contract_no_from_texts(
            [
                "委托已提交,合同号是0362577001",
            ]
        )
        self.assertEqual(contract_no, "0362577001")

    def test_extract_dialog_payload_captures_recursive_win32_texts(self) -> None:
        child_map = {
            100: [101],
            101: [102],
            102: [],
        }
        text_map = {
            101: "",
            102: "委托已提交，合同号：B202604250001",
        }
        class_map = {
            101: "Pane",
            102: "Static",
        }
        with (
            patch("tdxquant.uia_inspector.enumerate_child_windows", side_effect=lambda hwnd: child_map.get(hwnd, [])),
            patch("tdxquant.uia_inspector.get_text", side_effect=lambda hwnd: text_map.get(hwnd, "")),
            patch("tdxquant.uia_inspector.get_class_name", side_effect=lambda hwnd: class_map.get(hwnd, "")),
        ):
            payload = _extract_dialog_text_payload_from_sources(hwnd=100)
        self.assertEqual(payload["contract_no"], "B202604250001")
        self.assertEqual(payload["merged_texts"], ["委托已提交，合同号：B202604250001"])
        self.assertEqual(len(payload["win32_descendant_texts"]), 2)
        self.assertEqual(payload["win32_descendant_texts"][1]["text"], "委托已提交，合同号：B202604250001")

    def test_extract_dialog_payload_includes_uia_tree(self) -> None:
        class FakeInfo:
            def __init__(self, name: str, control_type: str, handle: int | None = None, class_name: str = "", rich_text: str = "", automation_id: str = "") -> None:
                self.name = name
                self.control_type = control_type
                self.handle = handle
                self.class_name = class_name
                self.rich_text = rich_text
                self.automation_id = automation_id
                self.rectangle = None

        class FakeElement:
            def __init__(self, info: FakeInfo, children: list["FakeElement"] | None = None) -> None:
                self.element_info = info
                self._children = children or []

            def window_text(self) -> str:
                return self.element_info.name

            def children(self) -> list["FakeElement"]:
                return self._children

            def descendants(self) -> list["FakeElement"]:
                items: list[FakeElement] = []
                for child in self._children:
                    items.append(child)
                    items.extend(child.descendants())
                return items

            def is_visible(self) -> bool:
                return True

            def is_enabled(self) -> bool:
                return True

        child = FakeElement(FakeInfo(name="委托已提交，合同号：B202604250001", control_type="Text", handle=2, class_name="Static"))
        root = FakeElement(FakeInfo(name="提示", control_type="Pane", handle=1, class_name="#32770"), [child])
        payload = _extract_dialog_text_payload_from_sources(hwnd=0, element=root)
        self.assertEqual(payload["contract_no"], "B202604250001")
        self.assertEqual(payload["uia_tree"]["root"]["name"], "提示")
        self.assertEqual(payload["uia_tree"]["nodes"][1]["name"], "委托已提交，合同号：B202604250001")


class PingAnOrderStateTests(unittest.TestCase):
    def test_write_pingan_last_order_state_persists_contract_no(self) -> None:
        result = Result(
            ok=True,
            code=ErrorCode.OK,
            message="completed pingan buy submit once",
            data={"input": {"code": "516820"}, "result_dialog": {"contract_no": "B202604250001"}},
        )
        with TemporaryDirectory() as tmp_dir:
            state_path = Path(tmp_dir) / "pingan-last-order.json"
            _write_pingan_last_order_state(result, state_path)
            payload = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["contract_no"], "B202604250001")

    def test_emit_pingan_contract_log_writes_stderr_line(self) -> None:
        stream = io.StringIO()
        _emit_pingan_contract_log("B202604250001", stream)
        self.assertIn("contract_no=B202604250001", stream.getvalue())


class PingAnProfileTests(unittest.TestCase):
    def test_resolve_pingan_buy_profile_balanced_defaults(self) -> None:
        profile = _resolve_pingan_buy_profile("balanced")
        self.assertEqual(profile["hid_pre_delay"], 0.2)
        self.assertEqual(profile["post_delay"], 0.2)
        self.assertEqual(profile["capture_final_uia"], False)
        self.assertEqual(profile["price_quantity_input_mode"], "uia")
        self.assertEqual(profile["dialog_lookup_mode"], "uia")

    def test_build_pingan_buy_submit_options_allows_overrides(self) -> None:
        options = _build_pingan_buy_submit_options(
            profile_name="fast",
            overrides={
                "post_delay": 0.6,
                "dialog_timeout": 1.1,
                "confirm_timeout": 2.2,
                "capture_final_uia": True,
            },
        )
        self.assertEqual(options["post_delay"], 0.6)
        self.assertEqual(options["dialog_timeout"], 1.1)
        self.assertEqual(options["confirm_timeout"], 2.2)
        self.assertEqual(options["capture_final_uia"], True)

    def test_build_pingan_buy_submit_options_accepts_price_quantity_input_mode_override(self) -> None:
        options = _build_pingan_buy_submit_options(
            profile_name="balanced",
            overrides={"price_quantity_input_mode": "hybrid_win32"},
        )
        self.assertEqual(options["price_quantity_input_mode"], "hybrid_win32")

    def test_build_pingan_buy_submit_options_accepts_dialog_lookup_mode_override(self) -> None:
        options = _build_pingan_buy_submit_options(
            profile_name="balanced",
            overrides={"dialog_lookup_mode": "win32_experimental"},
        )
        self.assertEqual(options["dialog_lookup_mode"], "win32_experimental")

    def test_resolve_pingan_buy_profile_turbo_defaults(self) -> None:
        profile = _resolve_pingan_buy_profile("turbo")
        self.assertEqual(profile["price_quantity_input_mode"], "hybrid_win32")
        self.assertEqual(profile["dialog_lookup_mode"], "win32_experimental")


if __name__ == "__main__":
    unittest.main()
