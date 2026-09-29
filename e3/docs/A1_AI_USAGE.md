# A1 E3 AI 使用记录

成员：焦龙，Git 作者 illusiri。

## 工具与任务

使用 OpenAI Codex。用户要求按 E3 PPT 和队友的 E3_TASKS.md 完成本人的 A1 工作，在原 DevOps-G16 中新增实验目录，避免改动其他成员产物。

## 提示与建议

- 阅读最终分工，确认 A1 做 MD/RD 样本、真实构建行为和 Linux 原始跟踪；C0/C1/C2 与参考修复属于其他成员。
- 采用队友规定的小写 e3/；脚本和运行目录均带 A1 标识，环境/报告放在本人约定路径。
- 先冻结故障样本并建立真实 Git 提交；自动运行时每次新建副本，记录命令、退出码、stdout/stderr、源码和 mtime/hash。
- 缺少课程实验包时按 PPT 手工搭建，不声称运行课程 run_lab.py。
- 保留人工预期来源 MANUAL_EXPECTED，将实际观察和 Linux 原始证据分别保存。

## 人工指示与处理

- 用户确认现有 VMware Linux 虚拟机；本次沿用已有环境，不要求课程服务器或 Docker。
- AI 建议的脚本、字段及文档由实际执行结果验证；没有伪造组员采纳记录或声称 A3/B3 已完成复核。
- Windows 和 Linux 的配置/版本分别记录；Linux 系统调用证据不能由 Windows 日志替代。
- 不改公共 Schema、A2/B1/B2 样本、A3/B3 公共文档；A1 文档集中在 e3/docs/A1_*.md 供汇总。

## 验证与关联文件

真实执行结果见 A1_REPORT.md、对应 work/commands.json 和 observations.json。固定源码提交、脚本提交和证据提交见 A1_CONTRIBUTIONS.md。本阶段的原始 trace 不等同 BuildChecker 完整检测算法的输出。

- Windows 和 Ubuntu 两轮行为均通过；Linux 额外完成 strace 取证、编译进程身份确认及 make -pn 声明核对。
- 运行 `a1_verify_evidence.py` 核验两轮证据，原始源码文件与真实提交的 hash 逐项相符，退出码/日志/程序输出/时间戳及源码对照均通过。
- Codex 的只读复核代理独立审查全部要求与证据，指出根忽略规则会漏掉环境摘要；本次单独强制加入 A1 环境文件，未改共享规则。
- 复核还建议把运行器的 dirty 检查改为 `git diff HEAD`，覆盖已暂存但未提交的源码修改；已修正。该修正不改变已记录的源码与实验结果。
- Linux 一轮 work 与原始跟踪合计约 200 KB；只提交日志、源码快照和元数据，不提交构建二进制。
- A1 证据使用局部 Git 属性保留原始字节；离线核验同时复算每个源码快照的 hash/大小，防止换行转换破坏证据。
