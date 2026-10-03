# E4 A3 文档与证据核查（2026-10-03）

本核查以仓库中的 A1/A2 交接记录为输入。A1/A2 的服务器 `work/` 原件、镜像和相邻 B 组仓库不在本地；以下“记录所述”与“A3 独立验证”严格区分。

| 成员 | 成功证据目录（成员记录） | 模板 SHA（成员记录） | A3 可核实范围 |
| --- | --- | --- | --- |
| A1 | `/root/241880485/DevOps-G16/e4/A-buildchecker/work/20261001-040329` | `9feb7a5675083a8ad0ad9fa3645010ced7bf2ffd` | A2 交接中引用；尚未读取服务器原件 |
| A2 | `/root/241880496/DevOps-G16/e4/A-buildchecker/work/20261002-184355` | 同上 | [A2 交接](A2_README.md) 记录 `env.json` / `template-sha.txt` / `head.txt` 一致；尚未读取服务器原件 |

A2 记录 `toolchain.lock` 完全一致、两次单测均为 `3 passed`、`smoke.json` 四项通过且相同；镜像 ID、运行目录、主机磁盘余量不同。A3 在本地确认模板 SHA 可由 Git 解析，A 组模板 README、Makefile、Dockerfile、compose、锁文件和密钥扫描脚本均存在。

## 无泄露三项

| 检查 | 当前结论 |
| --- | --- |
| `.env` 未跟踪 | 本地 `git ls-files` 无 `.env`；A2 记录其服务器克隆亦未跟踪，权限 600 |
| Git 历史无 Key | A2 的 `secret-scan.txt` 记录为“未发现问题”；A3 未读取该原始文件，不能独立证明整个历史 |
| 镜像 history 无 Key | A2 的扫描记录称覆盖镜像；A3 未访问服务器镜像，待核原始扫描日志 |

## 相邻组只看 README 重跑

截至本次核查，未收到相邻 B 组仓库地址与可访问环境；共享仓库中也没有 `e4/B-draft/`。因此 A3-1 尚未实际重跑。取得地址后应只按其 README 完成克隆、`make doctor`、`make all`，记录 SHA、成功目录、疑点、缺失步骤和修正建议，不填写虚构结论。

A 组现有 README 已提供独立克隆、切换固定 SHA、`make doctor`/`make all`、证据目录、固定 digest、阿里云 Debian 源及已知问题。复核时应注意 A1 直连 GitHub 曾超时，A2 直连成功；这不等于任意机器均可访问。A2 的两次假 Key 扫描目录晚于成功 `make all` 目录，不能将“最新目录”误认作成功证据。

## A 组复现入口与已知坑

在自己的克隆根目录先以 `git rev-parse HEAD` 记录 SHA；若做 A1/A2 的严格对照，检出共同模板 SHA `9feb7a5675083a8ad0ad9fa3645010ced7bf2ffd`，再 `cd e4/A-buildchecker`、`make doctor`、`make all`。从 `make all` 输出取得成功证据目录，核对同目录的七份文件以及 `env.json.template_sha`。基础镜像是 Dockerfile 中固定 digest 的 `m.daocloud.io` Python 镜像；Debian 包源为阿里云 HTTPS 镜像。首次构建下载可能很慢；若失败重试，按成功目录和日志判断，不按目录时间排序猜测。具体命令与风险见 [A 组模板 README](A-buildchecker/README.md)。
