# A2 E3 AI 使用记录

成员：万宇，Git 作者 `adscfe`。

## 工具与任务

使用 GitHub Copilot（VS Code，Chat/Agent 模式）。用户要求：先拉取远端最新版本，再按 `E3_TASKS.md` 完成本人 A2（EChecker 的 C0/C1/C2 增量基线），不要改动其他成员产物，并遵守“不代填他人姓名/贡献/SHA”“人工样例必须标注来源”的硬约定。

## 提示与建议

- 先读 `E3_TASKS.md` §5 A2 与 E3 PPT A 组步骤 9，确认交付物是 `e3/fixtures/commits/C0|C1|C2/` 与 `e3/expected/echecker-c0-c1-c2.md`，并要求“三个 SHA 可 checkout”。
- 把 C0/C1/C2 做成**本仓库真实的三次连续提交 + tag**（而不是只有目录快照），这样 `git diff --name-only C0 C1` 才是真正的“版本间变化”。
- 另建 `A-buildchecker` 之外的最小项目 `fixtures/commits/lab`，C0 声明正确、C1 增 `include` 漏声明、C2 只改 `CFLAGS`，与 PPT E3/24—27 一一对应。
- 用运行器脚本而不是手工敲命令：每条命令记 argv、cwd、退出码、stdout/stderr；每个阶段记文件 hash 与 mtime；`work/<run-id>/` 每次新建。
- 沿用 A1 的目录与命名习惯（`e3/scripts/a2_*.py`、`e3/env/toolchain-A2.txt`、`e3/docs/A2_*.md`、`e3/work/<时间>-A2-<后缀>/`），便于 A3 统一汇总。

## 人工指示与处理

- **被拒绝并改掉的做法 1**：第一版导出脚本用 `sha1(内容)` 校验快照与 tag 一致，实际 Git 对象 ID 是 `sha1("blob <长度>\0" + 内容)`，自检直接失败（`blob id mismatch for Makefile`）。改为正确的对象 ID 计算后 `--check` 通过；这个自检因此保留在脚本里。
- **被拒绝并改掉的做法 2**：第一版把 `main.o`、`app.exe` 一起复制进 `snapshots/`。与 A1 的“不提交构建二进制”口径冲突，改为只复制源码 + `state.json` 里的 hash/mtime，并重跑一轮（旧目录在提交前删除，未进入仓库）。
- **被拒绝并改掉的做法 3**：第一版“增量”步骤把目标版本的全部文件覆盖到运行时目录（包括内容未变的 `main.c`），这会让 `main.c` 的 mtime 变新而触发重建，C2 的“增量不重建”就不可能成立。改为按 `git diff --name-only <旧> <新>` 只覆盖真正变化的文件。
- AI 建议 Windows 上必须显式传 `--make/--cc/--python`（本机 `make` 不在 PATH；Git 系统配置 `core.autocrlf=true`），并给 fixture 目录加 `* text eol=lf`；这些都是实测验证过的，未凭猜测写入文档。
- AI 没有代填 A1/B 组/A3/B3 的姓名、贡献或 SHA；没有修改公共 Schema 与他人目录。

## 验证与关联文件

真实执行结果见 `e3/docs/A2_REPORT.md`、`e3/work/20261002-182617-A2-e1d9d6/commands.json` 与 `observations.json`（28 条命令全部退出 0，输出 10/12/12/13/12/19 与预期一致）。人工预期与真实日志分离，人工预期标注 `MANUAL_EXPECTED`，不计入工具准确率。提交 SHA 见 `e3/docs/A2_CONTRIBUTIONS.md`。

- 预期结论中的每一项都有独立判据：C1 的 MD 用“改 `feature.h` 不重编译（12） vs clean 重建（13）”证明，C2 的命令变化用 `make -n -B main.o` 快照与“增量 12 vs 全量 19”证明。
- 脚本自身带一致性防线：快照与 tag 的 blob 比对、`git diff --name-only` 的改动文件比对、每步输出断言，任何一条不满足都会失败退出而不是留下“看起来通过”的证据。
