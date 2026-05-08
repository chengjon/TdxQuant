# TDX Real-Machine Validation Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the remaining real-machine validation gaps for `implement-tdx-wsl-windows-bridge` and `implement-pingan-win32-trading-adapter` with one controlled Windows-side verification pass.

**Architecture:** Treat this as an evidence-collection run, not a new feature batch. Use the existing bridge, HID, Win32/UIA, and stable trade commands exactly as shipped, collect JSON artifacts per scenario, and decide task closure from observed window behavior rather than from code inspection.

**Tech Stack:** Native Windows Python, TongDaXin / PingAn desktop client, HID device, `python -m tdxquant.cli`, JSON artifact capture

---

## Scope

This run closes these exact remaining tasks:

- `implement-tdx-wsl-windows-bridge`
  - `4.4` validate whether HID input can advance TongDaXin from `请输入证券代码!` to the real confirmation path
- `implement-pingan-win32-trading-adapter`
  - `4.2` validate foreground / occluded / minimized recognition differences on the real client
  - `6.5` validate whether HID input advances TongDaXin into the real order confirmation path

This run does **not** add new code. It only decides whether the remaining tasks can be checked off, need documentation tightening, or require a follow-up change.

## Operator Preconditions

- Run on native Windows Python, not WSL.
- Keep the HID device attached and confirm the serial port number first.
- Launch the target client before starting:
  - TongDaXin window keyword: `通达信金融终端`
  - PingAn window keyword: `平安证券`
- Use a low-risk validation order:
  - quantity fixed to `100`
  - choose a liquid A-share or ETF code that the operator explicitly approves before the run
  - choose a clearly non-marketable limit price that the operator explicitly approves before the run
- Before any live submit step, confirm the operator is watching the screen and is ready to stop if the client behavior differs from expectation.

## Evidence Directory

Create one run directory on the Windows machine before starting:

```powershell
$run = "runtime\\verification\\2026-04-30-real-machine-closure"
New-Item -ItemType Directory -Force -Path $run | Out-Null
New-Item -ItemType Directory -Force -Path "$run\\bridge" | Out-Null
New-Item -ItemType Directory -Force -Path "$run\\pingan" | Out-Null
New-Item -ItemType Directory -Force -Path "$run\\screens" | Out-Null
```

Use these runtime values consistently in the commands below:

```powershell
$port = "COM3"
$code = "516820"
$price = "0.35"
$qty = 100
```

If the operator chooses different values, update all later commands to match and record the final values in the acceptance template.

### Task 1: Capture baseline bridge and desktop health

**Files:**
- Create: `runtime/verification/2026-04-30-real-machine-closure/bridge/tdx-bridge-health.json`
- Create: `runtime/verification/2026-04-30-real-machine-closure/bridge/tdx-hid-ping.json`
- Create: `runtime/verification/2026-04-30-real-machine-closure/pingan/trade-health.json`
- Create: `runtime/verification/2026-04-30-real-machine-closure/pingan/uia-windows-foreground.json`
- Create: `runtime/verification/2026-04-30-real-machine-closure/pingan/inspect-foreground.json`

- [ ] **Step 1: Capture bridge health and HID reachability**

Run:

```powershell
python -m tdxquant.cli tdx-bridge-health --hid-port $port --output "$run\\bridge\\tdx-bridge-health.json"
python -m tdxquant.cli tdx-trade-hid-ping --port $port --output "$run\\bridge\\tdx-hid-ping.json"
```

Expected:
- `tdx-bridge-health` returns structured JSON with the window and HID checks visible.
- `tdx-trade-hid-ping` returns `ok=true` or a clearly actionable HID error.

- [ ] **Step 2: Capture PingAn health and top-level window evidence in the foreground state**

Bring the PingAn client to the foreground, then run:

