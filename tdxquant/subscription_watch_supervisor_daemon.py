from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time

from .subscription_watch_background import SubscriptionWatchBackgroundController


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run an explicit subscription-watch supervisor daemon loop.")
    parser.add_argument("--root-dir", required=True)
    parser.add_argument("--max-ticks", type=int, required=True)
    parser.add_argument("--interval-seconds", type=float, default=0.0)
    parser.add_argument("--loop-sleep-seconds", type=float, default=30.0)
    parser.add_argument("--reason", default="supervisor_daemon")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    loop_sleep_seconds = max(float(args.loop_sleep_seconds), 0.0)
    controller = SubscriptionWatchBackgroundController(
        root_dir=Path(args.root_dir),
        python_executable=sys.executable,
    )
    while True:
        controller.supervisor_run(
            max_ticks=args.max_ticks,
            interval_seconds=args.interval_seconds,
            reason=args.reason,
        )
        time.sleep(loop_sleep_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
