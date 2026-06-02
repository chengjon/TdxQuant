# 通达信 TCalc 插件 DLL 示例边界

本文记录从外部 `D:\MyCode3\tdx\docs\TestPluginTCale` 采纳到当前仓库的通达信 TCalc 插件 DLL 示例材料。

外部同时存在二进制 Word 文档 `D:\MyCode3\tdx\docs\通达信DLL函数编程规范.doc`。该文档没有作为 `.doc` 原文件导入；本文仅摘录其中可交叉核对的接口和使用边界。

## 外部规范摘要

`通达信DLL函数编程规范.doc` 的可抽取要点如下：

- 文档版本记录包含 `1.00 / 2014-05-23` 与 `2.00 / 2024-07-15`。
- `2.00` 版本说明支持 `64` 位 DLL。
- 用户可自行编写公式函数 DLL 并载入通达信客户端，但用户 DLL 必须遵循通达信接口规范。
- 规范要求参考示范程序 `TestPluginTCale`。
- 通达信提供 `PluginTCalcFunc.h` 头文件，用于注册 DLL 函数基本信息。
- 注册函数名称为 `RegisterTdxFunc`，具体实现可参考 `TCalcFuncSets.cpp`。
- 插件函数的参数含义为 `(数据个数, 输出, 输入a, 输入b, 输入c)`，计算基于长度为 `DataLen` 的 `float` 数组。
- 用户函数应放入 `PluginTCalcFuncInfo` 全局数组 `g_CalcFuncSets`。
- 生成的 DLL 及相关依赖 DLL 需要复制到主程序 `T0002\dlls` 目录。
- 客户端进入后可用 `Ctrl+F` 打开公式管理器并绑定 DLL 函数。
- 公式侧示例 `TDXDLL2(1,H,C,C)` 表示调用第二号 DLL 中标记为 `1` 的函数；第一个参数用于标记调用 DLL 中的哪个函数。

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

本次没有导入外部目录中的生成、本机状态或二进制文档文件，包括：

- `TestPluginTCale.sdf`
- `TestPluginTCale.suo`
- `TestPluginTCale.vcxproj.user`
- `通达信DLL函数编程规范.doc`
- 编译输出、缓存和二进制 DLL

这些文件不是当前仓库需要执行的接口契约材料，且 `.sdf` 体积较大、`.suo/.user` 带有用户/机器状态、`.doc` 是旧式二进制 Word 格式，不适合直接进入当前项目。

## 当前边界

该示例只作为通达信原生插件 ABI 的参考资产。当前 TdxQuant 已有的公式能力仍以 Python/API bridge、provider contract 和 replay fixture 为主。

当前仓库不承诺：

- 编译 `TestPluginTCale` DLL。
- 部署 DLL 到真实通达信客户端。
- 自动在公式管理器绑定插件函数。
- 从 Python 或 CLI 加载、调用、执行该原生插件 DLL。
- 将该示例等同于新的公式 runtime capability。

若后续要把原生插件变成可用能力，应另拆 native plugin runtime change，并补齐 Windows 编译、部署、绑定、调用和真实客户端验证证据。
