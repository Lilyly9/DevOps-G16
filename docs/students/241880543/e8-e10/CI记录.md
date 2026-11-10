# B2 PR / CI 交付记录

角色 / 学号：B2 / 241880543；分支：`student/241880543/e8-e10`。

2026-11-10 的完整个人实验见 [个人报告](个人报告.md)。本轮以 [PR #14 检查页](https://github.com/Lilyly9/DevOps-G16/pull/14/checks) 和提交归档中 `work/ci-e8e10/` 的实际运行元数据为准。以下记录保留 2026-11-03 E9 单阶段交付时的状态。

- 公共导入依赖：`origin/teaching/e8-e10`，提交 `7f6a448`；本次先在个人分支复用，未替组长合并 main。
- 实现与 WSL 本地实验源码：`3befe15c3912056474c359b7990b84048f53773f`。
- 本地课程单测：9/9 通过；三种风格候选检查、副本应用及头变化增量构建通过。
- 本机 Docker 不可用；个人镜像未构建，image ID 未产生。
- 草稿 PR：[Lilyly9/DevOps-G16#14](https://github.com/Lilyly9/DevOps-G16/pull/14)，head=`student/241880543/e8-e10`，base=`teaching/e8-e10`。公共导入合并前保持依赖关系；没有替组长合并或修改保护。
- 本次交付 CI 源码 SHA：`883c7792c22752f4d9d35f57132e559beb91ae64`。它在实现提交 `3befe15` 后仅增加报告和证据，三个实验源码文件字节相同。
- 优先采用 PR 事件的 [E8–E10 run 41568698562](https://github.com/Lilyly9/DevOps-G16/actions/runs/41568698562)：headSha 精确匹配上述 SHA，conclusion=`success`，检查名 `e8e10-quality-gate`。9项测试和A/B六路线均完成，A轨矩阵30/30一致，B轨三项validation通过。这是公共CI回归，不登记成本人执行其他角色的个人实验。
- 同 SHA 的 [E7 A PR检查](https://github.com/Lilyly9/DevOps-G16/actions/runs/41568698521) 与 [E7 B PR检查](https://github.com/Lilyly9/DevOps-G16/actions/runs/41568698557) 均为 success；未删旧检查。
- 同 SHA 的push事件 [E8–E10 run 41568505083](https://github.com/Lilyly9/DevOps-G16/actions/runs/41568505083) 也成功；未用它替代PR事件的核对。
- Artifact：`e8e10-evidence-41568698562`，ID=`13200855273`，119,703字节，原设14天；过期时间2026-11-17 10:53:10（Asia/Shanghai）。已实际下载ZIP并校验完整性与API digest：`17a10af0867ff98658ad6accf6d970be3d0624a9878c1e5dceb080b239da56c7`。
- 原始run/jobs/artifacts JSON、公共验证日志、完整artifact ZIP及独立核验结果已保存在 `e9/evidence/B2-241880543/ci/41568698562/`，随分支持久保存；本机原下载还在 `work/ci-e8e10/41568698562/`。Actions 内构建并运行 `course-e8e10:ci`，不冒称已构建本人 `course-e8e10:241880543`。
- 后续只补充此CI记录和artifact证据的提交不改实验源码；其最新run另在PR检查页可查，不把前一次run的headSha改写为后续记录提交。
- 组长审核/合并、服务器副本及 B3 收件确认：尚未发生，个人代理不代填。
