# A2 · E6 证据索引（BuildChecker 自动检测 + 修复复检 + 自证门禁）

| 项 | 值 |
| --- | --- |
| 角色 / 学号 | A2 / 241880496 |
| 运行时间 | 2026-10-23T02:42Z — 03:05Z |
| 仓库 / 分支 | `Lilyly9/DevOps-G16` / `e5-7/A2-241880496` |
| 模板 SHA | `c343b5b0e05b7b60d44a5b872c47353442ff1387`（A 实验包入库提交） |
| 服务镜像 | `course1020-buildchecker:241880496` → `sha256:a89bcaea6dce8cca78049d44b921064f2c4c960cc543545ccaee70b9b8304c65`（amd64） |
| 主机 | Ubuntu 26.04 LTS on WSL2，x86_64，4 CPU，7.8 GiB，Docker 29.5.2，Compose 5.1.3，Python 3.14.4，GNU Make 4.4.1，Git 2.53.0 |

> 说明：本班次在本地 WSL2（非组内云主机）执行，原因与影响见文末“限制”。

> **最终 main 复核（2026-10-26）**：在 `36047e3` 上重跑全部步骤，结论一致（单测 19 passed、gate 8/8）。详见 [`recheck-20261026/index.md`](recheck-20261026/index.md)。

## 命令（可整段重跑）

```bash
cd e5/A-buildchecker
python3 scripts/doctor.py --out work/doctor-A2-01/env.json
python3 scripts/lab_cloud.py build --out work/build-A2-01 --image course1020-buildchecker:241880496 --build-timeout 1200
python3 scripts/lab_cloud.py e6 --out work/e6-before-A2 --image course1020-buildchecker:241880496
python3 scripts/lab_cloud.py e6 --fixed --out work/e6-after-A2 --image course1020-buildchecker:241880496
python3 scripts/verify_e6_evidence.py --before work/e6-before-A2/evidence/findings.json --after work/e6-after-A2/evidence/findings.json
python3 scripts/lab_cloud.py build --out work/build-A2-02 --image course1020-buildchecker:241880496
python3 scripts/lab_cloud.py gate --out work/e7-A2-selfcheck --image course1020-buildchecker:241880496
```

重跑时全部换新的 `--out` 目录（`--out` 必须位于 `work/` 下且为空，脚本会拒绝复用）。

## 预期 vs 实际

| 步骤 | 预期 | 实际 |
| --- | --- | --- |
| `doctor` | `problems` 为空 | 0 problems；`spec` 4 CPU / 7.8 GiB / 951.4 GiB |
| `build`（原始） | 15 passed | 15 passed，退出码 0 |
| `e6`（原始） | 入口退出码 1（`--fail-on-findings`），2 条错误 | 退出码 1；`status=SUCCEEDED`、`build_exit_code=0`、`clean_exit_code=0` |
| `e6 --fixed` | 退出码 0，`findings=[]` | 退出码 0，`findings=[]`，仅独立副本 Makefile 改动 |
| `verify_e6_evidence` | `passed=true`、仅 Makefile 变化 | `passed=true`、`changed_inputs=["Makefile"]` |
| `build`（含新增测试） | 17 passed（15 + 本人 2 项） | 17 passed，退出码 0 |
| `gate`（自证） | 退出码 0，8 项全通过 | 退出码 0，8/8 `passed=true` |

## 关键结论与证据定位

| 结论 | 证据 |
| --- | --- |
| `MISSING main.o → config.h` | `before/findings.json`：`t.14` 第 579 行、pid 14；`t.15` 第 23 行、pid 15（`openat` 成功只读打开） |
| `REDUNDANT main.o → unused.h` | `before/make-db.txt` 第 1053 行声明 `main.o: main.c unused.h`，本次构建未观察到读取 |
| 修复只改声明 | `after/make-db.txt` 与 `before/make-db.txt` 差异仅 `main.o: main.c unused.h` → `main.o: main.c config.h` |
| 其余输入未变 | `before/findings.json` 的 `input_sha256`：Makefile `fd1dcd76…`、config.h `ac32a92f…`、main.c `bfa1c2d1…`、unused.h `1e431554…`，与 after 相同 |

