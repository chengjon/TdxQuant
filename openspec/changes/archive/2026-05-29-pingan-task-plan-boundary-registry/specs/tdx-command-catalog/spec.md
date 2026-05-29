## MODIFIED Requirements

### Requirement: Command catalog trade plan summary SHALL expose non-execution trade input boundaries

The command catalog plan summary view SHALL expose a non-executing trade boundary for supported trading task entries without dispatching the underlying task, trade, report, or bundle execution.

#### Scenario: PingAn task buy plan exposes order input boundary

- **WHEN** a maintainer runs `catalog plan --entry task-buy --view summary`
- **THEN** the result MUST include `trade_plan_boundary.trade_command` set to `trade-buy`
- **AND** `execution_mode` MUST be `non_executing_catalog_plan`
- **AND** `dispatch_executed` MUST be `false`
- **AND** required/provided/missing input fields and input coverage counts MUST be derived without executing the task.

#### Scenario: PingAn task confirm-current plan exposes confirmation boundary

- **WHEN** a maintainer runs `catalog plan --entry task-confirm-current --view summary`
- **THEN** the result MUST include `trade_plan_boundary.trade_command` set to `trade-confirm-current`
- **AND** `input_kind` MUST be `confirmation`
- **AND** `execution_mode` MUST be `non_executing_catalog_plan`
- **AND** `dispatch_executed` MUST be `false`
- **AND** the boundary MUST NOT require order input fields.
