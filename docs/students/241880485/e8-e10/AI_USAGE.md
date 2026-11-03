# A1 E8–E10 A 轨 AI 使用记录

成员：焦龙 / 241880485；小组：G16 / A16；日期：2026-11-03。

## 使用的工具与上下文

本次使用 **OpenAI Codex** 辅助阅读课程材料、接入参考实现、编写个人回归测试、自动执行本组服务器实验、读取原始证据和起草本人文档。本轮继续任务时，还使用 Codex 子代理并行审查手册、修订旧分工及审查下载原件与文档。具体底层模型版本未单独记录，不推断型号；不把自动执行或子代理整理写成人工操作、签字或队友确认。

未在教学实验程序中调用外部模型 API，也未为 EChecker 检测或个人测试接入模型候选生成；这与使用 Codex 对话/代码助手是两件事。本次没有生成 MDFixer 的 LLM 候选，也不认领 B 组工作。

提供的主要上下文包括：2026-10-31 E8–E10 详细手册、助教最新“每人完成本组轨道三阶段”要求、课程 `lab.py` 与原 7 项测试、旧 G16 分工、原仓库与实时 Git/PR 状态、实际服务器环境、外层源码 SHA、本人 E8 原件，以及新 E9/E10 的 JSON、构建日志、内部历史 bundle、trace、make 数据库和真实单元测试输出。没有把 `05_来源与验证` 的教师演示、ARM64 示例 SHA、计时、路径或 CI 记录当作本人结果。

## 建议、采纳与拒绝

| 问题 / 建议 | 本次处理 | 理由与核验 |
| --- | --- | --- |
| 如何保持原仓库并避免三阶段代码分叉 | 采纳根 run_lab.py + labs/e8e10 单副本，e8/e9/e10 放阶段证据和索引 | 符合入口、helper 与 workflow 的硬编码路径，保留旧 E4–E7 |
| 个人测试怎样避免改同一个公共测试文件 | 使用 test_student_241880485.py；统一发现模式为 test_*.py | 容器真实输出发现本人方法，8 项通过 |
| 用什么自主案例检验缓存有效性 | 选择在 config.h 中新增 extra.h include | 主文件内容不变但实际依赖应增加，可检查旧图失效和新增 MD |
| 是否只比较发现数量或两份工具输出 | 不采用这种充分性判断；先定义完整人工预期，再比实际边/发现，并做动态核对 | 防止“数量相同但边错误”或两条路径共享错误 |
| 如何解释 config.h 的 openat | 不把单条 grep 或 stat 当成 MD；结合成功调用、编译 recipe 归属、输出及声明 | 标准进程链 13→14→15/16；t.15:579、t.16:23、数据库第1044行 |
| 旧分工能否让 E9/E10 仅引用队友 | 按最新要求改为本人完整执行三个阶段，保留原 E8、创建新 E9/E10 OUT | 本人 C0–C3、30 行矩阵和额外五次结果均有独立原件，不代填他人状态 |
| E9 的图复用是否意味着 Make 不执行 | 分别记录真实 make 与 scan | C1 重编 main.o，而两个目标依赖图仍复用 |
| E10 是否只比较发现数量 | 逐份比较 actual/declared/findings 完整集合，另加输入预期与动态核对 | 标准 30 行、60 JSON；相同条数仍可能指向错误边 |
| 五次测量能否逐次更新 previous | 不采用；每类五次均从同一上一场景历史图扫描 | 防止把刷新场景后四次变成复用，保留可比较口径 |
| 为 E10 自主任务选什么新变化 | 另建项目移除 config.h 的间接 include，并删除 extra.h | 检验旧图减边、extra.h MD 消除；与已有新增 include 测试互补 |
| 真实刷新场景增量略慢时如何报告 | 原样保留中位数、范围及小于 1 的比值 | 不以论文加速倍数替换本次 scan 小样例数据 |
| 资源与环境差异如何报告 | 记录实际 3.5 GiB；环境代码、锁与镜像 ID 未变时复用现有镜像 | 不写为满足 4 GiB 建议，不套用旧 doctor 状态 |

## 人工定义的预期与实现修改边界

本人自主用例使用显式预期：main.o 依赖 main.c/config.h/extra.h，helper.o 依赖 helper.c；发现集合恰为 config.h MD、extra.h MD、unused.h RD；只新增 extra.h MD；两个对象保守刷新。该预期由输入变化推导并在 Codex 辅助下写为断言，不是从检测器输出反填的 oracle。

E10 删除场景在扫描变更状态前保存另一份 [独立预期](../../../../e10/evidence/A1-241880485/extension/independent-expected.json)，标签为 `A1_EXPECTED_FROM_PLANNED_HEADER_REMOVAL`：main.o 回到 config.h/main.c；helper.o 不变；声明不变；只消除 extra.h MD，保留 config.h MD 和 unused.h RD；两个对象刷新、无复用。五次真实原始报告与预期分开保存，没有从检测器输出倒填预期。

没有修改教学核心 `lab.py`、固定环境 Dockerfile/锁文件或其他成员测试。实际个人测试为 [test_student_241880485.py](../../../../labs/e8e10/test_student_241880485.py)；E9 自主任务沿用该间接 include 独立测试与 E8 扩展证据，不机械增加重复测试。E9/E10 执行脚本按手册抽取原计算块，另加完整输入预期、历史保存和删除场景编排，仍调用共用 `scan()` / `buildchecker()`，没有复制检测实现。公共导入、测试发现适配、个人断言与课程参考代码分别说明，不能把整份参考实现记为本人原创。

