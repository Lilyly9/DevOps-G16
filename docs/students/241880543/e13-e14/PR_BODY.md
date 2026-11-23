最终 BuildChecker 重检异常或超时时，旧流程会留下候选 Makefile。此修改将验证和最终重检纳入同一恢复边界，仅全部成功且无 MISSING 才保留补丁；其余退出恢复原始字节并保存 rollback.json、job/trace 与 SHA256。

修复 E7 A/B 扫描对凭据读取表达式的误报，保留字面量及强格式密钥检测和完整历史扫描。E14 复用既有 e12-profile/project_path 支持真实项目，并对历史基线统一使用目标项目配置。

实际验证：

- Linux E11/E12 75 项、E14 5 项、扫描回归 3 项全部通过；已有 10 项 B2 契约及真实 C5 三路径原件。
- H1 jsmn、H3 tiny-AES-c 官方 E12 全五阶段成功，各 20 条同镜像执行记录通过核对，最终无 MISSING。
- C1：A1 transfer-eta 当次 A 侧报告经 SHA 校验交给 B2，B2 构建、补丁验证及动态复验通过；首次 HTTP 软件源失败和 HTTPS 派生候选均归档。
- 四个独立 HTTP 服务完成固定样例、H1、H3、transfer-eta 五阶段；健康、job/trace、报告 SHA、补丁接受和最终无 MISSING 均核验。
- 受控 DRAFT 超时返回 TIMEOUT，前后源摘要不变且无新增残留容器；随后新 job/trace 的正常任务五阶段成功。
- E7 修复提交 b376720 的 E7 A/B、E8/E10、E11/E12 远端检查全部成功；最新提交以实际 Checks 为准。

证据：docs/students/241880543/e13-e14/index.md 与 evidence/continuation-20261123/verified-runs.json。四服务按课程 Compose 的设置使用 docker run 启动；构建网络和 Git 环境适配均留原件。整组门禁与 RC 未申报通过，PR 保持草稿。

Closes #31
