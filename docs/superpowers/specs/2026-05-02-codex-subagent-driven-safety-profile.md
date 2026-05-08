# Codex Subagent-Driven Safety Profile

Date: 2026-05-02
Status: Approved working profile
Scope: Codex native `spawn_agent` usage in this repository

## Purpose

Define a safe, Codex-compatible subagent strategy for this repository after OMX-related model routing and runtime assumptions caused confusion.

This profile is intentionally conservative:

- Prefer Codex native subagents over OMX runtime workflows
- Prefer inherited parent model over explicit model override
- Prefer bounded roles over flexible orchestration
- Prefer inline execution immediately after the first dispatch/config failure

## Non-Goals

This profile does not define:

- OMX runtime worker/team routing
- tmux-based swarm orchestration
- HTTP or external transport delegation
- repository-specific implementation workflows

## Current Environment Assumptions

The active local Codex configuration currently pins the parent session model to `gpt-5.4`.

Subagent dispatch must therefore assume:

- parent session model is the default safe model
- child agents should inherit that model unless there is a concrete reason not to
- OMX role tables are advisory history, not live Codex dispatch config

## Hard Rules

1. Never treat `general-purpose` as a model name.
2. Never use OMX role/model tables to choose Codex child-agent models automatically.
3. Never pass a model name that is not present in the current Codex `spawn_agent` schema.
4. Default to omitting `spawn_agent.model`.
5. If the first child dispatch fails for model/config reasons, stop delegating and switch to inline execution for the current task.
6. Do not run more than one code-writing child agent at the same time.
7. Do not run two child agents with overlapping write scopes.

## Approved Codex Role Mapping

| Workflow role | Intended use | Codex `agent_type` | Model policy | Reasoning effort | Notes |
| --- | --- | --- | --- | --- | --- |
| `explore` | code search, symbol lookup, implementation discovery | `explorer` | inherit | `low` or `medium` | read-only only |
| `implementer` | isolated implementation task | `worker` | inherit | `medium` | single writer at a time |
| `spec-reviewer` | compare implementation against spec/plan | `default` | inherit | `medium` | no code changes |
| `quality-reviewer` | bug/risk/test-gap review | `default` | inherit | `high` | no code changes |
| `final-verifier` | final completion and evidence review | `default` | inherit | `high` | no code changes |

## Explicit Model Override Policy

Default policy: do not pass `model`.

Allowed explicit model whitelist only if inheritance is unavailable or demonstrably broken:

- `gpt-5.4`
- `gpt-5.4-mini`

Disallowed for Codex native subagent dispatch in this repository:

- `general-purpose`
- `gpt-5.3-codex-spark`
- any OMX-specific alias
- any model not listed by the active `spawn_agent` schema

## Concurrency Policy

Maximum concurrent child agents: `2`

Allowed pattern:

- one `explorer` in parallel with the main thread
- one `worker` plus one read-only reviewer/explorer only if scopes do not conflict

Disallowed pattern:

- two simultaneous `worker` agents
- any parallel agents touching the same files
- speculative fan-out after a dispatch/config error

## Downgrade Policy

Immediately downgrade to inline execution for the current task if any of the following occurs:

- `model not found`
- unsupported/invalid `agent_type`
- child agent launch failure
- mismatch between assigned role and actual child-agent behavior
- repeated need to resend large amounts of missing context

After downgrade:

- do not retry with ad hoc model guesses
- do not retry by translating old OMX terminology
- continue with direct local execution

## Dispatch Templates

### Explorer

Use for read-only repository questions.

```text
spawn_agent(
  agent_type="explorer",
  message="Answer this repository question only: <question>. Do not edit files. Return findings with file references.",
  reasoning_effort="low"
)
```

### Implementer

Use only for a bounded implementation slice.

```text
spawn_agent(
  agent_type="worker",
  message="Implement <task>. Only modify these files: <paths>. You are not alone in the codebase; do not revert others' changes. Return changed files, verification run, and residual risks.",
  reasoning_effort="medium"
)
```

### Reviewer

Use for spec or quality review only.

```text
spawn_agent(
  agent_type="default",
  message="Review the completed change only. Do not edit code. Return findings ordered by severity with file references and note any testing gaps.",
  reasoning_effort="high"
)
```

## Pre-Dispatch Checklist

Before dispatching a child agent, confirm all of the following:

- the task is independent enough to delegate
- the write scope is explicit
- the child does not need the whole parent-session history
- no OMX-specific terms are being used as live configuration
- no explicit `model` override is necessary
- fallback to inline execution is acceptable if dispatch fails

## Repository Policy

For this repository, the recommended default is:

- use child agents sparingly
- use `explorer` first for codebase lookup
- use `worker` only for isolated implementation slices
- use `default` for review roles
- inherit the parent `gpt-5.4` session model
- keep write concurrency at `1`

## Rationale

This profile intentionally optimizes for stability over throughput.

The failure mode seen previously was not "subagents are impossible"; it was "mixed routing assumptions across Codex native agents, OMX runtime terminology, and unsupported model names."

The safest correction is therefore not a more complex routing layer. It is a smaller one.
