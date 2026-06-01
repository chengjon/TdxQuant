# Architecture Deepening Opportunities

Date: 2026-06-01

Scope: TdxQuant codebase architecture review using the Matt Pocock `improve-codebase-architecture` vocabulary. This is an evaluation artifact only. It does not change `FUNCTION_TREE.md` status, OpenSpec state, or runtime behavior.

## Inputs

- `CONTEXT.md`: project language, architecture rules, and current pressure points.
- `docs/adr/0001-function-tree-single-feature-registry.md`: `FUNCTION_TREE.md` remains the single feature registry and status source.
- Current source tree metrics:
  - `tdxquant/cli.py`: 9,156 lines, 181 definitions.
  - `tdxquant/api/task.py`: 6,139 lines, 162 definitions.
  - `tdxquant/trade/manager.py`: 4,333 lines, 83 definitions.
  - `tdxquant/desktop/uia.py`: 3,287 lines, 91 definitions.
  - `tdxquant/provider_transport_replay.py`: 2,821 lines, 67 definitions.
  - `tdxquant/subscription_watch_background.py`: 2,768 lines, 102 definitions.
  - `tdxquant/provider_discovery.py`: 862 lines, with `_capability` spanning most of the file.

## Current Shape

The codebase has strong product governance: OpenSpec, archived evidence, tests, and `FUNCTION_TREE.md` prevent feature-state drift. The main architecture cost is not missing features. It is reduced locality in a few broad modules whose interfaces require maintainers to know too much of the implementation.

The highest-leverage deepening work should preserve existing CLI and manager interfaces while moving implementation knowledge behind narrower internal seams.

## Candidate 1: Catalog Command Runtime Module

**Files**

- `tdxquant/cli.py`: `build_parser`, `_build_catalog_summary_view`, `_validate_catalog_registry`, catalog plan/preview handling.
- `tdxquant/cli_catalog.py`
- `tdxquant/catalog.py`
- `tests/test_api_cli.py`

**Problem**

The command catalog has a good domain interface conceptually: list, validate, plan, preview, and run are read-oriented entry points around command entries and bundles. In implementation, much of the catalog parser, registry validation, summary projection, and trade-plan summary behavior lives in `tdxquant/cli.py`.

That makes `tdxquant/cli.py` a shallow module for catalog behavior: tests and changes must cross a very wide CLI interface even when the behavior is catalog-specific. The deletion test says deleting the catalog portion from `cli.py` would not remove complexity; it would reappear in every catalog command path unless concentrated elsewhere.

**Solution**

Create a deeper catalog command runtime module behind the CLI seam. Keep command syntax compatible, but move catalog registry validation, plan/preview summary projection, and selected output payload logic behind a small interface such as "build catalog command result from parsed arguments and loaded registry".

`tdxquant/cli.py` should stay an adapter: parse arguments, call the catalog runtime module, print the selected payload.

**Benefits**

- Locality: E-11 changes land in one module instead of spread across parser, handler, and summary functions.
- Leverage: direct tests can exercise catalog validation and summary projections without routing through the full CLI parser.
- Risk reduction: future catalog additions become less likely to accidentally imply execution semantics.

## Candidate 2: PingAn Trade Execution Module

**Files**

- `tdxquant/trade/manager.py`
- `tdxquant/desktop/uia.py`
- `tdxquant/trader/adapters/pingan_desktop.py`
- `tdxquant/brokers/pingan.py`
- `tests/test_trade_manager.py`
- `tests/test_pingan_trader_gateway.py`

**Problem**

PingAn desktop trading now has implemented feature status for D-07 and D-08, but the implementation knowledge is spread across the manager proxy, desktop UIA functions, broker adapter, trader gateway, audit helpers, readiness gates, lifecycle owner locks, and CLI/task entry points.

The interface a maintainer must understand is larger than the actual change they usually want to make. A small change to buy/submit-once behavior can require checking guard status, submission key behavior, audit artifact writing, UIA target lookup, result dialog handling, and function-tree evidence wording.

**Solution**

Introduce a deeper PingAn trade execution module that owns the order execution lifecycle behind one internal seam. The module should accept an order request, profile/options, and governance settings, then coordinate readiness guards, desktop execution adapter calls, result finalization, and audit projection.

The existing `TdxTradeManager.pingan.*` methods remain the public interface. The UIA/Win32/HID code stays behind adapter functions; it should not leak back into task/report/catalog callers.

**Benefits**

- Locality: D-07/D-08 behavior changes concentrate in one execution module.
- Leverage: tests can cover order execution invariants through a small interface while mocking only the desktop adapter seam.
- Safer evolution: future cancel/funds/position work can be kept separate instead of growing the current manager proxy further.

