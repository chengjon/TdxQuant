from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import sys
from typing import Any

from .api import TdxTaskManager
from .subscription_watch_background import (
    build_background_paths,
    read_active_payload,
    write_background_state,
    write_terminal_background_state,
)
from .subscription_watch_run import build_subscription_watch_run_paths


def _handle_sigterm(signum: int | None, frame: Any) -> None:
    del signum, frame
    raise KeyboardInterrupt()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tdxquant.subscription_watch_background_runner")
    parser.add_argument("--root-dir", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--code", action="append", dest="stock_list", required=True)
    parser.add_argument("--max-events", type=int, default=None)
    parser.add_argument("--max-seconds", type=float, default=None)
    parser.add_argument("--poll-interval", type=float, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    terminal_state = "failed"
    terminal_reason = "unexpected_exception"
    exit_code = 1
    paths = None
    run_paths = None
    run_id = None
    try:
        signal.signal(signal.SIGTERM, _handle_sigterm)
        args = _build_parser().parse_args(argv)
        root_dir = Path(args.root_dir)
        paths = build_background_paths(root_dir)
        run_id = args.run_id
        run_paths = build_subscription_watch_run_paths(paths.root_dir, run_id=run_id)
        write_background_state(
            paths,
            run_id=run_id,
            pid=os.getpid(),
            state="running",
            reason=None,
            runner_log_path=run_paths.runner_log_path,
        )
        manager = TdxTaskManager(
            profile="subscription_watch",
            profile_overrides={"run_root_dir": str(root_dir)},
        )
        result = manager.subscription_watch(
            stock_list=list(args.stock_list),
            max_events=args.max_events,
            max_seconds=args.max_seconds,
            poll_interval=args.poll_interval,
            run_id=args.run_id,
        )
        current_state = read_active_payload(paths) or {}
        terminal_state = "completed"
        terminal_reason = None
        if current_state.get("state") == "stopping":
            terminal_state = "stopped"
            terminal_reason = str(current_state.get("reason") or "operator_stop")
        elif not result.ok:
            terminal_state = "failed"
            terminal_reason = "task_failed"
        elif not isinstance(result.data, dict):
            raise TypeError("subscription_watch result must include a data mapping")
        elif result.data.get("summary", {}).get("interrupted") is True:
            terminal_state = "stopped"
            terminal_reason = str(result.data.get("summary", {}).get("stop_reason") or "keyboard_interrupt")
        print(
            json.dumps(
                {
                    "ok": result.ok,
                    "code": str(result.code),
                    "message": result.message,
                    "run_id": run_id,
                },
                ensure_ascii=False,
            )
        )
        exit_code = 0 if result.ok else 1
    except KeyboardInterrupt:
        terminal_state = "stopped"
        terminal_reason = "keyboard_interrupt"
        exit_code = 1
    except Exception:
        terminal_state = "failed"
        terminal_reason = "unexpected_exception"
        exit_code = 1
    finally:
        if paths is not None and run_id is not None:
            write_terminal_background_state(
                paths,
                run_id=run_id,
                state=terminal_state,
                reason=terminal_reason,
                runner_log_path=run_paths.runner_log_path if run_paths is not None else None,
            )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
