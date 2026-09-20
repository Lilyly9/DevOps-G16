# B1：DRAFT 接口样例

本目录是基于 A3 公共任务模型的 B1 提案。接口字段及产物格式尚待 A1、A2、B2 互查，不表示六名成员已经确认，也不表示 DRAFT 已实现。

所有 Dockerfile、构建日志和验证结果均为 `MANUAL_FIXTURE` 人工教学样例。`example.invalid` 仓库、镜像、40 位提交 SHA 和任务编号都是占位数据，不可直接执行；联调前须替换为真实且互相对应的值。样例的提交 SHA 指被构建项目版本，不是本接口仓库的 Git 提交。

## 职责与边界

DRAFT 生成**可构建环境**：依据仓库版本和构建要求，迭代生成 Dockerfile 并构建镜像，以 `build.command` 和 `verify_command` 在容器内成功作为明确成功判据，产出镜像引用、Dockerfile 与每轮日志，交付 BuildChecker、EChecker、MDFixer 三个下游服务。DRAFT 只负责环境本身，不检测 MD/RD、不修复代码；源码级构建失败是否应让检测服务继续诊断，见下方待确认项。

## 生命周期与字段

- `request.json`：`POST /v1/dockerfile-jobs` 的 JSON 请求，符合公共 `jobSubmission`。`job_type` 固定为 `DRAFT`；请求不发送服务端生成的 `job_id` 或 `status`。
- 成功受理返回 HTTP 202，格式如下。相同 `idempotency_key` 和相同请求应返回同一任务；同一键搭配不同请求应拒绝。此行为是 B1 提案，待共同确认。

```json
{
  "schema_version": "1.0.0",
  "job_id": "g16-example-draft-001",
  "trace_id": "g16-example-flow-001",
  "job_type": "DRAFT",
  "status": "QUEUED"
}
```

- `response.json`：`GET /v1/jobs/g16-example-draft-001` 环境生成完成后的 HTTP 200 查询结果，符合公共 `jobRecord`，不是创建任务时的立即响应。
- 成功产出可用镜像即 `SUCCEEDED`、`error: null`，镜像引用放在 `output.image`。迭代耗尽仍无法构建或超时属于系统执行失败，使用 `FAILED` 或 `TIMED_OUT`，`output` 为 `null`，`error` 至少提供 `code` 和 `message`。
- 失败示例：在完整任务记录中设置 `status: "FAILED"`、`output: null`、`error: {"code": "ENV_3002", "message": "镜像构建失败（迭代耗尽）", "retriable": false}`。超时用 `TIMED_OUT` / `EXEC_4002`。

| input 字段 | 类型 / 必填 | 含义 |
| --- | --- | --- |
| `repository.url` | string / 是 | 被构建项目 Git 仓库地址 |
| `repository.commit` | string / 是 | 该项目完整 40 位 SHA；产出镜像必须对应此版本 |
| `configuration_id` | string / 是 | 构建配置标识；写入输出供下游核对（此字段是否放入 DRAFT 输入属 B1 提案，待确认） |
| `build.project_root` | string / 是 | checkout 内的项目相对目录；本例是仓库根目录 `.` |
| `build.command` | string / 是 | 成功判据一：环境内执行必须成功的构建命令 |
| `build.verify_command` | string / 是 | 成功判据二：清理后重建的验证命令 |
| `max_iterations` | integer > 0 / 是 | Dockerfile 生成-构建-修正的最大轮数 |
| `timeout_seconds` | integer > 0 / 是 | 环境生成总超时秒数 |

`output.image` 给出以 sha256 digest 固定的镜像引用；`output.dockerfile_artifact_ref` 指向最终 Dockerfile 产物；`output.attempts` 按轮记录每轮结果、修改内容、选择理由和日志产物引用；`output.verification` 给出两条成功判据的最终结果。三个下游服务把 `output.image` 填入各自请求的 `input.environment.image`，把本任务编号填入 `input.environment.producer_job_id`。

