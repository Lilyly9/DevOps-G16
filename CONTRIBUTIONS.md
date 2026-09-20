# 成员贡献记录

每位成员记录本人负责的文件、提交说明和提交 SHA。未知信息不得由其他成员代填。

## A1

- 成员：焦龙；Git 作者：`illusiri`。
- 负责内容：BuildChecker 全量检测接口的请求、结果、MD/RD 表示和产物读取约定。
- 已完成：`contracts/buildchecker/request.json`、`response.json`、接口 README、服务专有 `contract.schema.json`、三份人工产物及 `validate.py`。
- 文档补充：README 中 A1 姓名/职责/进度、AI_USAGE 的 A1 部分、本贡献记录。
- 验证：五种合法生命周期消息、十个非法消息反例、三份产物实际读取及一致性检查、四个非法交接反例，均达到预期。
- 待协作：A2/B1/B2 交接互查、A3 独立字段复核、B3 汇总公共设计决定；尚未实施实际服务或声称全组已确认。
- 接口提交：`0370ef7111d582c05ac4f283ff033daa94971b84`（`feat(contracts): add A1 BuildChecker handoff examples`），作者 `illusiri`。
- 文档提交说明：`docs(e2): record A1 contribution and progress`；可通过 `git log --oneline --author=illusiri` 查到文档提交 SHA，避免在提交内部填写自身尚未生成的 SHA。

## A2

- 成员：万宇；Git 作者：`adscfe <asdfs1243@noreply.gitcode.com>`。
- 负责内容：EChecker 增量检测接口的请求、基线引用、增量结果与产物读取约定。
- 已完成：`contracts/echecker/request.json`、`response.json`、接口 README、服务专有 `contract.schema.json`、三份人工产物及 `validate.py`。
- 文档补充：README 中 A2 进度、AI_USAGE 的 A2 部分、本贡献记录。
- 验证：六个合法生命周期消息、二十五个非法消息反例、十二个交接与基线反例，均达到预期；校验脚本实际读取 A1 的 `ACTUAL_GRAPH` 与 `ERROR_REPORT`，核对提交、配置和任务来源，并检查基线增量闭合与未重检目标的图合并。接口字段名已按课程备查页的 EChecker 骨架对齐（`input.base_commit` + `baseline.actual_graph_uri`）。
- 已定口径（A2 本人）：模板之外的补充字段保留、命名合理即可；`base_commit` 与 `baseline.commit` 的重复值不强制一致，仅输出提示；`changed_paths` 是调用方提示；基线产物 `sha256` 不强制。
- 待协作：A1/B2 交接互查、A3 独立字段复核、B3 汇总基线版本策略；尚未实施实际服务或声称全组已确认。
- 接口提交：`330b787416afcfeb9789e77666dae197df57847f`（`feat(contracts): add A2 EChecker handoff examples`）、`df310803235768b70eb4d5598cdaa487dd987a13`（`fix(contracts): treat A2 baseline redundancy as a warning`），作者 `adscfe`。
- 文档提交说明：`docs(e2): record A2 contribution and progress`、`docs(e2): record A2 contract decisions`；可通过 `git log --oneline --author=<A2 作者名>` 查到文档提交 SHA，避免在提交内部填写自身尚未生成的 SHA。

## A3

- Git 作者：`WhiteNights`。
- 负责内容：公共异步任务模型、A 组接口公共字段一致性检查、与 B3 共同维护 README。
- 已完成：`contracts/task.schema.json`；在 A1/A2/B1/B2 接口完成后独立复核公共字段、生命周期、服务 Schema、产物读取和跨服务交接。
- Schema 提交：`381a951b353d899699aa63001297cb982ba8cce5`（`feat(contracts): define shared job schema`）。
- 初始文档提交：`bf520bfd832d0d904b659c8c8470cfb9682f6617`（`docs(e2): record A3 contract decisions`）。
- 最终文档：更新 `README.md`、`AI_USAGE.md`、`CONTRIBUTIONS.md`、`docs/Backlog.md` 和 `docs/INTEGRATION_CHECK.md`，提交说明为 `docs(e2): finalize A3 contract review`。
- 验证：公共 Schema 元校验、八个公共请求/响应样例、19 个 JSON 语法解析和四个服务的完整 `validate.py` 均通过；未声称运行真实服务。

