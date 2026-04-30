## Why

TdxQuant 已经完成同步 provider result contract，但上层系统在真正调用能力之前，仍然缺少标准化的 capability 清单、运行时健康探测和可执行的诊断建议。现在需要把 `capabilities / health / doctor` 做成稳定的 provider-facing contract，这样 `mystocks`、`quantix-rust` 和后续 sidecar/bridge 才能在调用前完成 preflight、能力分级和错误分流。

## What Changes

- Introduce a provider-facing capability discovery contract that lists exposed TdxQuant capabilities with stable naming, version, stability grade, side-effect grade, and entrypoint metadata.
- Add standardized provider health and doctor probes for platform, `tqcenter`, query runtime, subscription runtime, desktop window probing, and HID availability.
- Expose the new discovery contract through `TdxApiManager.runtime` and through dedicated CLI entrypoints: nested `api capabilities|health|doctor` plus flat `tdx-capabilities|tdx-health|tdx-doctor`.
- Reuse the canonical provider result envelope for discovery-style synchronous responses so upstream callers can consume them with the same machine-readable top-level contract.
- Keep existing low-level diagnostics such as `tdx-bridge-health` available, but do not treat them as the formal provider contract for upstream systems.

## Capabilities

### New Capabilities
- `tdx-provider-capability-discovery`: Provider-facing capability registry, health probes, doctor findings, grading metadata, and discovery-oriented synchronous JSON responses.

### Modified Capabilities
- `tdx-api-management`: Add provider discovery actions under `TdxApiManager.runtime` without collapsing runtime and provider-boundary concerns into unrelated domains.
- `tdx-api-cli-entry`: Add nested `api` and flat CLI entrypoints for capability discovery, health, and doctor responses.
- `tdx-provider-result-contract`: Extend the canonical synchronous provider result envelope to cover provider discovery style responses in addition to query/formula outputs.

## Impact

- Affected code:
  - provider discovery metadata/helpers
  - `tdxquant/api/bridge.py`
  - `tdxquant/api/runtime.py`
  - `tdxquant/api/manager.py`
  - `tdxquant/cli.py`
- Affected tests:
  - bridge/runtime probe tests
  - manager discovery result tests
  - CLI parser, dispatch, and provider envelope tests
- Affected docs:
  - provider contract documentation
  - next-step roadmap / integration guidance references
- Out of scope for this package:
  - HTTP service surface
  - subscription JSONL event contract
  - formula-specific payload schema
  - task/report/catalog output unification
  - desktop trading promotion to provider mainline
