# A1 E8–E10 A 轨决策记录

记录人：焦龙 / 241880485；日期：2026-11-03。范围：本人完整 E8-A、E9-A、E10-A。E8 运行源码 `9ee3242f8d7ea1b6bb4091e2947d85d33a37aa8a`；E9/E10 运行源码 `18a79582672a71d486abc656bc9007d4aebdceab`。实际结果见 [个人报告](个人报告.md)，原件分别见 [E8 索引](../../../../e8/evidence/A1-241880485/index.md)、[E9 索引](../../../../e9/evidence/A1-241880485/index.md)、[E10 索引](../../../../e10/evidence/A1-241880485/index.md)。

## 1. 历史基线采用真实 BuildChecker 对象图

**背景与约束。** E8 需要说明历史实际图的来源及未变化目标的复用。课程 `scan()` 用 GCC -MM 投影依赖；它可以独立核对对象依赖，但不等于已完成一次 strace 动态采集。

**选择。** 标准样例先保存 GCC 投影原件，再运行 BuildChecker，将实际图投影到 main.o/helper.o，写入 baseline 的 actual，并明确 `baseline_source`。后续未修改 C0 的扫描从这一份 baseline 复用。保留原始 t.*、进程树、make 数据库及精确发现，便于从结论回查。

**替代方案。** 仅保存 gcc -MM 结果更简短，但不足以证明动态基线来源；每次都重新动态扫描可以避免缓存判断，却没有验证 E8 所需的历史复用机制。

**代价与范围。** 动态采集需要 Linux、strace 和 SYS_PTRACE；本文只对项目内对象目标做投影比较，不把 app 链接任务和系统库混入两对象判据，也不宣称实现完整论文工具。

**实际验证。** [baseline](../../../../e8/evidence/A1-241880485/baseline/baseline.json) 来自真实对象图；[BuildChecker 报告](../../../../e8/evidence/A1-241880485/baseline/buildchecker/findings.json) 精确给出 config.h MD、unused.h RD；[incremental](../../../../e8/evidence/A1-241880485/baseline/incremental.json) 显示两个对象 reused、无 refreshed，actual/findings 不变。完整命令见 [执行脚本](../../../../e8/evidence/A1-241880485/baseline/executed-route.sh)。

## 2. 间接 include 采用保守失效，并用独立预期验证

**背景与约束。** 只修改已有头文件中的 include，main.c 内容不变。如果仅检查翻译单元文本或沿用旧发现，可能漏掉新增 extra.h 依赖。缓存有效性应绑定预处理指令、recipe、编译器/配置签名，不能只依据提交变化或构建成功。

**选择。** 本人的测试把 config.h 改为包含 extra.h，先明确 main.o 的三文件依赖、完整 MD/RD 集合和 added/resolved，再检查参考实现对两个对象保守刷新。随后比较增量/全量的 actual、declared、findings，并用变更后的真实 BuildChecker 再核对对象图与发现。

**替代方案。** 只刷新受影响的 main.o 有潜在效率收益，但需要可靠的影响范围证明，本次不把它作为已实现能力；只比较发现条数会漏掉错误边；只比较增量与全量也可能同时接受两边共有的错误。

**代价与范围。** helper.o 虽未增加依赖，仍随签名失效刷新，是教学实现的保守代价。本次验证正确性，不宣称最小刷新集合。该已有独立测试可沿用于 E9 自主任务，但本人仍另外完整执行 E9 C0–C3 与 E10 矩阵，不能由一个测试替代整阶段交付。

**实际验证。** [人工预期](../../../../e8/evidence/A1-241880485/extension/independent-expected.json) 与实际输出分别保存；[扩展检查](../../../../e8/evidence/A1-241880485/extension/extension-check.json) 的三项核对均为 true。内层版本为 `683b6b05d97233fe2c81f6697662e346a5cefd0b` → `20094b5a4d105c72ecbead91d3302b3834d47254`，与外层学生源码 SHA 区分。

## 3. E9 将构建行为、实际图与声明更新分别记录

**背景与选择。** Make 根据文件时间决定是否编译，课程扫描按预处理结构与编译配置判断历史图是否可复用，两者不能混为一谈。本人以新 OUT 执行 C0–C3，每个状态保留内部提交、报告与真实构建日志；C3 只修复声明时仍重新解析声明并计算发现消除。

**替代方案与代价。** 只保存最终报告无法证明变化驱动更新，依赖工作目录的最终文件也不能恢复中间状态。因此保存 [完整四版本历史 bundle](../../../../e9/evidence/A1-241880485/standard/project-history.bundle) 和 patch 日志，而不是复制多套实现。内部 bundle 只记录受测项目，不替代外层学生源码 SHA。

**实际验证。** [C1](../../../../e9/evidence/A1-241880485/standard/C1.json) 复用两个对象图，但 [真实 make 日志](../../../../e9/evidence/A1-241880485/standard/C1-build.log) 重编 main.o；[C2](../../../../e9/evidence/A1-241880485/standard/C2.json) 刷新两个对象并仅新增 extra.h MD；[C3](../../../../e9/evidence/A1-241880485/standard/C3.json) 复用实际图，消除 config.h/extra.h 两项 MD、保留 unused.h RD。四报告 commit 与内部四版本一一对应。

## 4. E10 使用完整集合判定和同一旧图的五次测量

