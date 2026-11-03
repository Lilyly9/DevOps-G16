# 决策记录（B1 · 郭德林 241880555 · E8-B）

背景与约束：E8-B 需要从固定 MD 报告生成候选补丁且不写回原项目；`lab.py` 是共享单文件，B2/B3 后续复用其 `patch()`/`validate()`；课程要求每人至少一个有独立预期的测试或实现改动。

选择与替代方案：
- 补丁定位：选择 direct 风格（在 main.o 显式前置条件列表追加 config.h），由参考实现 `patch()` 自动识别；替代为 macro（改 DEPS 变量定义）/mixed（保留 HEADERS 引用并在目标行追加），但本样例 Makefile 为显式列表，direct 改动最小且配方行字节不变。
- 拒绝保护：复用 `patch()` 的前置检查顺序——STALE_REPORT（commit 身份）→ UNSAFE_PATH → MISSING_INPUT → UNSUPPORTED_TARGET；替代方案是在外层另写包装校验，但会与 B2/B3 的共享逻辑重复，放弃。
- 个人贡献：选择独立测试（2 例）而非修改 `patch()` 实现；替代为实现改动，但共享函数改动影响 A/B 两轨，需全量对照与新 OUT 复跑，本次无此必要。

A/B 关注点（B：声明位置、失败怎样保证原目录不变）：本样例无共享宏，声明位置为显式目标行；失败路径上 `patch()` 只读源文件并返回 diff，从不写回——STALE_REPORT 用例（手册步骤 7）与本人的 UNSUPPORTED_TARGET 用例均以 before/after 字节断言验证原文件不变。

代价与覆盖范围：受限显式语法之外（隐式规则、多行配方、复杂宏展开）不在候选能力内；未知目标显式拒绝（UNSUPPORTED_TARGET）而非猜测行号；纯 RD 报告返回空 diff 而非执行删除。

验证命令与实际证据：
- `docker run ... python3 -m unittest discover -s labs/e8e10 -p 'test_*.py' -v` → `work/unit-tests-241880555-20261103-125346.log`（Ran 9 tests OK）
- E8-B 步骤 5–7 日志：`work/e8-B-manual.qsW6Xo/steps/`（PATCH_GENERATED_SOURCE_UNCHANGED、APPLY_CHECK_PASS_SOURCE_CLEAN、EXPECTED_REJECTION STALE_REPORT、SOURCE_BYTES_UNCHANGED）

## E9-B/E10-B 补充（2026-11-03，B1 额外执行）

- E9-B 声明位置：三种风格由 fixture 预设，`patch()` 按目标行形态自动选择（目标行整行为 `$(VAR)` → macro；含宏引用 → mixed；纯字面 → direct）。本人用例验证共享变量（macro）修复的跨目标影响——修改 DEPS 定义会同时改变所有引用目标（main.o 与 helper.o）的声明集合；独立预期初版漏算 helper.o 展开声明丢失 helper.c 产生的第二条 MISSING，实测后如实修正预期（失败/通过日志均保留，见 e9 证据索引）。
- E10-B 拒绝保护：三场景（错误测试预期 99 / 正确接受 / 坏 Patch）全按手册断言；`rollback=True` 的语义按手册取"源文件从未被写"（cmp 字节对照，非 git reset 回滚）。本人扩展增加"错位修复"用例——能应用、能构建、程序测试还过的候选，由 header_change（原 MD 的行为后果：头文件变化不触发重编译）与 no_missing（重检残留 MISSING）两项兜底拒绝，证明"五项全过才写回"的必要性。
- 仍不修改 `lab.py`：`patch()`/`validate()` 属 B2/B3 函数所有权范围（E8-10_TASKS.md §3.2），本人贡献保持独立测试；测试与文档已如实标注"非 B2/B3 主责交付"。
- 镜像复用决策：`lab.py` 与环境均未变化，E9-B/E10-B 复用 E8-B 的 `course-e8e10:241880555`（ID 8b8cba48…，与 environment-image-id.txt 一致），不重建。
