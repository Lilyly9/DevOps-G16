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
