# E3 并行测试基线

本目录的 A 组样本按课程 `E3_TASKS.md` 中 A1/A2/A3 的职责组织。人工预期放在 `expected/`，实际运行放在 `work/<run-id>/`，Linux 跟踪放在 `evidence/`；人工答案不得计入检测器准确率。当前仓库未包含 B1/B2 的 E3 样本，四服务总表待其提交后共同完成。

## A 组七列基线

| 版本 | 配置 | 命令 | 人工预期 | 实际观察 | 判断依据 | 出处 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 MD/RD | `a1-linux-gcc-default` | 见 [A1 样本 README](fixtures/md-rd/README.md) | `main.o` 缺 `config.h`，多 `unused.h` | 首次 1，改 `config.h` 后仍 1，clean 后 2；改 `unused.h` 触发多余重编译 | `main.c` 包含前者，Makefile 仅声明后者；仅有 `openat` 不足以独立判 MD | [人工预期](expected/buildchecker-md-rd.json)、[实测](work/20260929-110948-A1-00d164/observations.json) |
| A2 C0 | `a2-windows-gcc-default` | `make clean && make && ./app` | 项目文件范围无 MD/RD | clean 10 | 声明包含 `config.h` | [人工预期](expected/echecker-c0-c1-c2.md)、[实测](work/20261002-182617-A2-e1d9d6/observations.json) |
| A2 C1 | 同上 | 修改 `feature.h` 后 `make && ./app`，再 clean 重建 | `main.o` 缺 `feature.h` | 增量 12，修改头文件后仍 12，clean 后 13 | 新增 include，但 Makefile 未补声明 | 同上 |
| A2 C2 | 同上；CFLAGS 改为 `-O0 -DMODE=7` | 复用 C1 产物 `make && ./app`，再 clean 重建 | 上述 MD 仍存在；编译命令变化 | 增量 12，clean 19 | 普通 Make 不追踪命令变化 | 同上 |

## 目录、复现与校验

- `env/toolchain-A1.txt`、`env/toolchain-A2.txt` 记录 OS、架构、工具版本；详见 [环境说明](env/README.md)。
- `fixtures/md-rd/` 和 `fixtures/commits/C0|C1|C2/` 保存样本；C0/C1/C2 的真实 SHA 在 [A2 说明](A2_README.md)。
- 每次运行新建 `work/<日期-时间-成员-编号>/`，不覆盖旧记录；`commands.json` 保存命令、退出码和日志路径，日志名注明版本，`observations.json` 标注 `ACTUAL_RUN`。
- 人工答案在 `expected/` 标注 `MANUAL_EXPECTED` 或 `INSTRUCTOR_ORACLE`。本仓库两份答案均为 `MANUAL_EXPECTED`，不是工具输出。
- 在仓库根目录运行 `python e3/validate_e3.py`、`python e3/scripts/a1_verify_evidence.py`、`python e3/scripts/a2_export_commits.py --check`（需先在本地建立指向已记录 SHA 的 `C0/C1/C2` tag；A3 校验器直接按 SHA 核对，无此依赖）。A2 的行为重跑命令见 [A2 说明](A2_README.md)。

## E2 公共模型对齐

E3 文件是离线基线材料，不直接冒充 `jobRecord.artifacts`。如把文件登记为 E2 artifact，需补 `artifact_id`、`type`、`uri`、`media_type`、`producer_job_id`；`configuration_id` 应进入服务请求或报告的配置上下文，不能把 E3 本地 JSON 直接作为公共任务消息提交。`provenance`、运行命令、退出码等 E3 字段保留在材料或服务专有 payload 中；目前无需改 `contracts/task.schema.json`。

已知限制：A1 Linux 与 A2 Windows 工具链不同；A2 未运行课程 `run_lab.py`，而是等价自建真实提交链；E3 当前只验证人工样本和构建行为，尚无四服务检测器准确率或真实联调结果。
