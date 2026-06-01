## ADDED Requirements

### Requirement: PingAn implemented-status transition writer SHALL require eligible gate and explicit confirmation

`TdxTaskManager.pingan_implemented_status_transition(...)` SHALL transition D-07/D-08 FUNCTION_TREE rows only when an eligible transition gate, explicit confirmation, and apply mode are provided.

#### Scenario: Dry-run returns transition plan without writing files

- **GIVEN** a transition gate artifact uses schema `tdx.desktop_trade.pingan_implemented_status_transition_gate.v1`
- **AND** the gate has `eligible_for_status_transition_review=true`
- **AND** D-07 and D-08 currently have status `[部分实现]` in the caller-provided FUNCTION_TREE path
- **WHEN** the task runs with `dry_run=true`
- **THEN** it SHALL return `implemented_status_transition_plan`
- **AND** the plan SHALL list D-07 and D-08 with from status `[部分实现]` and to status `[已实现]`
- **AND** it SHALL NOT write the function tree file
- **AND** it SHALL NOT write the transition record artifact.

#### Scenario: Apply mode updates function tree and writes transition record

- **GIVEN** the gate is eligible
- **AND** the caller provides `apply=true`, `dry_run=false`, and `confirm_transition=true`
- **WHEN** the task executes the transition
- **THEN** it SHALL update D-07 and D-08 status cells from `[部分实现]` to `[已实现]` in the caller-provided function tree file
- **AND** it SHALL write a transition record artifact with schema `tdx.desktop_trade.pingan_implemented_status_transition_record.v1`
- **AND** the record SHALL include operator, reason, transition gate path, target nodes, before/after statuses, and `function_tree_status_transition_executed=true`
- **AND** the record SHALL include `order_submitted=false`, `control_dispatch_executed=false`, and `execution_mode=function_tree_status_transition`.

#### Scenario: Blocked gate prevents transition

- **GIVEN** the transition gate has `eligible_for_status_transition_review=false`
- **WHEN** the task evaluates the transition request
- **THEN** it SHALL return `ErrorCode.INVALID_REQUEST`
- **AND** it SHALL include the gate blocked reasons
- **AND** it SHALL NOT modify FUNCTION_TREE
- **AND** it SHALL NOT write a transition record artifact.

#### Scenario: Missing confirmation prevents transition

- **GIVEN** the transition gate is eligible
- **WHEN** the task runs with `apply=true` but `confirm_transition=false`
- **THEN** it SHALL return `ErrorCode.INVALID_REQUEST`
- **AND** it SHALL NOT modify FUNCTION_TREE
- **AND** it SHALL NOT write a transition record artifact.

#### Scenario: Writer remains non-trading

- **WHEN** the writer returns transition metadata
- **THEN** the metadata SHALL state that it does not execute PingAn workflows, submit orders, control the desktop, or prove production readiness by itself.
