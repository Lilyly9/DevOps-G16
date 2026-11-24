# 证据索引（A1 焦龙 241880485 · E13–E14）

所有路径相对 `docs/students/241880485/e13-e14/evidence/`。
逐文件 SHA-256 见同目录 **`MANIFEST.sha256`**（119 条，`sha256sum -c` 可校验）。

**执行人均为 A1 焦龙；宿主为课程云机 A16。** 队友产出在表中单列，不混入本人运行证据。

## 1. 环境与基线

| 文件 | 内容 | 说明 |
| --- | --- | --- |
| `logs/environment.txt` | `HEAD`、分支、`ORIGIN`、UTC 时间、CPU、MemTotal、Docker/Compose/Python 版本 | 源码 SHA `1a824ff6ef038787acb29fb290a8361429b6f408` |
| `logs/source-sha.txt` | 运行时的 `git rev-parse HEAD` | 与最终证书提交 `980e1a5` 的差异见报告 §9 |
| `logs/tests.log` + `.exit-code.txt` | 容器内 E11–E12 契约测试 | **65 tests OK**，退出码 0 |
| `logs/prepare.log` + `.exit-code.txt` | `run_e11e12.py prepare` | 退出码 0，生成 `data/integration-sample` |
| `logs/image.txt` | `course-e11e12:241880485` 镜像 ID 与大小 | `sha256:40b15f7e…` / 207 440 588 B |

## 2. C1 正常链路

| 文件 | 内容 |
| --- | --- |
| `c1/request.json` | 请求：`mode=e12`、`project_path=projects/transfer-eta`、`profile=true` |
| `c1/candidate.Dockerfile` | 固定 digest 候选 |
| `c1/commits.txt` | base/target 的 `git rev-parse` 与 `--stat` 差异 |
| `c1/run.exit-code.txt` | `C1_EXIT=0` |
| `c1/run.log` | 完整 stdout/stderr |
| `c1/run/` | `draft/full-check/incremental-check/repair/recheck` 信封、`baseline-full`、`target-full`、`final-full`、`validation` |
| `c1/summary.json` | 汇总：job `job-789dec04…`、235 产物、target 发现、recheck 缺失 0、报告 SHA 一致 |

**关键结论**：target 全量图为 `MISSING(eta_cli.o → defaults.h)`（`openat` 系统调用证据）；修复后 recheck 在同一 target commit 上 `MISSING=0`；`repair` 读取的报告 SHA 与磁盘 `incremental-check.json` 一致。

## 3. C7 失败隔离

| 文件 | 内容 |
| --- | --- |
| `c7/failed-request.json` | 变体 A：base 置 `0…0` |
| `c7/success-request.json` | 正常任务请求 |
| `c7/timeout-request.json` | 变体 B：`build_timeout=0.01` |
| `c7/exit-codes.txt` | `FAILED_EXIT=1`、`SUCCESS_EXIT=0`、`TIMEOUT_EXIT=1`、两个校验退出码 0 |
| `c7/e13-c7-a1-01-failed-result.json` | 失败任务：`job-fce3110d…`，`COMMAND_FAILED`，2 产物 |
| `c7/e13-c7-a1-01-success-result.json` | 成功任务：`job-802afa93…`，235 产物 |
| `c7/e13-c7-a1-02-timeout-result.json` | 超时任务：`job-434f0696…`，`DRAFT_FAILED`，48 产物 |
| `c7/isolation.json` / `.log` | 变体 A 校验：`PASS`，482 项检查 |
| `c7/isolation-timeout.json` / `.log` | 变体 B 校验：`PASS`，482 项检查 |
| `c7/runs.json` | 三个 run 的 status/job/trace/产物数/错误 |
| `c7/failed-console.log`、`success-console.log`、`timeout-console.log` | 三次运行的原始控制台输出 |

## 4. E14 四容器

| 文件 | 内容 |
| --- | --- |
| `e14/exit-codes.txt` | `COMPOSE_CONFIG_EXIT`、`COMPOSE_UP_EXIT`、`FAULT_EXIT`、`SAMPLE_EXIT`、两个扫描、`COMPOSE_DOWN_EXIT` |
| `e14/health.txt` | 四个角色 `/health` 的实际响应体 |
| `e14/compose-ps.txt`、`compose-ps-after.txt` | 运行前后 `compose ps`（四个 healthy） |
| `e14/compose-up.log`、`compose-down.log`、`compose-config.log` | 生命周期日志 |
| `e14/services.log` | 四个容器的角色日志（含 job/trace/状态/耗时） |
| `e14/scan-work.log`、`scan-services.log` | 运行时日志 Secret 扫描，退出码均 0 |
| `e14/request.json`、`fault-request.json`、`candidate.Dockerfile` | 固定样例请求与候选 |
| `e14/mirror-adaptation.txt` | 镜像源/apt 源替换的来源、digest、前后 SHA-256、原因 |
| `e14/sample-02/` | 五阶段信封、`result.json`、`summary.json`（`job-fc8b5db6…`，162 产物） |
| `e14/fault-02/` | 故障 run 的 `result.json` 与 `summary.json`（`job-b99f47f8…`，TIMEOUT，36 产物） |
| `e14/orchestrate.log`、`orchestrate-fault.log` | 两次编排的原始输出 |
| `e14/orchestrate-real-project.log`、`real-project-result.json`、`real-project.exit-code.txt` | **真实项目阻断证据**：`Unsupported teaching project profile`，退出码 1 |

**说明**：`e14/sample-02` 与 `fault-02` 使用的是镜像源适配版固定样例（base `527980…`、target `c3561b…`），不是教师原始 `ed3309e`/`21fb658`；两者都记录在 `mirror-adaptation.txt` 中，报告中未把适配版写成原始固定样例。

## 5. 队友成果（本人只读核验，不计入本人运行）

| 内容 | 来源 | 位置 |
| --- | --- | --- |
| `labs/e13e14/` 四容器入口、`handoff_a_to_b.py`、`scan_runtime_logs.py` | A2 万宇，PR #28 | `origin/main` |
| `labs/e11e12/pipeline.py` 的 `fixed_report_sha256` | A2 万宇，PR #28 | `origin/main` |
| B3 消费者拒绝测试与个人记录 | B3 吴佳静，PR #25 | `origin/main` |
| B2 报告内层 commit 校验 | B2 李敏君 | `origin/main` |

本人对 A2 的 `handoff_a_to_b.py` 与 `scan_runtime_logs.py` 做了逐文件比对（与 `03_实验包` 的差异仅为文档字符串、格式与指针赋值例外），未重写。

## 6. 校验方式

```bash
cd docs/students/241880485/e13-e14/evidence
sha256sum -c MANIFEST.sha256
```

## 7. 未纳入本索引的内容

`data/` 与 `work/` 属 `.gitignore` 忽略的本机生成物（请求克隆、构建中间件、沙箱目录）；其中被引用的关键 JSON 已复制进 `c1/run/`、`e14/sample-02/`、`e14/fault-02/`。原始 `data/integration-sample` 未修改。
