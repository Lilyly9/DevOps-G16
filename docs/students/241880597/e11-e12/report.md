# E11–E12 个人报告（B3 吴佳静 241880597）

学号/小组/轨道：241880597 / G16 / B16（DRAFT → MDFixer，B 侧消费/联调）
仓库与提交 SHA：Lilyly9/DevOps-G16，分支 `student/241880597/e11-e12`，代码提交 `待云端提交后填`（基于 main `待填`）。

## E11 轨道集成（B3 抽查主责）

B3 在 E11-B 中不是 DRAFT（B1）或 MDFixer（B2）的构建者，而是抽查方：核对 B1 的构建证据与 B2 的修复证据、输入目标 SHA 与动态重检结论。

- B1 DRAFT 抽查项：首轮 `MISSING_MAKE`、候选构建成功、构建与运行同一镜像、镜像运行输出 `1`。
- B2 MDFixer 抽查项：`candidate.patch`、`repair-plan.json`、`validation/validation.json` 的 `accepted=true`、最终动态重检无 MD、RD 可保留。
- 固定报告引用（E11）与真实报告引用（E12）分开标注，避免两轮结果混用。

> 抽查结论（2026-11-16 云端）：E11-B 验收通过。job_id=`job-6a0ecd29018f4e96a6c02d19e42cc4a2`，trace_id=`trace-e35069abbe75488c96cdb4bd40bf5ee7`；base=`91de1706f242b026882bfd9fc5da37926a209661`，target=`33a335ff5269466022a1c5078c748cca640e8f7c`。`validation/validation.json` `accepted=true`、`checks.no_missing=true` 且各子项全 true、`error=null`；`final-full/findings.json` 仅一条 `REDUNDANT`（main.o ← unused.h），无 `MISSING`，RD 按预期保留。四阶段 draft→fixed-md→repair→recheck 全 SUCCEEDED。

## E12 联调（B3 独立消费主责）

### 五阶段运行结果

> 云端 E12 CLI 运行成功（2026-11-16）。job_id=`job-c7baefcaa6f44881a79bfef7a153fd26`，trace_id=`trace-6f0fc4df6d37499c885abad2cc0848d3`。五阶段顺序 `draft → full-check → incremental-check → repair → recheck` 全 SUCCEEDED。full-check 对应 base=`91de1706f242b026882bfd9fc5da37926a209661`，其余四阶段（draft/incremental-check/repair/recheck）对应 target=`33a335ff5269466022a1c5078c748cca640e8f7c`。

### 消费侧字段映射

B3 从 A3 维护的 API 宿主经 SSH 转发取得交接清单，再按 `download_path` 下载原始增量封装，核对后交给 B2 修复入口。两段 HTTP 响应的字段与消费侧校验：

| 来源 | 字段 | B3 消费侧校验 |
| --- | --- | --- |
| 交接清单（e11e12-transfer-1） | schema_version / kind / job_id / trace_id / commit | schema 为 `e11e12-transfer-1`；kind=`incremental-check`；job_id 与 commit 与请求一致 |
| 交接清单 report | uri / sha256 / bytes | uri=`artifact://{job}/incremental-check.json`；sha256 与 bytes 与原始封装一致 |
| 交接清单 download_path | /v1/jobs/{job}/files/incremental-check.json | 路径精确匹配，下载原始字节 |
| 增量封装（e11e12-1） | schema_version / kind / status / commit / job_id / trace_id | schema/kind/status/commit 通过 `check_envelope`；job/trace 与清单一致 |
| 增量封装 data | data.commit / data.findings | 内层 `data.commit == target`（拒绝过期报告）；findings 原样交给 B2 |

三处哈希一致：交接清单 `report.sha256`、下载响应头 `X-Content-SHA256`、实际字节 sha256 必须一致，且字节大小一致。任一不符即 `ARTIFACT_HASH_MISMATCH`，不进入修复。下载报告保存原字节，重写 JSON 会改变摘要。

### 独立消费流程

> 云端实测（2026-11-16，均通过）：
> - 服务：`run_e11e12.py serve --port 8080`（loopback），`/health` 返回 `{"status":"ok"}`。
> - 提交：`POST /v1/jobs`（幂等键 `b3-e12-241880597-v1`）→ job_id=`job-7a94650e554e42289376ecb884be82de`，异步五阶段 SUCCEEDED，trace_id=`trace-c5c8a3a78bc74e63ae9c01e4e3151e57`。
> - 幂等：同 key 再提交返回同一 job_id、`SUCCEEDED`，未新建。
> - 消费：`report_exchange.py --base-url http://127.0.0.1:8080 --job job-7a94650e554e42289376ecb884be82de --target 33a335ff5269466022a1c5078c748cca640e8f7c --out work/b3-download-241880597` → `REPORT_TRANSFER_VERIFIED`。
> - 三处哈希一致：交接清单 `report.sha256`、响应头 `X-Content-SHA256`、实际字节 sha256 均=`796ec26961ed1655c9bd45a18e70191c507e3a4bc1e8bfa662d8b815fee67601`，字节大小 3414 一致；`verification.json` `passed=true`。
> - 产物：`transfer-manifest.json`、`incremental-check.json`（原字节 3414B）、`response-headers.json`、`verification.json` 保留于 `work/b3-download-241880597/`。
> - 交接：核验通过的 `data.findings` 原样交 B2 修复入口。

