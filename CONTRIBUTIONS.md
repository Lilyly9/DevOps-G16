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

## B2：E6-B 补充（241880543，2026-10-25）

- 分支：`e5-7/B2-241880543`；同步基线：`656dcd94b7bef84f9d477f34209a1c9494171810`；个人服务镜像：`course1020-draft:241880543`。
- 已完成：环境和 Git 身份检查、课程源码与测试审阅、Windows 本地单测 24 passed、14 个 Python 文件语法检查、课程入口平台拒绝与证据校验失败的真实输出归档、五项待验收核对表、`prepare_candidate()` 与安全限制说明、Linux 续跑命令与只读独立复核示例。
- 交付：[报告](e6/reports/B2-241880543.md)、[续跑步骤](e6/reports/B2-241880543-linux.md)、[证据索引](e6/evidence/B2-241880543/index.md)、`e6/README.md` 中仅 B2 的状态及入口、本条贡献和 AI 使用记录。
- 未完成：当前 Windows 无 Docker，真实服务镜像构建、E6 两轮构建、同 image ID 运行及 `input_sha256` 复核均需 Linux 云服务器。B2 当前不标记验收通过。
- 边界：没有修改课程源码、Dockerfile、他人测试/证据、CI 配置或远程设置；未执行 push、创建 PR 或合并。本地提交已由用户后续授权，准确提交 SHA 以本分支 `git log` 为准，不预填尚未生成的哈希。

## A2：E8—E10 补充（241880496，2026-11-10）

- 成员：万宇；学号 241880496；Git 作者 `adscfe <asdfs1243@noreply.gitcode.com>`；分支 `student/241880496/e8-e10`；本人主责阶段 E9-A（A 轨道三阶段全部完整跟做）。
- 环境：本机 Windows 11 + Docker Desktop 29.5.2（WSL2，4 vCPU / 8 GiB）与组内服务器（Linux 5.15 / 2 vCPU / 3.5 GiB / Docker 29.1.3）两套；实验镜像 `course-e8e10:241880496`，本机 `sha256:0a3e46d7…`、服务器 `sha256:22eae619…`，容器内 Debian 13、gcc 14.2.0、make 4.4.1、strace 6.13、Python 3.13.14。三条 A 轨道路线在两端都完整跑通，结果一致。
- 代码改动：`labs/e8e10/lab.py:48` 新增 `invalidation(key, old)`，`lab.py:81` 在 `scan()` 返回 `invalidation` 失效原因（不改刷新语义）；新增 `labs/e8e10/test_student_241880496.py`（3 项，间接 include 边集 / 仅源码失效原因 / 纯函数体不失效），`test_profile.py` 原 7 项未改。
- 交付证据：`e8/evidence/A2-241880496/`（真实 BuildChecker trace、make-db、两图、findings、7 步日志）、`e9/evidence/A2-241880496/`（baseline+C1/C2/C3、三份构建日志、10 步日志、内部历史）、`e10/evidence/A2-241880496/`（30 对 JSON、results.csv、performance-summary.csv、gate.json、最终 BuildChecker、13 步日志、`unit-tests.log`）。
- 报告：`docs/students/241880496/e8-e10/`（个人报告、ADR、AI_USAGE）；本文件与根 `AI_USAGE.md` 的 A2 段落。
- 关键结果：E8 `MISSING main.o→config.h`、`REDUNDANT main.o→unused.h`，未变化时两目标复用；E9 C1 复用、C2 刷新并新增 MD `extra.h`、C3 消除两项 MD 保留 RD；E10 六场景 30 行 `equal=True`、`gate.json rows=30 passed=true`、动态重检只剩 RD；单测 `Ran 10 tests ... OK`。
- 服务器复核（2026-11-10）：在 A16 共享服务器（`47.96.152.132`，Linux 5.15 / 2 vCPU / 3.5 GiB / Docker 29.1.3）克隆 `main`（`aecdbb3`）到 `~/devops-students/241880496/DevOps-G16`，重建镜像 `sha256:22eae619…`，按同一手册重跑三条 A 轨道路线（E8 `work/e8-A-manual.zycx8k`、E9 `work/e9-A-manual.0kqyk4`、E10 `work/e10-A-manual.861iod`，单测 10 passed），发现与本地一致；服务器计时显示复用场景增量约为全量的 1/5.8。材料 ZIP、提交存档与服务器原件已放在 `/root/devops-submissions/241880496/`（含 `README.md`、`交付状态.json`、`双端校验.log` 与 sha256），并 scp 回本机同结构目录。

