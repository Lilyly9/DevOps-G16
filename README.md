# DevOps E2 - 需求与接口契约

本仓库用于完成 DevOps 教学实验 E2。当前阶段只约定 DRAFT、BuildChecker、EChecker 和 MDFixer 四个服务之间的数据接口，保留接口样例、设计记录和个人贡献；不实现完整服务。

## 小组信息

- A 组编号：TODO（仓库中未记录）
- B 组编号：TODO（仓库中未记录）
- 配对关系：G16（具体 A/B 组号待确认）
- A1：焦龙，Git 作者 `illusiri`，负责 BuildChecker 接口
- A2：万宇，Git 作者 `adscfe`，负责 EChecker 接口
- A3：林涵，Git 作者 `WhiteNights`，负责公共任务模型和 A 组接口字段一致性检查
- B1：郭德林，Git 作者 `DelinGuo`，负责 DRAFT 接口
- B2：Git 提交作者 `jenicifor`，负责 MDFixer 接口；姓名待本人补充
- B3：Git 提交作者 `Lilyly9`，负责公共契约与集成；姓名待本人补充

## 成员分工

| 成员 | 负责内容 | 主要交付物 |
| --- | --- | --- |
| A1 | BuildChecker 接口 | `contracts/buildchecker/request.json`、`response.json` |
| A2 | EChecker 接口 | `contracts/echecker/request.json`、`response.json` |
| A3 | 公共任务模型 | `contracts/task.schema.json`，检查 A 组公共字段一致性 |
| B1 | DRAFT 接口 | `contracts/draft/request.json`、`response.json` |
| B2 | MDFixer 接口 | `contracts/mdfixer/request.json`、`response.json` |
| B3 | 公共契约与集成 | 检查统一 Job Schema 和四服务衔接，统一状态/错误语义，维护 `README.md`、`docs/Backlog.md`、`docs/ADR.md`、`docs/INTEGRATION_CHECK.md`、`AI_USAGE.md` |

所有成员还要补充自己的 `AI_USAGE.md` 和 `CONTRIBUTIONS.md` 记录。A3 与 B3 共同维护本 README。

B3 负责：

- 检查并完善统一 Job Schema；
- 统一任务状态与系统错误/检测发现语义；
- 检查 DRAFT、BuildChecker、EChecker、MDFixer 四服务接口衔接；
- 完善 README、ADR、AI_USAGE 和 B 组公共设计记录；
- 协助 A/B 两组进行接口联调并汇总待确认问题。

## 目录约定

```text
.
├── contracts/
│   ├── task.schema.json
│   ├── buildchecker/
│   │   ├── request.json
│   │   └── response.json
│   ├── echecker/
│   │   ├── request.json
│   │   └── response.json
│   ├── draft/
│   │   ├── request.json
│   │   └── response.json
│   └── mdfixer/
│       ├── request.json
│       └── response.json
├── docs/
│   ├── ADR.md
│   ├── Backlog.md
│   └── INTEGRATION_CHECK.md
├── AI_USAGE.md
├── CONTRIBUTIONS.md
└── README.md
```

目录中的文件由对应负责人创建。不要在自己的提交中替其他成员填写姓名、贡献或尚未确认的接口内容。

A1 的 BuildChecker 目录还包含服务专有 `contract.schema.json`、离线校验脚本 `validate.py` 和 `artifacts/` 下的三份人工产物。字段说明和交接待确认项见 [BuildChecker 接口说明](contracts/buildchecker/README.md)。其中 `request.json` 是创建请求，`response.json` 是任务完成后的查询结果；报告和依赖图均为人工样例，仓库、镜像和被检测提交均为占位值，不代表检测服务已运行。

A2 的 EChecker 目录同样包含服务专有 `contract.schema.json`、离线校验脚本 `validate.py` 和 `artifacts/` 下的三份人工产物，字段说明和交接待确认项见 [EChecker 接口说明](contracts/echecker/README.md)。其中 `request.json` 是增量检测的创建请求，`response.json` 是任务完成后的查询结果；其基线是 A1 的 `ACTUAL_GRAPH` 与 `ERROR_REPORT` 样例，全部字段值仍为占位数据，不代表检测服务已运行。

