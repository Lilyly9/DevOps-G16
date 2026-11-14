# A1 → A2/B1：E12 项目与镜像交接

截至 2026-11-14，已检查 G16 的 C/Make 目录和相关 Git 历史，以及可用的 E8–E10 A1 证据包。E3–E7 的 C 文件位于 fixtures、实验副本或证据目录，E8–E10 有样例提交及独立扩展的历史。它们能重验 BuildChecker，不能证明有满足手册的本组实际维护项目。真实项目验收登记为待补；以两组能确认来源、提交和实际修改的项目为准。

| 交给谁 | 已交接的原件 | 接真实项目时需对齐 |
| --- | --- | --- |
| A2 | [真实基线图](evidence/e12/baseline-full/actual-graph.json)、[缓存](evidence/e12/baseline-cache.json)、[目标全量](evidence/e12/target-full/findings.json)、[增量报告](evidence/e12/incremental-report.json) | 用实际项目提交和配置替换样例输入；目标和规则映射、扫描执行环境由 A2 继续接入 |
| B1 | [A16 候选副本](evidence/e12/candidate.Dockerfile)、[DRAFT 构建结果](evidence/e12/draft-build/result.json)、[六次镜像执行校验](evidence/e12/verification.json) | 候选需含 `strace`、GNU Make、项目编译工具链；以 DRAFT 通过验证的完整 `sha256:…` 为同一 Docker daemon 的执行输入 |
| B2 | [补丁](evidence/e12/candidate.patch)、[验证报告](evidence/e12/validation/validation.json)、[最终全量重检](evidence/e12/final-full/findings.json) | 本轮最后一次动态全量运行已使用 DRAFT 镜像；`validate` 内部的构建与运行仍在外层容器 |

真实项目选材时共同确认：仓库来源、base/target 的完整 SHA、提交差异及预期 MD、目标提交中的 `Dockerfile.broken`、候选及其摘要、构建测试命令、输出和头文件变化断言。若只有课程样例，就按样例验收继续联调，并等待合适项目或课程对替代数据的明确口径。
