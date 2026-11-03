# A1 E8-A AI 使用记录

成员：焦龙 / 241880485；小组：G16 / A16；日期：2026-11-03。

## 使用的工具与上下文

本次使用 **OpenAI Codex** 辅助阅读课程材料、整理分工边界、接入参考实现、编写个人回归测试、自动执行及读取本组服务器原始证据，并起草本人文档。本记录不将这些工作写成未使用 AI。具体底层模型版本未单独记录，不推断型号。

未在教学实验程序中调用外部模型 API，也未为 EChecker 检测或个人测试接入模型候选生成；这与使用 Codex 对话/代码助手是两件事。本次没有生成 MDFixer 的 LLM 候选，也不认领 B 组工作。

提供的主要上下文包括：2026-10-31 E8–E10 详细手册、课程 `lab.py` 与原 7 项测试、G16 分工、原仓库结构、实际服务器环境、外层源码 SHA、两个运行目录的 JSON/trace/make 数据库，以及本次真实单元测试输出。没有把助教 ARM64 示例的 SHA、路径、耗时或 CI 记录当作本人结果。

## 建议、采纳与拒绝

| 问题 / 建议 | 本次处理 | 理由与核验 |
| --- | --- | --- |
| 如何保持原仓库并避免三阶段代码分叉 | 采纳根 run_lab.py + labs/e8e10 单副本，e8 仅放阶段证据和索引 | 符合入口、helper 与 workflow 的硬编码路径，保留旧 E4–E7 |
| 个人测试怎样避免改同一个公共测试文件 | 使用 test_student_241880485.py；统一发现模式为 test_*.py | 容器真实输出发现本人方法，8 项通过 |
| 用什么自主案例检验缓存有效性 | 选择在 config.h 中新增 extra.h include | 主文件内容不变但实际依赖应增加，可检查旧图失效和新增 MD |
| 是否只比较发现数量或两份工具输出 | 不采用这种充分性判断；先定义完整人工预期，再比实际边/发现，并做动态核对 | 防止“数量相同但边错误”或两条路径共享错误 |
| 如何解释 config.h 的 openat | 不把单条 grep 或 stat 当成 MD；结合成功调用、编译 recipe 归属、输出及声明 | 标准进程链 13→14→15/16；t.15:579、t.16:23、数据库第1044行 |
| 是否把公共 CI 或本次扩展写成其他阶段完成 | 不采用；公共导入 7 测、本人本地 8 测与个人远程 CI 分开 | E9/E10由A2/A3负责，本人未执行对应阶段路线 |
| 资源与环境差异如何报告 | 记录实际 3.5 GiB，未写为满足4 GiB建议；本轮课程环境不改动且构建成功 | 使用本次环境与构建记录，不套用旧doctor状态 |

## 人工定义的预期与实现修改边界

本人自主用例使用显式预期：main.o 依赖 main.c/config.h/extra.h，helper.o 依赖 helper.c；发现集合恰为 config.h MD、extra.h MD、unused.h RD；只新增 extra.h MD；两个对象保守刷新。该预期由输入变化推导并在 Codex 辅助下写为断言，不是从检测器输出反填的 oracle。

没有修改教学核心 `lab.py`、固定环境 Dockerfile/锁文件或其他成员测试。实际个人代码为 [test_student_241880485.py](../../../../labs/e8e10/test_student_241880485.py)。公共导入及测试发现适配与该个人用例分别说明，不能把整份课程参考实现记为本人原创。

[independent-expected.json](../../../../e8/evidence/A1-241880485/extension/independent-expected.json) 标注 `MANUAL_EXPECTED_FROM_EDITED_INPUT`，是人工定义的判据；实际 trace、扫描报告和测试日志另存。自动化采集及文档整理不构成人工签字或队友确认，本文没有虚构此类记录。

## 实际验证命令与结果

实验学生源码：`9ee3242f8d7ea1b6bb4091e2947d85d33a37aa8a`。镜像为 `course-e8e10:241880485`，完整 ID 与实际命令见 [provenance/metadata.json](../../../../e8/evidence/A1-241880485/provenance/metadata.json)。

| 验证 | 实际输入 / 命令入口 | 已取得结果与原件 |
| --- | --- | --- |
| E8标准路线 | helper创建新OUT，顺序执行E8-A分步代码；scan → BuildChecker → baseline投影 → scan(project,baseline) | work/e8-A-manual.vwDixM；精确两项MD/RD；两个对象复用，刷新为空；[baseline](../../../../e8/evidence/A1-241880485/baseline/baseline.json)、[incremental](../../../../e8/evidence/A1-241880485/baseline/incremental.json) |
| 独立扩展 | 新项目中修改config.h并commit；增量/全量scan及BuildChecker前后核对 | work/e8-A-manual.jA7ZjJ；新增extra.h MD；[extension-check](../../../../e8/evidence/A1-241880485/extension/extension-check.json) 三项true |
| 全套单元测试 | 容器内 python3 -m unittest discover -s labs/e8e10 -p 'test_*.py' -v | [stderr](../../../../e8/evidence/A1-241880485/unit-tests/stderr.log)：8 tests、0.193s、OK；[exit-code](../../../../e8/evidence/A1-241880485/unit-tests/exit-code.txt)=0 |

完整执行脚本、终端输出及原件位置见 [个人报告](个人报告.md) 与 [证据索引](../../../../e8/evidence/A1-241880485/index.md)。上述功能结果来自真实云机容器运行，不是 AI 在对话中预测的结果；课程教学实现仍不是完整论文工具。

公共导入 PR #13 已合并，三门禁成功，但运行时仅有原 7 项课程测试。个人 [PR #15](https://github.com/Lilyly9/DevOps-G16/pull/15) 已创建，代码/证据提交 `57fda0aaf77ece6087f4cc5fc644377840865862` 的 E7-A、E7-B、E8-E10 三门禁均成功；[个人 PR 事件 run 41569763447](https://github.com/Lilyly9/DevOps-G16/actions/runs/41569763447) 包含原 7 项及本人 1 项测试，平台与 artifact 记录见 [CI记录](CI记录.md)。现场采集源码仍为 `9ee3242f8d7ea1b6bb4091e2947d85d33a37aa8a`，后续仅归档 CI 记录的提交不倒改原始源码身份、trace 或实验结果。PR #15 仍待组内审查合并。E9/E10、其他成员贡献与签字均不由本记录代填。
