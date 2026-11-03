# B3 CI-B 记录

E7-B 的 CI 闭环（正常 / 失败 / 恢复）由 B3（241880597）完成。main 分支保护要求 `e7-a-quality-gate` 与 `e7-b-quality-gate` 两个必需检查（见 [`../main-protection.json`](../main-protection.json)），本目录只记录 B3 实际执行的 B 轨检查，不宣称 A 轨检查已由本人执行。

## 三态记录

| 阶段 | 记录 | 结论 |
| --- | --- | --- |
| 正常 | [run 40212467838](https://github.com/Lilyly9/DevOps-G16/actions/runs/40212467838)，main 合入 PR #7（`eeb60ce`），`normal/run.json` | success，全步骤通过 |
| 失败 | [run 40212926689](https://github.com/Lilyly9/DevOps-G16/actions/runs/40212926689)，`888ac16` 故意错误 oracle，`failure/run.json` + `failure/job.log` | 单测 1 failed / 24 passed，`Build image and run service tests` 失败 |
| 恢复 | [run 40213089034](https://github.com/Lilyly9/DevOps-G16/actions/runs/40213089034)，`20b0364` 修正 oracle，`recovery/` | 25 passed、gate 6/6、扫描全通过，CI success |

## 拒绝与合并

演示 PR [#8](https://github.com/Lilyly9/DevOps-G16/pull/8)：先以错误 oracle 提交（`888ac16`）触发必需检查失败，合并被阻断；再以固定模板修正测试预期（`20b0364`），两个必需检查均成功后普通合并，merge commit `595f7a527fb108d401fffa578575006bc8b052df`，`merged_at` 2026-10-25T16:46:37Z。详见 [`PR-merged.json`](PR-merged.json)。

修正的是测试预期（`main(["version"])` 退出码由 1 改回 0），未修改服务算法；未使用管理员绕过、强推或跳过检查。模板来源与 SHA256 见 [`../../../e5/B-draft/ci/rejection-demo/course-source.json`](../../../e5/B-draft/ci/rejection-demo/course-source.json)。

## 归档文件

- `normal/run.json`：正常 run 的 GitHub 原始返回。
- `failure/run.json`、`failure/job.log`：失败 run 及完整 job 日志（含 `assert 0 == 1`、`1 failed, 24 passed`）。
- `recovery/run.json`、`recovery/gate-result.json`、`recovery/results.csv`、`recovery/unit-tests.log`：恢复 run 及下载 artifact 后核验的 gate/单测结果（25 passed、6/6）。
- `PR-merged.json`：PR #8 最终合并状态（merged、merge_commit_sha、merged_at）。
- `protection-readcheck.json`：B3 只读核对 main 保护；当前账号读取完整配置返回 404，必需检查以仓库内 `main-protection.json` 草案核对，且失败 PR 已被必需检查实际阻断。

> 说明：A3 以普通合并尝试捕获 `exit 1` 的拒绝日志；B3 采用「必需检查失败 → PR 合并阻断」路径，拒绝证据是必需检查的 failure 结论（`run 40212926689`），未在失败态再次发起合并调用。
