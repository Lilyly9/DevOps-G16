# A1：BuildChecker 接口样例

本目录是基于 A3 公共任务模型的 A1 提案。接口字段及产物格式尚待 A2、B1、B2 互查，不表示六名成员已经确认，也不表示 BuildChecker 已实现。

所有检测结果和图均为 `MANUAL_FIXTURE` 人工教学样例。`example.invalid` 仓库、镜像、40 位提交 SHA 和任务编号都是占位数据，不可直接执行；联调前须替换为真实且互相对应的值。样例的提交 SHA 指被检测项目版本，不是本接口仓库的 Git 提交。

## 生命周期与字段

- `request.json`：`POST /v1/full-check-jobs` 的 JSON 请求，符合公共 `jobSubmission`。`job_type` 固定为 `FULL_CHECK`；请求不发送服务端生成的 `job_id` 或 `status`。
- 成功受理返回 HTTP 202，格式如下。相同 `idempotency_key` 和相同请求应返回同一任务；同一键搭配不同请求应拒绝。此行为是 A1 提案，待共同确认。

```json
{
  "schema_version": "1.0.0",
  "job_id": "g16-example-full-001",
  "trace_id": "g16-example-flow-001",
  "job_type": "FULL_CHECK",
  "status": "QUEUED"
}
```

- `response.json`：`GET /v1/jobs/g16-example-full-001` 分析完成后的 HTTP 200 查询结果，符合公共 `jobRecord`，不是创建任务时的立即响应。
- 发现 MD/RD 时仍为 `SUCCEEDED`、`error: null`，问题放在 `output.findings`。系统执行失败使用 `FAILED` 或 `TIMED_OUT`，`output` 可为 `null`，`error` 至少提供 `code` 和 `message`。
- 分析器失败示例：在完整任务记录中设置 `status: "FAILED"`、`output: null`、`error: {"code": "ANALYSIS_5001", "message": "分析器执行失败", "retriable": false}`，不提供成功产物。超时用 `TIMED_OUT` / `EXEC_4002`。
- 非法创建请求应在受理前拒绝，不生成任务；具体 HTTP 错误响应及错误码由公共 ADR 最终统一。

| input 字段 | 类型 / 必填 | 含义 |
| --- | --- | --- |
| `repository.url` | string / 是 | 被检测项目 Git 仓库地址 |
| `repository.commit` | string / 是 | 该项目完整 40 位 SHA；不能只给分支名 |
| `environment.image` | string / 是 | 可获取且以 sha256 digest 固定的构建镜像 |
| `environment.producer_job_id` | string / 否 | 产生环境的 DRAFT 任务编号；手动提供环境时可省略 |
| `configuration_id` | string / 是 | 构建配置标识，编译器、编译选项或环境变化时须与下游确认并更新 |
| `build.project_root` | string / 是 | checkout 内的项目相对目录；本例是仓库根目录 `.` |
| `build.clean_command` | string / 是 | 在项目目录执行的清理命令 |
| `build.command` | string / 是 | 清理成功后执行的完整构建命令 |
| `timeout_seconds` | integer > 0 / 是 | 全量检测总超时秒数 |

`output.summary` 给出两类发现的数量；`output.findings` 给出完整发现列表，空列表表示没有发现。每项包含类型、目标、依赖文件、被检测提交、配置、来源、声明位置及证据。路径均相对于 `build.project_root`，行号从 1 开始。真实检测时应提供进程、文件访问或声明解析等真实证据，不能沿用人工证据冒充实际运行。

## 本例的含义

假设 Makefile 第 1 行为 `main.o: main.c unused.h`，编译 main.c 时实际使用 main.c 和 config.h。实际图有 `main.o -> config.h`，声明图没有，因此报告 MD；声明图有 `main.o -> unused.h`，该配置实际图没有，因此报告 RD。两张图都保留正常的 `main.o -> main.c` 边。

这是用来解释数据交换的最小图，不定义 BuildChecker 的完整检测算法。正式算法还需要处理间接依赖等情况。

## 产物格式和读取方式

任务顶层 `artifacts` 使用 A3 的公共产物结构。消费者按 `type` 寻找产物，不依赖数组顺序。

本次采用 `repo://` 作为**本地契约样例**的地址约定：删除前缀后，从 DevOps-G16 仓库根目录解析相对路径。例如 `repo://contracts/buildchecker/artifacts/actual-graph.json` 对应本仓库同路径文件。读取双方需使用同一份契约仓库版本；路径不得越出仓库。`validate.py` 演示了实际解析和读取。

这不是已部署的下载服务，也不是已获全组批准的生产存储方案。后续 B3 的 ADR 需与配对组确定共享下载地址、访问权限和版本策略，并验证另一组能读取产物。

三份产物均带有 `schema_version`、`sample_origin`、`producer_job_id`、`repository`、`configuration_id`。图使用 `nodes`（相对路径字符串列表）和 `edges`（`target`、`dependency` 对象列表）；边的方向是构建目标指向依赖文件。报告文件的 `findings` 与任务内联列表相同，本例保留两份是为了演示文件交接与直接查询，后续修改须同步。

## 与其他成员的交接

| 对方 | 需要确认的内容 |
| --- | --- |
| B1 / DRAFT | 是否能提供同一提交对应的可用镜像、配置和构建命令；本目录不替 B1 定义 DRAFT 响应结构 |
| A2 / EChecker | 用 `ACTUAL_GRAPH` 的 URI 作为历史图入口；其提交作为 base commit，配置必须一致；共同确认 nodes/edges 格式 |
| B2 / MDFixer | 读取 `ERROR_REPORT`，仅消费 `type == MISSING` 的发现；检查仓库、commit、配置和声明位置；不把 RD 当作 MD 修复 |
| A3 | 检查本目录的公共字段和枚举是否与 task.schema.json 一致 |
| B3 | 将确认后的产物读取、错误表示、幂等和版本策略写入公共 ADR，将未确认项纳入 Backlog |

## 校验

`contract.schema.json` 通过引用复用 A3 的公共模型，补充 FULL_CHECK 输入和结果约束；没有修改公共 Schema。离线校验器把两个 Schema 注册在内存中，无需访问 Schema 中的示例网址。

在仓库根目录运行（Python 3.9+；缺少依赖时先执行 `python -m pip install "jsonschema>=4.18,<5"`）：

```bash
python contracts/buildchecker/validate.py
```

脚本检查公共和服务专有 Schema、请求/结果关联、三份产物实际读取、提交/配置/任务来源一致性及 MD/RD 证据，并验证受理/失败/超时合法样例与非法输入反例。它仅校验离线接口样例，不构建镜像、不运行检测器，不代表双方联调完成。