## 目录内文件

| 路径 | 内容 |
| --- | --- |
| `doctor/env.json` | 环境自检（工具版本、资源、Git 本地身份、镜像加速） |
| `before/input/` | **输入副本**（`Makefile`、`main.c`、`config.h`、`unused.h`），SHA-256 与 `before/findings.json` 的 `input_sha256` 逐项一致 |
| `after/input/` | 修复后的输入副本，仅 `Makefile` 的哈希与 before 不同 |
| `before/runner/`、`after/runner/` | 入口命令、原始 `stdout.log`/`stderr.log` 与退出码 |
| `before/findings.json` | 原始样例检测报告（2 条错误、`trace_id=e6-d4fd7a0a183c4c218c5d346f1bdab355`） |
| `before/actual-graph.json`、`declared-graph.json`、`processes.json` | 实际图 / 声明图 / 进程归属 |
| `before/make-db.txt` | `make -p app` 的 Make 数据库原文（声明证据） |
| `before/trace/t.14`、`t.15` | 触发 MD 的两条读取记录（原始共 7 个 trace，见 `before/trace-index.md`） |
| `after/*` | 修复复检报告与两张图（`trace_id=e6-23a2a0ec5174466fad668a91a69ea9fe`） |
| `verify-e6.json` | 前后报告一致性校验输出 |
| `build/tests-17-passed.log` | 重建镜像后的单测输出（17 passed） |
| `gate/gate-result.json`、`gate/results.csv` | 自证门禁 8 项结果与 trace_id |
| `files.sha256` | 本目录全部文件的 SHA-256 清单，供逐字节核对 |

## 本人新增的测试

`services/buildchecker/tests/test_extra_241880496.py`（2 项，独立文件，未改动原有测试）：

1. `test_not_a_target_section_is_skipped`：`make -p` 的 `# Not a target:` 段不得被当作声明目标。
2. `test_order_only_prerequisite_read_by_recipe_is_missing_not_redundant`：order-only 前置若被 recipe 真实读取，必须报 `MISSING`（order-only 不触发重建），且不得报 `REDUNDANT`。

价值：原有用例覆盖 trace 侧边界与单点声明解析，但没有覆盖“声明解析 × 集合差”的衔接；这两项把该衔接钉住。

## 重跑方法（从 main 出发的最小步骤）

```bash
git switch main && git pull --ff-only
git switch -c e5-7/recheck-<学号> e5-7/A2-241880496
cd e5/A-buildchecker
python3 scripts/lab_cloud.py build --out work/build-recheck-01 --image course1020-buildchecker:<学号>
python3 scripts/lab_cloud.py e6 --out work/e6-recheck-before --image course1020-buildchecker:<学号>
python3 scripts/lab_cloud.py e6 --fixed --out work/e6-recheck-after --image course1020-buildchecker:<学号>
python3 scripts/verify_e6_evidence.py --before work/e6-recheck-before/evidence/findings.json --after work/e6-recheck-after/evidence/findings.json
```

`trace_id`、容器 ID、耗时必然不同；`findings` 条目、`changed_inputs` 结论必须相同。

## 限制

- **主机不同**：本班次在本地 WSL2（Ubuntu 26.04）执行，不在组内云主机。`doctor` 的必需项全部满足；如需与课程要求完全一致，应在云主机复跑并把 `env.json` 换成云主机版本。
- **内存调整**：WSL 原配置 `memory=2GB`（低于课程最低 4 GiB），已改为 8GB 后重跑；改动在用户目录 `.wslconfig`，不属于仓库内容。
- **gate 为自证运行**：仅用于证明“新增测试进入门禁”，正式 gate 与 CI 由 A3 负责，两者不共享结论。
