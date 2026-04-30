from __future__ import annotations

import re
from typing import Any

from .desktop import uia as _desktop_uia
from .desktop.uia import *  # noqa: F401,F403


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
        try:
            uia_tree = _desktop_uia._serialize_uia_subtree(element, max_depth=4)
        except Exception:
            uia_tree = None
        for node in list(uia_tree.get("nodes", [])) if isinstance(uia_tree, dict) else []:
            _append_unique_text(uia_texts, seen_texts, node.get("name"))
            _append_unique_text(uia_texts, seen_texts, node.get("rich_text"))

    all_texts = merged_texts + [text for text in uia_texts if text not in merged_texts]
    contract_no = _extract_contract_no_from_texts(merged_texts + uia_texts)
    return {
        "hwnd": dialog_hwnd,
        "contract_no": contract_no,
        "child_texts": child_items,
        "win32_descendant_texts": descendant_items,
        "merged_texts": merged_texts,
        "uia_texts": uia_texts,
        "uia_tree": uia_tree,
        "all_texts": all_texts,
    }
