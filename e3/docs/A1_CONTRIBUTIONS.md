# A1 E3 贡献记录

- 姓名：焦龙。
- Git 作者：illusiri。
- 工作范围：MD/RD 故障样本、人工依据、跨平台可重复运行、Linux 原始跟踪及本人证据说明。
- 样本目录：e3/fixtures/md-rd/。
- 人工预期：e3/expected/buildchecker-md-rd.json。
- 运行脚本：e3/scripts/a1_run_baseline.py。
- 实际证据：e3/work/ 中带 A1 标识的运行目录；Linux 跟踪另见 evidence/linux-verified/。
- 本人文档：e3/docs/A1_REPORT.md、A1_AI_USAGE.md、本文件及样本 README。
- A3/B3 后续汇总入口：本文件中的本人信息和报告的七列基线条目；无需修改其他成员内容。

## 可追溯提交

| 真实提交 SHA | 内容 |
| --- | --- |
| `9c36984236b97115f44daa24c5274a90dd905b37` | 冻结 MD/RD 故障样本及 Makefile.before，两轮实测均基于这一源码版本 |
| `f94237f996c8e0ade467f9ab180d469942b6356b` | 初始 A1 运行器、人工预期和本人记录；Ubuntu 实际执行的运行器版本由导出 manifest 锁定 |
| `7febaff4155313b6ea3a4e0337017592dd5562b9` | Windows/Ubuntu 真实日志、六阶段快照、Linux strace、环境、报告及离线核验；补充源码 dirty 检查与证据字节保护 |

本文的最终补充提交可用 `git log --oneline -- e3/docs/A1_CONTRIBUTIONS.md` 查询。以上版本均为本地真实提交，未推送状态不等同已经交付给全组。

## 验证结论

- Windows 运行：`20260929-110310-A1-4e5f8e`，13 条命令均退出 0，输出依次为 1、1、2、2。
- Ubuntu 运行：`20260929-110948-A1-00d164`，17 条命令均退出 0，同样输出 1、1、2、2，另外完成 Linux 原始跟踪。
- 离线核验通过：真实源码提交、快照字节与 hash/大小、命令与日志、修改时间、编译/链接，以及 GCC cc1 读取 config.h。
- 原始证据进入 Git 时保留实际字节；没有提交 app/main.o 二进制。
- A1 任务已完成，成员相互复跑和全组汇总待 A3/B3 组织；人工预期没有计入检测器准确率。
