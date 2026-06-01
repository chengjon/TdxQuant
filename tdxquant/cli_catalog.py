from __future__ import annotations

import argparse
import copy
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from .models import ErrorCode, Result


def _add_catalog_run_arguments(subparser: argparse.ArgumentParser, *, include_side: bool = False) -> None:
    subparser.add_argument("--view", choices=["detailed", "summary"], default="detailed")
    subparser.add_argument("--from-step")
    subparser.add_argument("--to-step")
    subparser.add_argument("--only-step")
    subparser.add_argument("--profile")
    subparser.add_argument("--api-profile")
    subparser.add_argument("--trade-profile")
    subparser.add_argument("--strategy-path")
    subparser.add_argument("--port")
    subparser.add_argument("--baudrate", type=int)
    subparser.add_argument("--timeout", type=float)
    if include_side:
        subparser.add_argument("--side", choices=["buy", "sell"])
    subparser.add_argument("--block-code")
    subparser.add_argument("--code")
    subparser.add_argument("--price")
    subparser.add_argument("--quantity", type=int)
    subparser.add_argument("--max-depth", type=int)
    subparser.add_argument("--close-result-dialog", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--price-quantity-input-mode", choices=["uia", "win32", "hybrid_win32"])
    subparser.add_argument("--dialog-lookup-mode", choices=["uia", "win32_experimental"])
    subparser.add_argument("--capture-final-uia", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--hid-pre-delay", type=float)
    subparser.add_argument("--post-delay", type=float)
    subparser.add_argument("--dialog-timeout", type=float)
    subparser.add_argument("--confirm-timeout", type=float)
    subparser.add_argument("--confirm-post-delay", type=float)
    subparser.add_argument("--result-timeout", type=float)
    subparser.add_argument("--result-close-pre-delay", type=float)
    subparser.add_argument("--refresh-before-trade", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--refresh-market")
    subparser.add_argument("--refresh-force", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--market")
    subparser.add_argument("--force", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--max-snapshot-price", type=float)
    subparser.add_argument("--required-block-code")
    subparser.add_argument("--required-block-type", type=int)
    subparser.add_argument("--required-list-type", type=int)
    subparser.add_argument("--formula-name")
    subparser.add_argument("--formula-arg")
    subparser.add_argument("--formula-return-count", type=int)
    subparser.add_argument("--formula-return-date", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--formula-stock-period")
    subparser.add_argument("--formula-start-time")
    subparser.add_argument("--formula-end-time")
    subparser.add_argument("--formula-count", type=int)
    subparser.add_argument("--formula-dividend-type", type=int)
    subparser.add_argument("--limit", type=int)
    subparser.add_argument("--contract-no")
    subparser.add_argument("--date")
    subparser.add_argument("--timezone")
    subparser.add_argument("--recent-limit", type=int)
    subparser.add_argument("--start-date")
    subparser.add_argument("--end-date")
    subparser.add_argument("--trade-ok", action=argparse.BooleanOptionalAction, default=None)
    subparser.add_argument("--task-name")
    subparser.add_argument("--ledger-jsonl-path")
    subparser.add_argument("--ledger-csv-path")
    subparser.add_argument("--json-output-path")
    subparser.add_argument("--csv-output-path")
    subparser.add_argument("--output", help="Optional path to write the JSON result")


def build_catalog_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> argparse.ArgumentParser:
    catalog_parser = subparsers.add_parser("catalog")
    catalog_subparsers = catalog_parser.add_subparsers(dest="catalog_command", required=True)

    catalog_list_parser = catalog_subparsers.add_parser("list")
    catalog_list_parser.add_argument("--view", choices=["detailed", "summary"], default="detailed")
    catalog_list_parser.add_argument("--kind", choices=["entry", "bundle", "all"], default="entry")
    catalog_list_filter_group = catalog_list_parser.add_mutually_exclusive_group()
    catalog_list_filter_group.add_argument("--entry")
    catalog_list_filter_group.add_argument("--bundle")
    catalog_list_parser.add_argument("--label")
    catalog_list_parser.add_argument("--output", help="Optional path to write the JSON result")

    catalog_validate_parser = catalog_subparsers.add_parser("validate")
    catalog_validate_parser.add_argument("--view", choices=["detailed", "summary"], default="detailed")
    catalog_validate_parser.add_argument("--kind", choices=["entry", "bundle", "all"], default="all")
    catalog_validate_filter_group = catalog_validate_parser.add_mutually_exclusive_group()
    catalog_validate_filter_group.add_argument("--entry")
    catalog_validate_filter_group.add_argument("--bundle")
    catalog_validate_parser.add_argument("--label")
    catalog_validate_parser.add_argument("--output", help="Optional path to write the JSON result")

    catalog_run_parser = catalog_subparsers.add_parser("run")
    catalog_run_filter_group = catalog_run_parser.add_mutually_exclusive_group(required=True)
    catalog_run_filter_group.add_argument("--entry")
    catalog_run_filter_group.add_argument("--bundle")
    _add_catalog_run_arguments(catalog_run_parser)

    catalog_plan_parser = catalog_subparsers.add_parser("plan")
    catalog_plan_filter_group = catalog_plan_parser.add_mutually_exclusive_group(required=True)
    catalog_plan_filter_group.add_argument("--entry")
    catalog_plan_filter_group.add_argument("--bundle")
    _add_catalog_run_arguments(catalog_plan_parser, include_side=True)

    catalog_preview_parser = catalog_subparsers.add_parser("preview")
    catalog_preview_filter_group = catalog_preview_parser.add_mutually_exclusive_group(required=True)
    catalog_preview_filter_group.add_argument("--entry")
    catalog_preview_filter_group.add_argument("--bundle")
    _add_catalog_run_arguments(catalog_preview_parser, include_side=True)

    return catalog_parser


@dataclass(frozen=True)
class CatalogCommandBoundary:
    resolve_entry: Callable[[str], Mapping[str, Any]]
    list_entries: Callable[[argparse.Namespace], Result]
    validate_registry: Callable[[argparse.Namespace], Result]
    plan_entry: Callable[..., Result]
    plan_bundle: Callable[[argparse.Namespace], Result]
    run_entry: Callable[..., Result]
    run_bundle: Callable[[argparse.Namespace], Result]
    build_summary_view: Callable[[argparse.Namespace, Result], dict[str, object] | None]

    def handle(self, args: argparse.Namespace) -> Result:
        try:
            if args.catalog_command == "list":
                return self.list_entries(args)
            if args.catalog_command == "validate":
                return self.validate_registry(args)
            if args.catalog_command in {"plan", "preview"}:
                if getattr(args, "bundle", None):
                    return self.plan_bundle(args)
                resolved = self.resolve_entry(args.entry)
                return self.plan_entry(
                    args=args,
                    entry_name=args.entry,
                    source=str(resolved["source"]),
                    preset_name=str(resolved["preset"]),
                )
            if getattr(args, "bundle", None):
                result = self.run_bundle(args)
                result.data["summary_view"] = self.build_summary_view(args, result)
                return result
            resolved = self.resolve_entry(args.entry)
            result = self.run_entry(
                args=args,
                entry_name=args.entry,
                source=str(resolved["source"]),
                preset_name=str(resolved["preset"]),
            )
            result.data["summary_view"] = self.build_summary_view(args, result)
            return result
        except ValueError as exc:
            return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=str(exc))


def select_catalog_output_payload(args: argparse.Namespace, result: Result) -> dict[str, object]:
    if (
        args.command == "catalog"
        and getattr(args, "view", "detailed") == "summary"
        and isinstance(result.data.get("summary_view"), dict)
    ):
        return copy.deepcopy(result.data["summary_view"])
    return result.to_dict()
