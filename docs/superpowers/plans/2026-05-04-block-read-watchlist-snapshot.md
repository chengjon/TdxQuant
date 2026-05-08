# Block Read Watchlist Snapshot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a provider-level read capability that returns a normalized watchlist snapshot from a single TongDaXin custom sector.

**Architecture:** Implement `block.read_watchlist_snapshot` as a wrapper around the existing raw `meta.sector_stocks` read path. Keep the raw query intact, and add a new normalization layer that validates `block_code`, distinguishes missing vs empty block, preserves first-seen order, deduplicates repeated members, and returns a stable snapshot contract through manager, CLI, replay fixtures, and discovery metadata.

**Tech Stack:** Python, existing TdxQuant manager/bridge APIs, pytest, replay fixtures, OpenSpec-aligned provider contracts

---

## File Structure

- Create: `tdxquant/block_snapshot.py`
  - Normalize raw sector-member rows into a stable watchlist snapshot.
  - Validate `block_code`.
  - Distinguish missing block vs empty block.
  - Standardize symbols, preserve order, deduplicate duplicates, emit warnings.
- Modify: `tdxquant/api/bridge.py`
  - Add `run_tdx_block_read_watchlist(...)`.
  - Reuse the existing raw sector-stocks bridge read path.
- Modify: `tdxquant/api/block.py`
  - Add `BlockApi.read_watchlist_snapshot(...)`.
- Modify: `tdxquant/api/manager.py`
  - Add `manager.block.read_watchlist_snapshot(...)`.
- Modify: `tdxquant/cli.py`
  - Add nested `api block-read-watchlist`.
  - Add flat `tdx-block-read-watchlist`.
- Modify: `tdxquant/query_contract.py`
  - Register `block.read_watchlist_snapshot` query metadata.
- Modify: `tdxquant/provider_discovery.py`
  - Expose the new capability through the existing discovery path.
- Modify: `tdxquant/replay_fixtures.py`
  - Register read-watchlist fixtures.
- Create: `tdxquant/fixtures/provider/block-read-watchlist-success.json`
- Create: `tdxquant/fixtures/provider/block-read-watchlist-empty.json`
- Create: `tdxquant/fixtures/provider/block-read-watchlist-missing-block.json`
- Create: `tdxquant/fixtures/provider/block-read-watchlist-invalid-member.json`
- Test: `tests/test_block_snapshot.py`
- Modify: `tests/test_api_manager.py`
- Modify: `tests/test_api_cli.py`
- Modify: `tests/test_replay_fixtures.py`
- Modify: `tests/test_replay_provider.py`
- Modify: `docs/TdxQuant_Project_Function_Map.md`
- Modify: `docs/TdxQuant_Next_Steps.md`

## Task 1: Build snapshot normalization core

**Files:**
- Create: `tdxquant/block_snapshot.py`
- Test: `tests/test_block_snapshot.py`

- [ ] **Step 1: Write the failing normalization tests**

```python
from tdxquant.block_snapshot import (
    BlockReadSnapshotRequest,
    build_block_watchlist_snapshot,
)
from tdxquant.models import ErrorCode


def test_build_block_watchlist_snapshot_preserves_order_and_deduplicates():
    result = build_block_watchlist_snapshot(
        BlockReadSnapshotRequest(block_code="ZXG"),
        raw_members=["000001", "600519", "000001"],
        sector_name="自选股",
    )
    assert result.ok is True
    snapshot = result.data["snapshot"]
    assert snapshot["block_code"] == "ZXG"
    assert snapshot["symbols"] == ["000001.SZ", "600519.SH"]
    assert snapshot["symbol_count"] == 2
    assert snapshot["source"] == "tongdaxin.custom_sector"
    assert snapshot["source_metadata"]["sector_name"] == "自选股"
    assert snapshot["source_metadata"]["raw_member_count"] == 3
    assert snapshot["source_metadata"]["duplicate_count"] == 1
    assert result.warnings == ["Deduplicated 1 repeated members in block ZXG"]


def test_build_block_watchlist_snapshot_returns_empty_success():
    result = build_block_watchlist_snapshot(
        BlockReadSnapshotRequest(block_code="ZXG"),
        raw_members=[],
        sector_name="空板块",
    )
    assert result.ok is True
    snapshot = result.data["snapshot"]
    assert snapshot["symbols"] == []
    assert snapshot["symbol_count"] == 0
    assert snapshot["source_metadata"]["raw_member_count"] == 0


def test_build_block_watchlist_snapshot_rejects_invalid_member():
    result = build_block_watchlist_snapshot(
        BlockReadSnapshotRequest(block_code="ZXG"),
        raw_members=["BADCODE"],
        sector_name="异常板块",
    )
    assert result.ok is False
    assert result.code == ErrorCode.INVALID_REQUEST
    assert "BADCODE" in result.message


def test_build_block_watchlist_snapshot_rejects_blank_block_code():
    result = build_block_watchlist_snapshot(
        BlockReadSnapshotRequest(block_code="   "),
        raw_members=["000001"],
        sector_name="无效板块",
    )
    assert result.ok is False
    assert result.code == ErrorCode.INVALID_REQUEST
    assert "block_code" in result.message
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python -m pytest tests/test_block_snapshot.py -q
```

