# A2 E3 实验报告：EChecker C0/C1/C2 增量基线

成员：万宇 / `adscfe`。日期：2026-10-02。依据：`E3_TASKS.md` 的 A2-1~A2-5，以及 E3 PPT 实际第 23—27、28 张（页脚 E3/24—28）。

## 结果

三条真实提交（tag `C0`/`C1`/`C2`）与六阶段对照全部实测完成（28 条命令退出码均为 0）：

| 阶段 | 实测输出 | 说明 |
| --- | --- | --- |
| C0 clean | **10** | 声明正确，输出 `BASE + MODE` |
| C1 增量（复用 C0 产物） | **12** | `main.c` 变了，必然重编译；**此时不能判“无 MD”** |
| C1 只改 `feature.h`（不 clean） | **12**，且无任何编译动作 | 漏重建：`main.o` 的声明缺 `feature.h` |
| C1 clean 重建 | **13** | 12 与 13 的差异就是 MD 的可核验依据 |
| C2 增量（复用 C1 产物） | **12**，且无任何编译动作 | 只改了 `CFLAGS`，普通 make 的时间戳检查看不到命令变化 |
| C2 clean | **19** | `10 + 2 + 7`，全量重建才用上 `-DMODE=7` |

结论：本样本对 EChecker 具备“可判断对错、别人能重跑”的增量基线；检测器尚未实现（E8），人工预期不计入工具准确率。三人复核与总表汇总由 A3/B3 组织，本记录不替他们填写完成状态。

## 固定版本与环境

- 仓库：`https://github.com/Lilyly9/DevOps-G16`；被检测项目：`e3/fixtures/commits/lab`。
- 真实提交（三个 tag，可 `git checkout`）：
  - `C0` = `ca57cfb89643e19f0c2ab73637ae2f962f8f7658`
  - `C1` = `ef88dd77c8a452fb4f11b2978d0e1157f425e1db`
  - `C2` = `900d64c1a60d81d106beb84e4c4593cb576e5a92`
- `git diff --name-only C0 C1` = `feature.h`、`main.c`；`git diff --name-only C1 C2` = `Makefile`。
- 本机没有课程 E3 实验包，按 PPT 手工等价搭建；没有运行课程 `run_lab.py`，也没有代做其他成员的产物。

| 环境 | GNU Make | C 编译器 | Python | Git |
| --- | --- | --- | --- | --- |
| Windows / AMD64 | MSYS GNU Make 4.4.1 | MinGW-W64 GCC 15.2.0 | 3.11.9 | 2.45.1.windows.1 |

本轮只在 Windows 上做了行为对照；本任务不需要 `strace`（Linux 原始跟踪是 A1 的 A1-9），所以不声称有 Linux 系统调用证据。工具绝对路径与完整版本见 `e3/env/toolchain-A2.txt` 与 `e3/work/<run-id>/environment.json`。

## 证据入口

| 运行 | 目录 | 状态 |
| --- | --- | --- |
| Windows 行为与命令快照 | [`20261002-182617-A2-e1d9d6`](../work/20261002-182617-A2-e1d9d6/observations.json) | 28 条命令全部退出 0，六阶段结论与预期一致 |
| 人工预期 | [`echecker-c0-c1-c2.md`](../expected/echecker-c0-c1-c2.md) / [`.json`](../expected/echecker-c0-c1-c2.json) | `MANUAL_EXPECTED`，与真实日志分离 |
| 版本快照 | [`fixtures/commits/`](../fixtures/commits/README.md) | `C0/`、`C1/`、`C2/` 与 tag 字节一致（`--check` 通过） |

每个 work 目录有 `environment.json`、`commands.json`、`observations.json`、`logs/` 和六个 `snapshots/`。每步命令都有 stdout、stderr 文件与真实退出码；运行中的 `app.exe`、`main.o` 只留在被忽略的 `runtime/` 副本，快照只保存源码与 `state.json`，不提交二进制。

## 可供 A3 汇总的七列基线条目

