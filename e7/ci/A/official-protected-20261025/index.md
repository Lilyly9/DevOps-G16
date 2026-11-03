# A3 官方失败、恢复和普通合并验收（2026-10-25）

本轮是 GitHub 实际操作，不依赖“默认设置完成”的假设。PR #5 的正常 A3 代码先普通合并进入 main；随后在同一个非草稿 PR #4 使用官方失败模板，记录失败和策略拒绝，再复制官方修复模板并普通合并。未使用 --admin、强推或管理员绕过。

| 项目 | 实际证据 |
| --- | --- |
| 正常代码入库 | [PR #5](https://github.com/Lilyly9/DevOps-G16/pull/5)，bootstrap/after-merge.json |
| 官方失败 | [run 40207305472](https://github.com/Lilyly9/DevOps-G16/actions/runs/40207305472)，1 failed / 18 passed |
| 非草稿被拒 | failure/pr-before-merge.json、merge-rejection.log、merge-exit-code.txt；退出 1，base branch policy prohibits the merge；尝试后仍 OPEN |
| 官方恢复 | [run 40207413777](https://github.com/Lilyly9/DevOps-G16/actions/runs/40207413777)，19 passed、gate 8/8，扫描/判定/回归全部成功 |
| 同一 PR 合并 | [PR #4](https://github.com/Lilyly9/DevOps-G16/pull/4)，recovery/PR-merged.json，普通合并成功 |

两次 run.json、run.log、artifacts.json 来自 GitHub；artifact-summary 是下载后逐文件核验的关键文本，artifact-files-sha256.json 是完整下载内容的哈希。被省略的二进制和完整 trace 仍保留在本地原始下载目录以及 GitHub artifact（受保留期限制）。

范围限制：main 显示 protected=true，A 的真实失败阻断和恢复合并已验证。但当前账号读取完整保护配置返回 404，不能据此确认 strict、管理员强制适用等所有开关。仓库只出现 A 工作流，B3 工作流未就绪，不能把 A-only 行为写成 A/B 双必需检查已完成。云主机 3.5 GiB 内存门槛仍待处理。此前旧自写样例和草稿阶段记录继续作为历史保存。