```powershell
python -m tdxquant.cli trade health --port $port --output "$run\\pingan\\trade-health.json"
python -m tdxquant.cli uia-windows --window-key "平安证券" --output "$run\\pingan\\uia-windows-foreground.json"
python -m tdxquant.cli inspect --output "$run\\pingan\\inspect-foreground.json"
```

Expected:
- `trade health` reports the runtime checks and any HID check outcome.
- `uia-windows` shows the expected top-level PingAn window.
- `inspect` captures the live control tree for later comparison.

### Task 2: Measure foreground / occluded / minimized detection differences

**Files:**
- Create: `runtime/verification/2026-04-30-real-machine-closure/pingan/uia-windows-occluded.json`
- Create: `runtime/verification/2026-04-30-real-machine-closure/pingan/inspect-occluded.json`
- Create: `runtime/verification/2026-04-30-real-machine-closure/pingan/uia-windows-minimized.json`
- Create: `runtime/verification/2026-04-30-real-machine-closure/pingan/inspect-minimized.json`

- [ ] **Step 1: Capture the occluded-window case**

Cover the PingAn window with another normal window without minimizing it, then run:

```powershell
python -m tdxquant.cli uia-windows --window-key "平安证券" --output "$run\\pingan\\uia-windows-occluded.json"
python -m tdxquant.cli inspect --output "$run\\pingan\\inspect-occluded.json"
```

Expected:
- The top-level window should still be discoverable.
- Any missing controls, stale bounds, or changed focus evidence must be noted in the acceptance record.

- [ ] **Step 2: Capture the minimized-window case**

Minimize the PingAn window, then run:

```powershell
python -m tdxquant.cli uia-windows --window-key "平安证券" --output "$run\\pingan\\uia-windows-minimized.json"
python -m tdxquant.cli inspect --output "$run\\pingan\\inspect-minimized.json"
```

Expected:
- If discovery still works, record that explicitly.
- If discovery degrades or fails, preserve the JSON and record whether the failure is acceptable boundary behavior or a blocker for task `4.2`.

### Task 3: Validate TongDaXin HID path progression

**Files:**
- Create: `runtime/verification/2026-04-30-real-machine-closure/bridge/tdx-hid-buy-probe-dry-run.json`
- Create: `runtime/verification/2026-04-30-real-machine-closure/bridge/tdx-hid-buy-probe-live.json`
- Create: `runtime/verification/2026-04-30-real-machine-closure/bridge/tdx-uia-dialogs-after-live.json`

- [ ] **Step 1: Validate dry-run preconditions first**

Bring TongDaXin to the foreground and make sure the buy page is visible, then run:

```powershell
python -m tdxquant.cli tdx-hid-buy-probe --port $port --code $code --price $price --quantity $qty --dry-run --output "$run\\bridge\\tdx-hid-buy-probe-dry-run.json"
```

Expected:
- The command confirms window and focus preconditions without sending HID input.
- If dry-run already shows focus or page problems, stop here and do not proceed to live HID submission.

- [ ] **Step 2: Run the first live HID progression probe**

With the operator watching the screen, run:

```powershell
python -m tdxquant.cli tdx-hid-buy-probe --port $port --code $code --price $price --quantity $qty --commit-key tab --submit-strategy post_wm_command_parent --pre-clear --output "$run\\bridge\\tdx-hid-buy-probe-live.json"
python -m tdxquant.cli uia-dialogs --include-all-windows --output "$run\\bridge\\tdx-uia-dialogs-after-live.json"
```

Expected:
- Success condition: the client progresses beyond the `请输入证券代码!` prompt and reaches a real confirmation or next-step order dialog.
- Failure condition: the same prompt still appears, or no confirmation-related state change is visible.

- [ ] **Step 3: If the first live probe fails, run one controlled fallback probe**

Only run this once, and only if Step 2 clearly failed with the same prompt:

```powershell
python -m tdxquant.cli tdx-hid-buy-probe --port $port --code $code --price $price --quantity $qty --commit-key enter --submit-strategy wm_command_parent --pre-clear --output "$run\\bridge\\tdx-hid-buy-probe-live-fallback.json"
python -m tdxquant.cli uia-dialogs --include-all-windows --output "$run\\bridge\\tdx-uia-dialogs-after-live-fallback.json"
```

