# tdx-function-tree-registry Specification

## ADDED Requirements

### Requirement: FUNCTION_TREE SHALL register managed lifecycle module evidence

`FUNCTION_TREE.md` SHALL register shared managed-process lifecycle module evidence for the implemented lifecycle governance node without changing feature status.

#### Scenario: B-16 cites shared managed lifecycle evidence

- **WHEN** provider replay and subscription watch background lifecycle diagnostics use `tdxquant.managed_lifecycle`
- **THEN** B-16 MUST cite the shared module, focused tests, architecture review, and this OpenSpec change as evidence
- **AND** the boundary MUST state that shared lifecycle provenance is diagnostic/refactoring evidence only and does not by itself start, stop, restart, supervise, or control PingAn trading processes.
