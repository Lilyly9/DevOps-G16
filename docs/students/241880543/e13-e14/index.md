# E13–E14 B2 交付记录

> **2026-11-23 发布更新：** 已重新 fetch 确认 main `28c94de`，在原工作区提交并 push 实现 `52ceaef901189af90863f8395c51a0bf5e22e8b1`。已创建 [Issue #31](https://github.com/Lilyly9/DevOps-G16/issues/31) 与 [草稿 PR #32](https://github.com/Lilyly9/DevOps-G16/pull/32)。发布前后审计及 10 项 B2、3 项交接测试均通过。远端 CI 待实际结果；H1/H3 完整 E12、C1 和 E14 仍未完成，不申报通过。[发布证据](evidence/publication.json)。以下 2026-11-22 的权限与发布阻断记录保留为历史状态。


李敏君 · 241880543 · MDFixer · 2026-11-22

个人分支：`student/241880543/e13-e14`；基线：`28c94defee5af11ada42f9842cf03db2cb9da2e3`。实现和证据已在独立检出保存为本地提交 `8ec82c35c2a9a6d5774dbaf04cad33e10e564e53`；原工作区改动、暂存状态和 stash 保留。fetch/push 实际联网失败，PR 与远端 CI 未完成，尚未确认最新远端 main，不申报整组验收通过。[本地交付记录](evidence/local-delivery.json)。

[个人报告](REPORT.md) · [ADR](ADR.md) · [Issue 正文](ISSUE_BODY.md) · [PR 正文](PR_BODY.md) · [复跑入口](run_evidence.py) · [新发 H1/H3](TEACHER_RUNS.md) · [提交入口](submit.py) · [历史运行记录](HISTORY.md)

本页记录受限会话生成时的状态，不是发布成功证明。本轮重新执行 Windows B2 10 项契约和报告交接 3 项，均退出 0；没有新增声称 Linux 或容器运行。提交入口默认只做校验，已实际运行通过源码摘要、旧证据哈希、ZIP CRC 和上述 13 项测试。命令及阻断见[本轮记录](evidence/session-current.json)。

| 检查 | 实际结果 | 证据 |
| --- | --- | --- |
| 本轮 Windows B2 / 报告交接 | 10 项 / 3 项通过，均退出 0 | [B2 日志](evidence/windows-b2-current.log) · [交接日志](evidence/windows-handoff-current.log) |
| E11/E12 全量 | 75 项通过，退出 0；含新增 B2 10 项契约 | [日志](evidence/linux-full-tests-confirmed.log) |
| E13/E14 报告交接 | 3 项通过，退出 0 | [日志](evidence/linux-handoff-tests-confirmed.log) |
| E8/E10 回归 | 21 项通过，退出 0 | [日志](evidence/linux-lab-tests-final.log) |
| 真实 DRAFT | 首次缺 make，候选构建成功并实际运行输出匹配 | [摘要](evidence/draft-build-summary.json) · [原始归档](evidence/draft-build.zip) |
| C5 损坏补丁 | 拒绝修复；源文件和目标 HEAD 未变 | [三路径摘要](evidence/docker-c5-summary.json) |
| C5 语义错误补丁 | 补丁可应用且构建和初始输出通过，头文件变化及依赖检查不通过；拒绝并回滚 | [原始归档](evidence/docker-c5.zip)中的 `wrong-dependency/` |
| C5 正确补丁 | 接受；真实 strace 最终重检无 MISSING，允许保留 RD | 同一归档中的 `recovery/` |
| H1 主执行 / H3 复核 | 新发原始项目、C0/C1、请求已固定；GCC 编译运行输出 1、静态扫描、补丁预检成功；完整 E12 入口退出 2，未启动流水线 | [新发项目记录](TEACHER_RUNS.md) · [原始归档](evidence/teacher/teacher-runs.zip) |
| C1 对手项目 | 未完成，不申报通过 | 尚待本轮 A→B 当次报告及完整消费复验；仓库内 tokenstat 历史结果不算本人新运行 |
| E14 四容器 | 未完成，不申报通过 | `evidence/e14-image-*.log` 保存构建失败；没有四容器成功记录 |
| 本地提交 | 完成：独立检出实现提交 `8ec82c3`，原工作区保留 | [提交位置和验证](evidence/local-delivery.json) |
| push / PR / 远端 CI | 未完成；独立检出 fetch/push 均因联网失败退出 128 | [实际状态](evidence/local-delivery.json) |

## 可追溯性

实际运行环境为 WSL Ubuntu 22.04 / Python 3.10.12。同镜像 C5 使用本轮 DRAFT 构建的 `sha256:1542170ad4477d3b2b3c48e6fa6abb75aac1a2c464e3ccf31308aaebd65eddda`。原始目录：`work/e13-241880543-draft-20261122-01/` 和 `work/e13-241880543-c5-docker-20261122-04/`。

[Linux 检查点清单](evidence/verification-current.json)记录该次实际工作区字节摘要及 Git 规范化字节摘要；二者可能因换行符不同而不同。原始 `verification.json` 与旧 Windows 测试日志只代表同步 main 之前的历史环境。新发教师包已补齐 H1/H3 原件；新状态以[本次会话记录](evidence/session-current.json)和[教师项目记录](TEACHER_RUNS.md)为准，旧清单的缺输入说明是历史状态。

[独立证据核对](evidence/review-check.json)确认：清单文件与实现摘要一致，两个 ZIP 的 CRC 检查通过，18 条容器执行记录的请求与实际镜像相同，退出码均为 0。核对仅审阅原件，没有新增声称容器运行。

## 复跑

在具有 Docker 的 Linux 环境，从仓库根目录执行，并使用新的 OUT：

```bash
python3 docs/students/241880543/e13-e14/run_evidence.py \
  --out work/e13-241880543-c5-docker-new \
  --draft-result work/e13-241880543-draft-20261122-01/result.json
```

该入口只验证隔离的 MDFixer C5。新发教师项目使用 `run_teacher.py`，具体命令见 [H1/H3 记录](TEACHER_RUNS.md)；E14 四容器及对手项目需分别运行。失败尝试均保留，不复用旧 OUT；WSL 所有权适配仅对测试进程配置 safe.directory，没有修改全局设置。

## 剩余交付

当前会话写入原仓库 `.git/FETCH_HEAD` 被拒绝，GitHub 连接失败，WSL 返回 `Wsl/E_ACCESSDENIED`；直接本地 clone 也遇到 MSYS 权限问题。随后通过只读 HEAD bundle 成功建立独立检出 `D:/workspace/DevOps-G16-B2-e13e14-snapshot-20261122`，保存实现提交 `8ec82c3`，独立目录中复跑 10 项 B2 和 3 项交接通过，暂存的规范化源码及原始证据字节哈希全部吻合。独立检出再次实际 fetch/push 均失败，不能宣称已同步最新远端 main。

在具有正常 Git 写入和联网能力的终端，从上述独立检出的根目录运行：

```powershell
python docs/students/241880543/e13-e14/submit.py --publish
```

该入口先校验证据，随后 fetch；必要时保留 stash 并合并 main，再校验、提交 B2 白名单内的文件，普通 push，创建或复用缺陷 Issue 及草稿 PR。遇到其他人的改动、冲突或实现与原 Linux 证据不符时停止，不删除 stash。实际提交 SHA、Issue 和 PR URL 写入新的 `work/e13-241880543-submit-*/delivery.json`；远端 CI 仍须等待实际结果，不会由脚本写成通过。`--publish` 尚未在本会话运行。

H1/H3 已取得本次原始输入，等待 Linux Docker/strace 完整运行；C1 当次交接和 E14 四容器仍未完成，不创建 RC 标签或代替组长发布。