## A2：E13-E14 补充（241880496）

- A2 定向交付：接入 `labs/e13e14/handoff_a_to_b.py`，将已成功的 E11-A `incremental-check` 报告转换为 B 可消费的 `fixed-md`，校验目标 SHA、job/trace、artifact URI、内容 SHA 和大小。
- C2/C3/C8：在 `labs/e11e12/pipeline.py` 增加固定报告传输 SHA 校验；新增 `labs/e11e12/test_student_241880496_e13e14.py` 与 `labs/e13e14/test_handoff.py`，覆盖旧报告拒绝、篡改哈希拒绝和幂等冲突。
- 定向验证：交接测试 3 项、原契约测试 10 项、A2 专项测试 4 项，合计 17 项通过。
- 服务器执行：在 `47.96.152.132` 运行本人及原契约测试 22 项通过；tokenstat E11-A 和 `fixed-md` 报告交接成功；C2 返回 `STALE_REPORT`、C3 返回 `ARTIFACT_HASH_MISMATCH`；真实 C8 同键同请求两次 HTTP 202 且同 job，不同 target HTTP 409 `IDEMPOTENCY_CONFLICT`。H1 jsmn 的 E11-A 也成功。
- H1 jsmn：E11-A 后，使用隔离候选副本 `candidate-a2-strace.Dockerfile` 增加 `strace`，在服务器跑通完整 E12 五阶段；job `job-070b682748c64331afa1d7815439098e`，候选镜像 ID `sha256:b34e18e15363ef86412b81a3d8800c7bc922714cfd1146be857ef0e1ecec10da`，未覆盖课程原候选。
- E14：本机 Docker Desktop 29.5.2 上固定样例五阶段通过（job `job-207b9359db854f218e24d5043f4e0f9b`）及 H1 jsmn 五阶段通过（job `job-9031e40cbcff42f1a5415e1b8eb4efa9`）；EChecker 报告 SHA、五阶段 job/trace 关联及产物 SHA 均核验。日志扫描 332 个文本文件，0 hits / 0 errors。首次本机尝试因 Windows Git CRLF 转换导致 patch 不匹配；以单次进程 `core.autocrlf=false` 重跑后通过，未改动原始提交。
- 服务器初次 E14 DRAFT 受 Docker Hub 拉取超时阻断；后来确认本机 Docker Hub 可用并完成上述成功重跑。服务器服务测试使用的是 `course-e11e12:241880464` 的本地别名，并非新构建的服务器个人镜像。
- 未代做：未声明真实跨组 C1-C8 全集、H2/H3、E14 配对组项目 E2E、故障恢复、RC 或远端 CI 已通过；成功与失败原始证据分别归档于个人记录目录。
- 文档：[个人索引](docs/students/241880496/e13-e14/index.md)、[ADR](docs/students/241880496/e13-e14/ADR.md)、[AI_USAGE](docs/students/241880496/e13-e14/AI_USAGE.md)。
- 未完成 / 未代做：未实施"按目标失效"（会改变既有测试与手册断言，需组内统一口径）；A1/B1/A3/B3 各阶段结论不由本人填写；与 B 组联调属 E11—E12。
- 提交：`adf0421` `feat(e8-e10): report invalidation reasons and add A2 student tests`；证据与文档提交 SHA 以本分支 `git log` 为准（未在提交内填写自身 SHA）。
## B2：E13–E14 本地修复（李敏君，241880543，2026-11-22）

