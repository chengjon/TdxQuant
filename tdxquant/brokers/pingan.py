from __future__ import annotations

from dataclasses import asdict
from typing import Any

from ..inspector import enumerate_controls, find_main_window
from ..models import ControlInfo, DetectionResult, ErrorCode, OrderRequest, Result
from ..runtime import resolve_runtime
from ..win32_api import IS_WINDOWS, click, set_text
from .base import BrokerAdapter


def _normalize(text: str | None) -> str:
    return str(text or "").strip().replace(" ", "")


def _rect_left(control: ControlInfo) -> int:
    return control.rect[0] if control.rect else 10**9


def _rect_top(control: ControlInfo) -> int:
    return control.rect[1] if control.rect else 10**9


class PingAnBrokerAdapter(BrokerAdapter):
    def __init__(self, title_keyword: str = "平安证券", exe_path: str | None = None) -> None:
        self.title_keyword = title_keyword
        self.exe_path = exe_path

    def health_check(self) -> Result:
        runtime = resolve_runtime(self.exe_path)
        data = {"runtime": runtime.to_dict()}
        if not runtime.ok:
            return Result(
                ok=False,
                code=runtime.code,
                message="runtime discovery failed",
                data=data,
                next_action=runtime.next_action,
            )
        window = find_main_window(self.title_keyword)
        data["window"] = window.to_dict()
        if not window.ok:
            message = "runtime path resolved but Win32 inspection is unavailable on this platform"
            if window.code != ErrorCode.UNSUPPORTED_PLATFORM:
                message = "runtime path resolved but trading window was not found"
            return Result(
                ok=False,
                code=window.code,
                message=message,
                data=data,
                next_action=window.next_action,
            )
        data["path_mapping"] = {
            "windows_path": runtime.data.get("windows_path"),
            "wsl_path": runtime.data.get("wsl_path"),
        }
        return Result(ok=True, code=ErrorCode.OK, message="health-check passed", data=data)

    def inspect(self) -> Result:
        window = find_main_window(self.title_keyword)
        if not window.ok:
            return window
        return enumerate_controls(int(window.data["main_hwnd"]))

    def detect(self) -> Result:
        inspection = self.inspect()
        if not inspection.ok:
            return inspection
        return self.detect_from_snapshot(inspection.data)

    def detect_from_snapshot(self, snapshot: dict[str, Any]) -> Result:
        controls = [ControlInfo(**item) for item in snapshot["controls"]]
        webview_summary = self._summarize_webview_controls(controls)
        if webview_summary["has_embedded_browser"] and len(controls) > 5000:
            return Result(
                ok=False,
                code=ErrorCode.CONTROL_NOT_FOUND,
                message="trade page appears to be rendered inside an embedded Chromium/WebView surface",
                data={
                    "detection": DetectionResult().to_dict(),
                    "main_hwnd": snapshot.get("main_hwnd"),
                    "webview_summary": webview_summary,
                },
                warnings=[
                    "Skipped native control matching because the exported snapshot is dominated by WebView/browser controls.",
                    "Current Win32 message automation relies on native Edit/Button controls and cannot address HTML inputs inside this WebView.",
                ],
                next_action=(
                    "Switch to a classic native trade page if available, or move to a browser/UIA/CDP-style automation approach for this client version."
                ),
            )
        if len(controls) > 10000:
            return Result(
                ok=False,
                code=ErrorCode.CONTROL_NOT_FOUND,
                message="snapshot is too large for native buy-control matching",
                data={
                    "detection": DetectionResult().to_dict(),
                    "main_hwnd": snapshot.get("main_hwnd"),
                    "webview_summary": webview_summary,
                    "control_count": len(controls),
                },
                warnings=[
                    "Skipped native control matching because the exported snapshot contains too many controls for a targeted buy-page probe.",
                ],
                next_action="Capture a narrower snapshot around the trade panel, or use a dedicated buy-page detect/export command.",
            )
        detection = self._match_buy_controls(controls)
        data = {
            "detection": detection.to_dict(),
            "main_hwnd": snapshot.get("main_hwnd"),
            "webview_summary": webview_summary,
        }
        if detection.code_hwnd and detection.quantity_hwnd and detection.buy_button_hwnd:
            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="detected Ping An buy-page controls",
                data=data,
                warnings=["Verify the matched handles against your real client version before sending a live click."],
            )
        if webview_summary["has_embedded_browser"]:
            return Result(
                ok=False,
                code=ErrorCode.CONTROL_NOT_FOUND,
                message="trade page appears to be rendered inside an embedded Chromium/WebView surface",
                data=data,
                warnings=[
                    "Current Win32 message automation relies on native Edit/Button controls and cannot address HTML inputs inside this WebView.",
                ],
                next_action=(
                    "Switch to a classic native trade page if available, or move to a browser/UIA/CDP-style automation approach for this client version."
                ),
            )
        return Result(
            ok=False,
            code=ErrorCode.CONTROL_NOT_FOUND,
            message="could not detect all required buy-page controls",
            data=data,
            next_action="Refine the control matching rules against the exported inspect snapshot.",
        )

    def buy(self, order: OrderRequest) -> Result:
        issues = order.validate()
        if issues:
            return Result(
                ok=False,
                code=ErrorCode.INVALID_REQUEST,
                message="buy request validation failed",
                data={"issues": issues},
                next_action="Fix the request payload and retry.",
            )
        detection = self.detect()
        if not detection.ok:
            return detection
        info = detection.data["detection"]
        actions: list[dict[str, object]] = []
        if not IS_WINDOWS:
            return Result(
                ok=False,
                code=ErrorCode.UNSUPPORTED_PLATFORM,
                message="buy execution requires native Windows Python",
                data={"detection": info},
                next_action="Run the same command from Windows Python after validating controls with inspect.",
            )
        set_text(int(info["code_hwnd"]), order.code)
        actions.append({"action": "set_text", "target": "code", "hwnd": info["code_hwnd"], "value": order.code})
        if info.get("price_hwnd") and order.price is not None:
            set_text(int(info["price_hwnd"]), order.price)
            actions.append({"action": "set_text", "target": "price", "hwnd": info["price_hwnd"], "value": order.price})
        set_text(int(info["quantity_hwnd"]), str(order.quantity))
        actions.append(
            {"action": "set_text", "target": "quantity", "hwnd": info["quantity_hwnd"], "value": str(order.quantity)}
        )
        if not order.dry_run:
            click(int(info["buy_button_hwnd"]))
            actions.append({"action": "click", "target": "buy_button", "hwnd": info["buy_button_hwnd"]})
        return Result(
            ok=True,
            code=ErrorCode.OK,
            message="buy flow executed" if not order.dry_run else "buy dry-run filled controls without clicking",
            data={"detection": info, "actions": actions, "dry_run": order.dry_run},
            warnings=["Post-click confirmation dialogs are not yet handled in this change."],
        )

    def _match_buy_controls(self, controls: list[ControlInfo]) -> DetectionResult:
        result = DetectionResult(evidence={"candidates": [], "scores": {}})
        edits = [control for control in controls if control.class_name.upper() == "EDIT"]
        buttons = [control for control in controls if control.class_name.upper() == "BUTTON"]
        labels = [control for control in controls if control.class_name.upper() in {"STATIC", "BUTTON"}]
        parent_map: dict[int | None, list[ControlInfo]] = {}
        labels_by_parent: dict[int | None, list[ControlInfo]] = {}
        for control in controls:
            parent_map.setdefault(control.parent_hwnd, []).append(control)
            if control.class_name.upper() in {"STATIC", "BUTTON"}:
                labels_by_parent.setdefault(control.parent_hwnd, []).append(control)
            result.evidence["candidates"].append(
                {
                    "hwnd": control.hwnd,
                    "class_name": control.class_name,
                    "text": control.text,
                    "parent_hwnd": control.parent_hwnd,
                    "child_index": control.child_index,
                }
            )

        code_candidate = self._pick_edit_candidate(
            edits, labels_by_parent, parent_map, primary_tokens=("代码", "证券代码"), secondary_tokens=("代码", "证券")
        )
        price_candidate = self._pick_edit_candidate(
            edits, labels_by_parent, parent_map, primary_tokens=("价格", "委托价"), secondary_tokens=("价格", "委托")
        )
        quantity_candidate = self._pick_edit_candidate(
            edits, labels_by_parent, parent_map, primary_tokens=("数量", "股数"), secondary_tokens=("数量", "股")
        )
        buy_candidate = self._pick_button_candidate(buttons)

        if code_candidate:
            result.code_hwnd = code_candidate["control"].hwnd
            result.evidence["code"] = code_candidate["evidence"]
            result.evidence["scores"]["code"] = code_candidate["score"]
        if price_candidate:
            result.price_hwnd = price_candidate["control"].hwnd
            result.evidence["price"] = price_candidate["evidence"]
            result.evidence["scores"]["price"] = price_candidate["score"]
        if quantity_candidate:
            result.quantity_hwnd = quantity_candidate["control"].hwnd
            result.evidence["quantity"] = quantity_candidate["evidence"]
            result.evidence["scores"]["quantity"] = quantity_candidate["score"]
        if buy_candidate:
            result.buy_button_hwnd = buy_candidate["control"].hwnd
            result.evidence["buy_button"] = buy_candidate["evidence"]
            result.evidence["scores"]["buy_button"] = buy_candidate["score"]

        if edits and result.code_hwnd is None:
            sorted_edits = sorted(edits, key=lambda item: (_rect_top(item), _rect_left(item), item.child_index or 0))
            result.code_hwnd = sorted_edits[0].hwnd
            result.evidence["code_fallback"] = {
                "reason": "first_edit_by_position",
                "control": asdict(sorted_edits[0]),
            }
        if len(edits) >= 2 and result.quantity_hwnd is None:
            sorted_edits = sorted(edits, key=lambda item: (_rect_top(item), _rect_left(item), item.child_index or 0))
            result.quantity_hwnd = sorted_edits[-1].hwnd
            result.evidence["quantity_fallback"] = {
                "reason": "last_edit_by_position",
                "control": asdict(sorted_edits[-1]),
            }
        return result

    def _pick_edit_candidate(
        self,
        edits: list[ControlInfo],
        labels_by_parent: dict[int | None, list[ControlInfo]],
        parent_map: dict[int | None, list[ControlInfo]],
        primary_tokens: tuple[str, ...],
        secondary_tokens: tuple[str, ...],
    ) -> dict[str, Any] | None:
        scored: list[dict[str, Any]] = []
        for control in edits:
            score = 0
            reasons: list[str] = []
            control_text = _normalize(control.text)
            if any(token in control_text for token in primary_tokens):
                score += 100
                reasons.append("self_text_primary_match")
            elif any(token in control_text for token in secondary_tokens):
                score += 60
                reasons.append("self_text_secondary_match")

            siblings = parent_map.get(control.parent_hwnd, [])
            for sibling in siblings:
                if sibling.hwnd == control.hwnd:
                    continue
                sibling_text = _normalize(sibling.text)
                if not sibling_text:
                    continue
                if any(token in sibling_text for token in primary_tokens):
                    distance = abs((sibling.child_index or 0) - (control.child_index or 0))
                    if distance <= 2:
                        score += 80 - distance * 10
                        reasons.append(f"sibling_label_primary_match:{sibling.hwnd}")
                elif any(token in sibling_text for token in secondary_tokens):
                    distance = abs((sibling.child_index or 0) - (control.child_index or 0))
                    if distance <= 2:
                        score += 40 - distance * 5
                        reasons.append(f"sibling_label_secondary_match:{sibling.hwnd}")

            for label in labels_by_parent.get(control.parent_hwnd, []):
                label_text = _normalize(label.text)
                if not label_text:
                    continue
                if any(token in label_text for token in primary_tokens):
                    if label.rect and control.rect:
                        vertical_delta = abs(label.rect[1] - control.rect[1])
                        horizontal_delta = control.rect[0] - label.rect[0]
                        if vertical_delta <= 40 and 0 <= horizontal_delta <= 300:
                            score += 70
                            reasons.append(f"aligned_label_primary_match:{label.hwnd}")
                elif any(token in label_text for token in secondary_tokens):
                    if label.rect and control.rect:
                        vertical_delta = abs(label.rect[1] - control.rect[1])
                        horizontal_delta = control.rect[0] - label.rect[0]
                        if vertical_delta <= 40 and 0 <= horizontal_delta <= 300:
                            score += 35
                            reasons.append(f"aligned_label_secondary_match:{label.hwnd}")

            if score:
                scored.append(
                    {
                        "control": control,
                        "score": score,
                        "evidence": {"control": asdict(control), "reasons": reasons},
                    }
                )
        if not scored:
            return None
        scored.sort(key=lambda item: (-item["score"], _rect_top(item["control"]), _rect_left(item["control"])))
        return scored[0]

    def _pick_button_candidate(self, buttons: list[ControlInfo]) -> dict[str, Any] | None:
        scored: list[dict[str, Any]] = []
        for control in buttons:
            normalized = _normalize(control.text)
            score = 0
            reasons: list[str] = []
            if "买入" in normalized:
                score += 100
                reasons.append("button_contains_buy")
            if "下单" in normalized:
                score -= 20
                reasons.append("button_contains_submit")
            if score:
                scored.append(
                    {
                        "control": control,
                        "score": score,
                        "evidence": {"control": asdict(control), "reasons": reasons},
                    }
                )
        if not scored:
            return None
        scored.sort(key=lambda item: (-item["score"], _rect_top(item["control"]), _rect_left(item["control"])))
        return scored[0]

    def _summarize_webview_controls(self, controls: list[ControlInfo]) -> dict[str, Any]:
        browser_classes = {
            "CefBrowserWindow",
            "Chrome_WidgetWin_0",
            "Chrome_RenderWidgetHostHWND",
        }
        matches = [asdict(control) for control in controls if control.class_name in browser_classes or "SubWebView" in str(control.text or "")]
        return {
            "has_embedded_browser": bool(matches),
            "browser_controls": matches[:10],
            "browser_control_count": len(matches),
        }
