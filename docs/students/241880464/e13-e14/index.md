# E13–E14 A3 个人报告与证据索引

林涵，241880464，A16/B16（G16）。个人分支 `student/241880464/e13-e14`。2026-11-24 从已同步的 main `0e2121192692866240355c4dcb275cf749ee6c1c` 接续 11 月 21 日的本地工作。云端实验运行器 `b9669cbe8ba89bd3c098c8e4dd1d128f426165da`，环境 Ubuntu 22.04 x86_64、Docker 29.1.3、Python 3.13，独立检出 `/root/241880464/DevOps-G16-e13-e14-A3-20261124`。运行器、服务镜像 ID、各任务完整 base/target、job/trace、产物数、验收和退出码见[云端核对记录](evidence/cloud-summary.json)。

## 个人实现与验证

- E11-B 从已校验的字节解析报告，归档 `fixed-md-input.json` 时保留同一份字节。收到的报告 SHA256、来源 job/trace、消费任务和最后的动态重检可以互相核对。
- C6 逐个检查显式输入，任一角色日志为空、二进制或缺失便返回 2。基线对“有效日志 + 空日志”返回 0，独立回归覆盖修复后的 2，以及假 Key 脱敏命中返回 1、清理后返回 0。Git 文件列表按 NUL 分隔读取，实测含中文名的暂存文件被命中。历史读失败会阻断扫描。[缺陷 Issue #33](https://github.com/Lilyly9/DevOps-G16/issues/33) · [修复前记录](evidence/c6-baseline.log) · [暂存试验](evidence/c6-stage-before.log)
- E14 在原工作流上增加服务镜像检查、独立日志扫描和 `verify_e14.py`。验证器逐项复算产物大小和 SHA256，并沿五阶段检查同一 job/trace、base/target、修复输入、候选补丁和最终无 MISSING。保留原有 C7 和 E7/E8–E12 检查。[PR #34](https://github.com/Lilyly9/DevOps-G16/pull/34) · [代码提交的 PR CI](https://github.com/Lilyly9/DevOps-G16/actions/runs/45324791201)

## E13 报告交接与交叉测试

| 任务 | A3 执行与判据 | 证据目录 |
| --- | --- | --- |
| 历史 tokenstat A→B 对照 | 来源为 A2 本轮 E11-A，A3 生成的 `fixed-md` 与 B3 实际收件字节相同，摘要 `1036c8955fe4bae6664a1bf88879113cc2be48b6d7cd358a0c20b70a505737af`。收件和后续修复分开判定。 | [A3 出件](evidence/tokenstat-fixed-md.json) · [B3 收件](https://github.com/Lilyly9/DevOps-G16/blob/7b9f98ade6d0ffdb7d9346fb75edc8696e558a37/docs/students/241880597/e13-e14/evidence/b-receive/fixed-md.json) |
| 真实项目新一轮 A→B | 对 A1 的 transfer-eta 新跑 E11-A 并导出 fixed-md。A3 在独立 B 消费工作目录调用 E11-B，核对原/传输/归档三份字节一致，补丁接受，动态复验无 MISSING。独立任务有自己的 job/trace。该次由 A3 自验。 | `work/a3-eta-a`、`work/a3-eta-b-replay` |
| B1 项目 A→B | 云端对 B1 的原始 bundle 跑 E11-A 并导出，在本机用原始候选独立进入 E11-B。传输和消费归档字节一致，补丁接受，重检无 MISSING。 | 云端 `work/a3-b-a`，本机 `work/a3-b-cross-consume`，[同任务对照](evidence/local-b-summary.json) |
| C2、C3 | 对 transfer-eta 和 B1 项目均运行拒绝测试。旧目标返回 `STALE_REPORT`，传输副本多一个换行返回 `ARTIFACT_HASH_MISMATCH`。四次均退出 1；拒绝时未生成补丁。 | `work/a3-{eta,b}-{c2,c3}`，`data/a3-e13/*-hashes.json` |
| C6 | 假 Key 只在隔离日志和隔离暂存区生成。日志先命中再清理，扫描退出 1 → 0。课程仓库跟踪文件与本克隆可见 Git 历史、服务镜像构建历史与环境变量、运行证据及四份角色日志均扫描通过。 | [命中及脱敏](evidence/cloud-c6-before.log) · [复扫](evidence/cloud-c6-after.log) · [源码历史](evidence/cloud-c6-source.log) · [镜像](evidence/cloud-c6-image.log) · [运行日志](evidence/cloud-final-scan.log) |
| C8 | 云端实测重复提交得到同一任务；用同键换 target 得到 HTTP 409 和 `IDEMPOTENCY_CONFLICT`，原任务状态未变。 | `work/a3-c8-api-final`、`work/api-jobs` |
| H1/H2/H3 | A3 独立运行教师包，H3 主跑、H2 复核、H1 补测。H3 原候选构建后因缺少 `strace` 停在全量检查，原件保留。三份隔离候选仅追加 `strace`，原候选与 C0/C1 不改。复测均五阶段通过、补丁接受、动态复验无 MISSING。 | `work/a3-H1-jsmn`、`work/a3-H2-inih`、`work/a3-H3-tiny-aes`、`work/a3-h3-original` |

H1/H2/H3 来自发放包 `e13-upstream-student.zip`，其摘要为 `d9818c5f34d6ff5b6016222dabd7f56daca09ceaa5f525be214e146e3d485435`。`work/a3-meta/teacher-projects.log` 保存上游链接和完整课程提交。`work/a3-meta/*.command`、`*.exit`、`*.log` 保存实际命令、退出码和输出。请求、候选原版摘要和适配副本均有记录。

## E14 四服务部署验证

使用隔离 Compose 项目 `e14-a3-241880464`，四个端口均仅绑定服务器回环地址。保存 `ps`、四个 `/health`、四服务分别的日志，并按每次任务的 job/trace 核对四角色实际处理记录。服务使用教学镜像，DRAFT 另生成候选运行镜像，两者 ID 分列。

- 固定样例在云端采用已有的同摘要镜像源适配版本，完整目标 `7e534c43bd3f123dc22099fe0e979b16b5e1fc34`。源标签校验拒绝的第一次尝试另存。云端首次成功及恢复各校验 162 件产物，原始 CI 样例也独立通过。
- 配对 A 项目 transfer-eta 在云端跑通。base `5ef9d829e2f893af23f60399dcb67095800d121e`，target `e7414083c4f1760cb234f96a9d75f2d0255e3f57`，作业 `job-1f1df29efe0a406a817664839ed13263`。五阶段、189 件产物、补丁接受及无 MISSING 均已核对。
- 配对 B 项目使用 B1 原始候选、原始 C0/C1 在本机 Docker 29.10.0 重跑。四角色健康、五阶段和 156 件产物验证通过，输出 `2`，补丁接受，最终无 MISSING。首个云端请求因候选改成镜像源后与原始 Dockerfile 标签不同被拒，保留失败证据。 [B 项目核对记录](evidence/local-b-summary.json)
- 把有效固定请求的 `build_timeout` 改为 0.01 秒，新的任务返回外层 FAILED、DRAFT 内层 TIMED_OUT，容器 ID 和 Docker 客户端进程清单无新增。恢复原时限后另一个新任务成功。证据在 `work/a3-e14-timeout-mirror`、`work/a3-e14-fixed-mirror-recovered` 及 `work/a3-meta/mirror-*`。收尾清理本次 Compose 项目。

## 归档与发布状态

原件包 `A3-E13-E14-20261124-cloud.tar.gz` 和 `A3-E13-E14-20261124-local-B.tar.gz` 放在课程目录的 `E13/提交材料/A3-E13-E14-20261124`，云端备份 `/root/devops-submissions/241880464/A3-E13-E14-20261124`。两个包均在本机和云端做过 SHA256 校验。校验命令为 `sha256sum -c ./*.tar.gz.sha256`。

[联合验收索引](acceptance.md) · [ADR](ADR.md) · [AI 使用记录](AI_USAGE.md)。代码 PR #34 已合入 `fa96f184760f1927621104542454450988e2eef0`，Issue #33 已关闭。主分支该提交的 5 个工作流均成功。RC 等待两组联合确认及组长安排。 [主分支 E13–E14 CI](https://github.com/Lilyly9/DevOps-G16/actions/runs/45325382170)
