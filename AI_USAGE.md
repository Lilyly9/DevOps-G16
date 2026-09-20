# AI 使用记录

每位成员只填写自己的工作。记录应说明 AI 提供了什么建议、人工怎样判断，以及最终如何验证。

## A3

### 工具与任务

- 工具：OpenAI Codex
- 任务：阅读 E2 分工材料，设计四个服务共用的异步任务 Schema，整理 README 中的公共契约说明。

### 提示摘要

要求按照课程文件规定的 A3 分工和执行顺序，在现有仓库中完成公共任务模型，不替其他成员伪造接口文件或贡献记录。

### AI 建议

- 使用 JSON Schema Draft 2020-12 描述公共格式。
- 分开描述创建请求、HTTP 202 受理响应和完整任务记录，避免创建请求伪造尚未产生的 `job_id`。
- 统一四类 `job_type` 和六类 `status`。
- 将服务专有内容保留在 `input` 和 `output`，把系统执行错误与 MD/RD 检测发现分开。
- 为大型依赖图、日志和 Patch 定义公共产物引用。

### 人工采纳、修改与拒绝

- 采纳生命周期分层，因为课程材料中的创建请求、202 响应和可查询 Job 所处阶段不同。
- 采纳课程规定的公共字段、任务类型和状态名称。
- 保留可选扩展字段，以支持后续兼容扩展。
- 没有把 EChecker 的 `baseline` 等服务专有字段写进公共层，避免公共 Schema 侵入 A1、A2、B1、B2 的职责。
- 没有生成其他成员的 request/response，也没有填写未知成员姓名或声称他们已经确认设计。

### 验证

- 使用 `jq empty contracts/task.schema.json` 验证 JSON 语法。
- 使用 `check-jsonschema --check-metaschema` 完成 Draft 2020-12 元 Schema 校验。
- 检查任务类型、状态枚举和 `jobRecord` 的八个必需公共字段。
- 两个合法生命周期样例通过公共 Schema；非法任务类型、成功但无输出、失败但无错误三个反例均被拒绝。
- 使用 `git diff --check` 检查空白错误。

## A1

### 工具与任务

- 成员：焦龙（Git 作者 `illusiri`）。
- 工具：OpenAI Codex。
- 任务：阅读课程 PPT、论文背景及成员分工，检查 A3 的公共模型，在指定 DevOps-G16 仓库内完成 BuildChecker 接口样例，并仅更新 README 中 A1 相关信息和进度。

### 提示摘要与 AI 建议

- 用户先要求解释 E2，再明确本人为 A1，并要求等待 A3 完成公共模型后开展工作。
- A3 完成后，用户指定 `第2次上机实验/Project/DevOps-G16`，要求完成 A1 工作并更新 README；随后明确姓名为焦龙，其他无关 A1 的信息不要动。
- AI 建议沿用 `jobSubmission` / `jobAccepted` / `jobRecord` 分层，FULL_CHECK 的发现使用 `SUCCEEDED` + `output.findings`。
- AI 建议补充人工 MD/RD 样例、可实际读取的图和报告、服务专有 Schema 与离线校验，检查下游交接所需的仓库版本、配置和任务来源。

### 人工指示与本次处理

- 已确认的人工指示：本人角色为 A1、姓名为焦龙；只处理指定仓库内的 A1 内容，不修改其他成员信息。
- 本次按 A3 模型保留公共字段，将专有约束放入 BuildChecker 自己的 Schema，未修改公共 Schema。
- 样例全部标明 `MANUAL_FIXTURE`，使用占位仓库、镜像和提交；未声称运行真实检测器。
- `repo://`、图格式、镜像 digest 和幂等处理属于 AI 辅助形成的 A1 提案，待本人及消费方审阅；没有代写“全组已采纳”或伪造人工确认。
- 未代做 A2/B1/B2 的接口或 B3 的公共设计文档。

