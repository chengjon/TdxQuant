# TdxQuant Context

This file defines the project language used by architecture, diagnosis, TDD, and issue-planning skills. For feature status, always defer to `FUNCTION_TREE.md`.

## Product Shape

TdxQuant is a local integration and governance layer around TongDaXin/TdxQuant data, formula, runtime, catalog, task/report, subscription, block watchlist, and desktop trading workflows.

The repo has two major runtime lines:

- Query and runtime line: `TdxApiManager`, provider bridge calls, replay fixtures, provider capability discovery, runtime profiles, task/report/catalog read paths.
- Desktop automation trading line: `TdxTradeManager`, PingAn desktop gateway, Win32/UIA/HID adapters, trade safety, lifecycle, and immutable audit artifacts.

The project is not a hosted multi-tenant service. It is primarily a local/bridge-oriented toolchain where external availability depends on the Windows TDX environment, bridge process, provider mode, broker client, or replay fixture selected by the caller.

## Canonical Feature Registry

`FUNCTION_TREE.md` is the single feature registry and status source.

Every feature node must carry:

- Status: one of `[已实现]`, `[部分实现]`, `[已设计/待实现]`, `[非目标/边界]`.
- Evidence: source, runtime config, tests, archived OpenSpec, fixture, or contract document.
- Boundary: what the feature currently guarantees and what it does not claim.

Do not create a competing `ROADMAP.md`. Designed or future capabilities belong in `FUNCTION_TREE.md` with explicit status and boundaries.

## Domain Terms

- Function node: one row in `FUNCTION_TREE.md` that describes a concrete capability, status, evidence, and boundary.
- Evidence: the code, tests, configs, fixtures, docs, or archived OpenSpec proving the status claim.
- Boundary: the explicit limit that prevents designed, replayed, fixture-backed, or environment-dependent behavior from being mistaken for live availability.
- Provider: the implementation or bridge used to satisfy market/meta/formula/block/runtime capability calls.
- Replay fixture: a deterministic contract and regression asset. A replay fixture is not proof of live provider readiness.
- Provider result contract: the normalized result envelope and field rules shared by provider-backed API paths.
- Runtime profile: local config describing how a command or task should run.
- Preset: named runtime option bundle for repeatable CLI/task/report invocation.
- Command catalog: read-only registry of available commands, names, sources, labels, options, and bundle plans.
- Command bundle: a catalog entry that groups steps; each step still inherits the boundary of the underlying function node.
- Task: higher-level orchestration exposed through `TdxTaskManager` and CLI task commands.
- Report: read-oriented aggregation or artifact generation; report availability does not imply write workflow readiness.
- Subscription watch: subscription status/event monitoring path, including foreground, background, and replay-backed variants.
- Block watchlist: TDX block/user watchlist read, import, sync, mutation, and audit surface.
- Desktop session: the Windows client interaction context used by desktop automation.
- PingAn desktop gateway: the current broker-specific automation path; it is not a general multi-broker platform.
- Trade audit: immutable artifact and lookup surface for desktop trading attempts, results, and diagnostics.

## Architecture Rules

- Keep query/runtime and desktop trading governance separate. Do not merge broker automation concerns back into the query API line.
- Treat CLI existence as an entrypoint claim, not as proof that every external provider or desktop environment is available.
- Treat replay, fake provider, and fixtures as contract evidence only. They do not prove live market, formula, block, subscription, or broker readiness.
- WSL-side code should consume structured bridge/provider output. It must not claim direct Win32/UIA/HID control unless that behavior runs on the appropriate Windows/bridge side.
- Use OpenSpec for substantive behavior changes. Archive completed changes and keep the resulting spec as durable evidence.
- Update `FUNCTION_TREE.md` whenever feature status, evidence, or boundary changes.

## Current Architecture Pressure Points

The current implementation is well governed but has several broad modules that reduce locality:

- `tdxquant/cli.py` owns parser construction, command dispatch, catalog rendering, validation, output, and many domain-specific options.
- `tdxquant/api/task.py` keeps many unrelated task families behind one large `TdxTaskManager` facade.
- `tdxquant/trade/manager.py` and `tdxquant/desktop/uia.py` carry high-risk desktop automation and lifecycle behavior in large modules.
- Provider replay, discovery, capability, and result contract semantics cross several files and should be treated as a coherent provider runtime boundary.

When refactoring, prefer deepening one domain boundary at a time while preserving CLI/API compatibility and FUNCTION_TREE evidence.