## B1

- 成员：郭德林；Git 作者：`DelinGuo`。
- 负责内容：DRAFT 环境生成接口的请求、结果、Dockerfile 与逐轮日志产物读取约定。
- 已完成：`contracts/draft/request.json`、`response.json`、接口 README、服务专有 `contract.schema.json`、三份人工产物及 `validate.py`。
- 文档补充：README 中 B1 姓名/职责/进度、AI_USAGE 的 B1 部分、本贡献记录。
- 验证：五种合法生命周期消息、十三个非法消息反例、三份产物实际读取及内容核对、A1/A2/B2 下游请求的镜像/配置/任务来源核对，以及九个非法交接反例，均达到预期。
- 待协作：A1/A2/B2 交接互查、A3 独立字段复核、B3 汇总公共设计决定；尚未实施实际服务或声称全组已确认。
- 接口提交：`8021fd2`（`feat(contracts): add B1 DRAFT environment handoff examples`），作者 `DelinGuo`。
- 文档提交说明：`docs(e2): record B1 contribution and progress`；可通过 `git log --oneline --author=DelinGuo` 查到文档提交 SHA，避免在提交内部填写自身尚未生成的 SHA。

## B2

- Git 提交作者：`jenicifor`；姓名待本人补充。
- 负责内容：MDFixer（REPAIR）修复缺失依赖接口的请求、结果、Git Patch 产物与读取约定。
- 已完成文件：`contracts/mdfixer/request.json`、`response.json`、接口 README、服务专有 `contract.schema.json`、`artifacts/fix-missing-config-h.patch` 及 `validate.py`。
- 文档补充：README 中 B2 的目录说明、进度勾选与校验命令、AI_USAGE 的 B2 部分、本贡献记录。
- 验证：六种合法生命周期消息、十二个非法消息反例、ERROR_REPORT 与 Patch 产物实际读取及一致性检查、五个非法交接反例，均达到预期。
- 待协作：A1/A2/B1 交接互查、A3 独立字段复核、B3 汇总公共设计决定；尚未实施实际服务或声称全组已确认。
- 接口提交：`b84cee05d9f63f5c4e8bc978df81811f1d3819e5`（`feat(contracts): add B2 MDFixer repair handoff examples`）。

## B3

- Git 提交作者：`Lilyly9`；姓名待本人补充。
- 负责：公共 Job 契约检查与完善、任务状态和错误语义统一、四服务接口集成检查、README 完善、Backlog 公共任务补充、ADR 编写、AI_USAGE 更新。
- 公共契约：复核 `contracts/task.schema.json` 的八个完成态字段、四种任务类型、六种状态和错误对象规则；补充 MD/RD 非系统错误及 artifact URI 的语义说明。
- 集成检查：核对 DRAFT 镜像/配置/生产任务、FULL_CHECK 图与 findings 报告、EChecker baseline/增量结果、MDFixer MISSING-only 输入及 Patch/build/test/recheck 输出。
- 文档：更新 `README.md`、`AI_USAGE.md` 和本记录；新增 `docs/Backlog.md`、`docs/ADR.md`、`docs/INTEGRATION_CHECK.md`。
- 边界：未修改 A1/A2/B1/B2 的接口样例和服务专有 Schema；未把离线 fixture 检查表述为真实服务联调。
- 首轮验证：19 个 JSON 文件通过语法解析；公共字段、枚举和跨文件衔接检查通过。B3 当时的环境缺少 `jsonschema`，因此没有把四个服务校验脚本记为已通过；随后 A3 在独立复核中使用固定版本临时依赖完整运行四个脚本，结果均通过。
- 公共文档提交：`d1f055b47c9093f785a3bc574973d629ff55ec83`（`B3`）。