### 验证

- 使用 Python `jsonschema 4.23.0` 的 Draft 2020-12 校验器及 `referencing 0.30.2`，离线解析公共 Schema 引用。
- 两份 Schema 元校验通过；创建、完成、受理、失败、超时共五种合法消息通过公共和服务 Schema。
- 读取三份 `repo://` 产物，核对生产任务、仓库/commit、配置、内联与文件报告、图节点/边及 MD/RD 示例证据。
- 十个非法消息反例被拒绝；四个交接反例（提交不一致、生产任务不一致、统计不一致、路径越界）被拒绝。
- 校验命令：`python contracts/buildchecker/validate.py`；仅为离线契约检查，不是算法验证或组间联调。
- 关联文件：`contracts/buildchecker/`、README 的 A1 信息、本记录及 CONTRIBUTIONS 的 A1 部分。提交版本见 CONTRIBUTIONS。

## A2

### 工具与任务

- 成员：万宇；Git 作者：`adscfe <asdfs1243@noreply.gitcode.com>`。
- 工具：GitHub Copilot（VS Code，模型 DeepSeek V4 Flash）。
- 任务：在 A3 公共任务模型和 A1 BuildChecker 交接约定的基础上，完成 EChecker 增量检测接口样例，并只更新 README 中 A2 的信息与进度。

### 提示摘要与 AI 建议

- 用户先说明本人为 A2，要求完成任务并只更新属于本人的内容，姓名等未知信息不得由他人代填。
- AI 建议沿用 `jobSubmission` / `jobAccepted` / `jobRecord` 分层，`job_type` 使用公共枚举中的 `INCREMENTAL_CHECK`。
- 用户提供课程《E2 需求与接口契约》PPT 路径后，AI 提取备查页（EChecker 输入输出），发现自己的初版字段名与模板不同：模板是 `input.base_commit` 与扁平的 `baseline.{actual_graph_uri, commit, configuration_id}`。人工决定改向模板对齐，把 A2 自己的补充（`producer_job_id`、`error_report_uri`）单独标注为待确认项，而不是默默发明字段。
- 用户提供姓名（万宇）和 Git 身份（`adscfe`）后，AI 填入 README 小组信息、CONTRIBUTIONS 与 AI_USAGE，未改动其他成员的姓名和贡献。
- AI 把“模板之外的补充字段是否保留”“`base_commit` 与 `baseline.commit` 的冗余如何处理”列为待确认项并保持硬校验；用户的口径是“冗余跳过，提示，命名合理即可，不强制”，于是 AI 把重复值的一致性从拒收条件降为 `WARN` 提示（并补一条正向测试证明“不一致也受理”），其余项按提示、不强制处理。这说明人工比 AI 更愿意接受课程模板带来的冗余，AI 只负责把口径写回契约与校验。
- AI 建议把 `baseline` 定义为“上一次检测任务 + 基线提交 + 配置 + `ACTUAL_GRAPH` + `ERROR_REPORT`”，并用基线的 `ERROR_REPORT` 判定 `NEW` / `CARRIED_OVER` / `RESOLVED`，而不是凭猜测推断历史发现。
- AI 建议实际图采用“受影响目标重建、其余边复用基线”的合并策略，使 EChecker 产出的 `ACTUAL_GRAPH` 能继续作为下一次增量检测的基线。

### 人工指示与本次处理

- 已确认的人工指示：角色为 A2；交付完整版（请求/结果样例、专有 Schema、离线校验、接口 README、人工产物）；只更新本人负责的文件与本人条目。
- `baseline` 的字段集合、`resolution` 的语义（只表示不再检出，不表示某人修复）、`changed_paths` 作为提示、基线哈希是否强制、`reused_targets` 的粒度，均标记为 A2 提案或待确认项并写入接口 README 的交接表，没有声称全组已采纳。
- 样例全部标明 `MANUAL_FIXTURE`，使用占位仓库、镜像和提交；未运行检测器，未构建镜像。
- 未代做 A1/B1/B2 的接口或 B3 的公共设计文档，也未填写其他成员的姓名和贡献。

