# A3 云端证据 · 2026-10-24

林涵 / 241880464 / G16 A16。读取用户从云服务器实际下载的原始包后，在本机逐文件验证。不是只根据终端转录得出结论；没有直接 SSH 重读，也没有收到服务器端压缩包哈希，故不宣称独立完成传输前后哈希对比。本机原包 SHA256 为 `f12433c271baab05b9e172542aaf8659795c2e010deaf30e57a738827af65055`，原件仅保留本机。

## 结论

云端功能验证 PASS：构建退出 0，18 项服务测试、6 项判定、2 项扫描回归通过，gate 8/8，语法/源码与完整 Git 历史/镜像扫描均退出 0。原始三次错误集合精确一致，trace_id 独立；修复后 findings=[]，只有 Makefile 输入哈希改变。源码 `176d624ec4e215aedeadb1a8057f87bb8d32eb4d`，镜像 `sha256:1aae40280c5a233f66cd72c771699f4c0a9453526a7ee2ce61b773f5109dc0ab`；构建后 inspect 与 gate 实际 inspect ID 相同。

**资源要求仍 PENDING**：Ubuntu 22.04.5、2 CPU、3.5 GiB 内存；doctor 原始 problems 明确低于 4 GiB。没有修改阈值或把自检写成通过。宿主 Python 3.10.12，镜像 Python 3.13.14，分别记录。

## 构建差异与失败保留

build-01 默认 lab_cloud 构建因 Docker Hub 超时退出 1。build-02 日志停在 Debian 索引下载，没有保存结束退出码，不能写成成功或虚填 130。build-03 使用 work 内临时 Dockerfile 与手动 docker build 成功，原始受跟踪 Dockerfile 保留。对照源码确认差异仅为 DaoCloud frontend/基础镜像下载地址、TUNA Debian 源及 apt 超时重试；基础镜像固定摘要与 pip 锁文件未改变，未修改算法。

## 文件位置

| 内容 | 相对路径 |
| --- | --- |
| 原始云端环境与未通过项 | raw/doctor.json |
| 成功构建、退出码、镜像信息、单测 | raw/build-03/ |
| 失败与停滞尝试 | raw/build-01/、raw/build-02/ |
| 正式 gate | raw/gate-01/gate/gate-result.json、results.csv |
| 场景输入、图、报告与 trace 锚点 | raw/gate-01/gate/各场景/ |
| 独立判定/扫描回归 | raw/oracle-tests.log、raw/scanner-tests.log |
| 源码历史/镜像扫描、语法 | raw/source-history-scan.log、image-scan.log、syntax-check.log 及各自退出码 |
| 容器工具链 | raw/toolchain.lock |
| 本机复核结果 | summary.json |

所有归档为实际文件的明确脱敏副本，移除了主机名、个人邮箱和绝对私有路径；未改变退出码、findings、trace_id、输入哈希、镜像 ID 或测试数量。完整 trace 与二进制产物只在本机原包，仓库保留报告直接引用的关键 trace，trace-index.json 写明节选范围。original-files-sha256.json 对应原文件，SHA256SUMS.json 对应脱敏副本。

## 重跑

进入个人克隆的 e5/A-buildchecker。确认 Docker/buildx 可用，镜像源前提与本次一致。用新 work 目录复制并按 raw/build-03/Dockerfile.mirror 的网络调整生成构建副本，构建并保存日志，再运行镜像 pytest 和课程 lab_cloud.py gate（每次使用新 --out、本人 --image）。标准源码/历史与镜像扫描命令仍为 scripts/secret_scan.py ../.. --history 及 --image course1020-buildchecker:241880464。切勿覆盖已有 work。

这份记录不替代 main 保护、实际拒绝合并日志和最终 MERGED。内存要求仍须老师认可或资源调整后重跑 doctor。