- 修复范围：labs/e11e12/pipeline.py 的验证 / 最终重检回滚边界；labs/e8e10/lab.py 的异常结果与摘要记录；新增 labs/e11e12/test_student_241880543_e13e14.py（10 项契约）。
- 个人材料：docs/students/241880543/e13-e14/，包含报告、ADR、PR 正文、可复跑 C5 留证入口及原始小件。31 项相关测试通过；实际 Git 损坏补丁被拒绝，源文件和目标提交不变。
- 实际限制：终端网络、源 .git 写入及 WSL 被拒绝；H1、真实 Docker 语义补丁复验及 E14 四容器待执行。尚未新建本轮分支、push、创建 PR / Issue 或获得远端 CI，不申报 E13/E14 整组验收通过。
- 当前源码起点 ea75b481a3ba0b4f02f68f8e80f464a4197f6252，工作区修改尚未提交；恢复权限后需同步最新 main 并按个人分支提交。具体环境、命令、退出码和实现文件摘要见个人证据索引。

- 本轮续验：已从 main 28c94de 建立 E13/E14 分支并保留 stash；Linux 全量 75 项、交接 3 项、E8/E10 回归 21 项通过，真实 DRAFT 及同镜像 C5 三路径通过。E14 构建受软件源联网阻断，H1/H3/C1 输入不齐全；上面的权限阻断描述为历史状态，最新证据见索引。

- 再次续做（2026-11-22）：本轮 Windows 10 项 B2 契约及 3 项报告交接通过；源码、证据哈希及 ZIP CRC 核验通过。补齐分工表 B2 行、Issue 正文及 submit.py。源码未再修改；Git 写入、联网、WSL 和独立 clone 的实际限制仍阻止提交 / push / PR，发布入口仅默认校验模式已运行，不宣称已完成远端交付或 E14。

- 新发材料续做：归档用户本次教师原始项目包，固定 H1/H3 的完整 C0/C1、上游身份、候选与请求；新增 run_teacher.py，实际执行 GCC 编译运行、静态依赖扫描和 Git 补丁预检，两个项目均输出 1 并定位 `helper.o -> extra.h`。原仓库前后字节相同且干净。官方 E12 因 Windows 平台在入口返回 2，保留三次尝试，完整 E12、C1 当次交接和 E14 不申报通过。见 [H1/H3 记录](docs/students/241880543/e13-e14/TEACHER_RUNS.md)。

- 本地提交已保存：独立检出 `D:/workspace/DevOps-G16-B2-e13e14-snapshot-20261122` 的实现提交为 `8ec82c35c2a9a6d5774dbaf04cad33e10e564e53`，原工作区暂存与未暂存状态保留。独立检出 13 项测试和提交字节哈希核验通过；实际 fetch/push 均联网失败，Issue/PR/CI 未完成。

- 2026-11-23 B2 续交付：E7 A/B 凭据读取误报修复及回归通过；H1/H3、A1 transfer-eta 当次 C1 修复和固定/H1/H3/真实项目四容器五阶段已有成功原件。新增 E14 project_path/profile 复用及基线配置兼容，详细证据见 docs/students/241880543/e13-e14/index.md。

## A3：E13–E14（林涵，241880464，2026-11-24）

- 报告消费保留哈希校验时读取的原字节。修复 C6 对空角色日志的误判，补齐四服务日志、镜像及产物校验。代码由 PR #34 合入，Issue #33 关闭。
- 实跑 C2/C3/C6/C8、教师发放的 H1–H3、A/B 两个实际项目的报告与四容器验证。云端超时与恢复、本机 B1 原始项目、归档和共同验收范围见 [A3 个人报告](docs/students/241880464/e13-e14/index.md)。
