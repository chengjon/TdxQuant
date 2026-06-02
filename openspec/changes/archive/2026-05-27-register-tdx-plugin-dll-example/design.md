## Context

The external `D:\MyCode3\tdx\docs\TestPluginTCale` sample is a small Visual Studio-era TongDaXin TCalc DLL plugin example. The prior functional-surface merge chose not to bulk import `docs/TestPluginTCale/*` and explicitly called out plugin/DLL material as a separate change. The current repository already has Python formula bridge APIs and provider contracts, but it does not compile, deploy, or load native TongDaXin plugin DLLs.

## Goals / Non-Goals

**Goals:**
- Preserve the useful TCalc plugin ABI shape as a curated text example.
- Document the exact boundary between formula bridge runtime support and native plugin/DLL reference material.
- Verify the checked-in sample contains the expected registration contract and excludes generated/user Visual Studio files.

**Non-Goals:**
- Compile a DLL, add MSBuild/Visual Studio project support, or add native CI.
- Deploy files into a TongDaXin installation or automate formula-manager binding.
- Add a Python wrapper that loads the plugin DLL or extend the current formula execution surface.

## Decisions

1. Import only source-level sample material plus a local README.

   The sample value is the ABI: `pPluginFUNC`, `PluginTCalcFuncInfo`, exported `RegisterTdxFunc`, and the `{0,NULL}` terminator. Source files are small and reviewable. Generated/user files such as `.sdf`, `.suo`, `.user`, build outputs, and caches are excluded because they are noisy, local-stateful, or too large for evidence.

2. Treat the imported sample as documentation/example evidence, not runtime capability.

   The feature registry will use a bounded status for plugin/DLL execution. This prevents the presence of a C++ sample from being read as proof that TdxQuant can compile, load, or bind native TongDaXin plugin DLLs.

3. Add a focused asset test instead of a compile test.

   The repository does not currently carry a native Windows build pipeline, and the sample targets TongDaXin/Visual Studio deployment. A text-level test is sufficient to protect the contract that this change actually imports: ABI signatures, exported registration function, sentinel terminator, deployment note, and excluded generated files.

## Risks / Trade-offs

- [Risk] Readers may confuse a checked-in C++ sample with supported plugin execution. → Mitigate with explicit README, docs, FUNCTION_TREE boundary, and spec wording.
- [Risk] The historical sample may not build unchanged in every modern Visual Studio environment. → Mitigate by not making build success a project contract and documenting the sample as ABI reference material.
- [Risk] Future plugin work could drift from this sample. → Mitigate by using OpenSpec capability names and a test that keeps the reference contract discoverable.
