# B2 / 241880543 · E6-B 证据索引

**状态：环境阻塞，E6-B 未通过验收。** 这里归档 Windows 检查和本地单测的真实输出，没有成功的两轮 Docker 构建或程序运行证据。

- 日期：2026-10-25（Asia/Shanghai）。
- 基线：`656dcd94b7bef84f9d477f34209a1c9494171810`。
- 分支：`e5-7/B2-241880543`。
- 个人服务镜像：`course1020-draft:241880543`（本次未构建）。
- [报告及五项核对表](../../reports/B2-241880543.md)；[Linux 续跑步骤](../../reports/B2-241880543-linux.md)。
- 原始输出目录：`e5/B-draft/work/B2-241880543-preflight-01/`。
- 归档：`preflight-01/`，逐字节复制；[SHA-256 清单](preflight-files.sha256)。`work/` 保持忽略，没有整体强制加入版本控制。

| 内容 | 文件 | 结果 |
| --- | --- | --- |
| 环境、材料缺失、所有已记录命令 | [summary.json](preflight-01/summary.json) | Windows；Docker 不存在；没有 result.json |
| 分支 / SHA / 本地身份 | `preflight-01/git-status/`、`git-head/`、`git-name/`、`git-email/` | 命令退出码均 0 |
| Python / Docker | `preflight-01/python-version/`、`python3-version/`、`docker-version/`、`docker-info/` | Python 3.10.10；python3 返回 9009；Docker 无法启动，退出码为 null |
| 原始 doctor 命令 | `preflight-01/requested-doctor-python3/` | python3 商店别名返回 9009 |
| 可用 Python 执行 doctor / build / e6 | `preflight-01/doctor-platform-check/`、`build-platform-check/`、`e6-platform-check/` | Linux 平台检查拒绝，分别退出 2；未执行 Docker |
| 课程证据校验标准输出 | [verify-e6/stdout.log](preflight-01/verify-e6/stdout.log) | `passed=false`，缺少 result.json |
| 课程证据校验标准错误 / 退出码 | [stderr.log](preflight-01/verify-e6/stderr.log)、[command.json](preflight-01/verify-e6/command.json) | 标准错误为空，真实退出码 1 |
| 本地单测 | [unit-tests/stdout.log](preflight-01/unit-tests/stdout.log)、[command.json](preflight-01/unit-tests/command.json) | 24 passed，退出 0；Docker 编排测试使用桩 |
| 候选静态处理 | [prepared-baseline.txt](preflight-01/prepared-baseline.txt) | 接受已有候选并生成失败基线；没有构建 |
| 独立文件存在性检查 | [independent-inventory/stdout.log](preflight-01/independent-inventory/stdout.log)、[inspect.py](preflight-01/independent-inventory/inspect.py) | 原始实验文件全部缺失；文件枚举进程返回 0，验收结论 FAIL |
| Windows 行尾配置 | `preflight-01/git-line-endings/` | 系统配置 core.autocrlf=true；候选索引 LF，工作区 CRLF |
| Linux 续跑文档静态检查 | `preflight-01/linux-guide-static-check-02/` | Python 语法通过；Git Bash `bash -n` 返回 0；独立检查面对真实缺失证据返回 1；未执行云端实验 |

每个命令目录均保存 `command.json`、`stdout.log`、`stderr.log`。`summary.json` 内的 `exit_code=null` 表示进程没有启动，不能当作 0；目录名中的 `platform-check` 表示平台拒绝检查，不能当作构建失败日志或成功实验。

`summary.json` 中 `syntax_check.passed=true` 和 `candidate_static_check.prepare_candidate_accepted=true` 仅对应本次静态检查。Docker 真实构建、同镜像运行、`hello E3` 输出和 `input_sha256` 复核仍待 Linux 实验。

`linux-guide-static-check/` 保留首次静态检查的子进程输出（Windows 默认编码）；当时外层打印遇到编码错误，随后以显式 UTF-8 在新目录 `linux-guide-static-check-02/` 重跑，没有覆盖首次记录。两次独立检查均因不存在真实实验结果而返回 1。
