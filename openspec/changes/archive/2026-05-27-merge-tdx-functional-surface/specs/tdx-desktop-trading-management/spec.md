## ADDED Requirements

### Requirement: Desktop trading management SHALL distinguish broker validation boundaries

The desktop trading management layer SHALL distinguish PingAn validated desktop execution from TongDaXin trading probe boundaries when adopting external merge evidence.

#### Scenario: PingAn mixed-chain buy loop is accepted
- **WHEN** PingAn validation evidence from the external `tdx` tree is adopted
- **THEN** desktop trading documentation and registry entries MUST state that the accepted execution path uses UIA field entry, HID first confirmation trigger, Win32 confirmation command, and HID result close
- **AND** the accepted boundary MUST include the requirement that the desktop returns to a next-order-ready state before continued operation

#### Scenario: PingAn execution is not represented as pure nonphysical Win32 submission
- **WHEN** documentation describes the accepted PingAn execution path
- **THEN** it MUST NOT claim that pure Win32 or pure UIA message submission alone completed the final trading loop

#### Scenario: TongDaXin trading evidence remains separate
- **WHEN** documentation describes TongDaXin trading bridge behavior
- **THEN** it MUST NOT inherit PingAn execution status
- **AND** it MUST retain its own evidenced boundary

### Requirement: Desktop trading management SHALL preserve current trade governance during merge

The merge SHALL preserve existing desktop trade safety, ledger, audit, and compatibility-governance behavior while adopting external `tdx` evidence.

#### Scenario: Merge updates docs or registry
- **WHEN** implementation updates desktop trading documentation or registry status
- **THEN** existing stable trade manager, trade service, submission ledger, and trade audit behavior MUST remain unchanged unless an explicit implementation task modifies them

#### Scenario: Focused trade verification runs
- **WHEN** desktop trading merge changes are applied
- **THEN** focused verification MUST include existing PingAn trade manager or gateway tests where local execution does not require a live client
