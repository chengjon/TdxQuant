## MODIFIED Requirements

### Requirement: Command catalog trade plan summary SHALL expose non-execution trade input boundaries

The command catalog plan and preview summary views SHALL expose non-executing trade boundaries for supported trading task entries without dispatching the underlying task, trade, report, or bundle execution.

#### Scenario: Submit-once buy task plan and preview expose buy side boundary

- **WHEN** a maintainer runs `catalog plan --entry task-buy-submit-once --view summary` or `catalog preview --entry task-buy-submit-once --view summary`
- **THEN** the result MUST include `trade_plan_boundary.trade_command` set to `trade-submit-once`
- **AND** `trade_plan_boundary.side` MUST be `buy`
- **AND** `execution_mode` MUST be `non_executing_catalog_plan`
- **AND** `dispatch_executed` MUST be `false`
- **AND** input coverage MUST be derived without executing the task.

#### Scenario: Submit-once sell task plan and preview expose sell side boundary

- **WHEN** a maintainer runs `catalog plan --entry task-sell-submit-once --view summary` or `catalog preview --entry task-sell-submit-once --view summary`
- **THEN** the result MUST include `trade_plan_boundary.trade_command` set to `trade-submit-once`
- **AND** `trade_plan_boundary.side` MUST be `sell`
- **AND** `execution_mode` MUST be `non_executing_catalog_plan`
- **AND** `dispatch_executed` MUST be `false`
- **AND** input coverage MUST be derived without executing the task.
