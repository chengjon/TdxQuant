# PingAn Contract Number Extraction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `pingan-buy-submit-once` extract the contract number from the result dialog and backfill it into command output, a fixed state file, and CLI logs.

**Architecture:** Extend the existing Ping An result-dialog parsing path so it merges Win32 child texts with UIA dialog texts before regex extraction. Keep persistence at the CLI boundary so command output serialization, fixed status-file writing, and stderr logging all use the same resolved `contract_no`.

**Tech Stack:** Python, unittest, pathlib, existing `tdxquant.uia_inspector` and `tdxquant.cli`

---

### Task 1: Cover contract extraction from merged dialog texts

**Files:**
- Modify: `tests/test_runtime.py`
- Modify: `tdxquant/uia_inspector.py`

- [ ] **Step 1: Write the failing test**

```python
def test_extract_contract_no_prefers_merged_dialog_texts(self) -> None:
    contract_no = _extract_contract_no_from_texts(
        [
            "提示",
            "委托已提交，",
            "合同号：B202604250001",
        ]
    )
    self.assertEqual(contract_no, "B202604250001")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_runtime.UIAContractExtractionTests.test_extract_contract_no_prefers_merged_dialog_texts -v`
Expected: `AttributeError` or import failure because helper does not exist yet.

- [ ] **Step 3: Write minimal implementation**

```python
def _extract_contract_no_from_texts(texts: list[str]) -> str | None:
    for text in texts:
        match = re.search(r"合同号[：: ]*([0-9A-Za-z]+)", text)
        if match:
            return match.group(1)
    return None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_runtime.UIAContractExtractionTests.test_extract_contract_no_prefers_merged_dialog_texts -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_runtime.py tdxquant/uia_inspector.py
git commit -m "test: cover pingan contract extraction"
```

### Task 2: Cover state-file backfill payload and write path

**Files:**
- Modify: `tests/test_runtime.py`
- Modify: `tdxquant/cli.py`

- [ ] **Step 1: Write the failing test**

```python
def test_write_pingan_last_order_state_persists_contract_no(self) -> None:
    result = Result(
        ok=True,
        code=ErrorCode.OK,
        message="completed pingan buy submit once",
        data={"input": {"code": "516820"}, "result_dialog": {"contract_no": "B202604250001"}},
    )
    with TemporaryDirectory() as tmp_dir:
        state_path = Path(tmp_dir) / "pingan-last-order.json"
        _write_pingan_last_order_state(result, state_path)
        payload = json.loads(state_path.read_text(encoding="utf-8"))
    self.assertEqual(payload["contract_no"], "B202604250001")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_runtime.PingAnOrderStateTests.test_write_pingan_last_order_state_persists_contract_no -v`
Expected: import failure because helper does not exist yet.

- [ ] **Step 3: Write minimal implementation**

```python
def _write_pingan_last_order_state(result: Result, state_path: Path) -> None:
    payload = {
        "ok": result.ok,
        "message": result.message,
        "contract_no": result.data.get("result_dialog", {}).get("contract_no"),
        "input": result.data.get("input", {}),
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_runtime.PingAnOrderStateTests.test_write_pingan_last_order_state_persists_contract_no -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_runtime.py tdxquant/cli.py
git commit -m "feat: persist pingan last order state"
```

### Task 3: Wire command logging and end-to-end targeted verification

**Files:**
- Modify: `tdxquant/cli.py`
- Modify: `tdxquant/uia_inspector.py`
- Test: `tests/test_runtime.py`

- [ ] **Step 1: Write the failing test**

```python
def test_emit_pingan_contract_log_writes_stderr_line(self) -> None:
    stream = io.StringIO()
    _emit_pingan_contract_log("B202604250001", stream)
    self.assertIn("contract_no=B202604250001", stream.getvalue())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_runtime.PingAnOrderStateTests.test_emit_pingan_contract_log_writes_stderr_line -v`
Expected: import failure because helper does not exist yet.

- [ ] **Step 3: Write minimal implementation**

```python
def _emit_pingan_contract_log(contract_no: str | None, stream: TextIO) -> None:
    if contract_no:
        print(f"[pingan-buy-submit-once] contract_no={contract_no}", file=stream)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_runtime.PingAnOrderStateTests -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_runtime.py tdxquant/cli.py tdxquant/uia_inspector.py
git commit -m "feat: log pingan contract number"
```
