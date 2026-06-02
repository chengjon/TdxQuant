# tdx-trading-hid-bridge Specification

## Purpose

定义 TongDaXin HID 交易桥接基线能力，包括买页探测、前台校验、HID 辅助买入探针和低风险验证模式。
## Requirements
### Requirement: Trading bridge SHALL probe TongDaXin buy-page prerequisites
The system SHALL expose a bridge command that detects whether the TongDaXin buy page, code input, price input, quantity input, and submit button are available before any trading automation attempt.

#### Scenario: Probe TongDaXin buy page
- **WHEN** a caller invokes the trading probe on a visible TongDaXin client
- **THEN** the bridge returns the detected control handles, evidence, and warnings in structured JSON

#### Scenario: Probe fails because the buy page is not available
- **WHEN** the TongDaXin client is not on the expected buy page
- **THEN** the bridge returns a structured control-not-found result with next action guidance

### Requirement: Trading bridge SHALL validate foreground and focus before HID input
The system SHALL refuse HID code input unless the TongDaXin main window is foregrounded and the expected code input control has focus.

#### Scenario: Focus validation succeeds
- **WHEN** the TongDaXin main window is foreground and the code edit control owns focus
- **THEN** the bridge allows the HID input sequence to continue

#### Scenario: Focus validation fails
- **WHEN** the TongDaXin main window is not foreground or the code edit control does not own focus
- **THEN** the bridge aborts the HID input attempt and returns next action guidance

### Requirement: Trading bridge SHALL support HID-assisted buy probing
The system SHALL expose a buy-probe command that uses HID for stock code input and Win32/UIA for price entry, quantity entry, submit triggering, and dialog capture.

#### Scenario: HID-assisted buy probe runs in dry-run mode
- **WHEN** a caller invokes the HID-assisted buy probe with `dry-run`
- **THEN** the bridge performs prerequisite validation without sending HID keystrokes or submitting an order

#### Scenario: HID-assisted buy probe runs with live HID input
- **WHEN** a caller invokes the HID-assisted buy probe with valid port, symbol, price, and quantity parameters
- **THEN** the bridge sends the configured HID code input sequence, fills price and quantity, triggers submit, and captures the resulting dialog state

### Requirement: Trading bridge SHALL preserve low-risk verification mode
The system SHALL support low-risk verification workflows in which operators use intentionally non-fillable prices to validate the buy chain without immediate execution risk.

#### Scenario: Operator uses non-fillable test price
- **WHEN** a caller invokes a buy probe with a deliberately non-fillable price
- **THEN** the bridge executes the probe without assuming the order should be matched immediately

#### Scenario: Bridge captures post-submit prompt
- **WHEN** a buy probe reaches a post-submit prompt or confirmation dialog
- **THEN** the bridge returns the captured prompt text and available actions in structured JSON

### Requirement: TongDaXin HID trading bridge SHALL remain probe-scoped until business input acceptance is evidenced

The TongDaXin HID trading bridge SHALL be represented as a probe and diagnostic capability unless evidence shows that the TongDaXin trading business layer accepts the automated security-code input chain.

#### Scenario: TongDaXin bridge can fill and trigger controls
- **WHEN** TongDaXin bridge evidence shows code, price, quantity, submit control discovery, field write/read, or post-submit prompt capture
- **THEN** the capability MAY be registered as probing, prerequisite validation, or diagnostic automation
- **AND** it MUST NOT be registered as full order submission solely from those control-level observations

#### Scenario: Security-code business acceptance is missing
- **WHEN** TongDaXin evidence still produces a prompt equivalent to missing security code after automated input
- **THEN** the capability MUST remain unavailable for full live order submission
- **AND** operator-facing documentation MUST name security-code business-layer acceptance as the blocker

#### Scenario: Future evidence resolves the blocker
- **WHEN** future validation proves that TongDaXin accepts automated security-code input and completes the confirmation/result loop
- **THEN** a separate OpenSpec change MUST update the capability boundary before documentation claims full live TongDaXin order submission
