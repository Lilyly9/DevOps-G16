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

待 A2 填写。

## B1

待 B1 填写。

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
