## MODIFIED Requirements

### Requirement: Command catalog trade plan summary SHALL expose non-execution trade input boundaries

The command catalog plan and preview summary views SHALL expose non-executing trade boundaries for supported trading task entries without dispatching the underlying task, trade, report, or bundle execution.

#### Scenario: PingAn task buy preview exposes order input boundary

- **WHEN** a maintainer runs `catalog preview --entry task-buy --view summary`
- **THEN** the result MUST include `trade_plan_boundary.trade_command` set to `trade-buy`
- **AND** `execution_mode` MUST be `non_executing_catalog_plan`
- **AND** `dispatch_executed` MUST be `false`
- **AND** required/provided/missing input fields and input coverage counts MUST be derived without executing the task.

#### Scenario: PingAn task confirm-current preview exposes confirmation boundary

- **WHEN** a maintainer runs `catalog preview --entry task-confirm-current --view summary`
- **THEN** the result MUST include `trade_plan_boundary.trade_command` set to `trade-confirm-current`
- **AND** `input_kind` MUST be `confirmation`
- **AND** `execution_mode` MUST be `non_executing_catalog_plan`
- **AND** `dispatch_executed` MUST be `false`
- **AND** the boundary MUST NOT require order input fields.
