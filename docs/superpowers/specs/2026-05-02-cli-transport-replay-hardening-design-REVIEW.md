---
status: reviewed
files_reviewed: 1
critical: 1
warning: 6
info: 2
total: 9
reviewer: claude-opus-4-7
date: 2026-05-02
---

# Review: CLI Transport Replay Hardening Design

Reviewed: `docs/superpowers/specs/2026-05-02-cli-transport-replay-hardening-design.md`

Cross-referenced against:
- `tdxquant/cli.py` (replay dispatch, argument registration)
- `tdxquant/replay_provider.py` (fixture resolution, materialization)
- `tdxquant/api/task.py` (subscription-watch replay path)
- `openspec/specs/tdx-provider-replay-mode/spec.md`
- `openspec/specs/tdx-provider-replay-fixtures/spec.md`
- `openspec/specs/tdx-api-cli-entry/spec.md`
- `openspec/specs/tdx-task-subscription-watch/spec.md`
- `openspec/specs/tdx-provider-result-contract/spec.md`

---

### CRITICAL-1: Nested `api` subcommand support matrix is incomplete

**Section:** Supported Command Matrix

The design mentions `tdxquant api ... --provider-mode replay` as a group but never enumerates **which nested `api` subcommands** are in scope. The code shows `_add_api_common_arguments` (cli.py:147-151) adds `--provider-mode`/`--fixture`/`--fixture-path` to **all** nested `api` commands indiscriminately -- including commands that have no replay fixture backing (e.g., `api divid-factors`, `api ipo-info`, `api financial-data`, `api stock-transaction-data`, etc.).

Without an explicit nested `api` support matrix, there's no contract for which subcommands must succeed vs. fail in replay mode, and no way to write the "unsupported replay capability" test cases the design calls for.

**Fix:** Add a nested `api` subcommand support matrix parallel to the flat command matrix. At minimum list `api capabilities`, `api health`, `api doctor`, `api formula-screen`, `api send-user-block` as supported and specify that all others must fail.

---

### WARNING-1: Fixture "priority" rule is misleading -- it's a mutual exclusion selection

**Section:** Replay Argument Policy, rule 4

The design states fixture selection priority as:
1. `--fixture-path`
2. `--fixture`
3. default built-in

But `--fixture` and `--fixture-path` are already enforced as mutually exclusive via `argparse.add_mutually_exclusive_group()` (cli.py:169-171). They can never coexist at CLI invocation time. The word "priority" implies a fallthrough chain, but it's actually a 3-way selection: if path given use it, else if name given use it, else use default.

**Fix:** Rewrite rule 4 as a selection algorithm, not a priority chain. Clarify that argparse-level mutual exclusion is the first guard, and the remaining selection is `--fixture-path` -> `--fixture` -> default.

---

### WARNING-2: `replay_fixture_map` programmatic API not addressed

**Section:** Implementation Surface

`TdxApiManager` accepts a `replay_fixture_map: dict` parameter (replay_provider.py:100-106) that allows programmatic per-capability fixture selection. This is already used by internal callers. The design doesn't mention it at all, which creates ambiguity about whether the CLI policy layer should intercept it or pass it through.

**Fix:** Add a Non-Goal or explicit scoping note acknowledging `replay_fixture_map` as a programmatic API that's out of scope for CLI transport hardening, but whose resolution logic must not be broken.

---

### WARNING-3: Design doesn't acknowledge the existing centralized replay dispatch

**Section:** Recommended Approach + Implementation Surface

The design recommends "Option B: Centralized CLI replay policy layer" as if it's new. But `_run_flat_replay_provider_command` (cli.py:2627-2672) **already is** a centralized replay dispatch for flat commands. It checks `provider_mode == "replay"`, creates a replay manager, and dispatches to the correct capability -- returning `unsupported replay flat command` for anything not in scope.

The design should acknowledge this existing layer and describe precisely what's being hardened vs. what's being added. Without this, the risk is duplication: a second policy layer layered on top of the first.

