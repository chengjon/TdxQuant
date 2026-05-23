#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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
OPENSPEC_EVIDENCE_RE = re.compile(
    r"OpenSpec(?:\s+覆盖)?\s+(?P<references>`[^`]+`(?:\s*(?:/|、|,|，|至|和)\s*`[^`]+`)*)"
)
BACKTICK_VALUE_RE = re.compile(r"`([^`]+)`")
LOCAL_EVIDENCE_PATH_PREFIXES = (
    "docs/",
    "openspec/changes/archive/",
    "openspec/specs/",
    "runtime/",
    "scripts/",
    "tdxquant/",
    "tests/",
)
AMBIGUOUS_PATH_VALUE_RE = re.compile(r"[\s*?\[\]{}$]")
FILE_SEGMENT_BEFORE_END_RE = re.compile(r"\.[^/]+/")


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


def _extract_openspec_change_ids(evidence: str) -> list[str]:
    match = OPENSPEC_EVIDENCE_RE.search(evidence)
    if not match:
        return []
    return [value.strip() for value in BACKTICK_VALUE_RE.findall(match.group("references")) if value.strip()]


def _openspec_change_exists(root: Path, change_id: str) -> bool:
    active_marker = root / "openspec" / "changes" / change_id / ".openspec.yaml"
    if active_marker.exists():
        return True
    archive_root = root / "openspec" / "changes" / "archive"
    if not archive_root.exists():
        return False
    for archived_change in archive_root.iterdir():
        if not archived_change.is_dir():
            continue
        if archived_change.name == change_id or archived_change.name.endswith(f"-{change_id}"):
            return True
    return False


def _is_literal_local_evidence_path(value: str) -> bool:
    if not value or "\\" in value or "://" in value:
        return False
    if AMBIGUOUS_PATH_VALUE_RE.search(value):
        return False
    if FILE_SEGMENT_BEFORE_END_RE.search(value):
        return False
    if not any(value.startswith(prefix) for prefix in LOCAL_EVIDENCE_PATH_PREFIXES):
        return False
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts


def _extract_local_evidence_paths(evidence: str) -> list[str]:
    paths: list[str] = []
    seen: set[str] = set()
    for value in (match.strip() for match in BACKTICK_VALUE_RE.findall(evidence)):
        if value in seen or not _is_literal_local_evidence_path(value):
            continue
        seen.add(value)
        paths.append(value)
    return paths


def _local_evidence_path_exists(root: Path, relative_path: str) -> bool:
    root = root.resolve()
    evidence_path = (root / relative_path).resolve()
    try:
        evidence_path.relative_to(root)
    except ValueError:
        return False
    return evidence_path.exists()


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
        for change_id in _extract_openspec_change_ids(row.evidence):
            if not _openspec_change_exists(root, change_id):
                errors.append(f"line {row.line_number} {row.node_id}: missing OpenSpec evidence {change_id}")
        for evidence_path in _extract_local_evidence_paths(row.evidence):
            if not _local_evidence_path_exists(root, evidence_path):
                errors.append(f"line {row.line_number} {row.node_id}: missing local evidence path {evidence_path}")

    return rows, errors


def _status_counts(rows: list[FeatureRow]) -> dict[str, int]:
    counts = {status.strip("`"): 0 for status in STATUS_ORDER}
    for row in rows:
        status = row.status.strip("`")
        if status in counts:
            counts[status] += 1
    return counts


def _summary(rows: list[FeatureRow]) -> str:
    counts = _status_counts(rows)
    status_summary = "; ".join(f"{status.strip('`')}={counts[status.strip('`')]}" for status in STATUS_ORDER)
    return f"rows={len(rows)}; {status_summary}; problems=0"


def _json_report(rows: list[FeatureRow], errors: list[str]) -> dict[str, object]:
    return {
        "valid": not errors,
        "row_count": len(rows),
        "status_counts": _status_counts(rows),
        "problem_count": len(errors),
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate FUNCTION_TREE.md as the single feature registry.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root containing FUNCTION_TREE.md")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Print a machine-readable JSON report")
    args = parser.parse_args(argv)

    rows, errors = validate_registry(args.root.resolve())
    if args.json_output:
        print(json.dumps(_json_report(rows, errors), ensure_ascii=False, sort_keys=True))
        return 1 if errors else 0
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(_summary(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
