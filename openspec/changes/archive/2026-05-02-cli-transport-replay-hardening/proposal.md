## Why

当前项目已经具备 in-process replay provider mode 和稳定 replay fixture bundle，但 `tdxquant ... --provider-mode replay` 还没有被正式固化成子进程级 transport contract。上层项目虽然可以离线调用正式 CLI 入口，却仍需要自行猜测支持矩阵、fixture 选择算法、stdout/output 关系和 replay 失败语义。

## What Changes

- Harden existing CLI replay entrypoints so supported nested `api`, flat provider commands, and `task subscription-watch` can be consumed as a stable subprocess transport.
- Define an explicit CLI replay support matrix instead of implicitly exposing replay arguments on commands without fixture backing.
- Normalize CLI replay selector behavior for `--provider-mode replay`, `--fixture`, `--fixture-path`, and `--output`.
- Ensure replay-mode failures return stable JSON envelopes with replay metadata and never silently fall back to live Windows runtime execution.
- Stabilize `subscription-watch` replay artifact discovery, alias fields, and malformed replay-bundle failure behavior for subprocess callers.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-api-cli-entry`: formalize CLI replay support matrix, selector algorithm, stdout/output mirroring, and normalized replay failure semantics for supported official commands.
- `tdx-task-subscription-watch`: formalize replay-mode completed-run artifact paths, legacy alias fields, and stable malformed replay-bundle failure behavior.

## Impact

- Affected code:
  - `tdxquant/cli.py`
  - `tdxquant/api/task.py`
  - replay helper usage in `tdxquant/replay_provider.py`
- Affected tests:
  - `tests/test_api_cli.py`
  - `tests/test_api_manager.py`
  - replay fixture / replay provider contract tests
- Affected documentation:
  - replay fixture contract docs
  - `subscription-watch` contract docs
- No breaking CLI command removals; unsupported replay combinations fail earlier and more explicitly.
