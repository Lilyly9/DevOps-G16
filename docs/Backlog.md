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
| 接口集成检查 | A3/B3 | `docs/INTEGRATION_CHECK.md` | DRAFT → BuildChecker → EChecker → MDFixer 的主要字段可衔接，并列出不能自行裁决的差异 | 已完成两轮离线检查；线性端到端策略待两组确认 |
| 架构决策记录 | B3 | `docs/ADR.md` | 记录异步 Job、产物引用、系统错误与检测发现分离 | 已完成 |
| 提交材料汇总 | A3/B3 | `README.md`、`AI_USAGE.md`、`CONTRIBUTIONS.md` | 成员工作、验证范围与待确认问题可追溯，不伪造提交 SHA | 已完成；A/B 组号和 B2/B3 姓名待本人确认 |

## 后续事项

- A/B 两组确认 EChecker 是否沿用 DRAFT/FULL_CHECK 的 `trace_id`，或将增量检查视为新链路。
- A/B 两组确认线性演示中 MDFixer 应消费 FULL_CHECK 报告还是最新 INCREMENTAL_CHECK 报告。
- 确认 `base_commit` 与 `baseline.commit` 不一致时的最终处理策略。
- 确认生产环境支持的 artifact URI scheme；仓库样例继续使用 `repo://`。
- A/B 两组补充 README 中的具体组号，B2/B3 补充姓名，并对以上开放问题做最终签字确认。

## A3 最终复核

2026-09-20，A3 在最新 `main` 上使用 `jsonschema 4.23.0` 和 `referencing 0.30.2` 独立运行四个服务的 `validate.py`，全部通过。公共 Schema 元校验、八个公共请求/响应样例和仓库内 19 个 JSON 文件也全部通过。该结果只证明离线契约、人工产物和负向样例一致，不代表真实服务已经实现或完成网络联调。

## E3 收尾更新（2026-10-05）

| 项目 | 责任方 | 状态 |
| --- | --- | --- |
| 四服务基线总表 | A3/B3+全员 | 已发布；用户明确确认已获全员确认 |
| §10 双向相互检查 | A3/B3 | B3 已检查 A 组；A3 实际复跑 B1/B2 并完成四问，见 e3/docs/A3_CROSS_REVIEW.md |
| B2 环境摘要 | A3 汇总 | 已从 B2 保存原件转录，保留来源及各轮独立环境 |
| E3 B2 姓名/Git 作者 | B2 | 仍待本人登记，技术基线与跨组核查已通过 |

## E4 A3 收尾后的共同待办（2026-10-03）

| 项目 | 负责人 | 已确认的状态与下一步 |
| --- | --- | --- |
| B 组实际 E4 模板与运行说明 | B1/B3 | 新克隆共享 main 无 e4/B-draft；用户确认尚未准备。接入实际模板及可执行 README 后再通知 A3 |
| B 组真实跨组重跑与四项核查 | A3/B3 | A3 已做 README 前置检查并记录缺项；待 B 组就绪后继续构建、原件及镜像核验 |
| A 组 E4 原件与文档汇总 | A3 | 已独立核验 A1/A2/A3 的七份证据、镜像与扫描，A1/A2 同 SHA 对照通过，A 组 §10 已转录核验信息 |
