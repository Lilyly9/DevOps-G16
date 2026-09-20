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
- 十三个交接反例被拒绍，包括 `base_commit` 与 `baseline.commit` 不一致、基线配置不一致、基线产物来源不一致、增量未闭合、产物路径越界、未重检目标被改动。
- 校验命令：`python contracts/echecker/validate.py`；仅为离线契约检查，不是算法验证或组间联调。
- 关联文件：`contracts/echecker/`、README 的 A2 信息、本记录及 CONTRIBUTIONS 的 A2 部分。提交版本见 CONTRIBUTIONS。

## B1

待 B1 填写。

## B2

待 B2 填写。

## B3

待 B3 填写并最终汇总。
