# A2：EChecker 增量检测接口样例

本目录是基于 A3 公共任务模型的 A2 提案。字段、基线表示和增量语义尚待 A1、B1、B2 互查，不表示六名成员已经确认，也不表示 EChecker 已实现。

所有发现和图均为 `MANUAL_FIXTURE` 人工教学样例。`example.invalid` 仓库、镜像、40 位提交 SHA 和任务编号都是占位数据，不可直接执行；联调前须替换为真实且互相对应的值。样例的提交 SHA 指被检测项目版本，不是本接口仓库的 Git 提交。基线的两份产物是 A1 目录中的真实文件，本目录校验脚本会实际读取它们。

## 生命周期与字段

- `request.json`：`POST /v1/incremental-check-jobs` 的 JSON 请求，符合公共 `jobSubmission`。`job_type` 固定为公共枚举中的 `INCREMENTAL_CHECK`；请求不发送服务端生成的 `job_id` 或 `status`。
- 成功受理返回 HTTP 202，格式如下。相同 `idempotency_key` 和相同请求应返回同一任务；同一键搭配不同请求应拒绝。此行为沿用 A1 提案，待共同确认。

```json
{
  "schema_version": "1.0.0",
  "job_id": "g16-example-incr-001",
  "trace_id": "g16-example-flow-002",
  "job_type": "INCREMENTAL_CHECK",
  "status": "QUEUED"
}
```

- `response.json`：`GET /v1/jobs/g16-example-incr-001` 分析完成后的 HTTP 200 查询结果，符合公共 `jobRecord`，不是创建任务时的立即响应。
- 发现 MD/RD 时仍为 `SUCCEEDED`、`error: null`，本次发现放在 `output.findings`。系统执行失败使用 `FAILED` 或 `TIMED_OUT`，`output` 可为 `null`，`error` 至少提供 `code` 和 `message`（课程备查页给出的错误码是 `ENV_3002` 镜像构建失败、`EXEC_4002` 超时、`ANALYSIS_5001` 分析器失败）。环境构建失败、超时或分析器失败不得写成 `SUCCEEDED`。
- 非法创建请求应在受理前拒绝，不生成任务；具体 HTTP 错误响应及错误码由公共 ADR 最终统一。

### input 字段

| input 字段 | 类型 / 必填 | 含义 |
| --- | --- | --- |
| `repository.url` | string / 是 | 被检测项目 Git 仓库地址，须与基线产物一致 |
| `repository.commit` | string / 是 | 本次待检测的头提交（课程材料中的 C1）完整 40 位 SHA；必须与 `base_commit` 不同 |
| `base_commit` | string / 是 | 课程模板字段：基线提交（课程材料中的 C0）完整 40 位 SHA |
| `baseline.commit` | string / 是 | 基线产物所对应的提交；与 `input.base_commit` 重复，二者不一致时只给出提示，不作为拒收条件 |
| `baseline.configuration_id` | string / 是 | 必须与 `input.configuration_id` 相同，否则基线图不可比 |
| `baseline.producer_job_id` | string / 是 | 产生基线图与报告的任务编号，可以是 `FULL_CHECK` 或更早的 `INCREMENTAL_CHECK`（**A2 补充**，模板未列） |
| `baseline.actual_graph_uri` | string / 是 | 基线实际图入口；本样例指向 A1 的 `ACTUAL_GRAPH` |
| `baseline.error_report_uri` | string / 是 | 基线发现列表入口，用于判定新增 / 消除（**A2 补充**，模板未列） |
| `environment.image` | string / 是 | 可获取且以 sha256 digest 固定的构建镜像，须与基线配置一致 |
| `environment.producer_job_id` | string / 否 | 产生环境的 DRAFT 任务编号；手动提供环境时可省略 |
| `configuration_id` | string / 是 | 构建配置标识（课程模板写作 `cc-MODE0` 这种形式）；编译器、编译选项或环境变化时须与下游确认并更新 |
| `build.project_root` | string / 是 | checkout 内的项目相对目录；本例是仓库根目录 `.` |
| `build.clean_command` | string / 是 | 在项目目录执行的清理命令 |
| `build.command` | string / 是 | 清理成功后执行的完整构建命令 |
| `changed_paths` | string[] / 否 | 调用方给出的变更路径提示，相对于 `build.project_root`；权威范围是结果里的 `scope.changed_paths` |
| `timeout_seconds` | integer > 0 / 是 | 增量检测总超时秒数 |