## 真实数据

真实 C/Make 项目由 A1 牵头：**transfer-eta**（估算传输耗时，in-repo `projects/transfer-eta/`）。B3 核对目标 SHA 与消费结果。

- 来源：`https://github.com/Lilyly9/DevOps-G16`，`project_path=projects/transfer-eta`。
- base=`5ef9d829e2f893af23f60399dcb67095800d121e`（Add a C command-line tool），target=`e7414083c4f1760cb234f96a9d75f2d0255e3f57`（configurable default transfer rate）。目标 SHA 与 A1 记录一致。
- 运行：`mode=e12` + `profile=true`，候选 `projects/transfer-eta/candidate.Dockerfile`（daocloud 基础镜像 + 清华源 apt）。
- 结果（2026-11-16 云端 CLI）：SUCCEEDED，job_id=`job-b3206ad827734ea9867cf3fecc333b1a`，trace_id=`trace-ccad58f4b473499aa396302a1e210d41`；五阶段 `draft→full-check→incremental-check→repair→recheck`。
- 增量检出 `MISSING(eta_cli.o, defaults.h)`，与 A1 `expected_missing` 一致；`validation/validation.json` `accepted=true`；`final-full` 无 MD（findings 空）。
- 消费：B3 独立消费入口已在固定样例经 HTTP 下载 + 三处哈希核验闭环；真实项目走同一 `download_report` 路径，API 侧 `/course/data` 置备由 A1/B1 负责（共享交付）。

> 说明：tokenstat 项目仍用旧 profile 名 `e11e12-project.json`（pipeline 现读 `e12-profile.json`），CLI 报 `INVALID_PROFILE`；非 B3 改动，改选 transfer-eta 后通过。

## 故障与处理

- 环境：`candidate.Dockerfile` 的 `apt-get update` 走 deb.debian.org 超时，改用清华源镜像 `candidate-mirror.Dockerfile`（在 apt-get 前插入 sed 换源 RUN 行）后构建通过。
- 共享命名：tokenstat 项目仍用旧 profile 名 `e11e12-project.json`，而 `pipeline.py` 经 `project_profile.py` 读取 `e12-profile.json`，CLI 报 `INVALID_PROFILE`；改选 A1 的 transfer-eta（已用 `e12-profile.json`）后通过，未改共享代码。

## 独立贡献与测试

`labs/e11e12/test_student_241880597.py`（B3 独立贡献：消费侧拒绝路径，对应任务表 §5 B3 方向「验证独立消费入口接受本轮报告，拒绝 commit 或内容哈希不匹配的产物」）：

| 用例 | 预期 |
| --- | --- |
| test_accept_current_report_and_three_hashes | 接受本轮报告，三处哈希一致，verification.passed=true |
| test_reject_output_exists | OUTPUT_EXISTS（传输目录已占用） |
| test_reject_manifest_schema | SCHEMA_MISMATCH |
| test_reject_manifest_job_mismatch | REPORT_IDENTITY_MISMATCH |
| test_reject_manifest_commit_mismatch | REPORT_IDENTITY_MISMATCH |
| test_reject_wrong_kind | ARTIFACT_TYPE_MISMATCH |
| test_reject_wrong_download_path | ARTIFACT_TYPE_MISMATCH |
| test_reject_wrong_report_uri | REPORT_IDENTITY_MISMATCH |
| test_reject_manifest_sha_mismatch | ARTIFACT_HASH_MISMATCH（清单 sha 与字节不符） |
| test_reject_header_sha_mismatch | ARTIFACT_HASH_MISMATCH（响应头 sha 与字节不符） |
| test_reject_byte_size_mismatch | ARTIFACT_HASH_MISMATCH（字节大小不符） |
| test_reject_inner_commit_expired | STALE_REPORT（外层 commit 对、内层 data.commit 过期） |
| test_reject_report_trace_mismatch | REPORT_IDENTITY_MISMATCH（报告 trace 与清单不符） |

本地验证：`python -m unittest labs.e11e12.test_student_241880597` 13 用例全绿；与 test_contract.py 合并 23 用例通过。测试以 mock 回放两段 HTTP 响应，不依赖 docker socket，CI 可跑。未改共享 pipeline/server/report_exchange 源码。

## 交付索引

| 任务 | 文件/URL | 结果 |
| --- | --- | --- |
| 独立契约测试 | labs/e11e12/test_student_241880597.py | 13 用例本地全绿 |
| E12 独立消费（serve+下载+核哈希+交 B2） | work/b3-download-241880597/（verification.json passed=true） | 三处 SHA 一致，通过 |
| E11-B 抽查 | work/e11-b-241880597-20261116c/（validation.json + final-full/findings.json） | accepted=true、无 MD、RD 保留，通过 |
| 真实项目（transfer-eta 核对+消费） | work/e12-transfer-eta-241880597-20261116/ | SUCCEEDED，MISSING(eta_cli.o, defaults.h)，accepted=true，无 MD |
| PR / CI | 待云端填 | TODO |
