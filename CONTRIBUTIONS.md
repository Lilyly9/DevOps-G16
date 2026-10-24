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

- 成员：林涵；Git 作者：`WhiteNights`。
- 负责内容：公共异步任务模型、A 组接口公共字段一致性检查、与 B3 共同维护 README。
- 已完成：`contracts/task.schema.json`；在 A1/A2/B1/B2 接口完成后独立复核公共字段、生命周期、服务 Schema、产物读取和跨服务交接。
- Schema 提交：`381a951b353d899699aa63001297cb982ba8cce5`（`feat(contracts): define shared job schema`）。
- 初始文档提交：`bf520bfd832d0d904b659c8c8470cfb9682f6617`（`docs(e2): record A3 contract decisions`）。
- 最终文档：更新 `README.md`、`AI_USAGE.md`、`CONTRIBUTIONS.md`、`docs/Backlog.md` 和 `docs/INTEGRATION_CHECK.md`，提交说明为 `docs(e2): finalize A3 contract review`。
- 验证：公共 Schema 元校验、八个公共请求/响应样例、19 个 JSON 语法解析和四个服务的完整 `validate.py` 均通过。

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

- 成员：吴佳静。
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

## A3：E3 补充

本人 E3 文件、真实提交与验证范围见 [A3 E3 贡献记录](e3/docs/A3_CONTRIBUTIONS.md)，逐项验收见 [A3 核查报告](e3/docs/A3_REPORT.md)。

## A3：E4 补充

本人 E4 文件、服务器原件核验与真实提交记录见 [A3 E4 贡献记录](e4/docs/A3_CONTRIBUTIONS.md)。

## B1：E3 补充

本人 E3 文件、双层判据实测与真实提交记录见 [B1 E3 贡献记录](e3/docs/B1_CONTRIBUTIONS.md)，任务对照与卡点记录见 [B1 实验报告](e3/docs/B1_REPORT.md)。

## B3：E3 补充

本人 E3 文件、B 组汇总与 §10 四问相互检查见 [B3 E3 贡献记录](e3/docs/B3_CONTRIBUTIONS.md)与 [B3 汇总报告](e3/docs/B3_REPORT.md)。本阶段负责把 B1/B2 样本并入四服务七列总表（`e3/README.md`）、沉淀 `docs/Backlog.md` 与 `docs/ADR.md`（新增 ADR-004）并核对 B 组命名对齐；B3 姓名：吴佳静，最终提交 SHA 待提交后填写。

### E3 A3 跨组收尾（2026-10-05）

A3 对 B 组实际复跑及四服务验收见 [收尾报告](e3/docs/A3_CROSS_REVIEW.md)，统一校验命令为 `python3 e3/validate_e3_all.py`。总表全员确认由用户明确提供，技术核验通过。

### E4 A3 本人交付收尾（2026-10-05）

本人按 B 组 README 在独立克隆成功重跑修正版，记录完整 SHA、成功路径和终端输出来源；交付及共同待办见 [A3 报告](e4/A3_REVIEW.md)。B1/B2 双人对照尚未提供，不代填或声明全组通过。

## B3：E4 补充

本人 E4 对相邻 A 组的相互检查见 [B3 相互检查入口](e4/B3_README.md)与 [结构化跨组记录](e4/docs/B3_A_CROSS_RECORD.json)。本次为仓库审查 + 证据链核对：A 组四份 README 完整、A1/A2 各有同 SHA `9feb7a…` 成功记录、仓库与 Git 历史无 Key、证据目录对应模板 SHA；未在 A16 ECS 实际重跑 `make all`、线上镜像引用 A3 独立核验。姓名：吴佳静；学号 241880597；Git 作者 `jenicifor`。
## A2：E5–E7 补充

- 成员：万宇；学号：241880496；Git 作者：`adscfe <asdfs1243@noreply.gitcode.com>`；分支：`e5-7/A2-241880496`。
- 负责阶段：E6（BuildChecker 自动检测与修复复检），对应组内私发的任务分工文档 §5 A2 与 §7.1 的 A2 门槛值。
- 仓库结构：把 A 实验包入库到 `e5/A-buildchecker/`（唯一一份代码），并按共用仓库约定拆成 `e5/`、`e6/`、`e7/` 三个阶段目录（`e6-7` 合并目录已废弃）。
- 代码改动：新增 `e5/A-buildchecker/services/buildchecker/tests/test_extra_241880496.py`（2 项边界测试）；未修改服务实现，未改动他人测试。
- 交付证据：`e6/evidence/A2-241880496/`（`index.md`、before/after 的 findings 与两张图、`make-db.txt`、关键 trace `t.14`/`t.15` 与 `trace-index.md`、`verify-e6.json`、单测日志、自证 gate 结果）。
- 报告：`e6/reports/A2-241880496.md`；阶段汇总与状态：`e6/README.md`。
- 关键结果：`MISSING main.o → config.h`、`REDUNDANT main.o → unused.h`；修复后 `findings=[]`、仅 Makefile 哈希变化；单测 15 → 17 passed；自证 gate 8/8。
- 运行环境：Ubuntu 26.04 LTS on WSL2（非组内云主机），4 CPU / 7.8 GiB，Docker 29.5.2；已在 `doctor/env.json` 与报告"故障与限制"中注明。
- 提交（分支 `e5-7/A2-241880496`）：
  - `c343b5b` `feat(e5-7): import A-buildchecker teaching lab from course package`
  - `cbbfb9e` `test(e5-7): add A2 boundary tests for Make database scope and order-only deps`
  - `a40a727` `docs(e5-7): add A2 E6 evidence, report and README section`
  - `49ceb98` `docs(e5-7): add E5-E7 task allocation and low-coupling handoff rules`
  - `6ab0c1f` `refactor(e5-7): split into per-stage e5/e6/e7 folders with shared code in e5`
  - `1705856` `docs(e5-7): fix remaining e5-7 paths after per-stage split`
- 未完成 / 未代做：A1 的 E5、A3 的 E7 与 CI 仍为占位；正式 gate、CI 运行与合并记录不由本人填写。

## E5–E7 · A3（241880464）

负责 A 轨道 E7 正式 gate、补充循环 phony 测试、根级 A CI 工作流、失败/恢复演示模板及证据报告。代码提交 `6c12a45c6a0ad111f077cb5234c3bd7f5a8d3a73`，作者 241880464（沿用本人邮箱）。演示分支不改算法。保护配置只起草，未应用；最终合并未完成。证据入口：`e7/reports/A3-241880464.md`。


### A3 新增课程材料补齐（2026-10-24）

本地源码提交 `a977ac905e7767ec4ec438fe3b4d84963b3dd824`：补齐 A CI 扫描与语法步骤，修复旧编码历史扫描，增加两项回归，导入官方演示测试。实际重建正常/错误/修复镜像并跑 gate；补验收 CSV、报告、来源哈希、脱敏证据与本地备份。未修改 B3 工作流、未代填组员、未推送或配置保护。