### 验证

- 使用 Python 3.11.9 的 `jsonschema` Draft 2020-12 校验器及 `referencing` 离线解析公共 Schema 引用。
- 两份 Schema 元校验通过；创建、完成、受理、运行中、失败、超时共六个合法消息通过公共和服务 Schema。
- 实际读取 A1 的 `ACTUAL_GRAPH` 与 `ERROR_REPORT`，核对仓库、提交、配置和任务来源，并检查基线增量闭合（基线发现 = 复用 + 解决）与未重检目标的图合并。
- 二十五个非法消息反例被拒绍，包括缺少 `baseline`、`baseline` 缺少 `commit` / `actual_graph_uri` / `error_report_uri`、`base_commit` 与头提交相同、结论计数不一致等。
- 十二个交接反例被拒绍，包括基线配置不一致、基线产物来源不一致、增量未闭合、产物路径越界、未重检目标被改动；`base_commit` 与 `baseline.commit` 不一致则故意保留为可受理，只输出提示。
- 校验命令：`python contracts/echecker/validate.py`；仅为离线契约检查，不是算法验证或组间联调。
- 关联文件：`contracts/echecker/`、README 的 A2 信息、本记录及 CONTRIBUTIONS 的 A2 部分。提交版本见 CONTRIBUTIONS。

## B1

### 工具与任务

- 成员：郭德林；Git 作者：`DelinGuo`。
- 工具：Claude Code（模型 Claude Sonnet 4.6）。
- 任务：在 A3 公共任务模型和 A1/A2/B2 既有样例的基础上，完成 DRAFT 环境生成接口样例，并只更新 README 中 B1 的信息与进度。

### 提示摘要与 AI 建议

- 用户要求完成成员 B1 对应的部分。AI 发现当前仓库不存在 `contracts/draft/` 文件且 git 历史无 B1 提交，判断前次会话生成的样例随仓库重新克隆丢失，本次在当前仓库重建。
- AI 从课程 PPT《E2_需求与接口契约_20260910.pptx》备查页提取 DRAFT 语义：输入为 `repository.url + commit`、`build.command + verify_command`、`max_iterations` 与时间限制（slide 20）；输出为 Dockerfile 与镜像引用、每轮日志/修改/选择理由、最终构建和验证结果；创建端点参考 slide 27 的 `POST /v1/dockerfile-jobs`；slide 4 确认 DRAFT 交接内容为环境、镜像、日志。
- AI 建议用两轮迭代样例说明迭代语义：第 1 轮缺 bison 构建失败，第 2 轮补齐后通过两条成功判据，产出 DOCKERFILE 一份与 BUILD_LOG 两份共三份产物。
- AI 建议 `validate.py` 除 Schema 校验外，实际读取 A1/A2/B2 的请求样例，核对 `producer_job_id`、镜像 digest 和 `configuration_id` 一致，把「三个下游消费 DRAFT 输出」变成可执行的检查。

### 人工指示与本次处理

- 已确认的人工指示：本人在 README/AI_USAGE/CONTRIBUTIONS 中写入姓名「郭德林」（Git 作者 `DelinGuo`）；其余接口细节为 B1 提案，未声称全组已采纳。
- `configuration_id` 放入 DRAFT 输入、成功判据职责划分、「源码级无法构建时 DRAFT 报 FAILED 还是让 BuildChecker 继续诊断」、迭代耗尽错误码是否复用 `ENV_3002`，均列为待确认项写入接口 README 的交接段。
- 样例全部标明 `MANUAL_FIXTURE`，使用占位仓库、镜像和提交；未运行 DRAFT，未构建真实镜像。
- 未代做 A1/A2/B2 的接口或 B3 的公共设计文档，未修改其他成员的文件与记录段。