[independent-expected.json](../../../../e8/evidence/A1-241880485/extension/independent-expected.json) 标注 `MANUAL_EXPECTED_FROM_EDITED_INPUT`，是人工定义的判据；实际 trace、扫描报告和测试日志另存。自动化采集及文档整理不构成人工签字或队友确认，本文没有虚构此类记录。

## 实际验证命令与结果

E8 实验学生源码：`9ee3242f8d7ea1b6bb4091e2947d85d33a37aa8a`；E9/E10：`18a79582672a71d486abc656bc9007d4aebdceab`。镜像为 `course-e8e10:241880485`，完整 ID 未变。实际命令、干净状态与源码哈希分别见 [E8 元数据](../../../../e8/evidence/A1-241880485/provenance/metadata.json) 和 [E9/E10 元数据](../../../../e10/evidence/A1-241880485/provenance/metadata.json)。

| 验证 | 实际输入 / 命令入口 | 已取得结果与原件 |
| --- | --- | --- |
| E8标准路线 | helper创建新OUT，顺序执行E8-A分步代码；scan → BuildChecker → baseline投影 → scan(project,baseline) | work/e8-A-manual.vwDixM；精确两项MD/RD；两个对象复用，刷新为空；[baseline](../../../../e8/evidence/A1-241880485/baseline/baseline.json)、[incremental](../../../../e8/evidence/A1-241880485/baseline/incremental.json) |
| 独立扩展 | 新项目中修改config.h并commit；增量/全量scan及BuildChecker前后核对 | work/e8-A-manual.jA7ZjJ；新增extra.h MD；[extension-check](../../../../e8/evidence/A1-241880485/extension/extension-check.json) 三项true |
| E9 完整分步路线 | 新 OUT 创建 fixture，C0 构建及 baseline；C1 普通变化、C2 include、C3 补声明；逐次 make/scan 和内部 commit | work/e9-A-manual.eqLOHp；四报告、C0/C1/C2 构建日志、四版本 bundle；[完整检查](../../../../e9/evidence/A1-241880485/standard/a1-complete-check.json) 通过 |
| E10 标准路线 | 新 OUT 中六类累积修改，各五次从相同上一场景旧图做增量/全量，再动态重检 | work/e10-A-manual.eVOOik；[results.csv](../../../../e10/evidence/A1-241880485/standard/matrix/results.csv) 30/30、60 JSON；[统计](../../../../e10/evidence/A1-241880485/standard/matrix/performance-summary.csv) 为真实 scan 计时；最终对象图一致 |
| E10 自主任务 | 新项目先建立间接 include 旧图，再移除 include 并删除 extra.h，重复五次并做动态前后核对 | work/e10-A-manual.n9BhPY；5/5、十份 JSON；[gate](../../../../e10/evidence/A1-241880485/extension/gate.json) 通过；extra.h MD 消除，保留原 config.h MD/unused.h RD |
| 全套单元测试 | 容器内 python3 -m unittest discover -s labs/e8e10 -p 'test_*.py' -v | 保留 E8 原日志；本轮 work/A1-E9E10-tests.7gI6Xf 的 [stderr](../../../../e10/evidence/A1-241880485/unit-tests/stderr.log)：8 tests、0.193s、OK；[exit-code](../../../../e10/evidence/A1-241880485/unit-tests/exit-code.txt)=0 |

完整执行脚本、终端输出及原件位置见 [个人报告](个人报告.md) 与 [E8](../../../../e8/evidence/A1-241880485/index.md)、[E9](../../../../e9/evidence/A1-241880485/index.md)、[E10](../../../../e10/evidence/A1-241880485/index.md) 证据索引。上述功能结果来自真实云机容器运行；子代理对手册和原件的审查是额外核验，不替代实验运行。课程教学实现仍不是完整论文工具，scan 计时不包括完整 clean build，不外推论文性能。

下载后子代理完成 [独立原件审查](../../../../e10/evidence/A1-241880485/verification/remaining-independent-audit.json)：199 项通过、errors 为空；核验内部 bundle 的 4/6/3 个版本、70 份 JSON、35 行 CSV 与统计，并用匹配源码解析器离线重解析三套共 30 份 trace。动态图/发现一致，原件哈希未变；审查工具和报告同样由 Codex 辅助生成，不记为人工独立签字。

公共导入 PR #13 已合并，三门禁成功，但当时仅有原 7 项课程测试。个人 [PR #15](https://github.com/Lilyly9/DevOps-G16/pull/15) 本轮开工实时核验仍开放；历史 E8 交付提交 `57fda0aaf77ece6087f4cc5fc644377840865862` 的三门禁成功，[run 41569763447](https://github.com/Lilyly9/DevOps-G16/actions/runs/41569763447) 包含原 7 项及本人 1 项测试。历史 `18a7958` 的成功检查也与本轮新交付分开；新增 E9/E10 证据与报告提交的真实 head SHA、CI 和 artifact 由 [CI记录](CI记录.md) 登记，不预填成功。PR 等待组内审查，未自动合并或更改分支保护。

本轮保留旧 E8 本机备份；完整 A1 个人 E8–E10 包按用户明确选择仅本机保存，生成及校验由最终备份记录登记，不上传完整包至服务器。A16 ↔ B16 不变，E11–E12 跨组交换和联调未做；其他成员的结果、贡献与签字均不由本记录代填。
