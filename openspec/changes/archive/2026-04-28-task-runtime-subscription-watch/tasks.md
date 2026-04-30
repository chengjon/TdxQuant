## 1. Contract Definition

- [x] 1.1 Define the foreground `subscription-watch` task contract, including event artifact and completion-summary requirements.
- [x] 1.2 Define the normalized JSONL event row schema and the structured status artifact fields.

## 2. Implementation

- [x] 2.1 Add subscription-watch event normalization and artifact helper utilities to the task layer.
- [x] 2.2 Implement `TdxTaskManager.subscription_watch(...)` on top of `manager.runtime.open_subscription_session()`.
- [x] 2.3 Add `task subscription-watch` CLI parsing and dispatch, and register a task profile for the workflow.

## 3. Verification and Docs

- [x] 3.1 Add task manager and task CLI tests that lock the watch workflow, artifact paths, and bounded-stop behavior.
- [x] 3.2 Document the `subscription-watch` task contract and update roadmap/function-map references.
- [x] 3.3 Run focused tests, `python -m compileall tdxquant`, and `openspec validate task-runtime-subscription-watch --type change --strict`.
