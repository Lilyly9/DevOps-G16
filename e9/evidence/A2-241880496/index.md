# E9-A 证据索引（A2 / 万宇 / 241880496 / G16 / 轨道 A）

轨道 A 手册《9_E9_A组.md》第 0—10 步的**实际运行**结果。运行时间 2026-11-10，环境同 [E8 证据](../../../e8/evidence/A2-241880496/index.md)：`course-e8e10:241880496`（gcc 14.2.0 / make 4.4.1 / strace 6.13 / Python 3.13.14）。

## 身份

| 项 | 值 |
| --- | --- |
| 学生源码 SHA | `adf0421e61575869c2f3cca9c908ef6f07620633`（[student-source-commit.txt](student-source-commit.txt)） |
| 环境镜像 ID | `sha256:0a3e46d733048835ae762a5c309618db438d559abedb9bfa96b07d3018c05f84` |
| 原始 OUT | `work/e9-A-manual.8b1g7u`（本目录为精选副本） |
| 复制命令 | `run_stage.ps1 -Stage e9 -Track A`（[脚本副本](../../../docs/students/241880496/e8-e10/run_stage.ps1)），逐步等价手册 `lab_python "$OUT" <<'PY' ... PY` |

## 逐提交结果

内部受测项目提交（[project-git-log.txt](project-git-log.txt)）：

| 版本 | 内部提交 | 变化 | 复用/刷新 | added / resolved | 发现 |
| --- | --- | --- | --- | --- | --- |
| C0 | `2be1465` | 初始 | 刷新 2（`NO_HISTORY`） | — | MD config.h，RD unused.h |
| C1 | `b445453` | 普通表达式 `VALUE+helper()+0` | 复用 `main.o` `helper.o`，刷新 0 | 无 | 同上（图复用） |
| C2 | `181b6b2` | `main.c` 新增 `#include "extra.h"` | 刷新 2（失效原因 `main.c`） | added MD extra.h | MD config.h + extra.h，RD unused.h |
| C3 | `e19c36d` | Makefile 补 `config.h extra.h` 声明 | 复用 2（声明图重算） | resolved config.h、extra.h | 仅 RD unused.h |

对应报告：[baseline.json](baseline.json)、[C1.json](C1.json)、[C2.json](C2.json)、[C3.json](C3.json)。

## 独立预期与结论

| 检查 | 预期 | 实际 | 结论 |
| --- | --- | --- | --- |
| C0 构建与基线 | 程序输出 `1`，恰好两条 MD/RD | [C0-build.log](C0-build.log) 三行 gcc，`C0_BUILD_AND_BASELINE_PASS` | PASS |
| C1 复用 | 两目标复用、发现不变 | `C1_REUSE_PASS ['main.o','helper.o']` | PASS |
| C1 实际 make | 仍重编 main.o 并链接（复用只指依赖分析） | [C1-build.log](C1-build.log)：`gcc -O0 -c main.c` + 链接，无 helper.c | PASS |
| C2 刷新 | `main.o` 实际集合增加 extra.h，新增 MD | `C2_REFRESH_PASS [['MISSING','main.o','extra.h']]`，`actual['main.o']=[config.h,extra.h,main.c]` | PASS |
| C3 消除 | 两项 MD 消除，RD 保留 | `C3_RESOLVED_PASS`；`findings=[REDUNDANT main.o unused.h]` | PASS |

## 目录内容

- 四份扫描报告、三份构建日志、结论性输出。
- `steps/`：10 份逐步容器日志，末行 `STEP_EXIT_CODE=0`（第 10 步为连续提交汇总）。
- 内部项目最终源码副本与 `project-git-log.txt`（内部 `.git` 不入库）。
