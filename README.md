# DevOps-G16 E2 接口契约

本仓库用于完成 DevOps 教学实验 E2。当前阶段只约定 DRAFT、BuildChecker、EChecker 和 MDFixer 四个服务之间的数据接口，保留接口样例、设计记录和个人贡献；不实现完整服务。

## 小组信息

- 配对组编号：G16
- A3：Git 作者 `WhiteNights`，负责公共任务模型和 A 组接口字段一致性检查
- A1、A2、B1、B2、B3：姓名和 Git 身份待对应成员补充

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
- EChecker 请求缺少 `baseline`。最后一项属于 EChecker 专有输入规则，需要由 A2 的接口契约补充。

## 当前进度

- [x] A3：定义公共 `task.schema.json`
- [ ] 六名成员共同确认公共字段和枚举
- [ ] A1：完成 BuildChecker 请求与响应样例
- [ ] A2：完成 EChecker 请求与响应样例
- [ ] B1：完成 DRAFT 请求与响应样例
- [ ] B2：完成 MDFixer 请求与响应样例
- [ ] A3：A1/A2 文件出现后执行公共字段一致性检查
- [ ] B3：整理 Backlog 和 ADR
- [ ] A3/B3：全员信息和接口完成后最终更新 README
- [ ] 所有人：补齐 AI 使用记录和贡献记录
