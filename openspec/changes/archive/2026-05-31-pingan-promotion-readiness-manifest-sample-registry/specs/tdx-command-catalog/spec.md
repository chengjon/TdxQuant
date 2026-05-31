## ADDED Requirements

### Requirement: Command catalog SHALL expose the PingAn readiness manifest sample as a non-executing task entry

The command catalog SHALL register the PingAn readiness manifest sample preset so maintainers can discover and inspect it without running the underlying task.

#### Scenario: Catalog list discovers the sample manifest entry by label

- **GIVEN** the command catalog contains a task entry named `plan-pingan-promotion-readiness`
- **WHEN** a maintainer runs `catalog list --kind entry --label readiness`
- **THEN** the resulting entries SHALL include `plan-pingan-promotion-readiness`
- **AND** the entry SHALL expose labels for `task`, `pingan`, `readiness`, `manifest`, and `readonly`.

#### Scenario: Catalog plan resolves the sample manifest entry without execution

- **GIVEN** the command catalog contains `plan-pingan-promotion-readiness`
- **WHEN** a maintainer runs `catalog plan --entry plan-pingan-promotion-readiness`
- **THEN** the result SHALL identify source `task`
- **AND** the dispatch summary SHALL identify command group `task`
- **AND** the dispatch summary SHALL identify command name `pingan-promotion-readiness-rollup`
- **AND** the resolved arguments SHALL include the sample manifest path
- **AND** the constraints SHALL report `execution_mode` as `non_executing`
- **AND** the constraints SHALL report `dispatch_executed` as `false`.
