## ADDED Requirements

### Requirement: FUNCTION_TREE SHALL register PingAn manual acceptance recorder without status promotion

`FUNCTION_TREE.md` SHALL record the PingAn live/manual acceptance recorder as D-07/D-08 partial implementation evidence while keeping both nodes `[部分实现]`.

#### Scenario: Recorder is registered as controlled manual evidence capture

- **WHEN** `FUNCTION_TREE.md` describes D-07 and D-08
- **THEN** both rows SHALL mention `pingan-live-manual-acceptance-recorder`
- **AND** both rows SHALL mention `task pingan-live-manual-acceptance`
- **AND** both rows SHALL mention `tdx.desktop_trade.pingan_live_manual_acceptance.v1`
- **AND** both rows SHALL keep status `[部分实现]`
- **AND** both rows SHALL state that this recorder does not execute PingAn workflows, does not prove production readiness, and does not prove implemented status.

