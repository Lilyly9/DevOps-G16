# E5 · 论文1复现

本目录是 E5–E7 的**唯一一份实验包代码**，E6/E7 复用同一份（不另存副本）。

| 路径 | 内容 |
| --- | --- |
| `A-buildchecker/` | A 实验包：`services/`、`scripts/`、`fixtures/`、`tests/`、`ci/`、`Makefile` |
| `B-draft/` | B 实验包（同上结构） |
| `evidence/A1-<学号>/`、`evidence/B1-<学号>/` | 本阶段证据归档 |
| `reports/A1-<学号>.md`、`reports/B1-<学号>.md` | 本阶段报告 |

> 任务分工与判据由组长私下分发，不随仓库提交；`work/` 不提交（实验包 `.gitignore` 已忽略）。

## 状态

| 角色 | 状态 | 关键判据 | 证据 |
| --- | --- | --- | --- |
| A1（E5-A） | 待填 | 输出 `1`；`make-db.txt` 含 `main.o: main.c unused.h`；trace 读到 `config.h` | — |
| B1（E5-B） | 已完成（2026-10-23） | `build_exit_code=1` 且日志含 `make: not found`；候选构建 0 且运行 `hello E3` | `evidence/B1-241880555/` |

## A1 · E5-A BuildChecker 原始证据

待本人补充（命令与预期见私发的任务分工文档 §5 A1）。

## B1 · E5-B DRAFT 失败与候选

- 证据：`evidence/B1-241880555/`（index.md 为入口）；报告：`reports/B1-241880555.md`
- 关键判据：服务镜像单测 **24 passed**；E5 采集脚本退出码 **0**；`build_exit_code=**1**`，`build-retry.log` 第 30/34 行 `make: not found`；候选构建 **BUILD_EXIT_CODE=0**；同镜像 `--network none` 运行 **VERIFY_EXIT_CODE=0**、输出精确 `hello E3`
- 镜像：`course1020-draft:241880555`（服务）、`course1020-draft-e5:241880555`（候选复建，`sha256:b5fc01af…`）
- 候选来源：Claude Sonnet 4.6（2026-10-23），两类提示全文独立生成，非 replay；最终候选 sha256 `ede21b0f…` 与包内 DeepSeek-E5.Dockerfile 逐字节一致（趋同，非复制），详见 `evidence/B1-241880555/candidate/候选来源记录.json`
- 运行环境：阿里云 B 组 ECS（ecs.c9i.large）；docker.io 直连被 DNS 污染，daemon.json 配 mirror+dns，apt 经 squid 走内网镜像；过程故障与处理见报告 §3

## 给 E6 / E7 的约定

- 执行前先 `cd ../e5/A-buildchecker`（或 `../e5/B-draft`），代码只有这一份。
- 镜像 tag 统一 `course1020-buildchecker:<学号>` / `course1020-draft:<学号>`，不要用默认 `:local`。
- 新增测试放本目录 `services/<service>/tests/test_extra_<学号>.py`，不要改动他人文件。
