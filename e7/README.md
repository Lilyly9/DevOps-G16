# E7 · 论文1验证（测试、CI 与合并门禁）

本目录只放 E7 的证据、报告与 CI 记录；实验包代码在 [`../e5/A-buildchecker`](../e5/A-buildchecker)、[`../e5/B-draft`](../e5/B-draft)。

> 任务分工与判据由组长私下分发，不随仓库提交。

## 状态

| 角色 | 状态 | 关键判据 | 证据 |
| --- | --- | --- | --- |
| A3（E7-A + CI-A） | 本地及 CI 正常/失败/恢复验证完成；保护/合并待验收 | 6 tests OK；18 项服务单测；gate 8/8 | [本人报告](reports/A3-241880464.md)、[证据](evidence/A3-241880464/index.md)、[CI](ci/A/README.md) |
| B3（E7-B + CI-B） | 待填 | gate 6 项全通过（五场景 + 单测）；超时容器已清理；CI 正常/失败/恢复 | `evidence/B3-<学号>/`、`ci/B/` |

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

林涵，241880464，分支 `e5-7/A3-241880464`。本地 Linux 实际运行：独立判定测试 6 项、服务单测 18 项、gate 八场景全部通过，总退出码 0；原始三次错误集合一致，修复后仅 Makefile 哈希变化且 findings 为空。

新增循环 phony 依赖测试并重建镜像。A 根工作流已运行成功，失败演示与恢复记录见 [报告](reports/A3-241880464.md) 和 [CI 索引](ci/A/README.md)。main 保护配置为待应用草案；当前账号无管理员权限，B3 工作流尚未就绪。保护拒绝合并和最终 MERGED 尚待实际验收，不声明整个 E7 已完成。

## B3 · E7-B + CI-B

待本人补充。