`baseline` 是 EChecker 的专有必填输入：缺少 `baseline`、或 `baseline` 缺少 `commit`、`configuration_id`、`actual_graph_uri`、`error_report_uri`、`producer_job_id` 的请求必须被拒绝；`input.base_commit` 缺失也属于非法请求。本目录 `validate.py` 覆盖了这些反例。字段缺失是硬错误，值重复（`base_commit` 与 `baseline.commit`）不是。

### 与课程模板的对应关系

课程备查页（EChecker 输入输出）给出的骨架是：

```json
{ "job_type": "INCREMENTAL_CHECK",
  "input": { "base_commit": "C0 的完整 SHA",
             "repository": { "commit": "C1 的完整 SHA" },
             "baseline": { "actual_graph_uri": "artifact://.../actual.json",
                           "commit": "C0 的完整 SHA",
                           "configuration_id": "cc-MODE0" } } }
```

本目录的字段名与该骨架一致，并做了两处**模板之外的补充**：`baseline.producer_job_id`（追溯基线由哪个任务产生）和 `baseline.error_report_uri`（没有基线发现列表就无法确定“新增”与“消除”）。两个字段的命名沿用模板风格，按“合理即可”保留。

模板在 `input.base_commit` 和 `baseline.commit` 给出同一信息，本接口保留两处以对齐模板骨架，但不把“两处不一致”当作拒收条件，仅在 `validate.py` 中输出 `WARN` 提示；真正的基线归属仍以 `baseline.commit` 与基线产物自身记录为准。

课程模板的产物地址写作 `artifact://...`，A1 为了离线可读选择了 `repo://`；两种写法都不违背公共 Schema，最终存储与下载方式属于 B3 的 ADR 待决项。

### output 字段

| output 字段 | 含义 |
| --- | --- |
| `scope.changed_paths` | 本次实际采用的变更路径，必须覆盖调用方提示 |
| `scope.checked_targets` | 本次重新构建并重新比对的构建目标 |
| `scope.reused_targets` | 直接复用基线实际图、未重新构建的目标 |
| `summary.missing_count` / `redundant_count` | 本次结果中 MD / RD 的数量 |
| `summary.new_count` / `carried_over_count` | 本次结果相对基线的状态分布 |
| `summary.resolved_count` | 基线中不再检出的发现数量 |
| `summary.checked_target_count` | 等于 `scope.checked_targets` 的长度 |
| `findings[]` | 本次结果，字段与 A1 的 finding 一致，另加 `status`（`NEW` / `CARRIED_OVER`） |
| `resolved_findings[]` | 基线的 `finding_id`、类型、目标、依赖、`baseline_commit` 与 `resolution` |

关于 `resolved_findings`：`resolution` 只表示“本次检查范围内不再检出”（`NO_LONGER_DETECTED`）或“已不在检查范围”（`OUT_OF_SCOPE`），不声称某个提交或某人修复了它。基线里的每一条发现必须在本次结果里是 `CARRIED_OVER`，或者出现在 `resolved_findings` 中，不能静默丢失去向。

## 本例的含义

基线是 A1 的 FULL_CHECK 结果：提交 `1111...` 在 `gcc-default-v1` 配置下，实际图有 `main.o -> config.h`，声明图没有，因此 MD `g16-md-001`；声明图有 `main.o -> unused.h` 而实际图没有，因此 RD `g16-rd-001`。

本次提交 `3333...` 改动了 `Makefile` 和 `main.c`：`Makefile` 把 `config.h` 加入 `main.o` 规则并删除 `unused.h`，但 `main.c` 新增了 `#include "util.h"` 而规则未同步。于是：

- 新增 MD `g16-inc-md-001`（`main.o` 依赖 `util.h`），`status` 为 `NEW`；
- 基线的两条发现都不再出现，写入 `resolved_findings`，`resolution` 为 `NO_LONGER_DETECTED`；
- `CARRIED_OVER` 为空；
- 正常的 `main.o -> main.c` 边在两张图中都保留。

增量策略在样例里是这样的：声明图在本次提交上整体重新解析（只需读文件，不需要构建环境），实际图只重建受影响目标再与基线合并，因此 EChecker 的 `ACTUAL_GRAPH` 可以继续作为下一次增量检测的基线。本例只有 `main.o` 一个目标且它受影响的，所以 `reused_targets` 为空；若改动波及全部目标，调用方应直接提交 `FULL_CHECK`。

这是用来解释数据交换的最小图，不定义 EChecker 的完整检测算法。正式算法还要处理间接依赖、头文件变化判定、目标级增量边界等情况。

## 产物格式和读取方式

任务顶层 `artifacts` 使用 A3 的公共产物结构。消费者按 `type` 寻找产物，不依赖数组顺序。