B2 的 MDFixer 目录同样包含服务专有 `contract.schema.json`、离线校验脚本 `validate.py` 和 `artifacts/` 下的 Git Patch 人工产物。字段说明和交接待确认项见 [MDFixer 接口说明](contracts/mdfixer/README.md)。`request.json` 是创建请求，`response.json` 是修复完成后的查询结果；Patch 和验证结果均为人工样例，仓库、镜像和被修复提交均为占位值，不代表修复服务已运行。

B1 的 DRAFT 目录同样包含服务专有 `contract.schema.json`、离线校验脚本 `validate.py` 和 `artifacts/` 下的 Dockerfile 与逐轮构建日志人工产物。字段说明和交接待确认项见 [DRAFT 接口说明](contracts/draft/README.md)。`request.json` 是创建请求，`response.json` 是环境生成完成后的查询结果；Dockerfile、日志和验证结果均为人工样例，仓库、镜像和被构建提交均为占位值，不代表环境生成服务已运行。

## 公共任务模型

[`contracts/task.schema.json`](contracts/task.schema.json) 使用 JSON Schema Draft 2020-12，集中定义四个服务共享的字段和枚举。

四种任务类型：

- `DRAFT`
- `FULL_CHECK`
- `INCREMENTAL_CHECK`
- `REPAIR`

六种任务状态：

- `QUEUED`
- `RUNNING`
- `SUCCEEDED`
- `FAILED`
- `TIMED_OUT`
- `CANCELLED`

Schema 区分三类生命周期消息：

1. `jobSubmission`：客户端创建任务的请求。此时服务端还没有生成 `job_id` 和 `status`。
2. `jobAccepted`：服务端接受任务后的 HTTP 202 响应，包含 `job_id` 和 `QUEUED`。
3. `jobRecord`：可查询的完整任务记录，统一包含 `schema_version`、`job_id`、`trace_id`、`job_type`、`status`、`input`、`output` 和 `error`。

各服务把专有字段放在 `input` 和 `output` 内。Schema 允许新增可选字段，以便进行兼容扩展；删除字段、改名、改变字段含义或修改枚举时，应更新 `schema_version` 并与消费方确认。

## 四服务流程

```text
DRAFT
  → BuildChecker（FULL_CHECK）
  → EChecker（INCREMENTAL_CHECK）
  → MDFixer（REPAIR）
  → 重新构建、测试、重检
```

A3 与 B3 已对样例链路进行离线字段核对。DRAFT 的固定镜像、配置和生产任务编号能进入三个下游；FULL_CHECK 的实际依赖图及 findings 报告能作为 EChecker 基线和 MDFixer 输入；INCREMENTAL_CHECK 明确记录基线、当前提交、配置、更新后图以及新增/消除 findings；REPAIR 只消费 `MISSING`，并用 Patch、summary 和 build/test/recheck 结果表达修复过程。详细证据和边界见 [`docs/INTEGRATION_CHECK.md`](docs/INTEGRATION_CHECK.md)。

## 状态与错误语义

- 检测到 MD 或 RD 表示分析正常完成，任务状态应为 `SUCCEEDED`，发现写入 `output.findings`。
- 环境构建失败、任务超时或分析器失败才写入 `error`，并使用 `FAILED` 或 `TIMED_OUT`。
- 参考错误码包括镜像构建失败 `ENV_3002`、任务超时 `EXEC_4002`、分析器失败 `ANALYSIS_5001`；公共 Schema 不把错误码封闭为枚举，以兼容各服务已有错误码。
- `SUCCEEDED` 必须有对象类型的 `output`，且 `error` 必须为 `null`。
- `FAILED` 和 `TIMED_OUT` 必须提供至少含 `code` 和 `message` 的错误对象。

大型依赖图、日志和 Patch 应作为产物传递。公共 Schema 已定义 `artifact_id`、`type`、`uri`、`media_type`、`producer_job_id` 和可选的 `sha256`。

产物 URI 的存储实现不在本实验中绑定到特定平台。仓库离线样例使用 `repo://`，消费方应先在 Job 的 `artifacts` 中按 `artifact_id` 找到元数据，再解析对应 `uri`；生产环境采用其他 URI scheme 时需由 A/B 两组共同确认。

## 校验方法

先检查 Schema 文件是合法 JSON：

