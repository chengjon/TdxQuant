## 1. Curated Assets

- [x] 1.1 Add `examples/tdx_plugin_tcalc/` with source-level TCalc plugin ABI sample files and a README.
- [x] 1.2 Add `docs/tdx-plugin-dll-function-reference.md` explaining imported files, excluded files, and runtime boundary.

## 2. Registry And Merge Notes

- [x] 2.1 Update `FUNCTION_TREE.md` to register the plugin/DLL sample as a bounded documentation/example asset.
- [x] 2.2 Update `docs/TdxQuant_tdx_functional_surface_merge.md` to mark the deferred plugin/DLL item as handled by this separate change.

## 3. Verification

- [x] 3.1 Add a focused asset test for the TCalc plugin ABI signatures and excluded generated/user artifacts.
- [x] 3.2 Run OpenSpec validation, the focused asset test, the function-tree registry validator, and diff checks.