本目录沿用 A1 的 `repo://` **本地契约样例**地址约定：删除前缀后，从 DevOps-G16 仓库根目录解析相对路径。读取双方需使用同一份契约仓库版本；路径不得越出仓库。`validate.py` 演示了实际解析和读取。

三份产物均带有 `schema_version`、`sample_origin`、`producer_job_id`、`repository`、`configuration_id`。图使用 `nodes`（相对路径字符串列表）和 `edges`（`target`、`dependency` 对象列表），边的方向是构建目标指向依赖文件，与 A1 格式一致。`actual-graph.json` 另有 `merge_policy` 和 `baseline` 块（`commit`、`configuration_id`、`producer_job_id`、`actual_graph_uri`），记录合并策略与来源基线，便于消费方核对；`error-report.json` 的 `findings`、`resolved_findings` 与任务内联列表相同，目的是演示文件交接与直接查询，后续修改须同步。这份人工误差报告仍是 A1 的实现选择，并非已公开的标准格式。

`sha256` 在公共 Schema 中是可选字段。本样例未填写，避免在仓库内部产生哈希耦合；A2 的口径是**不强制**填写，需要核验产物完整性的一方可以自行使用。

## 与其他成员的交接

| 对方 | 需要确认的内容 |
| --- | --- |
| A1 / BuildChecker | 基线入口使用 A1 的 `ACTUAL_GRAPH` 与 `ERROR_REPORT`：`uri`、`producer_job_id`、`repository`、`configuration_id` 是否长期稳定；`nodes`/`edges` 是否需要支持目标以外的节点类型；`actual-graph.json` 是否允许被 EChecker 作为下一次基线（包括由 `INCREMENTAL_CHECK` 产出的图） |
| B1 / DRAFT | 增量检测仍需可用镜像；`environment.producer_job_id` 的语义沿用 A1 提案，待 B1 确认 DRAFT 响应是否直接给出镜像 digest |
| B2 / MDFixer | 只消费 `ERROR_REPORT` 中标为 `MISSING` 的 `findings`；`resolved_findings` 表示不再检出，MDFixer 不应把它当作待修项 |
| A3 | 检查本目录的公共字段和枚举是否与 `task.schema.json` 一致（`INCREMENTAL_CHECK`、状态枚举、`jobRecord` 八个公共字段、产物结构）；`schema_version` 仍为 `1.0.0`，未修改公共模型 |
| B3 | 将基线版本策略（基线产物保留多久、`artifact://` 与 `repo://` 如何统一）、错误码统一、“变化波及全部目标时改交 FULL_CHECK”和幂等行为写入公共 ADR 或 Backlog；`sha256` 按不强制处理 |

A2 已定的口径：`baseline.producer_job_id` 与 `baseline.error_report_uri` 保留，命名按模板风格合理即可；`base_commit` 与 `baseline.commit` 的重复不强制一致（仅提示）；`changed_paths` 是调用方提示，结果必须覆盖它；基线产物 `sha256` 不强制填写；`resolution` 沿用 `NO_LONGER_DETECTED` / `OUT_OF_SCOPE`；`reused_targets` 以构建目标为粒度。

仍需搭档组确认：A1 产物字段与 `nodes`/`edges` 是否长期稳定；`artifact://` 与 `repo://` 如何统一（B3 的 ADR）；公共错误码与幂等行为的最终统一（B3）。

## 校验

`contract.schema.json` 通过引用复用 A3 的公共模型，补充 `INCREMENTAL_CHECK` 的输入和结果约束；没有修改公共 Schema。必填字段缺失由 Schema 拒绝；跨实例的一致性规则无法用 JSON Schema 表达（基线配置必须与请求一致、`base_commit` 必须不同于头提交、头提交发现必须与基线闭合、实际图不得改动未重检目标、结果必须覆盖变更提示），由 `validate.py` 检查。`base_commit` 与 `baseline.commit` 的重复值不属于拒收条件，仅输出提示。

在仓库根目录运行（Python 3.9+；缺少依赖时先执行 `python -m pip install "jsonschema>=4.18,<5"`）：

```bash
python contracts/echecker/validate.py
```

脚本检查公共和服务专有 Schema、请求/结果关联、实际读取基线的 `ACTUAL_GRAPH` 与 `ERROR_REPORT` 并核对提交/配置/任务来源、基线增量闭合（基线发现 = 复用 + 解决）、三份产物读取与图/报告一致性，并验证受理/运行中/失败/超时合法样例及非法输入与交接反例。它仅校验离线接口样例，不构建镜像、不运行检测器，不代表双方联调完成。