## Candidate 3: Managed Process Lifecycle Module

**Files**

- `tdxquant/trade/manager.py`
- `tdxquant/provider_transport_replay.py`
- `tdxquant/subscription_watch_background.py`
- `tests/test_trade_manager.py`
- `tests/test_provider_transport_replay.py`
- `tests/test_subscription_watch_background.py`

**Problem**

The codebase now has at least three lifecycle implementations with similar concepts:

- PingAn lifecycle control in `tdxquant/trade/manager.py`.
- Provider transport replay lifecycle in `tdxquant/provider_transport_replay.py`.
- Subscription watch background control in `tdxquant/subscription_watch_background.py`.

They all contain statefile, owner PID, lock, supervisor, restart, backoff, heartbeat/stale, and ownership logic. This is a real seam by the "two adapters" rule: there are already three adapters with the same lifecycle language.

The current duplication reduces locality. Bugs in owner validation, stale process detection, lock cleanup, or restart/backoff policy can be fixed in one line but remain subtly different in two other modules.

**Solution**

Create a managed process lifecycle module with a small interface for:

- statefile read/write and schema projection
- owner PID validation and ownership diagnostics
- lock acquisition/release
- supervisor tick/run decisions
- restart/backoff policy projection

Each runtime line supplies an adapter for its command shape and domain-specific status payload: PingAn trade lifecycle, provider replay daemon, and subscription watch background daemon.

**Benefits**

- Locality: lifecycle correctness is concentrated in one module.
- Leverage: one test suite can cover PID ownership, stale state, lock contention, restart limits, and backoff decisions across all adapters.
- Clearer FUNCTION_TREE evidence: lifecycle features can cite one shared module plus adapter-specific tests instead of many near-duplicate status projections.

## Candidate 4: Task Family Modules Behind `TdxTaskManager`

**Files**

- `tdxquant/api/task.py`
- `tdxquant/tasking.py`
- `tdxquant/reporting.py`
- `tests/test_api_manager.py`
- `tests/test_api_cli.py`

**Problem**

`TdxTaskManager` has become a broad facade for block tasks, subscription watch, ledger/report generation, trade audit lookup/reporting, PingAn status review, and trade execution task entries. Keeping the facade is useful for callers, but the implementation lacks locality: unrelated task families live in one large class.

The deletion test says the public facade earns its keep because removing it would spread task invocation knowledge across callers. The shallow part is the implementation layout inside the facade, not the external interface itself.

**Solution**

Keep `TdxTaskManager` as the public interface, but move implementation into task-family modules:

- block/watchlist tasks
- subscription tasks
- trade execution tasks
- trade audit/report tasks
- PingAn promotion/status tasks

`TdxTaskManager` becomes a coordinating adapter that delegates to these modules.

**Benefits**

- Locality: task changes are isolated by domain.
- Leverage: tests can target the task-family module where behavior lives, while retaining existing facade tests for compatibility.
- Lower merge friction: future OpenSpec slices touch smaller files.

## Candidate 5: Provider Capability Registry Module

**Files**

- `tdxquant/provider_discovery.py`
- `tdxquant/query_contract.py`
- `tdxquant/result_contract.py`
- `tdxquant/replay_provider.py`
- `tdxquant/provider_transport_replay.py`
- `tdxquant/api/bridge.py`

**Problem**

Provider capability semantics are important to the query/runtime line, but the capability registry is effectively encoded in a large `_capability` builder plus projections in separate replay/result/discovery modules.

This makes the provider interface harder to audit. A capability's live-provider readiness, replay fixture status, result contract, and transport replay behavior can drift unless a reviewer checks several modules and specs together.

**Solution**

Create a provider capability registry module that owns structured capability definitions and projection helpers. Discovery, replay fixture manifest, result contract diagnostics, and provider transport replay can consume the same definitions instead of duplicating field semantics.

**Benefits**

- Locality: capability status changes have one primary implementation location.
- Leverage: capability projections can be tested from registry definitions once and reused by discovery/replay/runtime callers.
- Better evidence discipline: FUNCTION_TREE and OpenSpec can cite one registry-backed source for capability status.

## Recommendation

Start with Candidate 3, the managed process lifecycle module. It has the clearest real seam because three adapters already exist, and it directly supports the user's recent focus on daemon lifecycle control, restart/backoff, process ownership, statefile writes, locks, and provider/trade runtime lifecycle management.

Second priority is Candidate 2. It is the best follow-up if the goal is to reduce risk around D-07/D-08 trading behavior after their current implementation status.

Candidate 1 is the best low-risk cleanup if the next cycle should avoid broker-side execution risk and keep working in read-only catalog space, but it should not be the default next step if the priority is mainline trading hardening.
