# A1 GitHub / CI 记录

## 公共导入

- [PR #13](https://github.com/Lilyly9/DevOps-G16/pull/13) 已按用户明确授权正常合并。
- 导入源提交 `7f6a448e9a85b37f81c47c9a949d834b925dea34`；main 合并提交 `f1653557d066f7a17b2d2dce020126c34b8f6fcf`。
- 新检查与原 E7 A/B 检查均成功；未修改分支保护。
- [PR 事件 run 41566357606](https://github.com/Lilyly9/DevOps-G16/actions/runs/41566357606) 对应导入版本，原7项测试和双轨六条参考路线。
- artifact `e8e10-evidence-41566357606`（ID 13198842503）已下载；它不能充当 A1 新增第8项测试的个人远程结果。

## 历史 E8 个人实验与个人 PR

实际云端实验源码为 `9ee3242f8d7ea1b6bb4091e2947d85d33a37aa8a`；本人镜像、标准和扩展两个 OUT、8项容器测试均已保存。它与后续代码/证据提交的用途不同，不倒改原始运行记录。

- 个人 [PR #15](https://github.com/Lilyly9/DevOps-G16/pull/15)，分支 `student/241880485/e8-e10`，已推送，等待组内审查合并。
- 已验证代码/证据提交：`57fda0aaf77ece6087f4cc5fc644377840865862`。
- [PR 事件 run 41569763447](https://github.com/Lilyly9/DevOps-G16/actions/runs/41569763447)：`head_sha` 精确对应上述提交，`completed / success`。
- 原 E7-A、E7-B 与新增 E8–E10 三门禁均成功；同 SHA 的 push run 41569749232 也成功。
- 本次远程日志明确出现 `test_header_include_invalidates_previous_dependency_graph`，原7项加本人1项，`Ran 8 tests in 0.378s`、`OK`。参考路线全部通过属于公共回归，不冒认其他人的个人任务。
- artifact `e8e10-evidence-41569763447`（ID **13200328435**，119745字节）和完整控制台日志均已下载，最终个人备份一并保存。精选 [CI 原件与下载校验](../../../../e8/evidence/A1-241880485/ci/personal/download-verification.json)、[真实测试/参考路线日志](../../../../e8/evidence/A1-241880485/ci/personal/validate-both-tracks.log)、[三门禁状态](../../../../e8/evidence/A1-241880485/ci/personal/pr-15-inspection.json)。

本记录随后仅做归档提交，会产生新的文档 SHA。此处保存的是已经验证的代码/证据 SHA，不能把旧 run 改写成新 SHA；最终文档提交仍由 PR 平台重新运行门禁。最终提交与真实 run、artifact 的精确绑定另存个人备份 `CI/final-source-and-run.json`，避免“把当前 SHA 写进自身提交”形成循环。

公共导入已合并；个人 PR 仍按分工交由组内审查。没有合并个人 PR、调整分支保护或代填他人结果。

## 本轮本人 E9-A / E10-A 交付

2026-11-03 已实时查询 PR #15：仍为 open；远程 main 为 `f1653557d066f7a17b2d2dce020126c34b8f6fcf`，本人远程分支为 `18a79582672a71d486abc656bc9007d4aebdceab`。已检查 A3、B1、B2 最新分支；没有将尚未合入 main 的队友改动直接并入本人分支。

本轮运行源码为 `18a79582672a71d486abc656bc9007d4aebdceab`；E9 OUT `work/e9-A-manual.eqLOHp`，E10 标准 OUT `work/e10-A-manual.eVOOik`，自主删除 OUT `work/e10-A-manual.n9BhPY`。手册实验、35行完整集合对照、动态重检与8项测试均已在服务器真实完成；下载后199项独立审查通过。[E9索引](../../../../e9/evidence/A1-241880485/index.md)、[E10索引](../../../../e10/evidence/A1-241880485/index.md) 保存手册交付，它们不依赖公共CI代替。

本轮新增交付提交的 PR 事件 CI 将在推送后按真实 head_sha、三项检查、run URL 与 artifact 下载校验登记。历史成功记录不填写为尚未运行的新提交结果。个人 PR 继续更新 #15，不自动合并，也不修改分支保护。最终文档提交与真实 run 的精确绑定另存完整本机个人备份 `CI/final-source-and-run.json`。
