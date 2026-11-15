# A1 → A2/B1：E12 项目与镜像交接

A1 本轮已在 G16 创建独立工具 `projects/transfer-eta`，实际基线、目标、候选、配置和验收入口见[子项目验收](transfer-eta.md)。A2 可用本机 API 实测产出的[目标报告](evidence/transfer-eta/api/output/incremental-check.json)和[下载校验](evidence/transfer-eta/api/verification.json)，B1/B2 可复查[项目候选](evidence/transfer-eta/candidate.Dockerfile)与[修复验证](evidence/transfer-eta/cli/validation/validation.json)。是否采用本轮新建项目作课程验收数据由课程方确认。

下面保留此前固定样例的交接记录。

| 交给谁 | 已交接的原件 | 接真实项目时需对齐 |
| --- | --- | --- |
| A2 | [真实基线图](evidence/e12/baseline-full/actual-graph.json)、[缓存](evidence/e12/baseline-cache.json)、[目标全量](evidence/e12/target-full/findings.json)、[增量报告](evidence/e12/incremental-report.json) | 用实际项目提交和配置替换样例输入；目标和规则映射、扫描执行环境由 A2 继续接入 |
| B1 | [A16 候选副本](evidence/e12/candidate.Dockerfile)、[DRAFT 构建结果](evidence/e12/draft-build/result.json)、[六次镜像执行校验](evidence/e12/verification.json) | 候选需含 `strace`、GNU Make、项目编译工具链；以 DRAFT 通过验证的完整 `sha256:…` 为同一 Docker daemon 的执行输入 |
| B2 | [补丁](evidence/e12/candidate.patch)、[验证报告](evidence/e12/validation/validation.json)、[最终全量重检](evidence/e12/final-full/findings.json) | 本轮最后一次动态全量运行已使用 DRAFT 镜像；`validate` 内部的构建与运行仍在外层容器 |

双方实际联调时从历史 target 取候选和对应报告，核对仓库来源、完整提交 SHA、报告哈希和预期修复结果。保留 B 端独立接收、消费及复验记录。
