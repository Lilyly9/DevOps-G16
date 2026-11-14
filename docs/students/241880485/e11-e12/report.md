# E11–E12 个人报告 · A1

续做记录见 [G16 子项目验收](transfer-eta.md)，包含 `transfer-eta` 两份实际提交、CLI 和本机 API 实测。本文保留此前 E11-A 和 E12 固定样例记录。

焦龙，241880485，A16，BuildChecker。配对为 B16。实验日期为 2026-11-14，个人分支为 `student/241880485/e11-e12`。E11-A 标准路线、自主版本对照和旧报告拒绝均已在 A16 Linux 完成。E12 固定样例的 CLI 五阶段亦已通过，其中三次 BuildChecker 全量在 DRAFT 构建出的同一镜像中执行。仓库沿用 [Lilyly9/DevOps-G16](https://github.com/Lilyly9/DevOps-G16)。

| 项目 | 来源 |
| --- | --- |
| 实验源码 | `456a375221ee963140b68be4afd2b26a96cc0f19` |
| 公共代码 | B1 的 [PR #20](https://github.com/Lilyly9/DevOps-G16/pull/20)，A1 开工时仍开放，本分支基于其 `5f97d7c` 提交 |
| 编排镜像 | `course-e11e12:241880485`，`sha256:40b15f7e375e5bbbb5929f2f22f52f4a194a340b1970d340512af444f69320a5` |
| E11 原始输出 | `/root/241880485/DevOps-G16-e11-A1-20261114/work/e11-a1-241880485-20261114.HTL9X4` |

## E11-A 轨道内集成

基线提交的 BuildChecker 通过 `make clean` 后运行 `strace` 跟踪 Make 的文件和进程事件，生成 Make 数据库和实际依赖图。EChecker 将项目内 `main.o`、`helper.o` 的实际入边投影到 `baseline-cache.json`，校验该投影与同一基线的 GCC 结果一致，再以此缓存扫描目标提交。目标提交另做独立 BuildChecker 全量采集。复核比较对象目标的 `actual`、`declared` 及完整 MD/RD 三元组集合。三个缓存边均能通过证据引用回到 `trace/t.<PID>` 和行号，原件中保存该行文本、进程号、系统调用、成功返回值和文件 SHA256。[标准缓存边溯源](evidence/standard/cache-edge-provenance.json) · [自主缓存边溯源](evidence/autonomous/cache-edge-provenance.json)

| 项目 | 变更与预期 | 实际结果 |
| --- | --- | --- |
| 标准路线 | 课程生成样例在目标提交中加入直接 `#include "extra.h"`。签名改变，两对象应刷新，新增一条 MD | `SUCCEEDED`。刷新 `main.o`、`helper.o`，复用为空。新增 `MD(main.o, extra.h)`，同时保留 `MD(main.o, config.h)` 和 `RD(main.o, unused.h)`。[标准结果](evidence/standard/incremental-report.json) |
| 自主版本对照 | 从本人 E9 历史 bundle 恢复 C0 `a817cc09960456b4eac8762d10d69037bf4aa767` 与 C1 `8e337b25d26c32f231f711f447c2d6399b435d4d`。C1 只改函数体表达式，预处理指令、配方、编译选项和编译器未改变 | `SUCCEEDED`。复用 `main.o`、`helper.o`，刷新为空；仍有 `MD(main.o, config.h)` 和 `RD(main.o, unused.h)`，新增与消除均为空。[自主输入差异](evidence/inputs/autonomous-base-target.diff) · [自主结果](evidence/autonomous/incremental-report.json) |

标准样例基线为 `46fc6c1b74681d6f3746c7d9dff9fca722ca936e`，目标为 `2bcd78df5e0733e1743fdb2fd7bf8be824df830f`。两次任务的 `full-check.json` 均绑定各自基线 SHA，`incremental-check.json` 均绑定各自目标 SHA。每次运行的两个阶段均使用 `e11e12-1` 封装和同一编排 `job_id`、`trace_id`，封装记录的产物 URI、字节数及 SHA256 已与实际文件核对。目标全量图、增量图及完整发现一致，标准和自主均保留独立的输入、快照、运行结果与编排标识。[实测汇总](evidence/summary.json) · [证据索引](index.md)

旧报告练习取标准路线实际产出的 `full-check.json`。先验证原报告可通过契约，再复制并仅把 `commit` 从期望的基线 SHA 换成另一已知目标 SHA，仍以原基线 SHA 校验。检查器返回 `STALE_REPORT`，测试中的下游标记未到达，原报告 SHA256 保持一致。这次验证针对报告消费契约，执行位置为 Linux 测试容器。[旧报告拒绝记录](evidence/stale-report-result.json)

## 本人贡献与 E12 进展

本人实现 E12 的 BuildChecker 容器执行适配。DRAFT 成功后，从构建记录提取完整镜像 ID。在基线全量、目标全量和最终全量重检的每次 clean 与 trace 构建中，按该 ID 创建容器，启动前核对 Docker 返回的 `.Image`，保存命令、实际镜像 ID、容器 ID、退出码以及构建和 trace 原件。执行路径使用独立的 `work/` 项目和 trace 目录。遇到镜像不符等错误时停止对应阶段。E11-A 保持课程编排镜像中的原执行入口。[执行适配器](../../../../labs/e11e12/draft_fullcheck.py) · [个人测试](../../../../labs/e11e12/test_student_241880485.py) · [决策记录](ADR.md)

本次 Linux 容器 `python3 run_e11e12.py test` 通过 **19 项**，其中本人新增 4 项，分别验证完整镜像 ID、工作区挂载边界、真实命令及日志记录、镜像不符时终止和清理。E11 的正反向运行均独立于单元测试，云端执行退出码为 0。[运行日志](evidence/logs/)

### E12 固定样例云端验证

| 项目 | 实际证据 |
| --- | --- |
| 云端 OUT / 辅助记录 | `work/e12-a1-draft-image-241880485-20261114T024540Z` / `work/a1-e12-proof-20261114T024540Z.TjTU9C` |
| 同一编排任务 | `job-8a1ef46c976448698d0f004cbc89d5d2` / `trace-3cd6971ebf334b2788f6f31cd3660d36` |
| 被测版本 | base `46fc6c1b74681d6f3746c7d9dff9fca722ca936e`，target `d5204f53b641173fd3f23c71ae37dda8ac6628e9` |
| DRAFT 实际镜像 | `sha256:c45a0b791b8cdc4cde2841d205fb123ef1e41f854dd7f405b6526758d1c55b1c` |
| 报告消费 | `repair` 引用本轮 `incremental-check.json`，实际 SHA256 `c6e5336f727b6c62e5addb8fe09dce0ec8a8dde5c18921b95e44af49c709bd62` |
| 补丁及最终状态 | 补丁 SHA256 `88074f66c291dcad1344c48f6a2b9ddd42d235d9d0415c85fb33310c5b7cb2af`，`accepted=true`，最终 0 MD、1 RD `unused.h` |

云端请求以本轮课程生成 C/Make 样例为输入，独立派生目标提交只调整 `Dockerfile.broken` 的基础镜像仓库前缀。修复候选沿用课程候选的基础镜像固定内容和依赖安装思路，增加 `strace`，并使用 A16 可达的镜像仓库和 apt 镜像源。源码提交、样例提交和候选内容分别留证。[E12 执行证据](evidence/e12/)

`draft → full-check → incremental-check → repair → recheck` 全部完成，复核脚本验证 162 个产物引用。BuildChecker 的基线、目标和最终全量检查各含一次 clean、一次 trace 构建，共六个实际容器均使用上述 DRAFT 镜像 ID，每次全量保存 10 份原始 trace。基线报告绑定 base，后续目标报告及修复引用绑定 target，最终仅保留 `RD(main.o, unused.h)`。[链路复核](evidence/e12/verification.json) · [修复封装](evidence/e12/repair.json) · [最终复验](evidence/e12/recheck.json)

这次固定样例运行中，EChecker 的 GCC 扫描和 MDFixer 补丁验证由编排容器执行。后续 `transfer-eta` 的配置路线把两者迁入对应 DRAFT 镜像，并在 A16 本机调用 API 实测。A16↔B16 的独立消费由双方另行联调。详见[子项目验收](transfer-eta.md)。

## 真实项目

E11 自主对照沿用本人 E9 课程衍生夹具的实际 Git 历史。续做时在原 G16 仓库内新建传输时间估算工具 `transfer-eta`，用两个实际功能提交作为 E12 输入。其技术验收已完成，是否符合课程对本组实际维护项目的要求待课程方确认。详见[自主项目来源](evidence/inputs/autonomous-dataset.json)和[子项目验收](transfer-eta.md)。

## 环境故障与恢复

首次构建编排镜像时，Docker Hub 的 Docker CLI 镜像 metadata 请求超时，构建退出码为 1，日志在 `work-e11-a1-environment.8WOHXG`。重试将同一个 Docker CLI 镜像 digest 经课程镜像站解析，镜像 tag、digest 与编排 Dockerfile 保持原口径。第二次退出码为 0，`work-e11-a1-environment.VR6DkD` 保存实际解析结果与工具链。A16 当时可见 2 CPU、3.5 GiB 内存。[环境与构建记录](evidence/environment/)

E12 的首次证据校验脚本只接受原固定样例路径，因而拒绝了云端镜像站派生样例。扩展数据来源识别后，对同一成功 OUT 重新执行证据校验，结果为 `PASSED`。五阶段编排和六个容器执行记录均来自原 OUT。[复核结果](evidence/e12/verification.json)

个人草稿 PR #21 以 B1 分支为基线，等待公共导入 PR #20 合入。云端实验源提交 `456a375221ee963140b68be4afd2b26a96cc0f19` 的 E7-A、E7-B、E8–E10、E11–E12 四项检查均已核验成功。E11–E12 PR 事件 run `43548159901` 的产物 ID 为 `14095027314`，push 事件 run `43548058094` 的产物 ID 为 `14094534869`，后者已下载。[个人 PR #21](https://github.com/Lilyly9/DevOps-G16/pull/21) · [公共 PR #20](https://github.com/Lilyly9/DevOps-G16/pull/20) · [PR CI](https://github.com/Lilyly9/DevOps-G16/actions/runs/43548159901) · [push CI](https://github.com/Lilyly9/DevOps-G16/actions/runs/43548058094)

完整云端原始证据包为 178309 字节，SHA256 `4c6e0364ac295b65e8a6eb505740a439fd55397cc87dc32d709ba556c6ba0de3`。本机个人交付包路径为 `E11-12/A1-E11-E12-个人交付备份-20261114.tar.gz`，完整交付包的校验独立记录。仓库内证据入口和复跑方式见 [索引](index.md)。
