# TongDaXin TCalc Plugin DLL Example

This directory preserves the reviewable source-level portion of the external sample from:

`D:\MyCode3\tdx\docs\TestPluginTCale`

It is kept as ABI reference material for TongDaXin formula plugin research. It is not a supported TdxQuant runtime path.

## Included

- `PluginTCalcFunc.h`: TCalc callback typedef and `PluginTCalcFuncInfo` registration struct.
- `TCalcFuncSets.h`: exported `RegisterTdxFunc` declaration.
- `TCalcFuncSets.cpp`: two tiny sample functions and the zero-mark/null-function sentinel registration table.
- `TestPluginTCale.cpp`: minimal DLL entry point.
- `stdafx.h` / `stdafx.cpp`: minimal Windows precompiled-header stubs, with casing normalized to match the sample includes.

## Excluded

The external sample also contains Visual Studio solution/project files and generated local state. This repository intentionally excludes `.sdf`, `.suo`, `.user`, build output, cache, binary DLL, and other machine-local artifacts.

## Boundary

Current TdxQuant formula support remains the Python/API bridge and provider contract surface. This sample does not mean the repository can compile, deploy, load, bind, or execute native TongDaXin plugin DLLs.
