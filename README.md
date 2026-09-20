# DevOps-G16 E2 接口契约

本仓库用于完成 DevOps 教学实验 E2。当前阶段只约定 DRAFT、BuildChecker、EChecker 和 MDFixer 四个服务之间的数据接口，保留接口样例、设计记录和个人贡献；不实现完整服务。

## 小组信息

- 配对组编号：G16
- A1：焦龙，Git 作者 `illusiri`，负责 BuildChecker 接口
- A3：Git 作者 `WhiteNights`，负责公共任务模型和 A 组接口字段一致性检查
- A2：万宇，Git 作者 `adscfe`，负责 EChecker 接口
- B2：Git 作者 `jinglsn`
- B1：郭德林，Git 作者 `DelinGuo`，负责 DRAFT 接口
- B3：姓名和 Git 身份待对应成员补充

## 成员分工

| 成员 | 负责内容 | 主要交付物 |
| --- | --- | --- |
| A1 | BuildChecker 接口 | `contracts/buildchecker/request.json`、`response.json` |
| A2 | EChecker 接口 | `contracts/echecker/request.json`、`response.json` |
| A3 | 公共任务模型 | `contracts/task.schema.json`，检查 A 组公共字段一致性 |
| B1 | DRAFT 接口 | `contracts/draft/request.json`、`response.json` |
| B2 | MDFixer 接口 | `contracts/mdfixer/request.json`、`response.json` |
| B3 | 公共设计文档 | `docs/backlog.md`、`docs/adr.md`，负责最终整理 |

所有成员还要补充自己的 `AI_USAGE.md` 和 `CONTRIBUTIONS.md` 记录。A3 与 B3 共同维护本 README。

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
│   ├── backlog.md
│   └── adr.md
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

## 状态与错误语义

- 检测到 MD 或 RD 表示分析正常完成，任务状态应为 `SUCCEEDED`，发现写入 `output.findings`。
- 环境构建失败、任务超时或分析器失败才写入 `error`，并使用 `FAILED` 或 `TIMED_OUT`。
- `SUCCEEDED` 必须有对象类型的 `output`，且 `error` 必须为 `null`。
- `FAILED` 和 `TIMED_OUT` 必须提供至少含 `code` 和 `message` 的错误对象。

大型依赖图、日志和 Patch 应作为产物传递。公共 Schema 已定义 `artifact_id`、`type`、`uri`、`media_type`、`producer_job_id` 和可选的 `sha256`。

## 校验方法

先检查 Schema 文件是合法 JSON：

```bash
jq empty contracts/task.schema.json
```

安装 `check-jsonschema` 后可检查 Schema 自身：

```bash
check-jsonschema --check-metaschema contracts/task.schema.json
```

四个服务的样例文件完成后，分别使用公共 Schema 校验：

```bash
check-jsonschema --schemafile contracts/task.schema.json \
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

## 当前进度

- [x] A3：定义公共 `task.schema.json`
- [ ] 六名成员共同确认公共字段和枚举
- [x] A1：焦龙完成 BuildChecker 请求与响应样例、可读取的人工报告/依赖图和离线校验；与 A2/B1/B2 的交接互查仍待进行
- [x] A2：完成 EChecker 请求与响应样例、专有 Schema、基线与增量的离线校验；与 A1/B2 的交接互查仍待进行
- [x] B1：郭德林完成 DRAFT 请求与响应样例、Dockerfile 与逐轮日志产物和离线校验；与 A1/A2/B2 的交接互查仍待进行
- [x] B2：完成 MDFixer 请求与响应样例、Git Patch 产物和离线校验；与 A1 的交接互查仍待进行
- [ ] A3：A1/A2 文件出现后执行公共字段一致性检查
- [ ] B3：整理 Backlog 和 ADR
- [ ] A3/B3：全员信息和接口完成后最终更新 README
- [ ] 所有人：补齐 AI 使用记录和贡献记录

A1 校验命令（Python 环境需安装 `jsonschema`）：

```bash
python contracts/buildchecker/validate.py
```

A1 已通过公共及专有 Schema 校验、产物读取与内容一致性检查，以及非法输入和交接不一致反例检查；已补充本人 AI 使用和贡献记录。以上不代表 A3 的独立复核、全组确认或实际服务联调已经完成。

A2 校验命令（Python 环境需安装 `jsonschema`）：

```bash
python contracts/echecker/validate.py
```

A2 已通过公共及专有 Schema 校验、读取 A1 产物作为基线后的来源/提交/配置一致性检查、基线增量闭合与图合并检查，以及缺少 `baseline` 等非法输入和交接不一致反例检查；已补充本人 AI 使用和贡献记录。以上不代表 A3 的独立复核、全组确认或实际服务联调已经完成。

B2 校验命令（Python 环境需安装 `jsonschema`）：

```bash
python contracts/mdfixer/validate.py
```

B2 已通过公共及专有 Schema 校验、ERROR_REPORT 读取与仅消费 MISSING 检查、Patch 产物读取与内容核对，以及非法输入和交接不一致反例检查。以上不代表 A3 的独立复核、全组确认或实际服务联调已经完成。

B1 校验命令（Python 环境需安装 `jsonschema`）：

```bash
python contracts/draft/validate.py
```

B1 已通过公共及专有 Schema 校验、Dockerfile 与逐轮日志产物读取及内容一致性检查、A1/A2/B2 下游请求的镜像/配置/任务来源核对，以及非法输入和交接不一致反例检查；已补充本人 AI 使用和贡献记录。以上不代表 A3 的独立复核、全组确认或实际服务联调已经完成。
