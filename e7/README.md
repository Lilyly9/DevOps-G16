# E7 · 论文1验证（测试、CI 与合并门禁）

本目录只放 E7 的证据、报告与 CI 记录；实验包代码在 [`../e5/A-buildchecker`](../e5/A-buildchecker)、[`../e5/B-draft`](../e5/B-draft)。

> 任务分工与判据由组长私下分发，不随仓库提交。

## 状态

| 角色 | 状态 | 关键判据 | 证据 |
| --- | --- | --- | --- |
| A3（E7-A + CI-A） | A 功能、官方失败拒绝、恢复及合并通过；资源/共享配置待确认 | 云端 6 判定+2 回归、18 服务测试、8/8 gate；新版 CI 全步骤成功 | [报告](reports/A3-241880464.md)、[云端证据](evidence/A3-241880464/cloud-20261024/index.md)、[验收表](evidence/A3-241880464/验收记录.csv) |
| B3（E7-B + CI-B） | E7-B gate + CI-B 闭环通过；内存门槛待确认 | gate 6/6（五场景 + 单测）；超时容器已清理；CI 正常/失败/恢复并合并 | [报告](reports/B3-241880597.md)、[证据](evidence/B3-241880597/)、[CI 记录](ci/B/README.md) |

## 目录

```text
e7/
  evidence/A3-<学号>/   # gate-result.json、results.csv、故障场景摘要
  evidence/B3-<学号>/   # gate-result.json、results.csv、五场景摘要、清理结论
  reports/A3-<学号>.md
  reports/B3-<学号>.md
  ci/
    main-protection.json  # 唯一一份：两个必需检查都在里面
    A/                    # runs、artifact、protection 回读、merge-rejection.log、PR-merged.json
    B/
```

## CI 约定（A3 / B3 共用，避免互相覆盖）

- 根级 workflow：`.github/workflows/e7-a-quality-gate.yml`（A3 独占）、`e7-b-quality-gate.yml`（B3 独占）；**job name** 必须分别是 `e7-a-quality-gate` / `e7-b-quality-gate`，与课程保护配置一致。
- `defaults.run.working-directory` 指向 `e5/A-buildchecker` / `e5/B-draft`；artifact 从 `e5/<track>/work/ci/` 上传。
- 演示分支固定 `e7-gate-reject-demo-a` / `e7-gate-reject-demo-b`（同仓不能重名）。
- main 保护只应用**一次**：A3 起草并 `PUT`，B3 只读核对。
- `gh auth login` 只在 A3/B3 执行，且不同账号时先设 `GH_CONFIG_DIR`。

## A3 · E7-A + CI-A

林涵，241880464，个人分支 `e5-7/A3-241880464`。本地与云服务器功能验证均通过；云端为 Ubuntu 22.04.5，18 项服务测试、6 项判定、2 项回归、源码/完整历史/镜像扫描、语法及八场景 gate 均成功。已实际下载并核验云端原始文件，归档为脱敏副本；保留镜像源临时配方和首次网络失败记录。

新版正常 GitHub CI run 40092663505 全步骤通过。云端 doctor 仍因内存 3.5 GiB < 4 GiB 未通过；2026-10-25 的 A 官方失败已被普通合并策略拒绝，恢复后同一 PR #4 已 MERGED，正常交付 PR #5 也已 MERGED；详见 [正式验收](ci/A/official-protected-20261025/index.md)。B 工作流及完整共享配置仍待确认。旧三态记录保留自写样例来源，不代替新版官方测试的正式保护验收。详见本人报告和验收表。

## B3 · E7-B + CI-B

吴佳静，241880597，个人分支 `e7-gate-reject-demo-b`。云端手动跑通 build 与 gate（单测 24 passed、gate 6/6、无残留容器）；CI 三态闭环完成：正常 run 40212467838 全步骤成功，官方错误 oracle 使 `e7-b-quality-gate` 失败（run 40212926689，1 failed / 24 passed）阻断 PR #8 合并，官方 fixed 模板恢复后 run 40213089034 的 25 passed、gate 6/6 全通过，同一 PR 普通合并（merge `595f7a5`）。修正的是测试预期，未改服务算法；未用管理员绕过。云端 doctor 仍因内存 3.5 GiB < 4 GiB 未通过，与 A3 同源。详见本人报告、[验收表](evidence/B3-241880597/验收记录.csv) 和 [CI 记录](ci/B/README.md)。
