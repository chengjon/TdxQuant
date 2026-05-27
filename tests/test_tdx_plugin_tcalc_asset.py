from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_DIR = ROOT / "examples" / "tdx_plugin_tcalc"


def _read(name: str) -> str:
    return (EXAMPLE_DIR / name).read_text(encoding="utf-8")


def test_tdx_tcalc_plugin_example_preserves_registration_abi() -> None:
    expected_files = {
        "README.md",
        "PluginTCalcFunc.h",
        "TCalcFuncSets.h",
        "TCalcFuncSets.cpp",
        "TestPluginTCale.cpp",
        "stdafx.cpp",
        "stdafx.h",
    }
    assert {path.name for path in EXAMPLE_DIR.iterdir() if path.is_file()} == expected_files

    plugin_header = _read("PluginTCalcFunc.h")
    sets_header = _read("TCalcFuncSets.h")
    sets_source = _read("TCalcFuncSets.cpp")
    readme = _read("README.md")
    reference_doc = (ROOT / "docs" / "tdx-plugin-dll-function-reference.md").read_text(encoding="utf-8")

    assert "typedef void (*pPluginFUNC)(int, float*, float*, float*, float*)" in plugin_header
    assert "typedef struct tagPluginTCalcFuncInfo" in plugin_header
    assert "unsigned short nFuncMark" in plugin_header
    assert "pPluginFUNC pCallFunc" in plugin_header
    assert "__declspec(dllexport) BOOL RegisterTdxFunc(PluginTCalcFuncInfo** pFun)" in sets_header
    assert "PluginTCalcFuncInfo g_CalcFuncSets[]" in sets_source
    assert "{1, (pPluginFUNC)&TestPlugin1}" in sets_source
    assert "{2, (pPluginFUNC)&TestPlugin2}" in sets_source
    assert "{0, NULL}" in sets_source
    assert "T0002/dlls/" in sets_source
    assert "not a supported TdxQuant runtime path" in readme
    assert "does not mean the repository can compile, deploy, load, bind, or execute" in readme
    assert "2024-07-15" in reference_doc
    assert "支持 `64` 位 DLL" in reference_doc
    assert "TDXDLL2(1,H,C,C)" in reference_doc
    assert "通达信DLL函数编程规范.doc" in reference_doc


def test_tdx_tcalc_plugin_example_excludes_generated_user_and_binary_artifacts() -> None:
    forbidden_patterns = (
        "*.sdf",
        "*.suo",
        "*.user",
        "*.dll",
        "*.lib",
        "*.pdb",
        "*.obj",
        "__pycache__",
    )

    for pattern in forbidden_patterns:
        assert not list(EXAMPLE_DIR.rglob(pattern)), pattern
