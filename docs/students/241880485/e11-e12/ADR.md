# ADR-001 · 使用 DRAFT 构建镜像执行 E12 全量检测

日期 2026-11-14。作者焦龙（A1，241880485）。E11-A 和本决策覆盖的 E12 固定样例验证均已在 A16 Linux 执行。实现位于提交 `456a375221ee963140b68be4afd2b26a96cc0f19`。[个人报告](report.md)

## 问题和选择

E12 需要核对 DRAFT 构建出来的环境确实执行过下游检测。参考编排能产生候选镜像与五阶段报告，但 BuildChecker 原先在编排容器内运行，报告中的 DRAFT 镜像字段不足以证明编译、读取和 trace 发生在哪个环境。可分别保留编排容器执行、按可变 tag 启动候选容器，或按 DRAFT 返回的完整镜像 ID 创建、核对及启动容器。

选定第三种。E12 的 BuildChecker `make clean` 和 `strace … make -p app` 分别在同一 `sha256:<64位>` DRAFT 镜像中运行，启动前检查 Docker 实际分配的 `.Image`。这使基线和目标两次全量检测及最后一次全量重检具有可核验的环境身份。原来的图归因、声明解析和发现计算继续共用 `full_check`，仅将 subprocess 执行位置交给 `DraftExecutor`。E11-A 使用已有编排环境，E11-B 的固定报告入口保留原接口。[执行代码](../../../../labs/e11e12/draft_fullcheck.py) · [编排代码](../../../../labs/e11e12/pipeline.py)

## 数据与失败处理

| 边界 | 输入或约束 | 保存的结果 |
| --- | --- | --- |
| DRAFT → 全量执行器 | DRAFT 最后一次成功构建返回的完整 `image_id`；宿主检出绝对路径由启动器传入 `E11E12_DOCKER_HOST_ROOT` | 对每个阶段的 clean 和 trace 构建分别保存 `clean-execution.json`、`build-execution.json`，内含请求镜像 ID、实际镜像 ID、命令、容器 ID 和退出码 |
| BuildChecker → EChecker | 基线 `actual-graph.json` 限定对象目标并与 GCC 依赖对照 | `baseline-cache.json`、基线 `full-check.json`、目标 `incremental-check.json` 与独立全量对照；保留原始 trace 与文件哈希 |
| 报告消费边界 | 阶段状态、`schema_version`、报告类型、提交 SHA、产物 SHA256 | 校验失败时记录错误码。提交不符返回 `STALE_REPORT`；镜像身份不符或执行失败使该全量阶段失败 |

候选需具备编译工具与 `strace`。全量执行容器只挂载当前阶段的项目快照，以及跟踪命令所需的 trace 目录。命令在禁网、限制 CPU/内存和进程上限的容器运行，跟踪命令单独授予 `SYS_PTRACE`；完成或异常后清理本次命名容器。镜像缺失、挂载越界、镜像身份不符和执行超时均可检查相应记录，路径设计没有回退执行环境。这会为每次全量检测增加两个短生命周期容器，也要求候选满足实际检测工具依赖。[执行代码](../../../../labs/e11e12/draft_fullcheck.py)

## 验证与后续接口

Linux 共 19 项测试通过。A1 的 4 项测试覆盖完整且不可变的镜像引用、挂载位置、执行及归档命令、实际镜像不一致时的中断与清理。E11-A 云端标准与自主版本的图和发现对照均通过，篡改实际封装的提交后得到 `STALE_REPORT`。两类验证分别保留证据。[E11 实测汇总](evidence/summary.json) · [旧报告验证](evidence/stale-report-result.json) · [个人测试](../../../../labs/e11e12/test_student_241880485.py)

E12 固定样例云端任务 `job-8a1ef46c976448698d0f004cbc89d5d2` 完成五阶段，162 个产物引用通过复核。基线、目标和最终全量的六个容器记录均显示 `requested_image_id` 和启动前读取的 `actual_image_id` 等于 DRAFT 构建出的 `sha256:c45a0b791b8cdc4cde2841d205fb123ef1e41f854dd7f405b6526758d1c55b1c`。每次全量的 10 份 trace 保留，最终 0 MD、1 RD。样例候选含 `strace`，目标和候选的镜像站适配单独留证。[E12 链路复核](evidence/e12/verification.json)

在上述固定样例中，镜像执行边界为 BuildChecker 的基线、目标、复验三次全量检查。EChecker 的 GCC 扫描和 MDFixer 补丁验证由编排容器执行。详见[证据索引](index.md)。

## 续做决定 · 仓库子目录与同镜像验证

使用 Git sparse checkout 分别签出原仓库的基线和目标，再从对应子目录构建。这样可以复查组仓库原始 SHA，也使 DRAFT 构建和产物目录只使用所选子项目。显式开启项目配置时，运行器从目标提交读出对象映射、Make 目标与头文件变化条件，并记录配置 SHA256。原 E8–E10 的输入继续使用既有默认值。

项目配置启用后，GCC 投影和补丁后的 Make、程序与测试使用本轮 DRAFT 的镜像。Git 的版本读取和补丁应用留在编排容器。独立保存每次容器执行有助于查明命令或镜像不匹配，也增加了启停容器的成本。A16 CLI 与本机 API 各验证 21 条相同镜像执行记录。B 侧独立消费由两组继续交接。详见[子项目验收](transfer-eta.md)。
