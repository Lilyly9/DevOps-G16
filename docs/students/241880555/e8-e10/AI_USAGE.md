# AI使用记录（B1 · 郭德林 241880555）

工具/模型/日期：Claude Code（claude-sonnet-4-6），2026-11-03。

输入上下文与问题：本人提供课程分工与手册（E8-10_TASKS.md、00_公共准备.md、8_E8_B组.md、08_个人测试编写示例.md、07_提交与排错.md）及服务器访问方式；AI 协助完成：公共准备（服务器环境检查、材料包上传、GitHub device 授权、个人分支与镜像构建）、E8-B 手册步骤 0–8 的命令执行与输出核对、自主测试编写与运行、个人报告/ADR/证据索引撰写。

模型建议：
- 按手册逐步生成 SSH 命令与 `lab_python` Python 步骤代码；每步独立核对 STEP_EXIT_CODE。
- 自主测试由 AI 依据 `lab.py` 中 `patch()` 的实际拒绝路径（UNSUPPORTED_TARGET 等）设计两例并先给出独立预期。
- GitHub 认证：gh 2.4.0 过旧且 `gh auth login --web` 的 PTY 自动化卡在光标位置查询，AI 建议升级 gh 2.62.0 并改用 GitHub 标准 device flow（Python 直连 OAuth API）。

采纳/拒绝及理由：全部命令与断言与手册原文核对后采纳；未采纳的尝试：`gh auth login --web` 的 script PTY 自动化（挂起）→ 改为 device flow 后成功。服务器 gh 2.4.0 → 2.62.0 升级（apt 版过旧，从 GitHub Releases 下载二进制安装）。

人工修改：独立预期表述、测试类名/文件名（test_student_241880555.py）经本人确认；仓库/分支/学号/GitHub 账号（241880555/delinguo）由本人提供并核对。

实际验证命令/输入/结果：全部步骤输出以 `work/e8-B-manual.qsW6Xo/steps/` 6 份日志与 `work/unit-tests-241880555-20261103-125346.log`（Ran 9 tests OK）为准；报告中的 SHA、镜像 ID、OUT 均取自真实输出文件（student-source-commit.txt、environment-image-id.txt、scan 输出）。

未调用模型 API 于实验本身：教学包不要求调用外部模型；scan/patch 结果全部来自容器内参考实现，AI 未参与或替代任何检测/补丁计算，只做命令编排、记录与文档。

## 追加（E9-B/E10-B，2026-11-03）

任务：本人要求在 E8-B 之外继续完整执行 E9-B/E10-B 参考路线，保留运行结果并各增加一个有独立预期的测试。AI 协助：按手册生成步骤命令与 `lab_python` 代码、逐步核对 STEP_EXIT_CODE；基于 `lab.py` 中 `patch()`/`validate()` 的实际行为设计两个新用例并先给出独立预期；撰写 e9/e10 证据索引并更新个人报告/ADR。

采纳/修正：E9-B 用例初版独立预期只写一条 edit，容器实测出现第二条 MISSING(helper.o,helper.c)（helper.o 声明改为 `$(DEPS)` 后原字面依赖 helper.c 从展开结果消失）；AI 解释成因后经本人确认修正预期，预期修正前的失败日志（193600）与修正后的通过日志（193709）均保留。E10-B 用例选择"错位修复"（config.h 加到 helper.o 行）而非编写示例的"编译失败"路径，以覆盖 header_change+no_missing 双检查兜底的拒绝原因。全部步骤输出与手册断言核对后采纳。

人工修改：测试类名、独立预期表述、e9/e10 README 与证据索引中"非 B2/B3 主责交付"的定位均经本人确认；仓库/分支/学号由本人提供。

实际验证命令/输入/结果：E9-B 步骤日志 `work/e9-B-manual.KUAgZz/steps/`（4 份）、E10-B 步骤日志 `work/e10-B-manual.i9gc5v/steps/`（7 份）、单测日志 193600/193709；报告中的 SHA、OUT、validation 结果均取自真实输出文件。未调用模型 API 于实验本身：scan/patch/validate 结果全部来自容器内参考实现，AI 未参与或替代任何检测/补丁/验证计算。