**Fix:** Add a "Current State" subsection documenting `_run_flat_replay_provider_command` and `_add_replay_provider_arguments` as the existing centralized replay dispatch, then describe what gaps this design fills.

---

### WARNING-4: Subscription watch artifact contract omits existing fields

**Section:** Subscription Watch Replay Artifact Contract

The design lists these required return fields:
- `run_id`, `run_dir`, `manifest_path`, `status_path`, `summary_path`, `events_jsonl_path`

But the actual implementation (task.py:1299-1309) also returns:
- `events_csv_path`, `jsonl_output_path`, `csv_output_path`, `status_output_path`

Omitting these means the contract test won't validate fields that callers already depend on.

**Fix:** Include `events_csv_path` in the required artifact path list. Note that `jsonl_output_path`/`csv_output_path`/`status_output_path` are legacy compatibility aliases that resolve to the canonical paths when no `--output` override is given.

---

### WARNING-5: `--output` flag interaction with replay transport contract is unspecified

**Section:** Subprocess Transport Contract + Replay Argument Policy

The `_add_api_common_arguments` (cli.py:151) adds `--output` to write JSON to a file. The design prescribes that `stdout` must only contain the machine-readable JSON envelope, but doesn't address whether `--output` is supported in replay mode, whether it redirects stdout away, or whether it's excluded from the transport contract.

**Fix:** Add a rule: either (a) `--output` is supported in replay mode and writes the same JSON that would go to stdout, or (b) `--output` is excluded from replay transport support and must fail if combined with `--provider-mode replay`.

---

### WARNING-6: No-live-fallback test strategy lacks verification method

**Section:** Testing Strategy, section 5

The design says these cases "must stably fail, and prove they will not access live runtime." But it doesn't specify **how to prove** no live runtime access occurs. In the current code, replay execution is purely in-process -- there's no network call, no subprocess spawn. The "proof" is architectural (replay_provider.py never imports live bridge code).

**Fix:** Specify that no-live-fallback verification is done via (a) confirming replay execution path never imports or calls live runtime modules, (b) running replay tests on a machine with no Windows runtime and confirming success, or (c) mocking the live bridge and asserting it's never called.

---

### INFO-1: Failure normalization should specify JSON envelope shape

**Section:** Replay Failure Normalization

The design says "stdout still outputs stable failure JSON" but doesn't specify the envelope shape. Looking at the code, `execute_sync_replay` (replay_provider.py:254-265) returns a `Result` with `ok=False, code=ErrorCode.INVALID_REQUEST, message=..., data={"replay_source": {...}}`. But the `_run_flat_replay_provider_command` catch at line 2638-2639 returns a different shape: `Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=str(exc))` without the `replay_source` data.

**Fix:** Unify the failure Result shape in the design: always include `replay_source` metadata in failure results, matching the `execute_sync_replay` convention.

---

### INFO-2: Risks section misses the `api` command coverage gap

**Section:** Risks

The current risks focus on CLI file size, JSON output inconsistencies, and fixture path leakage. The most impactful unmentioned risk is: the nested `api` commands all accept replay arguments via `_add_api_common_arguments`, but most have no replay fixture backing. If the support matrix isn't explicitly defined (see CRITICAL-1), callers will discover this gap only at runtime.

**Fix:** Add a risk: "Nested `api` commands all accept `--provider-mode replay` arguments, but most subcommands have no replay fixture. Without an explicit support matrix, the failure mode for unsupported capabilities will be discovered only at invocation time."

---

## Summary

The design is well-structured and correctly identifies the core goal (CLI subprocess replay as a stable transport contract). The main gap is **grounding in existing code**: a centralized replay dispatch already exists, the argument policy is partially enforced, and the subscription-watch materialization is already implemented. The design should be revised to:

1. Document current state before prescribing changes (WARNING-3)
2. Define the complete support matrix for both flat and nested commands (CRITICAL-1)
3. Align the artifact contract with actual return fields (WARNING-4)
4. Resolve the `--output` interaction (WARNING-5)