Expected:

- FAIL with `ModuleNotFoundError: No module named 'tdxquant.block_snapshot'`

- [ ] **Step 3: Write the minimal snapshot core**

```python
from __future__ import annotations

from dataclasses import dataclass

from .models import ErrorCode, Result


@dataclass(slots=True)
class BlockReadSnapshotRequest:
    block_code: str


def _normalize_symbol(raw_code: str) -> str | None:
    code = str(raw_code).strip()
    if not code.isdigit() or len(code) != 6:
        return None
    if code.startswith(("0", "1", "2", "3")):
        return f"{code}.SZ"
    if code.startswith(("5", "6", "9")):
        return f"{code}.SH"
    return None


def build_block_watchlist_snapshot(
    request: BlockReadSnapshotRequest,
    *,
    raw_members: list[str],
    sector_name: str,
) -> Result:
    block_code = str(request.block_code).strip()
    if not block_code:
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message="block_code must not be blank")

    seen: set[str] = set()
    symbols: list[str] = []
    duplicate_count = 0
    for raw_member in raw_members:
        normalized = _normalize_symbol(raw_member)
        if normalized is None:
            return Result(
                ok=False,
                code=ErrorCode.INVALID_REQUEST,
                message=f"unable to normalize block member: {raw_member}",
            )
        if normalized in seen:
            duplicate_count += 1
            continue
        seen.add(normalized)
        symbols.append(normalized)

    warnings: list[str] = []
    if duplicate_count:
        warnings.append(f"Deduplicated {duplicate_count} repeated members in block {block_code}")

    return Result(
        ok=True,
        code=ErrorCode.OK,
        message="block watchlist snapshot built",
        warnings=warnings,
        data={
            "snapshot": {
                "block_code": block_code,
                "symbols": symbols,
                "symbol_count": len(symbols),
                "source": "tongdaxin.custom_sector",
                "source_metadata": {
                    "sector_name": sector_name,
                    "raw_member_count": len(raw_members),
                    "duplicate_count": duplicate_count,
                },
            }
        },
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
python -m pytest tests/test_block_snapshot.py -q
```

Expected:

- PASS

- [ ] **Step 5: Commit**

```bash
git add tdxquant/block_snapshot.py tests/test_block_snapshot.py
git commit -m "feat: add block watchlist snapshot core"
```

## Task 2: Add bridge and manager entrypoints

**Files:**
- Modify: `tdxquant/api/bridge.py`
- Modify: `tdxquant/api/block.py`
- Modify: `tdxquant/api/manager.py`
- Test: `tests/test_api_manager.py`

- [ ] **Step 1: Write the failing manager test**

```python
from unittest import mock


@mock.patch("tdxquant.api.block.run_tdx_block_read_watchlist")
def test_manager_block_read_watchlist_snapshot_attaches_metadata(mock_run):
    from tdxquant.api.manager import TdxApiManager
    from tdxquant.models import ErrorCode, Result

    mock_run.return_value = Result(
        ok=True,
        code=ErrorCode.OK,
        message="ok",
        data={"snapshot": {"block_code": "ZXG", "symbols": ["000001.SZ"], "symbol_count": 1}},
    )

    manager = TdxApiManager()
    result = manager.block.read_watchlist_snapshot(block_code="ZXG")

    assert result.ok is True
    assert result.data["snapshot"]["block_code"] == "ZXG"
    assert result.data["management"]["capability"] == "block.read_watchlist_snapshot"
    mock_run.assert_called_once()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python -m pytest tests/test_api_manager.py -k "block_read_watchlist_snapshot" -q
```

Expected:

- FAIL because `run_tdx_block_read_watchlist` and/or `read_watchlist_snapshot` does not exist

- [ ] **Step 3: Wire bridge, block API, and manager**

