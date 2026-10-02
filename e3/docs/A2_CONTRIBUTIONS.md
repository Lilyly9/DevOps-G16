# A2 E3 贡献记录

- 姓名：万宇。
- Git 作者：`adscfe <asdfs1243@noreply.gitcode.com>`。
- 工作范围：EChecker 的 C0/C1/C2 真实提交链、三版本快照与导出/校验脚本、增量基线实测、人工预期与本人记录。
- 样本目录：`e3/fixtures/commits/`（`lab/` 为当前工作副本，`C0/`、`C1/`、`C2/` 为冻结快照）。
- 人工预期：`e3/expected/echecker-c0-c1-c2.md`、`e3/expected/echecker-c0-c1-c2.json`。
- 脚本：`e3/scripts/a2_export_commits.py`、`e3/scripts/a2_run_echecker_baseline.py`。
- 实际证据：`e3/work/20261002-182617-A2-e1d9d6/`；环境摘要 `e3/env/toolchain-A2.txt`。
- 本人文档：`e3/docs/A2_REPORT.md`、`e3/docs/A2_AI_USAGE.md`、本文件、`e3/fixtures/commits/README.md`、`e3/A2_README.md`。
- A3/B3 后续汇总入口：本文件的本人信息与报告的七列基线条目；无需修改其他成员内容。

## 可追溯提交

| 真实提交 SHA | 内容 |
| --- | --- |
| `ca57cfb89643e19f0c2ab73637ae2f962f8f7658` | tag `C0`：初始版本，`main.o: main.c config.h` 声明正确，clean 输出 10 |
| `ef88dd77c8a452fb4f11b2978d0e1157f425e1db` | tag `C1`：`main.c` 新增 `#include "feature.h"`（`FEATURE 2`），Makefile 未同步 |
| `900d64c1a60d81d106beb84e4c4593cb576e5a92` | tag `C2`：只改 `CFLAGS = -O0 -DMODE=7`，源码保持 C1 |

快照、脚本、实测证据与文档的提交说明依次为 `test(e3): export A2 EChecker version snapshots and baseline runner`、`test(e3): record A2 C0 C1 C2 increment evidence`、`docs(e3): add A2 EChecker baseline expectations and records`；最终 SHA 可用
`git log --oneline --author=adscfe -- e3/` 查询，避免在提交内部填写自身尚未生成的 SHA。以上均为本地真实提交，是否已推送以远端 `origin/main` 为准。

## 验证结论

- 一轮实测（`20261002-182617-A2-e1d9d6`）28 条命令全部退出 0，输出依次为 10、12、12、13、12、19，与人工预期一致。
- C1 只改 `feature.h` 时 `make` 无任何编译动作、`main.o` 的 sha256 与 mtime 均未变化，程序仍输出 12；`make clean` 后为 13 —— MD 依据可核验。
- `make -n -B main.o` 命令快照：C0 与 C1 完全相同，C2 含 `-DMODE=7`；C2 增量 12、全量 19。
- `a2_export_commits.py --check` 通过：三个快照目录与对应 tag 的 blob 逐字节一致。
- 原始证据进入 Git 时保留实际字节（work 目录 `* -text`，fixture 目录 `* text eol=lf`）；没有提交 `app.exe`/`main.o` 二进制。
- A2 任务已完成，组内相互复跑与全组汇总待 A3/B3 组织；人工预期没有计入检测器准确率。
