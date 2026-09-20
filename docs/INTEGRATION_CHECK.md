# B3 四服务接口集成检查

## 范围与方法

本记录检查仓库中的人工 JSON fixture、服务专有 Schema、公共 Job Schema 和产物引用，不代表真实服务、镜像构建、检测算法或跨组网络联调已经运行。

本次实际执行了：

- 用 PowerShell `ConvertFrom-Json` 解析仓库内 19 个 JSON 文件；全部解析成功。
- 对四个完成态响应检查八个公共字段、四种 `job_type`、六种公共状态、成功态 `error: null` 和 MD/RD findings 语义。
- 跨文件比较镜像、`producer_job_id`、`configuration_id`、依赖图/报告 URI 和 REPAIR 消费的 finding 类型。
- 尝试运行四个已有 `validate.py`；当前 Python 环境缺少 `jsonschema`，四个脚本均在导入阶段退出，因此未记为通过。

## 衔接结果

| 上游 → 下游 | 字段/产物映射 | 结果 |
| --- | --- | --- |
| DRAFT → FULL_CHECK | `output.image` → `input.environment.image`；DRAFT `job_id` → `environment.producer_job_id`；`configuration_id` 保持一致 | 通过离线值比较 |
| DRAFT → INCREMENTAL_CHECK | 同一固定镜像、生产任务和配置进入 EChecker | 通过离线值比较 |
| DRAFT → REPAIR | 同一固定镜像、生产任务和配置进入 MDFixer | 通过离线值比较 |
| FULL_CHECK → INCREMENTAL_CHECK | `ACTUAL_GRAPH.uri` → `baseline.actual_graph_uri`；`ERROR_REPORT.uri` → `baseline.error_report_uri`；基线 commit、配置和生产任务可追溯 | 通过离线值比较 |
| FULL_CHECK → REPAIR | `ERROR_REPORT.uri` → `error_report_uri` | 通过离线值比较 |
| INCREMENTAL_CHECK 输出 | 输入明确 baseline、历史图、当前 `repository.commit`、`configuration_id`；输出用 `ACTUAL_GRAPH` 产物表达更新图，用 `findings`/`resolved_findings` 表达新增/消除项 | 字段齐全 |
| REPAIR 输入约束 | `consumed_finding_ids` 均对应来源报告内 `type == MISSING` 的 finding，没有消费 `REDUNDANT` | 通过离线值比较 |
| REPAIR 输出 | `patches` + `GIT_PATCH` 产物表达 Patch，`summary` 表达修复报告，`verification.build/test/recheck` 表达构建、测试和重检 | 字段齐全 |

四个完成态响应都具有 `schema_version`、`job_id`、`trace_id`、`job_type`、`status`、`input`、`output`、`error`。创建请求遵循生命周期边界：提交时尚无服务端生成的 `job_id` 和 `status`；HTTP 202 受理结果由公共 Schema 的 `jobAccepted` 表达。

## 已确认的语义

- FULL_CHECK 示例在包含 MISSING 和 REDUNDANT findings 时仍为 `SUCCEEDED` 且 `error: null`，符合“检测发现不是系统失败”。
- `ERROR_REPORT` 是现有业务产物类型名，内容是 findings；它不是 `job.error`。
- REPAIR 的专有文档、Schema 和样例都限定为 Missing Dependency 修复；当前样例没有消费 RD。
- 服务专有字段均保留在 `input`/`output` 中，本次没有重写 A1、A2、B1、B2 的接口文件。

## 发现的差异

这些差异未妨碍现有离线分支样例，但不应由 B3 单方面改名或选择策略：

1. EChecker 示例使用 `trace_id: g16-example-flow-002`，DRAFT、FULL_CHECK 和 REPAIR 使用 `g16-example-flow-001`。这可能表示增量检查是新链路，也可能破坏预期的端到端 trace 连续性。
2. 当前 fixture 展示的是两个分支：FULL_CHECK → EChecker，以及 FULL_CHECK → MDFixer；MDFixer 仍消费 FULL_CHECK 的原提交报告，没有直接消费 EChecker 的新提交报告。因此“DRAFT → BuildChecker → EChecker → MDFixer”尚无单条线性 fixture。
3. EChecker 同时保留 `input.base_commit` 和 `input.baseline.commit`。A2 已决定值不一致时只告警，并以产物归属信息为准；最终跨组策略仍需确认。
4. DRAFT/MDFixer 使用 `build.command` + `verify_command`，BuildChecker/EChecker 使用 `clean_command` + `command`。字段属于各服务专有输入，现有样例无需机械统一，但编排方需要明确转换规则。
5. 离线产物使用 `repo://`。EChecker 接受通用非空 URI，而 DRAFT/MDFixer 专有 Schema 对样例产物使用更窄的 `repo://` 约束；生产 URI scheme 尚未确定。

## 需要 A/B 两组确认的问题

- 增量检查是否必须沿用前序 DRAFT/FULL_CHECK 的 `trace_id`？
- 线性流程中的 MDFixer 应消费 FULL_CHECK 报告，还是最新 INCREMENTAL_CHECK 报告？若两者都支持，如何标识选择规则？
- `base_commit` 与 `baseline.commit` 不一致时，最终是拒绝、告警，还是明确某一字段优先？
- 编排层如何把两套 build 字段映射为一致的“清理、构建、验证”步骤？
- 生产环境允许哪些 artifact URI scheme，如何鉴权和校验完整性？
- DRAFT 因源码本身无法构建时应 `FAILED`，还是输出结构化结果交给 BuildChecker 继续诊断？