```bash
jq empty contracts/task.schema.json
```

可使用 `uvx` 临时运行校验器，无需修改项目依赖：

```bash
uvx check-jsonschema --check-metaschema contracts/task.schema.json
```

四个服务的样例文件完成后，分别使用公共 Schema 校验：

```bash
uvx check-jsonschema --schemafile contracts/task.schema.json \
  contracts/buildchecker/request.json \
  contracts/buildchecker/response.json \
  contracts/echecker/request.json \
  contracts/echecker/response.json \
  contracts/draft/request.json \
  contracts/draft/response.json \
  contracts/mdfixer/request.json \
  contracts/mdfixer/response.json
```

还应至少手工验证以下无效情况会被拒绝：

- `job_type` 改成 `ABC`；
- `SUCCEEDED` 任务的 `output` 为 `null`；
- `FAILED` 或 `TIMED_OUT` 任务没有错误对象；
- EChecker 请求缺少 `baseline`。最后一项属于 EChecker 专有输入规则，已由 A2 的接口契约（`contracts/echecker/contract.schema.json` 与 `validate.py`）补充，并覆盖了 `baseline` 缺少必填字段的正反例。

## 当前完成情况

- [x] DRAFT interface
- [x] FULL_CHECK interface
- [x] INCREMENTAL_CHECK interface
- [x] REPAIR interface
- [x] Unified Job contract
- [x] Interface integration check（离线样例字段与产物引用检查；非实际服务联调）
- [x] ADR
- [x] A3 独立公共字段与四服务校验复核
- [x] AI_USAGE（六个角色均已有记录）
- [ ] A/B 两组确认集成检查记录中的开放问题

四类接口的请求/响应、专有 Schema、人工产物和校验脚本均已存在。A3/B3 已完成公共字段与样例链路复核；实际服务联调、真实构建/检测/修复以及全员最终签字不在本次离线检查的完成声明内。

## 现有成员验证记录

A1 校验命令：

```bash
uv run --with jsonschema==4.23.0 --with referencing==0.30.2 \
  python contracts/buildchecker/validate.py
```

A1 已通过公共及专有 Schema 校验、产物读取与内容一致性检查，以及非法输入和交接不一致反例检查；A3 已独立复跑通过。以上不代表全组确认或实际服务联调已经完成。

A2 校验命令：

```bash
uv run --with jsonschema==4.23.0 --with referencing==0.30.2 \
  python contracts/echecker/validate.py
```

A2 已通过公共及专有 Schema 校验、读取 A1 产物作为基线后的来源/提交/配置一致性检查、基线增量闭合与图合并检查，以及缺少 `baseline` 等非法输入和交接不一致反例检查；A3 已独立复跑通过，其中 `base_commit` 与 `baseline.commit` 不一致按 A2 约定产生警告而非拒绝。以上不代表全组确认或实际服务联调已经完成。

B2 校验命令：

```bash
uv run --with jsonschema==4.23.0 --with referencing==0.30.2 \
  python contracts/mdfixer/validate.py
```

B2 已通过公共及专有 Schema 校验、ERROR_REPORT 读取与仅消费 MISSING 检查、Patch 产物读取与内容核对，以及非法输入和交接不一致反例检查；A3 已独立复跑通过。以上不代表全组确认或实际服务联调已经完成。

B1 校验命令：

```bash
uv run --with jsonschema==4.23.0 --with referencing==0.30.2 \
  python contracts/draft/validate.py
```

B1 已通过公共及专有 Schema 校验、Dockerfile 与逐轮日志产物读取及内容一致性检查、A1/A2/B2 下游请求的镜像/配置/任务来源核对，以及非法输入和交接不一致反例检查；A3 已独立复跑通过。以上不代表全组确认或实际服务联调已经完成。

## 最终离线复核结论

2026-09-20，A3 在最新 `main` 上完成独立复核：公共 Schema 元校验通过，八个请求/响应样例全部通过公共 Schema，仓库内 19 个 JSON 文件均可解析，四个服务的 `validate.py` 均完整通过。当前剩余工作只包括 README 中未确认的 A/B 组号、B2/B3 姓名，以及 [`docs/INTEGRATION_CHECK.md`](docs/INTEGRATION_CHECK.md) 中需要两组共同决定的开放问题。
