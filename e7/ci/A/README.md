# A3 CI 记录

这些记录只证明实际执行的检查，不宣称保护已应用或 PR 已合并。

| 阶段 | 记录 |
| --- | --- |
| 正常 | [run 40088682607](https://github.com/Lilyly9/DevOps-G16/actions/runs/40088682607)，源码 `6c12a45`，18 项服务测试 + 八项 gate 通过 |
| 失败 | [PR run 40088810222](https://github.com/Lilyly9/DevOps-G16/actions/runs/40088810222)，源码 `8f05148`，1 failed / 18 passed；另存 push run 40088775891 |
| 恢复 | [PR run 40088885448](https://github.com/Lilyly9/DevOps-G16/actions/runs/40088885448)，源码 `96683c3`，19 passed、gate 8/8，CI success |

各阶段 `run.json`、`run.log`、`artifacts.json` 是 GitHub 返回的实际记录；`artifact-summary/` 保存下载后核验的源码 SHA、测试日志、gate JSON/CSV；`artifact-files-sha256.json` 记录整个下载内容的哈希。完整 artifact 临时下载到 `/tmp/devops-a3-<阶段>-artifact`，远程可按 artifacts.json 的 ID 下载（保留 30 天）。未将容器内编译产物提交。

演示 PR：[#4](https://github.com/Lilyly9/DevOps-G16/pull/4)，保持草稿。`failure/PR.json` 保存失败时的实际状态。即使 mergeStateStatus 是 BLOCKED，也不能归因于分支保护：它是草稿，且 main 的 `protected=false`。未尝试实际合并；未伪造 merge-rejection.log、退出码 1 或 PR-merged.json。

## 保护配置的剩余工作（仓库所有者执行）

`../main-protection.json` 是待应用草案。A 检查 App ID 15368 已通过 check-runs 实测；B3 须先提交 B 工作流并产生 `e7-b-quality-gate` 检查，然后核实其 App ID。当前账号 `admin=false`，详见 repository-access.json。

两个检查都就绪后，由管理员读取当前配置，确认不会覆盖新增的团队规则，再按任务要求一次性应用草案。不要先把不存在的 B 检查设为必需，否则所有 PR 都会等待它。

管理员可在仓库根运行以下命令（不是本次已执行命令）：

```sh
sha=$(git rev-parse HEAD)
gh api "repos/Lilyly9/DevOps-G16/commits/$sha/check-runs"
gh api --method PUT repos/Lilyly9/DevOps-G16/branches/main/protection --input e7/ci/main-protection.json
gh api repos/Lilyly9/DevOps-G16/branches/main/protection
```

其中 sha 必须对应 GitHub 上已经产生两个检查的真实提交；本地未推送的提交不能用于核对。保护应用后，重新安排失败演示：失败时确认非草稿 PR 因必需检查而 BLOCKED、普通合并被拒绝并退出 1；只修正测试预期后两轨道检查成功，再记录最终 MERGED、mergeCommit、mergedAt。不能用本次草稿状态替代这轮验收。

路径门控放在工作流内部，不使用 workflow 级 paths 过滤，避免必需检查停在 Pending；依据：[GitHub 官方说明](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)。

## 新材料补齐后的本地状态（2026-10-24）

当前源码 `a977ac905e7767ec4ec438fe3b4d84963b3dd824` 已补语法、源码/历史和镜像扫描；旧编码解码修复已验证。新版工作流 actionlint 与本地等价执行通过，但按本人要求未推送，故旧三态 run 不代表新版本已在 GitHub 验证。官方演示测试本地错误/恢复结果见 `../../evidence/A3-241880464/course-recheck-20261024/`。原有远程记录及自写样例来源保留。

main-protection.json 现按官方 A 模板补齐 review/force-push/deletion/conversation 设置，并添加同仓 B 必需检查；仍为未应用草案。B App ID 必须实际核对，不能因模板写 15368 就称已验证。接手时先让 A/B 工作流就绪，再由仓库所有者配置保护并做正式拒绝/恢复/合并验收。不得直接对当前草稿 PR 的状态作保护结论。
