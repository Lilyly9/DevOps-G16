# B2：MDFixer 接口样例

本目录是基于 A3 公共任务模型的 B2 提案。接口字段及产物格式尚待 A1、A2、B1 互查，不表示六名成员已经确认，也不表示 MDFixer 已实现。

所有 Patch 和验证结果均为 `MANUAL_FIXTURE` 人工教学样例。`example.invalid` 仓库、镜像、40 位提交 SHA 和任务编号都是占位数据，不可直接执行；联调前须替换为真实且互相对应的值。样例的提交 SHA 指被修复项目版本，不是本接口仓库的 Git 提交。

## 职责与边界

MDFixer 修复 BuildChecker 报告中的 **Missing Dependency（MD）**：为声明缺失的构建目标补上缺失的依赖声明，生成 Git Patch，并在同一环境下重新构建、测试、重检以验证。它**只消费 `type == MISSING` 的发现**，不把 `REDUNDANT` 当作 MD 修复，也不删除被报告为冗余的声明。

## 生命周期与字段

- `request.json`：`POST /v1/repair-jobs` 的 JSON 请求，符合公共 `jobSubmission`。`job_type` 固定为 `REPAIR`；请求不发送服务端生成的 `job_id` 或 `status`。
- 成功受理返回 HTTP 202，格式如下。相同 `idempotency_key` 和相同请求应返回同一任务；同一键搭配不同请求应拒绝。此行为是 B2 提案，待共同确认。

```json
{
  "schema_version": "1.0.0",
  "job_id": "g16-example-repair-001",
  "trace_id": "g16-example-flow-001",
  "job_type": "REPAIR",
  "status": "QUEUED"
}
```

- `response.json`：`GET /v1/jobs/g16-example-repair-001` 修复完成后的 HTTP 200 查询结果，符合公共 `jobRecord`，不是创建任务时的立即响应。
- 成功产出 Patch 或拒绝候选补丁均属正常分析完成，仍为 `SUCCEEDED`、`error: null`，结果放在 `output`。系统执行失败（环境构建失败、超时等）使用 `FAILED` 或 `TIMED_OUT`，`output` 可为 `null`，`error` 至少提供 `code` 和 `message`。
- 环境构建失败示例：在完整任务记录中设置 `status: "FAILED"`、`output: null`、`error: {"code": "ENV_3002", "message": "镜像构建失败", "retriable": false}`。超时用 `TIMED_OUT` / `EXEC_4002`。

| input 字段 | 类型 / 必填 | 含义 |
| --- | --- | --- |
| `repository.url` | string / 是 | 被修复项目 Git 仓库地址 |
| `repository.commit` | string / 是 | 该项目完整 40 位 SHA；必须与所引报告一致 |
| `environment.image` | string / 是 | 可获取且以 sha256 digest 固定的构建镜像 |
| `environment.producer_job_id` | string / 否 | 产生环境的 DRAFT 任务编号；手动提供环境时可省略 |
| `configuration_id` | string / 是 | 构建配置标识；必须与所引报告一致 |
| `build.project_root` | string / 是 | checkout 内的项目相对目录；本例是仓库根目录 `.` |
| `build.command` | string / 是 | 应用候选补丁后执行的构建命令 |
| `build.verify_command` | string / 是 | 用于验证修复的清理+重建命令 |
| `error_report_uri` | string / 是 | BuildChecker 产出的 ERROR_REPORT 的 `repo://` 地址 |
| `makefile_path` | string / 是 | 待修复的 Makefile 路径，应与 MD 发现的 `location.path` 一致 |
| `timeout_seconds` | integer > 0 / 是 | 单次修复+验证总超时秒数 |

`output.summary` 给出消费的发现编号、修复数与拒绝数；`output.patches` 描述每个已修复 MD 的补丁引用和声明风格；`output.rejected` 记录验证失败而被拒绝的候选及原因；`output.verification` 给出构建、测试、重检结果。路径均相对于 `build.project_root`。

## 本例的含义

引用 BuildChecker 的 `error-report.json`，其中含一个 MD（`g16-md-001`：`main.o` 实际依赖 `config.h` 但声明缺失）和一个 RD（`g16-rd-001`：`unused.h`）。MDFixer 仅消费 `g16-md-001`，把 `config.h` 加入 `main.o` 规则声明，`unused.h` 保持不动：

```diff
-main.o: main.c unused.h
+main.o: main.c unused.h config.h
```

补丁产出后，在 `gcc-default-v1` 配置下执行 `build.command` 和 `verify_command` 均通过；重检的 `remaining_missing` 为 0。RD 不属于 MDFixer 职责，本例不删除 `unused.h`，留待下游或人工按配置决定。

## 产物格式和读取方式

任务顶层 `artifacts` 使用 A3 的公共产物结构。消费者按 `type` 寻找产物，不依赖数组顺序。本次唯一产物是 `type == GIT_PATCH` 的 Git Patch，`media_type` 为 `text/x-diff`，用标准 `git apply` 即可读取；与 A1 的 JSON 产物不同，Patch 是纯文本 diff，其来源（仓库、commit、配置、生产任务）由任务 `input`/`output` 和 `artifacts` 元数据承载，不在 diff 正文内重复。

`repo://` 是本仓库**本地契约样例**的地址约定：删除前缀后，从 DevOps-G16 仓库根目录解析相对路径。读取双方需使用同一份契约仓库版本；路径不得越出仓库。`validate.py` 演示了实际解析和读取。`sha256` 在需要核验 Patch 完整性时补充，本例为占位样例暂不提供。

这不是已部署的下载服务，也不是已获全组批准的生产存储方案。后续 B3 的 ADR 需与配对组确定共享下载地址、访问权限和版本策略，并验证另一组能读取产物。

## 与其他成员的交接

| 对方 | 需要确认的内容 |
| --- | --- |
| A1 / BuildChecker | 读取其 `ERROR_REPORT`；仅消费 `type == MISSING` 的发现；检查仓库、commit、配置和声明位置一致；不把 RD 当作 MD 修复 |
| B1 / DRAFT | 修复验证需要同一提交对应的可用镜像和构建命令；本目录不替 B1 定义 DRAFT 响应结构 |
| A2 / EChecker | 修复后的重检可触发新一轮 `FULL_CHECK` 或 `INCREMENTAL_CHECK`，需共同确认重检如何携带更新后的图 |
| A3 | 检查本目录的公共字段和枚举是否与 task.schema.json 一致 |
| B3 | 将确认后的 Patch 读取、拒绝语义和版本策略写入公共 ADR，将未确认项纳入 Backlog |

## 校验

`contract.schema.json` 通过引用复用 A3 的公共模型，补充 REPAIR 输入和结果约束；没有修改公共 Schema。离线校验器把两个 Schema 注册在内存中，无需访问 Schema 中的示例网址。

在仓库根目录运行（Python 3.9+；缺少依赖时先执行 `python -m pip install "jsonschema>=4.18,<5"`）：

```bash
python contracts/mdfixer/validate.py
```

脚本检查公共和服务专有 Schema、请求/结果关联、ERROR_REPORT 实际读取、仅消费 MISSING 的约束、Patch 产物实际读取与内容核对，并验证受理/失败/超时/拒绝候选合法样例与非法输入反例。它仅校验离线接口样例，不构建镜像、不生成真实 Patch、不运行重检，不代表双方联调完成。
