# CI记录（B1 · 郭德林 241880555）

| 项 | 值 |
| --- | --- |
| PR URL | https://github.com/Lilyly9/DevOps-G16/pull/17 |
| 个人分支 | student/241880555/e8-e10 |
| 报告提交 SHA | 8a3986dd6abd243471c5e5c44fc4d5d541ce78d3（`git rev-parse HEAD`，见提交 feat(e8-b)） |
| workflow | .github/workflows/e8e10.yml（检查名 **e8e10-quality-gate**，workflow 显示名 "E8-E10 teaching validation"）+ 原 E7 A/B quality gate |
| run URL | https://github.com/Lilyly9/DevOps-G16/actions/runs/41582298352（pull_request 事件） |
| headSha | 8a3986dd6abd243471c5e5c44fc4d5d541ce78d3（与报告提交一致，已核对） |
| conclusion | success（CI_EXIT=0，`gh run watch --exit-status`） |
| artifact | e8e10-evidence-41582298352（A/B 双轨六路线证据），已下载至 `work/ci-e8e10/41582298352/artifacts/`，`run.json` 同目录 |

## 同一提交的其他检查（pull_request 事件）

| 检查 | run | 结论 |
| --- | --- | --- |
| E7 A quality gate | 41582298333 | success |
| E7 B quality gate | 41582298335 | success |
| E8-E10 teaching validation（e8e10-quality-gate） | 41582298352 | success |

> 本表记录报告提交（8a3986d）对应的真实 CI。CI记录.md 的回填提交（docs 变更）在 PR checks 中同样绿色，最终以 PR 最新 headSha 的 checks 为准。
