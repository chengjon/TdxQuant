## Why

The external `D:\MyCode3\tdx` tree contains a small TongDaXin TCalc DLL plugin sample under `docs\TestPluginTCale`, and the previous merge explicitly deferred plugin/DLL material into a separate change. Bringing the curated sample into this repository preserves the useful ABI reference without importing generated Visual Studio state or claiming runtime plugin support.

## What Changes

- Add a curated `examples/tdx_plugin_tcalc/` sample that documents the TCalc plugin function registration shape.
- Add a short reference document explaining what was imported, what was excluded, and how it relates to the current formula bridge.
- Update the single feature registry and merge summary so plugin/DLL support remains clearly bounded as documentation/example material only.
- Add a focused test that verifies the imported sample keeps the expected ABI signatures and excludes generated/user files.

## Capabilities

### New Capabilities
- `tdx-plugin-dll-example`: Documents and verifies the curated TongDaXin TCalc DLL plugin sample asset boundary.

### Modified Capabilities
- `tdx-functional-surface-merge`: Mark the previously deferred `TestPluginTCale` plugin/DLL documentation item as handled by a separate bounded asset change.

## Impact

- Affected docs/assets: `docs/tdx-plugin-dll-function-reference.md`, `examples/tdx_plugin_tcalc/`, `FUNCTION_TREE.md`, `docs/TdxQuant_tdx_functional_surface_merge.md`.
- Affected tests: new focused asset test only.
- No runtime API, CLI command, DLL compilation, TongDaXin client deployment, or trading behavior changes.
