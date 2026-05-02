# TdxQuant Provider Result Contract

本文定义 TdxQuant 当前同步 provider-facing 结果 contract 的第一版约束。

适用范围：

- `TdxApiManager` 驱动的查询与公式类同步结果
- `TdxApiManager.runtime` 驱动的 `capabilities / health / doctor` 同步结果
- `tdxquant api ...` 的 JSON 输出
- 平铺 query / formula / discovery bridge 命令的 JSON 输出

暂不适用：

- `subscription-watch` 或其他长时 JSONL 事件流
- `task / report / catalog` 全部输出
- `desktop trade` 输出协议

## 1. Compatibility Policy

这轮 contract hardening 采用 **兼容优先**，不是立即把旧字段硬切掉。

旧输出以：

- `ok`
- `code`
- `message`
- `data`
- `warnings`
- `next_action`

为主。

当前 canonical 输出改为 provider-facing envelope：

- `success`
- `ok`
- `code`
- `message`
- `capability`
- `capability_version`
- `schema_version`
- `request_id`
- `started_at`
- `finished_at`
- `elapsed_ms`
- `runtime`
- `warnings`
- `data`
- `artifacts`

其中：

- `success` 是当前 canonical 布尔字段
- `ok` 当前保留一个兼容版本周期，并且必须与 `success` 完全一致
- `next_action` 如存在，当前保留在 `data.next_action`
- 失败路径也必须返回同样的 JSON envelope
- CLI 失败时仍应返回非零退出码，但 JSON envelope 不应切换形态

## 2. Canonical Envelope

当前建议的同步 JSON envelope 形态如下：

```json
{
  "success": true,
  "ok": true,
  "code": "ok",
  "message": "optional human summary",
  "capability": "formula.screen",
  "capability_version": "v1",
  "schema_version": "2026-04-28",
  "request_id": "optional-request-id",
  "started_at": "2026-04-28T12:00:00Z",
  "finished_at": "2026-04-28T12:00:01Z",
  "elapsed_ms": 1042.0,
  "runtime": {
    "provider": "tdxquant",
    "provider_version": "dev",
    "mode": "cli"
  },
  "warnings": [],
  "data": {},
  "artifacts": []
}
```

## 3. Field Rules

- 时间字段使用 `RFC3339`
- symbol 使用字符串表达
- 枚举使用固定字面值，不使用自由文本
- `success` 是 canonical 顶层成功字段
- `ok` 是 `success` 的兼容别名，值必须完全一致
- `warnings` 始终为数组
- `artifacts` 始终为数组
- `data` 始终为对象
- `elapsed_ms` 始终为 JSON 数值
- capability-specific payload 放在 `data`
- CLI provider 失败仍使用同样 envelope，只通过非零退出码表达 shell 层失败语义

## 4. Current Scope

第一版 contract 先解决公共 envelope，不一次性定义全部 capability-specific `data` schema。

当前已经纳入：

- query / formula 同步返回
- provider discovery / health / doctor 同步返回

`capabilities / health / doctor` 的 capability-specific `data` schema 说明，见：

- [TdxQuant_Provider_Capability_Discovery.md](/opt/iflow/TdxQuant/docs/TdxQuant_Provider_Capability_Discovery.md)

当前已经单独落文档的 capability-specific contract：

- [TdxQuant_Provider_Formula_Screen_Contract.md](/opt/iflow/TdxQuant/docs/TdxQuant_Provider_Formula_Screen_Contract.md)
- [TdxQuant_Provider_Block_Mutation_Safety.md](/opt/iflow/TdxQuant/docs/TdxQuant_Provider_Block_Mutation_Safety.md)
- [TdxQuant_Provider_Subscription_Event_Contract.md](/opt/iflow/TdxQuant/docs/TdxQuant_Provider_Subscription_Event_Contract.md)
- [TdxQuant_Provider_Replay_Fixtures.md](/opt/iflow/TdxQuant/docs/TdxQuant_Provider_Replay_Fixtures.md)

下一步优先继续补：

- 更高一层的 fake provider / live replay mode
