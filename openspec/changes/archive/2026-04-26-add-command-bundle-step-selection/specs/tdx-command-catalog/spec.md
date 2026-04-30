## MODIFIED Requirements

### Requirement: Command catalog CLI SHALL support named multi-step bundles composed from existing catalog entries
The system SHALL allow callers to define a named bundle that references multiple existing catalog entries and executes them sequentially through the existing single-entry dispatch path.

#### Scenario: Caller lists available catalog bundles
- **WHEN** a caller executes the catalog listing command for bundles
- **THEN** the system MUST return the available bundle names together with their resolved step metadata

#### Scenario: Caller runs a catalog bundle
- **WHEN** a caller executes a named catalog bundle
- **THEN** the system MUST execute each referenced step through the existing catalog entry dispatch path rather than a duplicated workflow

#### Scenario: Explicit CLI arguments override bundle step defaults
- **WHEN** a caller executes a named catalog bundle and also provides overlapping CLI arguments explicitly
- **THEN** the system MUST prefer the explicit CLI argument values over the bundle step default options

#### Scenario: Bundle step references an unsupported catalog entry
- **WHEN** a bundle step references a catalog entry that does not exist or does not resolve
- **THEN** the system MUST reject the request with an invalid-request style error instead of dispatching an unknown workflow

#### Scenario: Bundle execution stops after a failed step
- **WHEN** a bundle step returns a failure result
- **THEN** the system MUST stop executing subsequent steps and return bundle metadata that identifies the failed step

#### Scenario: Caller runs only a selected bundle step
- **WHEN** a caller executes a named catalog bundle with `only-step`
- **THEN** the system MUST execute only the selected step and skip all other bundle steps

#### Scenario: Caller runs a bundle step range
- **WHEN** a caller executes a named catalog bundle with `from-step` and/or `to-step`
- **THEN** the system MUST execute only the selected contiguous step range in bundle order

#### Scenario: Caller requests an unknown or invalid bundle step range
- **WHEN** a caller provides an unknown step name or an invalid range where the resolved start step is after the resolved end step
- **THEN** the system MUST reject the request with an invalid-request style error instead of executing any bundle steps
