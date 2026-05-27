# 通达信 TCalc 插件 DLL 示例边界

本文记录从外部 `D:\MyCode3\tdx\docs\TestPluginTCale` 采纳到当前仓库的通达信 TCalc 插件 DLL 示例材料。

## 采纳内容

当前仓库只纳入可审查的源码级示例：

- `examples/tdx_plugin_tcalc/PluginTCalcFunc.h`
- `examples/tdx_plugin_tcalc/TCalcFuncSets.h`
- `examples/tdx_plugin_tcalc/TCalcFuncSets.cpp`
- `examples/tdx_plugin_tcalc/TestPluginTCale.cpp`
- `examples/tdx_plugin_tcalc/stdafx.h`
- `examples/tdx_plugin_tcalc/stdafx.cpp`

核心接口形状如下：

- `pPluginFUNC`：插件函数指针，形如 `(DataLen, OUT, INa, INb, INc)`。
- `PluginTCalcFuncInfo`：以 `nFuncMark` 绑定函数编号，以 `pCallFunc` 绑定函数地址。
- `RegisterTdxFunc`：导出给 TCalc 调用的注册函数，返回 `g_CalcFuncSets`。
- `{0, NULL}`：函数表结束哨兵。

外部示例注释说明：生成的 DLL 及相关依赖 DLL 需要放到通达信安装目录 `T0002/dlls/` 下，再在公式管理器绑定。

## 排除内容

本次没有导入外部目录中的生成或本机状态文件，包括：

- `TestPluginTCale.sdf`
- `TestPluginTCale.suo`
- `TestPluginTCale.vcxproj.user`
- 编译输出、缓存和二进制 DLL

这些文件不是接口契约材料，且 `.sdf` 体积较大、`.suo/.user` 带有用户/机器状态，不适合进入当前项目。

## 当前边界

该示例只作为通达信原生插件 ABI 的参考资产。当前 TdxQuant 已有的公式能力仍以 Python/API bridge、provider contract 和 replay fixture 为主。

当前仓库不承诺：

- 编译 `TestPluginTCale` DLL。
- 部署 DLL 到真实通达信客户端。
- 自动在公式管理器绑定插件函数。
- 从 Python 或 CLI 加载、调用、执行该原生插件 DLL。
- 将该示例等同于新的公式 runtime capability。

若后续要把原生插件变成可用能力，应另拆 native plugin runtime change，并补齐 Windows 编译、部署、绑定、调用和真实客户端验证证据。