**选择。** 每类五次从相同上一场景历史图扫描，比较完整 `actual`、`declared`、`findings`，保存每次增量/全量 JSON 与原始计时；只有末次结果成为下一场景历史图。最终用真实 BuildChecker 动态对象图与发现交叉核对。

**替代方案与代价。** 只比较条数可能掩盖目标或依赖边错误；每次立即更新旧图会把刷新场景后几次变成复用，改变测量问题。完整保存 60 份 JSON 较冗长，但可验证 30 行 CSV、每次输入和完整集合。GCC 与动态路径各有共同限制，仍需从输入推导独立预期，不能只看两个工具相互一致。

**实际验证。** [results.csv](../../../../e10/evidence/A1-241880485/standard/matrix/results.csv) 六类各五次、30/30 一致；[完整独立检查](../../../../e10/evidence/A1-241880485/standard/matrix/a1-complete-check.json) 核对全部预期集合和最终动态图。unchanged/body/declaration 为 2 复用、0 刷新，include/flags/header 为 0 复用、2 刷新。header 前 extra.h 已被直接包含，所以签名变化而实际图不再增边。

**计时口径。** [统计](../../../../e10/evidence/A1-241880485/standard/matrix/performance-summary.csv) 为 `scan()` 耗时，含 Git/GCC 检查、解析与 gcc -MM，不含完整 clean build。真实刷新场景全量/增量中位数比约 0.980、0.980、0.994，保留增量略慢的结果；五次小样例不支持论文级性能结论。

## 5. 自主删除场景验证历史依赖能够消失

**选择。** 另建项目，先让 config.h 间接包含 extra.h 建基线，再移除 include 并删除 extra.h。扫描前定义 [完整独立预期](../../../../e10/evidence/A1-241880485/extension/independent-expected.json)：main.o 回到 config.h/main.c，helper.o 仍只 helper.c；只消除 extra.h MD，保留 config.h MD、unused.h RD；两个对象保守刷新。

**替代方案与代价。** 再重复新增 include 与已有 E8 测试覆盖相近；直接删除仍被包含的头文件会导致编译器失败，测到另一个问题。因此本次同时移除已无效的引用，验证合法输入下依赖边和发现消除，三版本内部历史保留操作顺序。

**实际验证。** 五次均使用同一个变更前历史图，保存十份原始报告。[自主结果](../../../../e10/evidence/A1-241880485/extension/results.csv) 为 5/5 一致，增量中位数 10.123 ms、全量 9.964 ms，比值 0.984；动态前后对象图与独立预期一致，程序输出 1。[gate](../../../../e10/evidence/A1-241880485/extension/gate.json) 明确记录两个内部基线/变更 SHA 与三项检查通过。

## 6. 共用代码、个人交付和环境复用

**选择。** 三阶段教学代码只在根 `labs/e8e10/` 保留一份；本人测试使用 [test_student_241880485.py](../../../../labs/e8e10/test_student_241880485.py)，不改同伴测试或教学核心。公共导入将测试发现模式统一为 `test_*.py`，避免个人新文件被精确的 `test_profile.py` 模式漏掉。本人标准与扩展各用新 OUT，不覆盖旧基线。

**代价与验证。** 分文件后仍需真实核对发现日志，而非仅数文件。保留 [E8 测试日志](../../../../e8/evidence/A1-241880485/unit-tests/stderr.log)，本轮 [E9/E10 后新测试日志](../../../../e10/evidence/A1-241880485/unit-tests/stderr.log) 同样包含原 7 项加本人 1 项，8 项通过、退出 0。E9/E10 已核验环境代码与锁文件不变，复用相同镜像 ID，无需因挂载的实验或报告变化重复构建。实际镜像与源码哈希见 [新元数据](../../../../e10/evidence/A1-241880485/provenance/metadata.json)。

**交付范围。** 按最新要求，每人完整完成本组轨道 E8–E10；阶段方向仅用于讨论和公共维护，不能用队友记录代替个人运行。A16 ↔ B16 保持，跨组产物交换与联调留至 E11–E12。继续更新本人 [PR #15](https://github.com/Lilyly9/DevOps-G16/pull/15)，不自动合并或修改保护；历史 E8 CI 与本轮新增交付 SHA 的 CI 分开记录，见 [CI记录](CI记录.md)。外层运行源码、内部样例提交、交付/CI SHA 各自保留。

**归档选择。** 服务器保留本人原始 OUT；仓库保存可审查的文字、trace、输入与历史 bundle。保留已有本机 E8 包，本轮完整个人包及 SHA256 仅保存在本机，不上传完整包到服务器；它不代表 A16 全组最终交付。

**离线复核。** [独立原件审查](../../../../e10/evidence/A1-241880485/verification/remaining-independent-audit.json) 199 项通过、无错误；bundle 可恢复全部 4/6/3 版本，70 份 JSON 与 35 行 CSV/统计一致，三套共 30 份 trace 按匹配源码解析器重解析一致，原件哈希保持。该复核提高可审查性，不替代动态采集本身。

可见内存 3.5 GiB 低于材料建议的 4 GiB，保留 [实际环境记录](../../../../e8/evidence/A1-241880485/preparation/environment.json)。已完成本次功能验证不意味着资源建议已满足。源码、环境、人工预期和真实输出分别追溯，不借助旧 E5 doctor 结果推导本次结论。
