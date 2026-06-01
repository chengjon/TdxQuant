from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from ..models import ErrorCode, Result


PINGAN_LIFECYCLE_SUPERVISOR_SCHEMA = "tdx.desktop_trade.pingan_lifecycle_supervisor.v1"


@dataclass(frozen=True)
class PingAnSupervisorOwnerGateDecision:
    supervisor_owned: bool
    owner_payload: dict[str, Any] | None
    owner_status: str
    owner_token_matches: bool
    owner_pid_alive: bool | None
    stale_detected: bool
    rejection_result: Result | None = None


@dataclass(frozen=True)
class PingAnSupervisorRestartDecision:
    status: str
    restart_attempt_count: int
    last_restart_at: datetime | None
    next_allowed_restart_at: datetime | None
    restart_executed: bool
    backoff_executed: bool
    process_restart_requested: bool


class PingAnLifecycleController:
    def evaluate_supervisor_owner_gate(
        self,
        *,
        owner_status_result: Result,
        statefile_path: Path,
        lock_path: Path,
        owner_token: str,
        stale_after_seconds: float,
        max_restart_attempts: int,
        backoff_seconds: float,
        process_restart_enabled: bool,
        process_restart_recheck_enabled: bool,
        process_restart_recheck_delay_seconds: float,
    ) -> PingAnSupervisorOwnerGateDecision:
        owner_payload = (
            owner_status_result.data.get("lifecycle_owner_lock")
            if isinstance(owner_status_result.data, dict)
            else None
        )
        owner_payload = owner_payload if isinstance(owner_payload, dict) else None
        owner_status = str(owner_payload.get("status") or "status_check_failed") if owner_payload else "status_check_failed"
        owner_token_matches = bool(owner_payload and owner_payload.get("current_owner_token") == owner_token)
        owner_pid_alive = owner_payload.get("owner_pid_alive") if owner_payload else None
        stale_detected = bool(owner_payload.get("stale_detected")) if owner_payload else False
        supervisor_owned = (
            owner_status_result.ok
            and owner_status == "owned"
            and owner_token_matches
            and not stale_detected
            and owner_pid_alive is True
        )
        if supervisor_owned:
            return PingAnSupervisorOwnerGateDecision(
                supervisor_owned=True,
                owner_payload=owner_payload,
                owner_status=owner_status,
                owner_token_matches=owner_token_matches,
                owner_pid_alive=owner_pid_alive,
                stale_detected=stale_detected,
            )

        if owner_status != "owned":
            status = "owner_lock_not_owned"
        elif not owner_token_matches:
            status = "owner_token_mismatch"
        elif stale_detected:
            status = "owner_lock_stale"
        else:
            status = "owner_pid_not_alive"

        payload = {
            "schema_version": PINGAN_LIFECYCLE_SUPERVISOR_SCHEMA,
            "action": "tick",
            "status": status,
            "execution_mode": "explicit_operator_lifecycle_supervisor_control",
            "statefile_path": str(statefile_path),
            "lock_path": str(lock_path),
            "owner_token": owner_token,
            "current_owner_token": owner_payload.get("current_owner_token") if owner_payload else None,
            "owner_lock_status": owner_payload,
            "owner_token_matches": owner_token_matches,
            "owner_pid_alive": owner_pid_alive,
            "owner_pid_status": owner_payload.get("owner_pid_status") if owner_payload else "missing",
            "stale_after_seconds": float(stale_after_seconds),
            "stale_detected": stale_detected,
            "supervisor_owned": False,
            "broker_health_ok": None,
            "control_dispatch_executed": False,
            "statefile_write_executed": False,
            "restart_executed": False,
            "backoff_executed": False,
            "process_restart_enabled": bool(process_restart_enabled),
            "process_restart_requested": False,
            "process_restart_executed": False,
            "process_restart_status": None,
            "process_restart_result": None,
            "process_restart_recheck_enabled": bool(process_restart_recheck_enabled),
            "process_restart_recheck_delay_seconds": max(0.0, float(process_restart_recheck_delay_seconds)),
            "process_restart_recheck_requested": False,
            "process_restart_recheck_executed": False,
            "post_restart_broker_health_ok": None,
            "post_restart_broker_health_code": None,
            "post_restart_broker_health_message": None,
            "lifecycle_recovery_status": "not_requested",
            "restart_attempt_count": 0,
            "max_restart_attempts": max_restart_attempts,
            "backoff_seconds": backoff_seconds,
            "last_restart_attempt_at": None,
            "next_allowed_restart_at": None,
            "order_submitted": False,
            "process_kill_executed": False,
            "pid_ownership_claimed": False,
            "side_effect_level": "none",
            "boundary": (
                "Explicit local PingAn lifecycle supervisor tick requires an owned lifecycle statefile; "
                "this rejected tick does not observe broker health, write lifecycle state, submit orders, "
                "execute workflows, kill/start processes, or claim real desktop PID ownership."
            ),
        }
        return PingAnSupervisorOwnerGateDecision(
            supervisor_owned=False,
            owner_payload=owner_payload,
            owner_status=owner_status,
            owner_token_matches=owner_token_matches,
            owner_pid_alive=owner_pid_alive,
            stale_detected=stale_detected,
            rejection_result=Result(
                ok=False,
                code=ErrorCode.INVALID_REQUEST,
                message="PingAn lifecycle supervisor requires an owned lifecycle owner lock",
                data={"lifecycle_supervisor": payload},
            ),
        )

    def decide_restart_policy(
        self,
        *,
        broker_health_ok: bool,
        restart_attempt_count: int,
        previous_last_restart_at: datetime | None,
        now: datetime,
        max_restart_attempts: int,
        backoff_seconds: float,
        process_restart_enabled: bool,
    ) -> PingAnSupervisorRestartDecision:
        last_restart_at = previous_last_restart_at
        next_allowed_restart_at: datetime | None = None
        restart_executed = False
        backoff_executed = False
        process_restart_requested = False

        if broker_health_ok:
            return PingAnSupervisorRestartDecision(
                status="healthy",
                restart_attempt_count=0,
                last_restart_at=None,
                next_allowed_restart_at=None,
                restart_executed=False,
                backoff_executed=False,
                process_restart_requested=False,
            )

        if previous_last_restart_at is not None and backoff_seconds > 0:
            next_allowed_restart_at = previous_last_restart_at + timedelta(seconds=backoff_seconds)
        inside_backoff = next_allowed_restart_at is not None and now < next_allowed_restart_at
        if inside_backoff:
            status = "backoff_waiting"
            backoff_executed = True
        elif restart_attempt_count >= max_restart_attempts:
            status = "max_restart_attempts_reached"
        else:
            status = "restart_recorded"
            restart_attempt_count += 1
            restart_executed = True
            last_restart_at = now
            process_restart_requested = bool(process_restart_enabled)
            if backoff_seconds > 0:
                next_allowed_restart_at = now + timedelta(seconds=backoff_seconds)

        return PingAnSupervisorRestartDecision(
            status=status,
            restart_attempt_count=restart_attempt_count,
            last_restart_at=last_restart_at,
            next_allowed_restart_at=next_allowed_restart_at,
            restart_executed=restart_executed,
            backoff_executed=backoff_executed,
            process_restart_requested=process_restart_requested,
        )
