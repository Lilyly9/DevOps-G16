# A16 期末实验核验索引

2026 年 11 月 26 日于 A16 云机验证教师样例、真实 E12、真实四服务及现场模式。原始运行源码为 `f714fe9570422a96d8f8fc91f75de16d66f28205`。真实项目是 `projects/transfer-eta`，基线为 `5ef9d829e2f893af23f60399dcb67095800d121e`，目标为 `e7414083c4f1760cb234f96a9d75f2d0255e3f57`。仓库中的复现入口接收各成员自己的运行配置。 [运行入口](../../../labs/final-microservice/README.md)

| 验收 | 真实结果 | 对照证据 |
| --- | --- | --- |
| 教师样例 | 正常和恢复成功，停 Worker 三次尝试后失败，可选读超时也有终态 | [任务摘录](evidence/teacher-sample.json) |
| 真实 E12 | 五阶段通过，235 件产物摘要复算一致，21 次项目命令运行于同一候选镜像 | [请求](evidence/e12-request.json) · [镜像与产物核验](evidence/e12-verification.json) |
| 错误补丁 | 普通测试通过，头文件变更验证失败。补丁拒绝，HEAD、工作区和 Makefile 摘要对照一致 | [补丁](evidence/incomplete-dependency.patch) · [拒绝结果](evidence/rejection.json) · [验证前](evidence/reject-before.json) · [验证后](evidence/reject-after.json) |
| 真实四服务 | EChecker 探测 `1 → 0 → 1`，停机任务 `DOWNSTREAM_UNAVAILABLE`，成功 2、失败 1。两次成功各核验 189 件产物 | [正常](evidence/normal-verification.json) · [故障](evidence/echecker-down.json) · [恢复](evidence/recovered-verification.json) · [探测曲线](evidence/prometheus-role-ready.json) · [任务计数](evidence/prometheus-jobs-total.json) |

全量归档作为期末报告附件保存在 A16 本机交付目录。归档摘要可与 [SHA256SUMS](evidence/SHA256SUMS.txt) 对照。组员复验和回传要求见 [分工文档](assignment.md)。
