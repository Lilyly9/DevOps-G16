# E14 候选发布说明（B3 · 241880597）

> B3 主责维护候选发布核对记录。本说明汇总 `v0.9-rc` 候选涉及的仓库、完整 SHA、镜像、E13 门禁、CI 与已知问题。RC 标签与 Release 由组长执行，B3 核对。

## 候选范围

- 候选标签：`v0.9-rc`（不覆盖已有 `C0`/`C1`/`C2` 标签）。
- 配对：A16 ↔ B16，仓库 `https://github.com/Lilyly9/DevOps-G16`。
- 发布对象：E11-E12 四服务（BuildChecker / EChecker / DRAFT / MDFixer）经 `labs/e13e14/compose.yaml` 编排，接受 `labs/e13e14/orchestrate.py` 五阶段编排。

## 两轨实际仓库与完整 SHA

| 轨 | 仓库 | base（C0） | target（C1） | profile |
| --- | --- | --- | --- | --- |
| A（tokenstat） | A1/A2 提供 | `74fd1f2a86ea4e345245e41011f300aa94ae56c1` | `7fabf45ec98fb1b7ffe101b3621272b93f0be4d5` | 默认（main/helper/config） |
| B（e13-b-project） | B1 提供，`data/e13-b-project` | `e9ce878b1e2c46bd7d86e463ff9115b2fc2e6158` | `48b64156548b3fd8af1ed9ed25eee60d0f92371d` | `profile=true`（多文件） |

- B 轨四容器 E2E：job `job-5afabf021a0a46ff8f19088c25c8a556` / trace `trace-11436bef785140c9bb56516b75c220db`，五阶段 SUCCEEDED，recheck 无 MISSING。
- 固定样例四容器 E2E：job `job-695e68fd67f04a22b6b2f01efa3adf13` / trace `trace-a3580ab57c5c484a9f3099ea7b1815b2`，五阶段 SUCCEEDED。

## 镜像 ID / digest

| 镜像 | 标识 | 说明 |
| --- | --- | --- |
| 服务镜像 `course-e11e12:241880597` | image ID `98c22b63fa7e` | 云机已构建，四容器运行基础 |
| B 轨候选镜像（DRAFT 产出） | `sha256:683694107f57eda5e7c84fe2416c61bd85a5a11d159c7c15f6124e5497407d2c` | 由 `data/e13-b-project/candidate.Dockerfile` 构建，验证输出 `2` 匹配 |
| H3 候选镜像（DRAFT 产出） | `sha256:ab14d2113ccf4b652651db281e8a960f844c200e3bf6b4fb2c4c7f2b09f19159` | 候选补装 `strace`，验证输出 `1` 匹配 |

## E13 门禁状态

| 项 | 状态 | 证据 |
| --- | --- | --- |
| C1-C8 交叉测试 | C2/C3/C4/C7/C8 有结论；C1/C5/C6 待对应主责闭环 | [cross-test-record.md](cross-test-record.md) |
| H1 jsmn / H2 inih / H3 tiny-AES-c | 三者均已五阶段通过（A2 / B1 / B3） | H3 见 [cross-test-record.md](cross-test-record.md) |
| 运行日志 Secret 扫描 | 0 hits / 0 errors | `scan_runtime_logs.py` 退出码 0 |
| 远端必需 CI | 未绿（云机访问 GitHub TLS 超时） | [blockers.md](blockers.md) BLOCK-3 |

## CI 状态

- 远端 GitHub Actions 必需 CI 尚未在可访问 GitHub 的机器上跑绿；云机 `git fetch/clone` 报 `GnuTLS recv error (-110)`。
- 绕过：云机以本地 remote（`/root/241880555/DevOps-G16`）绕过 TLS（见 [ADR.md](ADR.md)）；`push`/PR/CI 需在本地 Windows 完成。

## 已知问题

- BLOCK-3：云机访问 GitHub 不通，RC 发布「必需 CI 绿色」判据暂不满足，`v0.9-rc` 标签尚未打出。
- 全组 C1/C5/C6 未闭环前，不判定整组 E13/E14 验收通过。

## 发布前置

仅当以下全部满足后才创建 `v0.9-rc`：阻断 Issue 为零、C1-C8 有明确结论、H1-H3 各有结果、日志扫描通过、必需 CI 绿色。