### 验证

- 使用 Python 3.14.5 的 `jsonschema 4.26.0` Draft 2020-12 校验器及 `referencing`，离线解析公共 Schema 引用。
- 两份 Schema 元校验通过；创建、受理、完成、失败、超时共五种合法消息通过公共和服务 Schema。
- 实际读取 Dockerfile 与两份逐轮日志，核对 `MANUAL_FIXTURE` 标注、成功判据标记行与请求 commit 一致；实际读取 A1/A2/B2 请求样例核对镜像、配置与生产任务来源。
- 十三个非法消息反例被拒绝；九个非法交接反例（配置不一致、产物引用缺失/类型错误、轮次不连续、末轮非 SUCCESS、生产任务不一致、路径越界、commit 不一致、下游镜像不一致）被拒绝。
- 校验命令：`python contracts/draft/validate.py`；仅为离线契约检查，不是环境构建验证或组间联调。
- 关联文件：`contracts/draft/`、README 的 B1 信息、本记录及 CONTRIBUTIONS 的 B1 部分。提交版本见 CONTRIBUTIONS。

## B2

### 工具与任务

- 工具：claude+deepseek v4-pro
- 任务：完成 MDFixer（REPAIR）接口样例

### 提示摘要与 AI 建议

- 用户先要求明确项目目标并填写 gitignore，随后确认本人为 B2，要求按 A1 的既有风格完成 MDFixer 接口，最后同步进度到 README。
- AI 建议沿用 `jobSubmission` / `jobAccepted` / `jobRecord` 分层，REPAIR 的修复结果使用 `SUCCEEDED` + `output` 表示。
- AI 建议 MDFixer 仅消费 `type == MISSING` 的发现，通过 `error_report_uri` 引用 BuildChecker 的 ERROR_REPORT，并把 Patch 作为 `GIT_PATCH` 产物传递。
- AI 建议补充服务专有 Schema、可实际读取的 Git Patch 产物和离线校验，检查报告来源的仓库、commit、配置与生产任务一致性。

### 人工采纳、修改与拒绝

- 采纳生命周期分层与公共字段，将专有约束放入 MDFixer 自己的 Schema，未修改公共 Schema。
- 采纳「只消费 MISSING、不删除 RD」的边界，与课程「修复只针对 Missing Dependency」一致。
- 样例全部标明 `MANUAL_FIXTURE`，使用占位仓库、镜像和提交；未声称运行真实修复或重检。
- `repo://`、`error_report_uri`、Patch 产物和「拒绝候选仍为 SUCCEEDED」属于 AI 辅助形成的 B2 提案，待本人及消费方审阅；没有代写「全组已采纳」或伪造人工确认。
- 未代做 A2/B1 的接口或 B3 的公共设计文档，也未代填本人姓名或其他成员信息。

### 验证

- 使用 Python `jsonschema`（4.18+）的 Draft 2020-12 校验器及 `referencing`，离线解析公共 Schema 引用。
- 两份 Schema 元校验通过；创建、完成、受理、失败、超时、拒绝候选共六种合法消息通过公共和服务 Schema。
- 读取引用的 ERROR_REPORT 与 Git Patch 产物，核对报告仓库/commit/配置、仅消费 MISSING、Patch 内容与生产任务来源。
- 十二个非法消息反例被拒绝；五个非法交接反例（消费 RD、报告 commit 不一致、Patch 引用缺失产物、生产任务不一致、路径越界）被拒绝。
- 校验命令：`python contracts/mdfixer/validate.py`；仅为离线契约检查，不是算法验证或组间联调。
- 关联文件：`contracts/mdfixer/`、README 的 B2 信息、本记录及 CONTRIBUTIONS 的 B2 部分。提交版本见 CONTRIBUTIONS。

## B3

待 B3 填写并最终汇总。
