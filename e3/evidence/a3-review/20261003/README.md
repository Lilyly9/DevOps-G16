# A3 E3 独立核查证据（2026-10-03）

`commands.json` 及同目录 stdout/stderr 日志来自本次临时克隆、tag 准备、快照校验和两份运行器的真实执行。`summary.json` 固定被复跑仓库的 SHA。

`behavior-reruns.json` 按原始命令保存两轮运行的 argv、cwd、退出码、stdout/stderr 完整 UTF-8 文本和原始日志 SHA-256，并保留 environment 与 observations；这是对临时运行文件的汇集，执行者为 A3。样本角色字段沿用运行器，不能当成 A1/A2 的新个人运行记录。

本机未安装 strace，因此 A1 新运行的 linux_trace_status 为 NOT_RUN；已保存 A1 Ubuntu 跟踪由 A3 校验器调用深度核验。

`validation.stdout.log`/`validation.stderr.log` 和 `negative-checks.json` 是本次补强后校验器的通过记录与故障注入结果；故障只在临时克隆中注入，不修改成员原始证据。
