# Stable Snapshots

## 1. 目的

这个目录用于保存每一次已经实机验证通过的稳定版本快照。

每个快照都应满足两个目标：

- 可以直接回退代码
- 可以快速看懂该稳定版的能力边界、有效优化和已撤回实验

## 2. 命名规则

目录名统一使用：

- `<日期>-<主题>-stable-vN`

例如：

- `2026-04-25-pingan-buy-fast-stable-v1`

## 3. 每个快照的最小内容

每个稳定快照目录内至少包含：

- `README.md`
- `code/tdxquant/cli.py`
- `code/tdxquant/uia_inspector.py`
- `code/tests/test_runtime.py`

如果某次稳定版本还依赖其他关键文件，也要一起复制进去。

## 4. README 应记录的内容

每个快照说明文档至少写清：

- 版本用途
- 当前稳定版本定义
- 保留的有效优化
- 撤回的实验
- 本次稳定实测基线
- 回退建议

## 5. 当前已保存快照

### 2026-04-25-pingan-buy-fast-stable-v1

- 主题：`pingan-buy` 快速路径稳定基线
- 状态：已实机验证
- 关键特征：
  - 保留 `hybrid_win32`
  - 保留 `focus_quantity_input` 缓存复用
  - 撤回确认框/结果窗 UIA 顶层直查实验
- 参考文档：
  - `2026-04-25-pingan-buy-fast-stable-v1/README.md`

### 2026-04-25-pingan-buy-fast-stable-v2

- 主题：`pingan-buy` 快速路径极速稳定基线
- 状态：已实机验证
- 关键特征：
  - 保留 `hybrid_win32`
  - 保留 `focus_quantity_input` 缓存复用
  - 新增 `dialog_lookup_mode=win32_experimental`
  - 使用 Win32 顶层窗口枚举替代确认框/结果窗查找
- 当前基线：
  - 总耗时约 `12.41s`
  - 合同号 `0361808002`
- 参考文档：
  - `2026-04-25-pingan-buy-fast-stable-v2/README.md`

## 6. 更新流程

以后每次确认新的稳定版本时，按下面顺序执行：

1. 新建快照目录
2. 复制当前稳定代码
3. 编写该版本 `README.md`
4. 同步到运行目录
5. 在本索引中追加一条记录

## 7. 回退原则

如果后续实验导致下面任一问题：

- 下单链路不再稳定
- 确认框无法自动推进
- 结果窗无法自动关闭
- 合同号提取失败
- 总耗时明显回升

优先从最近一个稳定快照回退，而不是在实验代码上继续叠补丁。
