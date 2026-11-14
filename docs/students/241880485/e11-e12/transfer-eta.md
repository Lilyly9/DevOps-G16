# E12 子项目验收 · transfer-eta

焦龙（241880485），A16。数据来自同一个 G16 GitHub 仓库的 `projects/transfer-eta`。该工具是本轮新建的 C/Make 子项目，用于估算证据包和构建产物的传输时间。本次提交包含实际的功能变更和修复，组内维护历史从本轮开始。课程方尚未确认这个新项目是否满足本组真实项目的验收口径。

| 版本 | 完整提交 | 变更 |
| --- | --- | --- |
| 基线 | `5ef9d829e2f893af23f60399dcb67095800d121e` | 根据文件大小和显式速率向上取整计算秒数，校验无效和溢出输入 |
| 目标 | `e7414083c4f1760cb234f96a9d75f2d0255e3f57` | 新增可选的默认速率，可显式覆盖。为复现增量构建故障，目标版本保留原来的对象依赖声明 |
| E12 执行代码 | `be439f44e73704c4dece24962746a13125a94d40` | 支持原仓库内的子目录和项目配置，保留基线与目标的原始 Git SHA |
| 修复后的项目 | `2efac5983b38ce9ddf05d194ba29169bba10e5b0` | 将生成的头文件依赖加入项目 Makefile。提交中的 Makefile SHA256 与 E12 实际修复副本一致 |

配置从目标提交的 `e12-profile.json` 读取，指定目标与源码映射、GNU Make 构建和测试目标、CLI 参数和头文件验收条件。其 SHA256 为 `b7d37051c32c3ddb7d5fc6d4f740290bfc3782d4768cbb19856211db4330ec07`。DRAFT 读取仓库维护的候选，首轮观察到 `MISSING_MAKE`，第二轮补装 GNU Make、编译器与 `strace`，实际运行输出 `eta_seconds=13`。详见[数据清单](evidence/transfer-eta/dataset.json)、[请求](evidence/transfer-eta/request.json)、[项目配置](evidence/transfer-eta/e12-profile.json)和 [DRAFT 封装](evidence/transfer-eta/cli/draft.json)。

| 操作 | 实测结果 |
| --- | --- |
| 目标版默认速率 8 MiB/s，运行 `./transfer-eta 100` | `eta_seconds=13` |
| 改头文件至 5 MiB/s，执行普通 `make` | 仍为 `eta_seconds=13`，`make` 判定程序已是最新 |
| 同一个未修复版本随后执行 `make -B transfer-eta` 强制重建 | `eta_seconds=20` |
| 应用 E12 补丁后，重新从 8 改到 5 并执行普通 `make` | 重新编译 `eta_cli.o` 并链接，输出 `eta_seconds=20` |

BuildChecker 基线发现为空。目标全量和增量都恰好报告 `MD(eta_cli.o, defaults.h)`。实际图将该边定位到 `target-full/trace/t.11` 第 923 行对 `defaults.h` 的成功读取。修复消费了本轮增量封装并校验哈希，只补上一条 Make 声明。项目测试和头文件变化断言均通过，最终动态复验 **0 MD / 0 RD**。详见[修复前实测](evidence/transfer-eta/native-proof.log)、[原始边](evidence/transfer-eta/cli/target-full/actual-graph.json)、[补丁](evidence/transfer-eta/cli/candidate.patch)、[修复验证](evidence/transfer-eta/cli/validation/validation.json)和[最终图结论](evidence/transfer-eta/cli/final-full/findings.json)。

| 入口 | 任务和跟踪号 | 实测 |
| --- | --- | --- |
| A16 CLI | `job-8da9e7061d5140a184a621f54f200464` / `trace-b58a3d878e5d45419d276e94fb96f88d` | 五阶段通过，核对 235 个产物和 21 条同镜像容器执行记录 |
| A16 本机 API | `job-efd02a52b7604d6c9bfd416f3741979b` / `trace-ac983c4d568b48978ef12e587cec005f` | 五阶段通过，核对 235 个产物和 21 条同镜像容器执行记录。同请求重复提交返回同一任务，改 target 返回 409，6 个下载文件的响应头、清单和内容 SHA256 一致 |

两次任务各自使用该任务 DRAFT 给出的不可变镜像 ID。21 条记录覆盖 BuildChecker 清理与跟踪、EChecker GCC 采集和 MDFixer 构建、测试与头文件变化验证。原始记录分别在 [CLI 核验](evidence/transfer-eta/cli-verification.log)和 [API 核验](evidence/transfer-eta/api/evidence-verification.log)。HTTP 提交和下载证据另见 [API 响应核验](evidence/transfer-eta/api/verification.json)。本机 API 由 A1 提交和验收，A16↔B16 的独立报告消费仍由双方另行联调。

A16 本次课程容器测试 24 项通过。代码 PR CI 的四项检查通过，固定样例仍走原入口。本机原始压缩包下载后的 SHA256 为 `5ed5a6d19ab266d91a0efe14c53d24a29afe0ad904dd056c4bf92b83b5fe7896`，与 A16 一致。CLI 与 API 的 470 个清单引用已按原始字节复验。证据见 [Linux 测试](evidence/transfer-eta/tests.log)、[代码 CI](https://github.com/Lilyly9/DevOps-G16/actions/runs/43556317479)和[个人草稿 PR](https://github.com/Lilyly9/DevOps-G16/pull/21)。

复跑时从 GitHub 克隆到运行器的 `data/` 下，签出包含两个提交的分支。请求保留 `project_path`、`profile`、base 和 target，更新 `repo` 和 `candidate` 为当前容器的 `/course/data/` 路径。候选从历史目标提交取出，使用 `python3 run_e11e12.py run --request <请求> --out <新 work 目录>`。
