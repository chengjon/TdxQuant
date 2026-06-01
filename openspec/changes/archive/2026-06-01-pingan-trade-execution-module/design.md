## Context

The architecture review identified Candidate 2 as the next mainline step after shared lifecycle hardening. D-07/D-08 are already marked `[已实现]`, so this change is not a status promotion. It is a locality refactor around the real PingAn order execution path.

Today the public manager methods remain valuable, but the implementation body mixes several responsibilities:

- request identity and side/method naming
- idempotency and submission ledger checks
- max-price safety gates
- lifecycle owner and broker-readiness gates
- desktop adapter dispatch
- result finalization and audit metadata

The first slice should be small enough to verify behavior preservation. The tracer bullet is `buy_submit_once`, because it is a D-08 path with explicit submit-once identity and existing safety/audit/idempotency tests.

## Goals / Non-Goals

**Goals:**
- Introduce a small internal PingAn execution request object.
- Introduce one execution function that accepts the request, precomputed gate state, and a desktop dispatch callback.
- Delegate `TdxTradeManager.pingan.buy_submit_once(...)` through the new module without changing public output shape.
- Keep tests focused on behavior: method identity, dispatch parameters, rejected idempotency/safety/lifecycle gates, and audit finalization compatibility.
- Record FUNCTION_TREE evidence as architecture hardening, not a new feature claim.

**Non-Goals:**
- No new desktop UIA/Win32/HID primitive.
- No new CLI/task/catalog command.
- No change to real live trade safety defaults.
- No migration of every PingAn method in one slice.
- No lifecycle supervisor rewrite in this change.

## Decisions

- Keep `TdxTradeManager.pingan.*` as the public interface. Callers should not import or depend on the new internal module.
- Extract the execution seam into `tdxquant.trade.pingan_execution` instead of adding another class inside `manager.py`. This creates a direct test target and reduces pressure on the broad manager file.
- Make `buy_submit_once` the first delegated path. It gives D-08 coverage without mixing buy, sell, confirm-current, and lifecycle supervisor changes in one commit.
- Pass existing manager callbacks into the module rather than making the module own persistence or UIA imports directly. This keeps rollback straightforward and avoids duplicating artifact-writing logic.

## Risks / Trade-offs

- A too-small extraction can become a pass-through. Mitigation: the module owns normalized request identity and gate-to-dispatch decision flow, not only a function call wrapper.
- A too-large extraction could change trade behavior. Mitigation: one public method migrates first, with existing focused tests kept green.
- Execution terminology can overclaim capability. Mitigation: specs and FUNCTION_TREE boundary state that this is an internal seam and does not add a new desktop execution primitive or guarantee live broker readiness.