## 本例的含义

第 1 轮 Dockerfile 只安装 make，容器内执行 `make all` 时日志显示 `bison: Command not found`，判定为环境依赖缺失而非源码问题；第 2 轮在 apt 安装列表加入 bison，`build.command`（`make all`）与 `verify_command`（`make clean && make all`）均以退出码 0 通过，达到 `max_iterations` 内的成功判据，镜像固定为占位 digest `sha256:2222…`。

A1 的 FULL_CHECK、A2 的 INCREMENTAL_CHECK 和 B2 的 REPAIR 请求样例都引用 `g16-example-draft-001` 与该镜像 digest，`validate.py` 会实际读取三份下游请求核对这些值一致。这用于演示交接关系，不代表三个下游已复核本目录。

## 产物格式和读取方式

任务顶层 `artifacts` 使用 A3 的公共产物结构。消费者按 `type` 寻找产物，不依赖数组顺序。本次共三份产物：一份 `type == DOCKERFILE` 的最终 Dockerfile 和两份 `type == BUILD_LOG` 的逐轮构建日志，`media_type` 均为 `text/plain`，可直接按文本读取。Dockerfile 头部和日志头部均标注 `MANUAL_FIXTURE` 说明人工来源；日志正文中的轮次结论行（如 `build.command PASS`）用于机器核对成功判据。

`repo://` 是本仓库**本地契约样例**的地址约定：删除前缀后，从 DevOps-G16 仓库根目录解析相对路径。例如 `repo://contracts/draft/artifacts/Dockerfile` 对应本仓库同路径文件。读取双方需使用同一份契约仓库版本；路径不得越出仓库。`validate.py` 演示了实际解析和读取。`sha256` 在需要核验产物完整性时补充，本例为占位样例暂不提供。

这不是已部署的镜像仓库或日志下载服务，也不是已获全组批准的生产存储方案。后续 B3 的 ADR 需与配对组确定镜像推送地址、日志共享方式和版本策略，并验证另一组能读取产物。

## 与其他成员的交接

| 对方 | 需要确认的内容 |
| --- | --- |
| A1 / BuildChecker | 消费 `output.image` 与本任务编号作为 `input.environment`；确认镜像内工具链满足 `configuration_id` 与构建命令要求 |
| A2 / EChecker | 增量检测复用同一镜像；若新提交需要不同环境，是否触发新的 DRAFT 任务待确认 |
| B2 / MDFixer | 修复验证使用同一镜像；确认镜像内含 `verify_command` 所需工具 |
| A3 | 检查本目录的公共字段和枚举是否与 task.schema.json 一致 |
| B3 | 将确认后的镜像引用方式、日志读取和版本策略写入公共 ADR，将未确认项纳入 Backlog |

待确认的 B1 提案：`configuration_id` 是否放入 DRAFT 输入；`build.command`/`verify_command` 作为成功判据的职责划分；源码级无法构建时 DRAFT 应报 `FAILED` 还是给出结构化结果让 BuildChecker 继续诊断；`max_iterations` 耗尽后的错误码是否复用 `ENV_3002`。

## 校验

`contract.schema.json` 通过引用复用 A3 的公共模型，补充 DRAFT 输入和结果约束；没有修改公共 Schema。离线校验器把两个 Schema 注册在内存中，无需访问 Schema 中的示例网址。

在仓库根目录运行（Python 3.9+；缺少依赖时先执行 `python -m pip install "jsonschema>=4.18,<5"`）：

```bash
python contracts/draft/validate.py
```

脚本检查公共和服务专有 Schema、请求/结果关联、Dockerfile 与逐轮日志产物实际读取与内容核对、最终轮成功判据，并实际读取 A1/A2/B2 的请求样例核对镜像、配置和任务来源一致，同时验证受理/失败/超时合法样例与非法输入、非法交接反例。它仅校验离线接口样例，不构建镜像、不运行容器，不代表双方联调完成。