Expected:
- Either the fallback reaches confirmation and rescues task closure, or it confirms that the remaining tasks cannot be closed yet.

### Task 4: Validate PingAn split-step confirmation boundary on the real client

**Files:**
- Create: `runtime/verification/2026-04-30-real-machine-closure/pingan/trade-preflight.json`
- Create: `runtime/verification/2026-04-30-real-machine-closure/pingan/trade-submit-ready.json`
- Create: `runtime/verification/2026-04-30-real-machine-closure/pingan/uia-dialogs-after-submit-ready.json`
- Create: `runtime/verification/2026-04-30-real-machine-closure/pingan/trade-confirm-current.json`

- [ ] **Step 1: Reconfirm preflight before any live boundary step**

Run:

```powershell
python -m tdxquant.cli trade preflight --port $port --code $code --price $price --quantity $qty --output "$run\\pingan\\trade-preflight.json"
```

Expected:
- The request-level readiness checks pass or fail clearly with structured details.

- [ ] **Step 2: Validate the pre-confirm boundary without advancing confirmation**

Run:

```powershell
python -m tdxquant.cli trade submit-ready --port $port --code $code --price $price --quantity $qty --output "$run\\pingan\\trade-submit-ready.json"
python -m tdxquant.cli uia-dialogs --include-all-windows --output "$run\\pingan\\uia-dialogs-after-submit-ready.json"
```

Expected:
- The command either reaches the confirmation boundary or returns a structured reason why it could not.
- This step should not yet confirm the order.

- [ ] **Step 3: Only if Step 2 reached the confirmation boundary, validate the current confirm advance**

Run:

```powershell
python -m tdxquant.cli trade confirm-current --output "$run\\pingan\\trade-confirm-current.json"
```

Expected:
- The result must show whether the current confirmation was advanced and whether a result dialog was observed.
- If the operator stops before confirmation for safety reasons, record that explicitly and leave the step intentionally unclosed.

### Task 5: Fill the acceptance record and decide closure

**Files:**
- Update: `docs/superpowers/plans/2026-04-30-tdx-real-machine-validation-closure.md`

- [ ] **Step 1: Copy the template below into the operator notes or the final validation report**

```markdown
# Real-Machine Validation Record

Date:
Operator:
Machine:
Native Windows Python version:
TongDaXin client version:
PingAn client version:
HID device / firmware:
Serial port:

Test order values:
- code:
- price:
- quantity:

## A. Bridge baseline
- `tdx-bridge-health`:
- `tdx-trade-hid-ping`:

## B. PingAn window-state matrix
- foreground discovery:
- occluded discovery:
- minimized discovery:
- observed differences:

## C. TongDaXin HID progression
- dry-run preconditions:
- live probe result:
- fallback probe result:
- did the prompt `请输入证券代码!` disappear:
- did a real confirm dialog appear:

## D. PingAn split-step validation
- `trade preflight`:
- `trade submit-ready`:
- did confirm boundary appear:
- `trade confirm-current`:
- did result dialog appear:

## E. Task closure decision
- `implement-tdx-wsl-windows-bridge` task `4.4`:
- `implement-pingan-win32-trading-adapter` task `4.2`:
- `implement-pingan-win32-trading-adapter` task `6.5`:

## F. Follow-up required
- none / doc-only / code change / new OpenSpec change
- exact next action:
```

- [ ] **Step 2: Apply the closure rule consistently**

Use this rule:
- Close a task only when the JSON artifacts and observed window behavior agree.
- If the real client still shows `请输入证券代码!`, do **not** close the HID progression tasks.
- If foreground works but occluded or minimized states materially degrade recognition, do not blindly close `4.2`; close it only if the documented boundary is acceptable and explicitly recorded.

