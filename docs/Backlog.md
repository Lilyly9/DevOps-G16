# E2 Backlog

状态说明：`已完成` 表示仓库中的离线契约、样例或文档已具备并通过本次可执行检查；不等同于真实服务实现或跨组联调完成。

| 任务 | 责任方 | 产物 | 验收条件 | 状态 |
| --- | --- | --- | --- | --- |
| 统一任务模型 | A/B 共同 | `contracts/task.schema.json` | DRAFT、FULL_CHECK、INCREMENTAL_CHECK、REPAIR 四类对象均可表达，公共字段、状态和错误语义一致 | 已完成；待两组最终确认 |
| DRAFT 接口 | B | `contracts/draft/` | 下游能理解环境、固定镜像、日志、配置和构建信息 | 已完成离线样例与校验脚本 |
| FULL_CHECK 接口 | A | `contracts/buildchecker/` | 能输出实际/声明依赖图以及 MD/RD findings | 已完成离线样例与校验脚本 |
| INCREMENTAL_CHECK 接口 | A | `contracts/echecker/` | 明确 baseline、历史图、当前 commit、configuration；baseline 缺失时请求能被 Schema 拒绝 | 已完成离线样例与校验脚本 |
| REPAIR 接口 | B | `contracts/mdfixer/` | 只消费 `MISSING` / MD，并表达 Patch、修复摘要、构建、测试和重检结果 | 已完成离线样例与校验脚本 |
| 产物访问约定 | A/B 共同 | 公共 Schema、README、ADR-002 | 下游能按 artifact reference 和 URI 读取图、报告、日志与 Patch，不绑定未确定的存储平台 | 已完成仓库内 `repo://` 约定；生产 URI scheme 待确认 |
| 接口集成检查 | B3 | `docs/INTEGRATION_CHECK.md` | DRAFT → BuildChecker → EChecker → MDFixer 的主要字段可衔接，并列出不能自行裁决的差异 | 已完成离线检查；线性端到端样例待两组确认 |
| 架构决策记录 | B3 | `docs/ADR.md` | 记录异步 Job、产物引用、系统错误与检测发现分离 | 已完成 |
| 提交材料汇总 | B3 | `README.md`、`AI_USAGE.md`、`CONTRIBUTIONS.md` | B3 工作、验证范围与待确认问题可追溯，不伪造提交 SHA | 已完成，SHA 待提交后填写 |

## 后续事项

- A/B 两组确认 EChecker 是否沿用 DRAFT/FULL_CHECK 的 `trace_id`，或将增量检查视为新链路。
- A/B 两组确认线性演示中 MDFixer 应消费 FULL_CHECK 报告还是最新 INCREMENTAL_CHECK 报告。
- 确认 `base_commit` 与 `baseline.commit` 不一致时的最终处理策略。
- 确认生产环境支持的 artifact URI scheme；仓库样例继续使用 `repo://`。
- 在安装 `jsonschema` 的课程环境中重新运行四个 `validate.py`；本次环境缺少该依赖，未声称通过。