```python
# tdxquant/api/bridge.py
from ..block_snapshot import BlockReadSnapshotRequest, build_block_watchlist_snapshot
from ..models import ErrorCode, Result


def run_tdx_block_read_watchlist(*, block_code: str, strategy_path: str | None = None) -> Result:
    raw_result = run_tdx_data_sector_stocks(
        block_code=block_code,
        block_type=0,
        list_type=0,
        strategy_path=strategy_path,
    )
    if not raw_result.ok:
        return raw_result

    raw_payload = raw_result.data.get("result") or {}
    records = raw_payload.get("records") or []
    if not records:
        return build_block_watchlist_snapshot(
            BlockReadSnapshotRequest(block_code=block_code),
            raw_members=[],
            sector_name=block_code,
        )

    raw_members = [str(row.get("code", "")).strip() for row in records if isinstance(row, dict)]
    if not raw_members and raw_payload.get("records") == []:
        return build_block_watchlist_snapshot(
            BlockReadSnapshotRequest(block_code=block_code),
            raw_members=[],
            sector_name=block_code,
        )
    if not raw_members:
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=f"block_code not found: {block_code}")

    sector_name = block_code
    return build_block_watchlist_snapshot(
        BlockReadSnapshotRequest(block_code=block_code),
        raw_members=raw_members,
        sector_name=sector_name,
    )


# tdxquant/api/block.py
from .bridge import run_tdx_block_read_watchlist

class BlockApi:
    ...
    def read_watchlist_snapshot(self, block_code: str) -> Result:
        return run_tdx_block_read_watchlist(block_code=block_code, strategy_path=self.strategy_path)


# tdxquant/api/manager.py
class _BlockManagerProxy:
    ...
    def read_watchlist_snapshot(self, *, block_code: str):
        return self._manager._attach_management_metadata(
            self._manager.block_api.read_watchlist_snapshot(block_code=block_code),
            capability="block.read_watchlist_snapshot",
            method_name="read_watchlist_snapshot",
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
python -m pytest tests/test_api_manager.py -k "block_read_watchlist_snapshot" -q
```

Expected:

- PASS

- [ ] **Step 5: Commit**

```bash
git add tdxquant/api/bridge.py tdxquant/api/block.py tdxquant/api/manager.py tests/test_api_manager.py
git commit -m "feat: add block read watchlist manager entrypoint"
```

## Task 3: Add CLI entrypoints

**Files:**
- Modify: `tdxquant/cli.py`
- Test: `tests/test_api_cli.py`

- [ ] **Step 1: Write the failing CLI parser and dispatch tests**

```python
def test_api_block_read_watchlist_command_parses(self):
    args = parse_args(["api", "block-read-watchlist", "--block-code", "ZXG"])
    self.assertEqual(args.command, "api")
    self.assertEqual(args.api_command, "block-read-watchlist")
    self.assertEqual(args.block_code, "ZXG")


@mock.patch("tdxquant.cli.TdxApiManager")
def test_handle_api_block_read_watchlist_uses_manager(self, mock_manager_cls):
    manager = mock_manager_cls.return_value
    manager.block.read_watchlist_snapshot.return_value = Result(
        ok=True,
        code=ErrorCode.OK,
        message="ok",
        data={"snapshot": {"block_code": "ZXG", "symbols": ["000001.SZ"], "symbol_count": 1}},
    )
    args = parse_args(["api", "block-read-watchlist", "--block-code", "ZXG"])
    result = _handle_api_subcommand(args)
    self.assertTrue(result.ok)
    manager.block.read_watchlist_snapshot.assert_called_once_with(block_code="ZXG")
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "block_read_watchlist" -q
```

Expected:

- FAIL because parser/dispatch does not exist yet

- [ ] **Step 3: Add nested and flat CLI commands**

```python
# tdxquant/cli.py
api_block_read_watchlist_parser = api_subparsers.add_parser("block-read-watchlist")
api_block_read_watchlist_parser.add_argument("--block-code", required=True)

flat_block_read_watchlist_parser = subparsers.add_parser("tdx-block-read-watchlist")
flat_block_read_watchlist_parser.add_argument("--block-code", required=True)

if args.api_command == "block-read-watchlist":
    return manager.block.read_watchlist_snapshot(block_code=args.block_code)

if args.command == "tdx-block-read-watchlist":
    manager = TdxApiManager(strategy_path=args.strategy_path if hasattr(args, "strategy_path") else None)
    return manager.block.read_watchlist_snapshot(block_code=args.block_code)
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
python -m pytest tests/test_api_cli.py -k "block_read_watchlist" -q
```

Expected:

- PASS

- [ ] **Step 5: Commit**

```bash
git add tdxquant/cli.py tests/test_api_cli.py
git commit -m "feat: add block read watchlist CLI commands"
```

## Task 4: Register replay fixtures and discovery metadata

**Files:**
- Modify: `tdxquant/query_contract.py`
- Modify: `tdxquant/provider_discovery.py`
- Modify: `tdxquant/replay_fixtures.py`
- Create: `tdxquant/fixtures/provider/block-read-watchlist-success.json`
- Create: `tdxquant/fixtures/provider/block-read-watchlist-empty.json`
- Create: `tdxquant/fixtures/provider/block-read-watchlist-missing-block.json`
- Create: `tdxquant/fixtures/provider/block-read-watchlist-invalid-member.json`
- Modify: `tests/test_replay_fixtures.py`
- Modify: `tests/test_replay_provider.py`

