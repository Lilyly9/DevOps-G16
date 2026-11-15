# AI 使用记录（A2 / 241880496，E8—E10）

## 工具/模型/日期

GitHub Copilot（VS Code 会话内助手模型，2026-11-10）。用途为执行手册、把命令翻译到 Windows 宿主、整理证据与草拟文档；不用于替他人填写结论。

## 输入上下文与问题

- 上下文：课程材料 `DevOps_E8_E10/02_操作手册/` 的 A 轨道三份手册、`03_实验包` 的 `run_lab.py`/`labs/e8e10/lab.py`/`test_profile.py`、`04_模板`，以及本人已入库的 E2—E7 交付。
- 问题：①手册命令以 Linux SSH 会话为前提，本机是 Windows + Docker Desktop，如何在不改实验语义的前提下逐步执行并保留 `STEP_EXIT_CODE`；②自主任务选"新增独立预期用例"还是"实现改动"；③证据如何按阶段精选入库。

## 模型建议

1. 用 `work/_run/run_stage.ps1` 把手册每一步映射为一次 `docker run`（同一镜像、`--network none`、`--cap-add SYS_PTRACE`、挂载仓库到 `/course`），把 `STEP_EXIT_CODE` 追加到 `work/<OUT>/steps/*.log`，与 `classroom_helpers.sh:lab_python` 等价。
2. 自主任务选"用例 + 小改动"：在 `scan()` 中新增 `invalidation` 原因字段（不改刷新语义），并加三项用例。
3. 证据按 `e8|e9|e10/evidence/A2-241880496/` 存放精选副本（含逐步日志、报告 JSON、trace/make-db、六场景 30 份成对 JSON），完整原件留在被忽略的 `work/`。

## 采纳/拒绝及理由

- 采纳 1：避免在 Windows 上改写课程 Python 入口；所有步骤仍是"输入 → 容器内执行 → 断言 → `STEP_EXIT_CODE`"，可逐条手工复现。
- 采纳 2：理由见 [ADR](ADR.md)——`invalidation` 只增加可解释性，`test_profile.py` 原 7 项与三条手册断言保持通过。
- **拒绝**："按目标失效"实现改动（只刷新受影响目标）。它会改变 `refreshed` 既有期望、使 `test_include_added_invalidates_cache` 与 E9-A 手册第 7 步断言失效，属跨阶段口径变更，已列入扩展计划而非本次提交。
- **拒绝**：把 E10 的 `full/inc` 比值写成"加速倍数"。实测 0.74–1.18 且抖动与量级相同，写成加速属于过度解读，报告只保留原始中位数与解释。
- 人工纠正：首版 PowerShell 用默认 ANSI 读取步骤脚本，导致容器内 `结论.txt` 文件名与内容出现乱码；已改为显式 UTF-8 读文件 + UTF-8 控制台输出，删除坏样本并以新 OUT 重跑（`work/e8-A-manual.myt4ld`、`work/e9-A-manual.8b1g7u`、`work/e10-A-manual.pyylyj` 为有效证据）。

## 人工修改

- 逐条核对每个断言的**独立预期**（先写下 `main.o=[config.h,main.c]`、C2 新增 MD `extra.h`、C3 `resolved` 两项、E10 六场景复用/刷新分布）再运行，未用实现输出反推期望。
- 报告中的耗时、commit 前缀、trace 行号（`trace/t.14:579`）、`make-db.txt:1044` 均取自本次实际输出，未照抄教师示例。
- 证据副本的取舍（剔除 `*.o`/`app`/内部 `.git`，保留 `project-git-log.txt`）与索引文字由本人确认。

## 实际验证命令/输入/结果

```bash
# 单元测试（原 7 项 + 本人 3 项）
docker run --rm --network none -e HOME=/tmp -e PYTHONPATH=/course/labs/e8e10:/app \
  -v "$PWD:/course" -w /course course-e8e10:241880496 \
  python3 -m unittest discover -s labs/e8e10 -p 'test_*.py' -v      # Ran 10 tests ... OK（退出 0）

# 三条路线（等价手册逐步命令，每步 STEP_EXIT_CODE=0）
python run_lab.py build                                            # ENV_BUILD_EXIT=0
work\_run\run_stage.ps1 -Stage e8  -Track A                        # STAGE_DONE=e8-A
work\_run\run_stage.ps1 -Stage e9  -Track A                        # STAGE_DONE=e9-A
work\_run\run_stage.ps1 -Stage e10 -Track A                        # STAGE_DONE=e10-A
```

## 参考实现与本人贡献边界

- 课程参考实现（`run_lab.py`、`labs/e8e10/lab.py`、`test_profile.py`、`.github/workflows/e8e10.yml`）来自助教分发包，**不是**本人自主开发成果；本次未改动 `run_lab.py`、`test_profile.py` 与工作流。
- 本人新增：`labs/e8e10/lab.py` 的 `invalidation()` 与 `scan()` 返回字段、`labs/e8e10/test_student_241880496.py`（3 项）、`docs/students/241880496/e8-e10/` 三份文档、`e8|e9|e10/evidence/A2-241880496/` 证据与索引，以及 `CONTRIBUTIONS.md`/`AI_USAGE.md`/阶段 README 的本人部分。
- 未调用模型生成的内容：课程代码本身、他人阶段结论、Actions 运行结果（以 GitHub 实际记录为准）。
