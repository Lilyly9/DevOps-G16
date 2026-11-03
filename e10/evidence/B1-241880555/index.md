# B1 · 241880555（郭德林）E10-B 证据索引

- 日期：2026-11-03；角色：**B1**（B 组 E8 主责；本次按任务要求额外完整执行 E10-B 参考路线，**非 B3 主责交付**，B3 本人交付以其学号证据为准；B 组汇总仍由 B3 负责）
- 环境：Aliyun ECS（Ubuntu 22.04，x86_64）；镜像 `course-e8e10:241880555` = sha256:8b8cba482ea52745fcd4514c719084d4561be82209834fc3cec73771389be276（与 E8-B 同一镜像，未重建）
- 外层学生源码 SHA：ee84236f41a658fb4d779f2d2bf6f1aa11e03c87（`OUT/student-source-commit.txt`）
- 内部样例 C0 SHA：2cec34200ab1fcf6479db9b4611101810c6a8121（`OUT/project` HEAD；fixed-md-report.json 的 commit 同值；接受后的 Makefile 修改保留为未提交工作区状态，符合手册"git status 只显示 Makefile 待提交"）
- 本次 OUT：`work/e10-B-manual.i9gc5v`（完整原件保留于本人克隆 `work/`，被 .gitignore 忽略不提交）

## 完整命令与重跑步骤

服务器仓库根 `/root/241880555/DevOps-G16`（分支 `student/241880555/e8-e10`）：

```bash
E8_PACK=$HOME/devops-materials/DevOps_E8_E10/03_实验包
source "$E8_PACK/classroom_helpers.sh"
lab_ready
lab_new_run e10 B         # 新建唯一 OUT（重跑会得到新目录）
OUT=$(cat work/last-e10-B.path)
# 步骤1：lab_python → fixture(out/'project')
# 步骤2：cat Makefile/main.c/config.h/helper.c；git log -1（先独立写预期）
# 步骤3：lab_python → scan→fixed-md-report.json；patch→candidate.patch+patch-plan.json；
#          cp Makefile source-before.Makefile
# 步骤4：lab_python → validate(...,fail_test=True) → reject-test/（预期99拒绝）
# 步骤5：cat validation/build/incremental 日志；cmp source-before 与源 Makefile
# 步骤6：lab_python → validate(...) 默认预期1 → accept/（五项全过才写回）
# 步骤7：cat build/incremental/recheck + git diff -- Makefile + 两个 config.h
# 步骤8：lab_python → broken.patch 拒绝 → reject-patch/（已接受版本受保护）
# 步骤9：lab_python → buildchecker 重检 + results.csv + gate.json
# 步骤10：cat results/gate；git status --short；cmp source-after-accept
```

断线恢复：`OUT=$(cat work/last-e10-B.path)`。

## 关键结果（steps/ 日志一一对应）

| 手册步骤 | 日志（steps/） | 关键输出 |
| --- | --- | --- |
| 1 fixture | 20261103-192629-1.log | CREATED，C0=2cec342 |
| 3a scan | 20261103-192629-2.log | REPORT_COMMIT 2cec342；MISSING(main.o,config.h)+REDUNDANT(main.o,unused.h) |
| 3b patch | 20261103-192629-3.log | `+main.o: main.c unused.h config.h`；PATCH_GENERATED_SOURCE_UNCHANGED |
| 4 拒绝(预期99) | 20261103-192630-4.log | EXPECTED_TEST_REJECTION：accepted=False、checks.test=False、rollback=True、source_unchanged=True |
| 6 接受(预期1) | 20261103-192749-1.log | ACCEPTED_ALL_CHECKS_PASS：五项 checks 全 True，source_unchanged=False |
| 8 坏Patch拒绝 | 20261103-192751-2.log | EXPECTED_BAD_PATCH_REJECTION：error=COMMAND_FAILED git apply（No valid patches in input），rollback=True |
| 9 重检+gate | 20261103-192751-3.log | B_GATE_PASS 3/3；BuildChecker 重检无 MISSING |

## 三场景验证结果（validation.json 摘要）

| 场景 | patch_applies | build | test | header_change | no_missing | accepted | rollback | source_unchanged |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| reject-test（预期99） | True | True | **False** | True | True | False | True | True |
| accept（预期1） | True | True | True | True | True | **True** | False | False |
| reject-patch（坏Patch） | —（apply 失败即中止） | — | — | — | — | False | True | True |

- 头文件变化证据：sandbox config.h 由 VALUE 1 改为 2 后，`incremental.log` 显示重新编译 main.o 并链接 app，程序输出 2；源 project 的 config.h 仍为 `#define VALUE 1`（只写回通过的 Makefile）。
- 回滚语义：`rollback=True` 表示原 Makefile 从未被修改（cmp source-before/source-after-accept 均退出 0），不是先污染再 git reset。
- 最终动态重检：`recheck-buildchecker/`（完整 trace/make-db/actual-graph/declared-graph/findings.json）无 MISSING，REDUNDANT(main.o,unused.h) 允许保留；`accept/recheck.json` 为受限 GCC 扫描，两者不可混称。

## 本目录精选产物（字节复制自 OUT，SHA256SUMS.txt 全量校验）

- `fixed-md-report.json`、`candidate.patch`、`patch-plan.json`：输入与候选
- `source-before.Makefile` / `source-after-accept.Makefile`：修复前与已接受版本的字节对照
- `reject-test-validation.json` / `accept-validation.json` / `reject-patch-validation.json`：三场景结果
- `build.log` / `incremental.log` / `recheck.json`：accept 的构建、头变化增量与受限重检证据
- `results.csv`（3 行全 passed=True）、`gate.json`（track=B, passed=true, rows=3）、`结论.txt`
- `broken.patch`：无效补丁原文；`steps/`（7 份完整步骤日志）

## 个人扩展（labs/e8e10/test_student_241880555.py，类 StudentE10B_MisplacedFix_241880555）

| 用例 | 独立预期 | 实际 |
| --- | --- | --- |
| test_misplaced_fix_buildable_but_rejected_no_source_write | 候选把 config.h 加到 helper.o 行（错位修复）：patch_applies/build/test 三项通过，但 no_missing=False（MISSING(main.o,config.h) 残留）且 header_change=False（main.o 声明缺 config.h，头文件改 VALUE=2 后 make 不重编、程序仍输出 1）；accepted=False、rollback=True、源 Makefile 逐字节保持 | 通过 |

错位修复结论：能应用、能构建、程序测试还过的候选仍可能是坏修复——`header_change` 检查（原 MD 的行为后果）与 `no_missing` 重检共同兜底，五项全过才写回。

## 归档与备份

- 完整 work 原件不在 Git 中：从归档或本人克隆 `work/e10-B-manual.i9gc5v/` 获取
- 归档路径见 `docs/students/241880555/e8-e10/个人报告.md` 与服务器 `~/devops-submissions/241880555/`
- GitHub：PR #17（`student/241880555/e8-e10` → `main`）；CI 见 `docs/students/241880555/e8-e10/CI记录.md`
