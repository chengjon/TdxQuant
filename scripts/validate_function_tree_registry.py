#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys


ALLOWED_STATUSES = {
    "`[已实现]`",
    "`[部分实现]`",
    "`[已设计/待实现]`",
    "`[非目标/边界]`",
}
STATUS_ORDER = [
    "`[已实现]`",
    "`[部分实现]`",
    "`[已设计/待实现]`",
    "`[非目标/边界]`",
]
PENDING_BOUNDARY_MARKERS = (
    "待实现",
    "未实现",
    "不可用",
    "不代表",
    "未覆盖",
    "不能",
    "不会",
    "不自动",
    "不直接",
)
FEATURE_ROW_RE = re.compile(r"^\|\s*(?P<node_id>[A-Z]-\d+)\s*\|")


@dataclass(frozen=True)
class FeatureRow:
    line_number: int
    node_id: str
    name: str
    status: str
    evidence: str
    boundary: str


def _split_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_feature_rows(text: str) -> tuple[list[FeatureRow], list[str]]:
    rows: list[FeatureRow] = []
    errors: list[str] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = FEATURE_ROW_RE.match(line)
        if not match:
            continue
        cells = _split_markdown_row(line)
        node_id = match.group("node_id")
        if len(cells) < 5:
            errors.append(f"line {line_number} {node_id}: expected at least 5 table cells")
            continue
        rows.append(
            FeatureRow(
                line_number=line_number,
                node_id=node_id,
                name=cells[1],
                status=cells[2],
                evidence=cells[3],
                boundary=cells[4],
            )
        )
    return rows, errors


def validate_registry(root: Path) -> tuple[list[FeatureRow], list[str]]:
    errors: list[str] = []
    function_tree_path = root / "FUNCTION_TREE.md"
    if not function_tree_path.exists():
        return [], [f"{function_tree_path}: missing FUNCTION_TREE.md"]
    if (root / "ROADMAP.md").exists():
        errors.append("ROADMAP.md: competing roadmap is not allowed; use FUNCTION_TREE.md as the single registry")

    rows, parse_errors = parse_feature_rows(function_tree_path.read_text(encoding="utf-8"))
    errors.extend(parse_errors)
    if not rows:
        errors.append("FUNCTION_TREE.md: no feature rows found")

    seen_ids: dict[str, int] = {}
    for row in rows:
        if row.node_id in seen_ids:
            errors.append(f"line {row.line_number} {row.node_id}: duplicate id first seen on line {seen_ids[row.node_id]}")
        else:
            seen_ids[row.node_id] = row.line_number

        if row.status not in ALLOWED_STATUSES:
            allowed = ", ".join(STATUS_ORDER)
            errors.append(f"line {row.line_number} {row.node_id}: unsupported status {row.status}; allowed: {allowed}")
        if not row.evidence:
            errors.append(f"line {row.line_number} {row.node_id}: evidence column is required")
        if not row.boundary:
            errors.append(f"line {row.line_number} {row.node_id}: boundary column is required")
        if row.status == "`[已设计/待实现]`" and not any(marker in row.boundary for marker in PENDING_BOUNDARY_MARKERS):
            errors.append(
                f"line {row.line_number} {row.node_id}: pending rows must explicitly signal pending or unavailable status"
            )

    return rows, errors


def _summary(rows: list[FeatureRow]) -> str:
    counts = {status: 0 for status in STATUS_ORDER}
    for row in rows:
        if row.status in counts:
            counts[row.status] += 1
    status_summary = "; ".join(f"{status.strip('`')}={counts[status]}" for status in STATUS_ORDER)
    return f"rows={len(rows)}; {status_summary}; problems=0"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate FUNCTION_TREE.md as the single feature registry.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root containing FUNCTION_TREE.md")
    args = parser.parse_args(argv)

    rows, errors = validate_registry(args.root.resolve())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(_summary(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
