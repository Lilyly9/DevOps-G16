# A16 / B16 E13–E14 联合验收索引（A3 汇总）

远端基线 `0e2121192692866240355c4dcb275cf749ee6c1c`，[基线 E13/E14 CI](https://github.com/Lilyly9/DevOps-G16/actions/runs/45315301356)。A3 [PR #34](https://github.com/Lilyly9/DevOps-G16/pull/34) 关联 [Issue #33](https://github.com/Lilyly9/DevOps-G16/issues/33)。修复已合入 `fa96f184760f1927621104542454450988e2eef0`，Issue 已关闭。该提交的 5 个工作流均通过。 [合并后 E13/E14 CI](https://github.com/Lilyly9/DevOps-G16/actions/runs/45325382170)

| 判据 | 可抽查证据 | 状态 |
| --- | --- | --- |
| C1 正常链路 | [A1 实际项目和原件](../../241880485/e13-e14/index.md)、[B2 跨组轮次与复验](../../241880543/e13-e14/index.md)、[A3 transfer-eta E11-A→E11-B 同字节自验](evidence/cloud-summary.json)、[B3 tokenstat 收件](https://github.com/Lilyly9/DevOps-G16/blob/7b9f98ade6d0ffdb7d9346fb75edc8696e558a37/docs/students/241880597/e13-e14/evidence/b-receive/fixed-md.json) | 已有真实报告与修复证据。B2 记录的 E12 路径会重新做增量检测，作为独立消费验收时须以 E11-B 的同字节证据为准。新 transfer-eta A3 交接任务待 B 侧对同一 job/trace 留证。 |
| C2、C3、C8 | [A2 实跑](../../241880496/e13-e14/index.md) · [A3 独立复验](index.md) | 旧目标拒绝、哈希拒绝、HTTP 409 对照均有结果 |
| C4 超时 | [B1 主跑](../../241880555/e13-e14/index.md) · [A3 受控超时与恢复](index.md) | 外层失败、内层超时、无残留对照均已登记 |
| C5 错误补丁与回滚 | [B2 报告及三路径原件](../../241880543/e13-e14/index.md) | B2 实跑，接受与拒绝分别留证 |
| C6 假 Key 和扫描 | [A3 个人记录](index.md) · [Issue #33](https://github.com/Lilyly9/DevOps-G16/issues/33) | 两次扫描退出 1→0，源码/历史/镜像/四角色日志通过。缺日志误判的问题已修复，已合入 |
| C7 失败隔离 | [A1 A侧](../../241880485/e13-e14/index.md) · [B3 B侧](https://github.com/Lilyly9/DevOps-G16/blob/7b9f98ade6d0ffdb7d9346fb75edc8696e558a37/docs/students/241880597/e13-e14/cross-test-record.md) · [A3 PR CI](evidence/ci-c7-isolation.json) | 两端和 CI 均有独立任务证据 |
| H1、H2、H3 | [A3 三项目请求与结果摘要](evidence/cloud-summary.json) · [A2 H1](../../241880496/e13-e14/index.md) · [B1 H2](../../241880555/e13-e14/index.md) · [B3 H3](https://github.com/Lilyly9/DevOps-G16/blob/7b9f98ade6d0ffdb7d9346fb75edc8696e558a37/docs/students/241880597/e13-e14/cross-test-record.md) | A3 三次均通过；原候选失败单独归档 |
| E14 四角色 | [A3 云端固定样例、transfer-eta 与恢复](index.md) · [A3 原始 B 项目复验](evidence/local-b-summary.json) · [B3 配对 B 项目四服务](https://github.com/Lilyly9/DevOps-G16/blob/7b9f98ade6d0ffdb7d9346fb75edc8696e558a37/docs/students/241880597/e13-e14/candidate-release.md) | 健康、五阶段、摘要和补丁验证都有实际记录 |
| RC、发布和回退 | [B3 候选说明](https://github.com/Lilyly9/DevOps-G16/blob/7b9f98ade6d0ffdb7d9346fb75edc8696e558a37/docs/students/241880597/e13-e14/candidate-release.md) | 候选待发布。正式候选提交、组内复核、发布级回退与标签由组长和 B3 验收 |

A3 的受控失败恢复是同一运行器下的任务恢复。发布级回退须用实际候选与已知可用版本另行核对。远端团队分支继续由各执行人维护，报告内早期“待执行”的文字以更新的原始运行和提交为准。
