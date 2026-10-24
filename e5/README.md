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
| A1（E5-A） | 复现实测/补测完成；环境自检待达标（2026-10-24） | E5=0、输出 `1`；声明/cc1 读取/同任务 as 输出对应；容器 **18 passed**；doctor=1（3.5<4 GiB） | [证据](evidence/A1-241880485/index.md)、[报告](reports/A1-241880485.md) |
| B1（E5-B） | 已完成（2026-10-23） | `build_exit_code=1` 且日志含 `make: not found`；候选构建 0 且运行 `hello E3` | `evidence/B1-241880555/` |

## A1 · E5-A BuildChecker 原始证据

- A1：焦龙 / 241880485；证据入口 [index.md](evidence/A1-241880485/index.md)，[报告](reports/A1-241880485.md)。
- 实际源码 `ac7a040ec615c13bca7d2ec2b79347108631237a`；镜像 `course1020-buildchecker:241880485`，image ID `sha256:a8c15fd4391437a3f5497e9feee0d4e3053d4a488e2d1576cb8c12d65c9edc23`。
- 新 E5 入口退出 **0**，输出 **1**；`make-db.txt:1061` 声明 `main.o: main.c unused.h`，`trace/t.16:580` 成功只读打开 config.h，`t.15:64,84` 和 `t.17:23` 支持同 recipe 目标归属；手工判断 MD=config.h、RD=unused.h。
- 新增独立 `test_extra_241880485.py` 一项回归，容器 **18 passed**（课程 15 + A2 2 + A1 1）；共享服务实现/他人测试未改。
- **环境限制**：原 doctor=1，唯一必需项为 A16 可见内存 3.5 GiB < 脚本最低 4；完整 DoD 未标全通过。构建首次 Docker Hub frontend 超时后，用本人构建副本沿用 E4 已验证网络下载地址，固定 digest/锁未变；全部差异和失败日志可查。
- A1 不代做 A2 的 E6 修复复检或 A3 的 E7/CI。

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
