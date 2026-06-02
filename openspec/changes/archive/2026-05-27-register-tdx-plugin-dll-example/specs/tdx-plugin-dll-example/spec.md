## ADDED Requirements

### Requirement: Curated TCalc plugin DLL example SHALL preserve the public registration ABI
The system SHALL provide a curated source-level example for the TongDaXin TCalc plugin DLL registration contract.

#### Scenario: Inspect plugin ABI reference
- **WHEN** a developer inspects the checked-in TCalc plugin example
- **THEN** the example MUST contain the `pPluginFUNC` callback typedef, `PluginTCalcFuncInfo` registration struct, exported `RegisterTdxFunc` function, and a zero-mark/null-function sentinel entry

### Requirement: Plugin DLL example SHALL exclude generated and user-local artifacts
The system SHALL keep generated Visual Studio state, user settings, caches, and large database artifacts out of the imported plugin example.

#### Scenario: Verify excluded external artifacts
- **WHEN** the plugin example is checked into the repository
- **THEN** it MUST NOT include `.sdf`, `.suo`, `.user`, build output, cache, or binary DLL artifacts from the external `D:\MyCode3\tdx\docs\TestPluginTCale` tree

### Requirement: Plugin DLL example SHALL declare a non-runtime boundary
The system SHALL document that the TCalc plugin DLL sample is reference material and not a supported runtime execution path.

#### Scenario: Read plugin boundary
- **WHEN** a developer reads the plugin/DLL reference material or the feature registry
- **THEN** the material MUST state that the current repository does not compile, deploy, load, bind, or execute native TongDaXin plugin DLLs