| 版本 | 配置 | 命令 | 预期 | 实际 | 依据 | 出处 |
| --- | --- | --- | --- | --- | --- | --- |
| C0 `ca57cfb` | `MODE=0`，`-O0` | `make clean`；`make`；`./app.exe` | 10 | **10**（编译+链接各一次） | `main.c` 只读 `config.h`，声明已含它 | `logs/c0-*`；`snapshots/01-C0-clean` |
| C1 `ef88dd7` | 同一配置 | 覆盖 C1 的 `main.c`/`feature.h` 后 `make`；`./app.exe` | 12 | **12**（重编译 `main.o`） | C0→C1 改了 `main.c`，必然重建 | `logs/c1-incremental*`；`snapshots/02-C1-incremental-from-C0` |
| C1 同上 | 同一配置 | 只把 `feature.h` 的 `FEATURE` 改成 3，不 clean，`make`；`./app.exe` | 不重编译、仍 12 | **仍 12**，`make` 输出“对 all 无需做任何事”，`main.o` 的 sha256/mtime 未变 | `main.o` 的声明缺 `feature.h` | `logs/c1-touch-feature*`；`snapshots/03-C1-stale-after-feature-edit` |
| C1 同上 | 同一配置 | `make clean`；`make`；`./app.exe` | 13 | **13** | 重新编译才纳入 `FEATURE 3` | `logs/c1-clean-rebuild*`；`snapshots/04-C1-clean-rebuild-feature3` |
| C2 `900d64c` | `-O0 -DMODE=7` | 复用 C1 产物，只覆盖 `Makefile` 后 `make`；`./app.exe` | 增量 12 | **12**，无编译动作，`main.o` 未变 | 目标依赖只有 `main.o`，时间戳检查看不到命令变化 | `logs/c2-incremental*`；`snapshots/05-C2-incremental-reusing-C1` |
| C2 同上 | 同上 | `make clean`；`make`；`./app.exe` | clean 19 | **19** | 全量重建才用上 `-DMODE=7` | `logs/c2-clean-rebuild*`；`snapshots/06-C2-clean` |

## 命令变化与声明快照的具体解释

`make -n -B main.o` 的命令快照（原文见 `logs/*-main-o-command.stdout.log`）：

- C0：`.../gcc.exe -O0 -c main.c -o main.o`
- C1：`.../gcc.exe -O0 -c main.c -o main.o`（与 C0 **完全相同**）
- C2：`.../gcc.exe -O0 -DMODE=7 -c main.c -o main.o`（与 C1 不同）

`make -pn` 过滤出的声明（原文见 `logs/*-make-pn.declared.txt`）三个版本都是：

```
main.o: main.c config.h
```

结合 `main.c` 的 `#include "config.h"` 与 `#include "feature.h"`，可以解释 C1/C2 的 MD 判断；结合 `CFLAGS` 的两次取值，可以解释 C2 增量 12 与全量 19 的差异。

**一条限制**：普通 `make` 不记录“上次用的是什么命令”，本阶段只把它作为**现象**留证（增量 12 / 全量 19、命令快照不同）；“命令变化未被捕获”的检测与归一化属于后续 EChecker（E8）与 E10 的一致性对照。

## 复现与离线核验

从仓库根目录，任意装有 GNU Make、C 编译器和 Python 3 的环境：

```bash
python e3/scripts/a2_export_commits.py --check          # 快照与 tag 字节一致
python e3/scripts/a2_run_echecker_baseline.py \
  --make <make> --cc <cc> --python <python>             # 每次新建 work/<run-id>/
```

`a2_export_commits.py` 的 `--check` 重算每个快照的对象 ID 并与 tag 的 blob 比较；`a2_run_echecker_baseline.py` 在跑之前会再做一次同样的校验，并用 `git diff --name-only` 确认 C0→C1、C1→C2 的实际改动文件就是预期的那几个。任一条不满足都会直接报错退出，不会产出“看起来通过”的证据。

## 与队友的交接

- A3：读取本报告的七列基线条目、`e3/env/toolchain-A2.txt` 与 work 目录，复跑后在公共文档记录自己的结论；`expected/echecker-c0-c1-c2.json` 的字段名沿用 E2 的 EChecker 契约（`type`/`target`/`dependency`/`configuration_id`/`changed_paths`），如需新增字段请先记 Backlog。
- B 组 / E12：C0 的图可作历史基线；本项目与 A1 的 MD/RD 样例是两个独立 fixture，不要混用各自的人工答案。
- 本人任务已完成；相互检查及总表汇总待队友执行。没有修改公共 Schema、A1/B 组样本或 A3/B3 的公共文档。
