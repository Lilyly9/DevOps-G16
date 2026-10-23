# E5 · 论文1复现

本目录是 E5–E7 的**唯一一份实验包代码**，E6/E7 复用同一份（不另存副本）。

| 路径 | 内容 |
| --- | --- |
| `A-buildchecker/` | A 实验包：`services/`、`scripts/`、`fixtures/`、`tests/`、`ci/`、`Makefile` |
| `B-draft/` | B 实验包（同上结构） |
| `evidence/A1-<学号>/`、`evidence/B1-<学号>/` | 本阶段证据归档 |
| `reports/A1-<学号>.md`、`reports/B1-<学号>.md` | 本阶段报告 |

> 任务分工与判据见仓库根 [E5-7_TASKS.md](../E5-7_TASKS.md)；`work/` 不提交（实验包 `.gitignore` 已忽略）。

## 状态

| 角色 | 状态 | 关键判据 | 证据 |
| --- | --- | --- | --- |
| A1（E5-A） | 待填 | 输出 `1`；`make-db.txt` 含 `main.o: main.c unused.h`；trace 读到 `config.h` | — |
| B1（E5-B） | 待填 | `build_exit_code=1` 且日志含 `make: not found`；候选构建 0 且运行 `hello E3` | — |

## A1 · E5-A BuildChecker 原始证据

待本人补充（命令与预期见 E5-7_TASKS.md §5 A1）。

## B1 · E5-B DRAFT 失败与候选

待本人补充（命令与预期见 E5-7_TASKS.md §6 B1）。

## 给 E6 / E7 的约定

- 执行前先 `cd ../e5/A-buildchecker`（或 `../e5/B-draft`），代码只有这一份。
- 镜像 tag 统一 `course1020-buildchecker:<学号>` / `course1020-draft:<学号>`，不要用默认 `:local`。
- 新增测试放本目录 `services/<service>/tests/test_extra_<学号>.py`，不要改动他人文件。