- [ ] **Step 1: Write the failing fixture/discovery tests**

```python
def test_block_read_watchlist_fixture_is_registered():
    from tdxquant.replay_fixtures import get_replay_fixture_path
    path = get_replay_fixture_path("block-read-watchlist-success")
    assert path.name == "block-read-watchlist-success.json"


def test_block_read_watchlist_discovery_metadata_is_exposed():
    from tdxquant.provider_discovery import list_capabilities
    capabilities = list_capabilities()
    capability = next(item for item in capabilities if item["name"] == "block.read_watchlist_snapshot")
    query_metadata = capability["query_metadata"]
    assert query_metadata["supports_empty_results"] is True
    assert query_metadata["returns_ordered_symbols"] is True
    assert query_metadata["deduplicates_members"] is True
    assert query_metadata["normalizes_symbols"] is True
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python -m pytest tests/test_replay_fixtures.py tests/test_replay_provider.py -k "block_read_watchlist" -q
```

Expected:

- FAIL because fixture registration and/or discovery metadata does not exist

- [ ] **Step 3: Add query metadata and representative fixtures**

```python
# tdxquant/query_contract.py
_QUERY_CONTRACT_REGISTRY["block.read_watchlist_snapshot"] = {
    "query_shapes": [
        {
            "query_kind": "block.read_watchlist_snapshot",
            "selectors": ["block_code"],
            "query_params": [],
        }
    ],
    "supports_requested_fields": False,
}
_QUERY_REPLAY_SUPPORTED_CAPABILITIES.add("block.read_watchlist_snapshot")


# tdxquant/provider_discovery.py
_capability(
    "block.read_watchlist_snapshot",
    domain="block",
    description="Read one TongDaXin custom sector as a normalized watchlist snapshot.",
    stability="stable",
    side_effect_level="read_only",
    manager_method="block.read_watchlist_snapshot",
    api_command="block-read-watchlist",
    flat_command="tdx-block-read-watchlist",
    requires=["native_windows_python", "tqcenter"],
)
```

Fixture examples:

```json
{
  "success": true,
  "ok": true,
  "code": "ok",
  "message": "block watchlist snapshot built",
  "warnings": [],
  "artifacts": [],
  "data": {
    "snapshot": {
      "block_code": "ZXG",
      "symbols": ["000001.SZ", "600519.SH"],
      "symbol_count": 2,
      "source": "tongdaxin.custom_sector",
      "source_metadata": {
        "sector_name": "自选股",
        "raw_member_count": 2,
        "duplicate_count": 0
      }
    }
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
python -m pytest tests/test_replay_fixtures.py tests/test_replay_provider.py -k "block_read_watchlist" -q
```

Expected:

- PASS

- [ ] **Step 5: Commit**

```bash
git add tdxquant/query_contract.py tdxquant/provider_discovery.py tdxquant/replay_fixtures.py tdxquant/fixtures/provider/block-read-watchlist-*.json tests/test_replay_fixtures.py tests/test_replay_provider.py
git commit -m "feat: add block read watchlist fixtures and discovery metadata"
```

## Task 5: Update docs and run focused verification

**Files:**
- Modify: `docs/TdxQuant_Project_Function_Map.md`
- Modify: `docs/TdxQuant_Next_Steps.md`

- [ ] **Step 1: Update roadmap and capability docs**

Add concise notes that:

- `block.read_watchlist_snapshot` now exists as the reverse read path
- it is provider-level and read-only
- file export and task wrapping remain deferred

- [ ] **Step 2: Run focused verification**

Run:

```bash
python -m pytest tests/test_block_snapshot.py tests/test_api_manager.py tests/test_api_cli.py tests/test_replay_fixtures.py tests/test_replay_provider.py -q
```

Expected:

- PASS

- [ ] **Step 3: Run diff hygiene**

Run:

```bash
git diff --check
```

Expected:

- no output

- [ ] **Step 4: Commit**

```bash
git add docs/TdxQuant_Project_Function_Map.md docs/TdxQuant_Next_Steps.md
git commit -m "docs: add block read watchlist snapshot notes"
```

## Spec Coverage Check

- Provider-level read capability: covered by Tasks 1-3
- Stable snapshot contract: covered by Task 1
- Missing/empty/invalid semantics: covered by Task 1
- Replay fixtures: covered by Task 4
- Discovery metadata: covered by Task 4
- Docs/roadmap sync: covered by Task 5

## Self-Review

- No placeholders left in code/test steps.
- `symbol_count` is used consistently.
- The plan explicitly reuses `meta.sector_stocks` as the raw read substrate.
- No task/export/file-import work was added beyond the approved scope.
