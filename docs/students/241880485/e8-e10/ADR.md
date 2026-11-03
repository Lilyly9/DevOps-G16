# A1 E8-A 决策记录

记录人：焦龙 / 241880485；日期：2026-11-03。范围：A16 的 E8-A 标准复现与本人间接 include 扩展，学生源码 `9ee3242f8d7ea1b6bb4091e2947d85d33a37aa8a`。实际环境与结果见 [个人报告](个人报告.md)，原件入口见 [A1 证据索引](../../../../e8/evidence/A1-241880485/index.md)。

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

**代价与范围。** helper.o 虽未增加依赖，仍随签名失效刷新，是教学实现的保守代价。本次验证正确性，不宣称最小刷新集合，也不将一次扩展核对写成 E9 完整路线或 E10 统计。

**实际验证。** [人工预期](../../../../e8/evidence/A1-241880485/extension/independent-expected.json) 与实际输出分别保存；[扩展检查](../../../../e8/evidence/A1-241880485/extension/extension-check.json) 的三项核对均为 true。内层版本为 `683b6b05d97233fe2c81f6697662e346a5cefd0b` → `20094b5a4d105c72ecbead91d3302b3834d47254`，与外层学生源码 SHA 区分。

## 3. 共用代码与个人证据分离

**选择。** 三阶段教学代码只在根 `labs/e8e10/` 保留一份；本人测试使用 [test_student_241880485.py](../../../../labs/e8e10/test_student_241880485.py)，不改同伴测试或教学核心。公共导入将测试发现模式统一为 `test_*.py`，避免个人新文件被精确的 `test_profile.py` 模式漏掉。本人标准与扩展各用新 OUT，不覆盖旧基线。

**代价与验证。** 分文件后仍需真实核对发现日志，而非仅数文件。[容器测试日志](../../../../e8/evidence/A1-241880485/unit-tests/stderr.log) 实际包含新增方法，原 7 项加本人 1 项共 8 项通过。课程环境未改且成功构建，修改挂载测试无需重复构建同一镜像。个人 [PR #15](https://github.com/Lilyly9/DevOps-G16/pull/15) 已创建，提交 `57fda0aaf77ece6087f4cc5fc644377840865862` 的 E7-A、E7-B、E8-E10 三门禁成功；[PR 事件 run 41569763447](https://github.com/Lilyly9/DevOps-G16/actions/runs/41569763447) 验证原 7 项加本人 1 项测试。该提交保存代码与证据，现场实际采集源码仍为 `9ee3242f8d7ea1b6bb4091e2947d85d33a37aa8a`；后续仅归档 CI 记录的新提交不倒改实验原件。PR 仍待组内审查合并，平台记录见 [CI记录](CI记录.md)；公共导入的 7 测不作为个人 8 测远程证据。

可见内存 3.5 GiB 低于材料建议的 4 GiB，保留 [实际环境记录](../../../../e8/evidence/A1-241880485/preparation/environment.json)。已完成本次功能验证不意味着资源建议已满足。源码、环境、人工预期和真实输出分别追溯，不借助旧 E5 doctor 结果推导本次结论。
