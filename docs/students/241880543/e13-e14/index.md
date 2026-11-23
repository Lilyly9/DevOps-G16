# E13–E14 B2 交付记录

李敏君 · 241880543 · MDFixer · 更新于 2026-11-23

分支 `student/241880543/e13-e14`，基线 `28c94defee5af11ada42f9842cf03db2cb9da2e3`。[PR #32](https://github.com/Lilyly9/DevOps-G16/pull/32) · [Issue #31](https://github.com/Lilyly9/DevOps-G16/issues/31)。原未提交改动已纳入提交，原 stash 备份保留。

| 验证项 | 本轮实际结果 | 原始证据 |
| --- | --- | --- |
| E7 A/B 扫描修复 | 全仓库和历史扫描退出 0；读取凭据表达式不再误报，字面量密钥、含默认值的调用仍被拒绝 | `evidence/continuation-20261123/scanner-*.log`；远端修复提交四类 CI 均成功，见 `ci-scanner-fix.json` |
| Linux 回归 | E11/E12 75 项、E14 5 项、扫描回归 3 项均退出 0 | 同目录 `linux-e11e12.log`、`linux-e14.log`、`scanner-tests-linux.log` 及 exit |
| C5 | 真实损坏补丁拒绝、可构建但依赖错误的补丁拒绝回滚、正确补丁接受与 strace 最终重检通过 | [既有三路径原件](evidence/docker-c5.zip) |
| H1 jsmn / H3 tiny-AES-c | 本轮官方 E12 五阶段全部成功，同镜像命令各 20 条，最终无 MISSING，原始项目摘要和 Git 干净状态不变 | [本轮教师项目原件](evidence/continuation-20261123/teacher-linux.zip) |
| C1 A→B 正常链路 | A1 transfer-eta 新运行 A 侧检测、导出当次报告，B2 核对 SHA 后完成 E12 修复与动态复验，最终无 MISSING | [当次 A 报告和首次 B 尝试](evidence/continuation-20261123/c1-a-and-first-b.zip) · [B 成功重跑](evidence/continuation-20261123/c1-b-recovery.zip) |
| E14 四容器 | 固定样例、H1、H3、真实 transfer-eta 五阶段均成功；四个独立服务的 /health、角色日志、job/trace、报告 SHA、补丁接受及最终无 MISSING 均核对通过 | [H1](evidence/continuation-20261123/e14-four-services.zip) · [固定样例和 H3](evidence/continuation-20261123/e14-fixed-h3.zip) · [真实项目](evidence/continuation-20261123/e14-real-project.zip) |
| E14 超时恢复 | 实际 TIMEOUT 后源摘要不变、无新增容器；随后新 job/trace 正常五阶段成功 | [恢复原件](evidence/continuation-20261123/e14-fault-recovery.zip) |

[逐项 SHA、job/trace 与归档校验清单](evidence/continuation-20261123/verified-runs.json) · [本轮说明](CONTINUATION.md) · [报告](REPORT.md) · [ADR](ADR.md) · [教师项目来源](TEACHER_RUNS.md) · [历史记录](HISTORY.md)。最终 PR 提交的远端 CI 以 GitHub Checks 实际状态为准；已有绿色记录绑定具体源码提交，不能套用到后续提交。

## 复现与范围

本轮为 WSL Ubuntu 22.04 / Docker 29.1.3 实测。运行镜像由仓库课程 Dockerfile 的独立副本构建，使用可达的官方软件源及 host 构建网络；测试命令容器仍使用原有网络隔离。独立适配层记录了 Docker 构建网络包装脚本、Git 对挂载测试目录的信任和 core.filemode 配置。教师原始源码和 Git C0/C1 不变；C1 仅派生 HTTPS 安装候选，保留原候选摘要。

四服务使用课程 Compose 文件对应的端口、资源限制和挂载，以四条独立 docker run 命令部署。本轮验证的是四容器实际 HTTP 链路；没有执行 docker compose 命令。启动命令、容器 inspect、健康响应和退出码全部归档，各次仅清理本人容器。运行入口与构建副本保存在 `evidence/continuation-20261123/runners/`；每次需使用新的 OUT。

本页只申报上述 B2 实跑项目。整组 C1–C8、H2、E13 总门禁、跨机共享入口、RC 标签和 Release 仍须由对应成员及组长汇总，本人没有将整组 E13/E14 标记通过。失败尝试、旧 Windows 权限阻断和旧清单保留为历史证据，不能当作当前结果。
