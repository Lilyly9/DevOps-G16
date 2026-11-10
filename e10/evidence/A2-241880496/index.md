# E10-A 证据索引（A2 / 万宇 / 241880496 / G16 / 轨道 A）

轨道 A 手册《10_E10_A组.md》第 0—13 步的**实际运行**结果，以及个人扩展（间接 include 用例 + 失效原因报告）的单元测试。运行时间 2026-11-10，环境同 E8：`course-e8e10:241880496`（gcc 14.2.0 / make 4.4.1 / strace 6.13 / Python 3.13.14，宿主 Windows 11 + Docker Desktop WSL2，4 vCPU / 8 GiB）。

## 身份

| 项 | 值 |
| --- | --- |
| 学生源码 SHA | `adf0421e61575869c2f3cca9c908ef6f07620633`（[student-source-commit.txt](student-source-commit.txt)） |
| 环境镜像 ID | `sha256:0a3e46d733048835ae762a5c309618db438d559abedb9bfa96b07d3018c05f84` |
| 原始 OUT | `work/e10-A-manual.pyylyj`（本目录为精选副本） |
| 复现 | `run_stage.ps1 -Stage e10 -Track A`（[脚本副本](../../../docs/students/241880496/e8-e10/run_stage.ps1)），逐步等价手册 `lab_python "$OUT" <<'PY' ... PY` |

## 六场景逐项结果（每类 5 次，共 30 行）

[results.csv](matrix/results.csv) 的 30 行 `equal` 全为 `True`；[gate.json](matrix/gate.json) 为 `{"track":"A","passed":true,"rows":30}`。

| 场景 | 变化 | 复用/刷新 | 失效原因 | 发现 |
| --- | --- | --- | --- | --- |
| unchanged | 无源码变化 | 复用 2 / 刷新 0 | `[]` | MD config.h，RD unused.h |
| body | `helper.c` 函数体等价改写 | 复用 2 / 刷新 0 | `[]` | 同上 |
| include | `main.c` 新增 `#include "extra.h"` | 复用 0 / 刷新 2 | `['main.c']` | 新增 MD extra.h |
| declaration | Makefile 补 `config.h extra.h` | 复用 2 / 刷新 0 | `[]` | 仅 RD unused.h |
| flags | `CFLAGS -O0 → -O1` | 复用 0 / 刷新 2 | `['flags']` | 仅 RD unused.h |
| header | `config.h` 新增 `#include "extra.h"` | 复用 0 / 刷新 2 | `['config.h']` | 仅 RD unused.h |

`失效原因` 列来自本人新增的 `lab.py:invalidation()`（见个人报告）。每个场景末次增量结果成为下一场景历史图；每类 5 次全部与同输入全量扫描的 `actual/declared/findings` 集合完全一致。

## 五次计时中位数（本机扫描耗时，含 git/gcc 调用与 gcc -MM）

| 场景 | n | 增量中位数 s | 全量中位数 s | 增量 min–max s | full/inc |
| --- | --- | --- | --- | --- | --- |
| unchanged | 5 | 0.1051 | 0.1119 | 0.0980–0.1093 | 1.06 |
| body | 5 | 0.0732 | 0.0867 | 0.0549–0.0875 | 1.18 |
| include | 5 | 0.1087 | 0.1183 | 0.0690–0.2335 | 1.09 |
| declaration | 5 | 0.1044 | 0.1077 | 0.0640–0.1477 | 1.03 |
| flags | 5 | 0.0774 | 0.0575 | 0.0650–0.1216 | 0.74 |
| header | 5 | 0.1125 | 0.1050 | 0.0786–0.1314 | 0.93 |

样本只有几十毫秒，单次抖动与计时粒度同量级，因此不改写为论文中的加速倍数；结论只用于“同一进程内两条路径等价”与“耗时量级”这两点。

## 动态重检

第 8 步对最终项目再跑一次真实 BuildChecker：[matrix/final-buildchecker/findings.json](matrix/final-buildchecker/findings.json) 为 `SUCCEEDED`，只剩 `REDUNDANT main.o unused.h`（`make-db.txt` 中声明行为 `main.o: main.c unused.h config.h extra.h`），trace 目录 `t.13`—`t.21`。函数内部已断言 BuildChecker 对象目标投影与 `scan()` 发现一致。

## 目录内容

- `matrix/`：`results.csv`、`performance-summary.csv`、`gate.json`、六类汇总 JSON、30 份成对原始 JSON（`<case>-r<n>-incremental.json` / `<case>-r<n>-full.json`）、`final-buildchecker/`（trace、make-db、两图、findings；其 `project/` 编译产物未入库）。
- `结论.txt`、内部项目最终源码副本与 `project-git-log.txt`。
- `steps/`：13 份逐步容器日志，末行 `STEP_EXIT_CODE=0`。
- `unit-tests.log`：`python3 -m unittest discover -s labs/e8e10 -p 'test_*.py' -v`，原 7 项 + 本人 3 项共 `Ran 10 tests ... OK`，退出 0。
