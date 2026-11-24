# B1（郭德林 241880555）E13-E14 个人证据索引

实际环境：云服务器 root@47.97.103.111（Ubuntu 22.04，x86_64），仓库 `/root/241880555/DevOps-G16`。
分支：`student/241880555/e13-e14`，基线 `origin/main` = `28c94defee5af11ada42f9842cf03db2cb9da2e3`（含 A2 PR#28 已合入的 `labs/e13e14/` 与 `pipeline.py` 的 `fixed_report_sha256` 校验）。
教学镜像：`course-e11e12:241880555` = `sha256:f22141ff5d9ca00fbb691e4df240090f1f1673200b54c8bb12d0227ca392205e`（2026-11-13 构建，E11-E12 复用，本轮未重建）。

## 0. 代码导入与独立测试

- main 已包含实验包的 `labs/e13e14/{handoff_a_to_b.py,orchestrate.py,scan_runtime_logs.py,service.py,compose.yaml,test_handoff.py}`（A2 合入）；B1 本轮导入缺失的 CI 模板 `.github/workflows/e13e14.yml`，并把工作流的 unittest 发现路径由模板的 `labs/e13e14/tests` 适配为 main 实际结构的 `labs/e13e14`。
- B1 独立测试 `labs/e13e14/test_student_241880555_e13e14.py`（4 用例，CI 无 Docker 可跑）：
  1. 合法 A 报告经 `make_handoff` 转换、请求携带匹配 `fixed_report_sha256` 时，通过传输 SHA 门、信封身份检查、snapshot 与默认 profile 检查，停在 patched DRAFT 边界（`EXECUTION_FAILED`/`CI_NO_DOCKER`）。
  2. 报告字节被篡改且沿用旧 SHA → `ARTIFACT_HASH_MISMATCH`（changed during transfer），且不产生 snapshot 目录。
  3. 非法 SHA 格式 → `ARTIFACT_HASH_MISMATCH`（must be a lowercase SHA-256）。
  4. 报告文件缺失 → `ARTIFACT_HASH_MISMATCH`（missing）。
- 首轮 PR #29 CI：e11e12/e8e10/E7 gate 绿；e13e14 `contracts` 失败（模板写死 `scripts/secret_scan.py`，main 实际路径为 `labs/e11e12/environment/scripts/secret_scan.py`）、`four-services` 失败（GitHub runner 非-root checkout 使容器内 git 报 dubious ownership）。修复：workflow 扫描路径改为实际路径；`labs/e13e14/compose.yaml` 为四容器增加 `GIT_CONFIG_COUNT/KEY_0/VALUE_0`（safe.directory=*），compose config 复核通过。
- 回归：`python3 run_e11e12.py test` OK（15 用例）；`labs/e13e14` discover 7 用例 OK；`test_contract.py`、`labs/e11e12/test_student_241880555.py` 均 OK。测试文件名带 `_e13e14` 后缀，避免与 `labs/e11e12/test_student_241880555.py` 模块同名冲突（首轮实测触发 ImportError 后改名）。

## 1. B 侧交换项目固定（E13 主责）

`data/e13-b-project/`（入库：`repo.bundle` + 配套文件；`repo/` 为运行时副本，gitignored）：

| 项 | 值 |
| --- | --- |
| 仓库（bundle） | `data/e13-b-project/repo.bundle`，SHA256 `56093e7a303e3ee614688abbdc4dbb9b1dd5e8769c38737d6423433a89410eb8` |
| base (C0) | `e9ce878b1e2c46bd7d86e463ff9115b2fc2e6158`（完整构建，含 `e12-profile.json` 与 `Dockerfile.broken`） |
| target (C1) | `48b64156548b3fd8af1ed9ed25eee60d0f92371d`（`helper.o` 规则去掉 `extra.h` 依赖，形成 MD 缺口） |
| 预期输出 | `2`（`VALUE + helper()`，helper 返回 `HELPER_BASE=1`；header_change `#define VALUE 1→2` 输出变 `3`） |
| 候选 | `candidate.Dockerfile`（清华源 ADR-001 模式 + build-essential + strace），SHA256 `60c973f651cfba963675c9b19b46bd56a4071427e92bd9758509ffe8e7f39202` |
| profile | `e12-profile.json`（schema `e12-project-1`），请求带 `profile: true` |
| 请求 | `e12-b1.json`（B1 自测）、`e11-a-b1.json`（交 A 侧跑全量+增量） |
| 交换说明 | `exchange.json`（提供人 B1、SHA、候选来源、运行限制 build_timeout=600、不交换 .env/真实 Key） |

**B1 自测五阶段**（`work/e13-b-project-b1-05`，退出码 0，SUCCEEDED）：
job `job-836f2d82eba9448a892e8a1becdb3d41` / trace `trace-49b3db22184d4f1f995d58931dafb544`；draft→full-check→incremental-check→repair→recheck 全过；recheck findings 无 MISSING；DRAFT 镜像（交接 A1/A2/B2 同镜像核查用）`sha256:b9b0016bea573345c577449d4fca9df5ebcec300d3caac13503cfb1453f57ca4`（`draft-build/result.json` attempts[-1].image_id）。

**排错过程（失败运行保留，不复用旧目录）**：
- `work/e13-b-project-b1-01`：repo 缺课程约定的 `Dockerfile.broken`（`vendor/draft/autobuild.py:84` 直接读取），`EXECUTION_FAILED`。C0 补文件重建。
- `work/e13-b-project-b1-02`、`-03`：draft 成功但 full-check 的 traced 容器失败——`build-stderr.log`：`exec: "strace": executable file not found in $PATH`。main 版 pipeline 在 e12 模式下经 `DraftExecutor` 在 DRAFT 镜像内做 traced full-check，要求镜像含 strace；候选补装 strace。
- `work/e13-b-project-b1-04`：`REPAIR_REJECTED`，`checks.test=False`——无 profile 时 `lab.validate` 硬编码期望输出 `1`/`2`（固定样例约定），与 B 项目输出 2 冲突。为 repo 增加 `e12-profile.json` 并在请求带 `profile: true` 后通过。

## 2. C4 超时主跑（E13 主责）

请求 `data/e13-timeout-request.json`（固定样例 `e11-b.json` 派生，`build_timeout: 0.01`）→ `work/e13-c4-241880555-01`（`C4_RUN_EXIT=1`）：

- 外层 `result.json`：`FAILED` / `DRAFT_FAILED`，message `Docker client command exceeded 0.01s`。
- 内层 `draft-build/result.json`：`TIMED_OUT`，`elapsed_ms=12`。
- 残留核查（`work/e13-c4-241880555-01/residue-check/`）：
  - `NO_VERIFY_CONTAINER_STARTED`（超时发生在第一轮构建，验证容器未启动）；
  - `NO_MATCHING_DOCKER_BUILD_CLIENT`（`ps` 无对应 docker build 客户端进程）；
  - `docker ps` 仅见他人长驻容器 `course-e11e12:241880597`（非本轮产物，未触碰）。
- 正式交叉测试用对方实际项目复跑 C4 已于 round2 完成（见 §6-3）。

## 3. H2 inih 主执行（E13，A1+B1 主执行，A3/B3 复核）

解压 `e13-upstream-student.zip` → `data/e13-upstream-student/`（不入库）；三项目 C0/C1 与上游来源核对输出已保存。H2：base `aafc740a2cac05a74541abede93b7d59ed23b87f`，target `3aadb81763c79651e4dfa99b725ba921ee2b8a39`，上游 https://github.com/benhoyt/inih pin `611ab51f8dd7ec583543815b0de693495045fbf8`。

- 第一轮 `work/e13-H2-inih-241880555-01`（教师原候选，退出码 1）：draft `SUCCEEDED`，full-check 失败——traced 容器缺 strace（与 §1 b1-02 同因），job `job-09f5641fe9d44298b3ff6512d74fe833` / trace `trace-20a6870e5bda489e8ef19ef0d57e0ac9`。失败目录保留。
- 修复：派生 `H2-inih/candidate-strace.Dockerfile`（原候选补装 strace，SHA256 `1e5b8ef428466af0bada6a963b53d047b6276d690d4deb51f15df839f3126934`）与 `request-e12-strace.json`。
- 复测 `work/e13-H2-inih-241880555-02`（退出码 0，五阶段 SUCCEEDED）：job `job-eb0b617667464f82b81849c67deda245` / trace `trace-e98f627176c24362bece833f8b633873`；`validation/validation.json` accepted=true（patch_applies/build/test/header_change/no_missing 全 true）；recheck commit=target 且 MISSING=0。
- H1/H3 分别由 A2+B2、A3+B3 主跑，B1 未越位。

## 4. E14 四容器、固定样例 E2E、受控故障恢复（E14 主责）

- 四容器：`E14_ROOT=$PWD E14_IMAGE=course-e11e12:241880555 docker compose -f labs/e13e14/compose.yaml -p e14-241880555 up -d`；`compose ps` 留证 `work/e14-compose-241880555/compose-ps.txt`——buildchecker/echecker/draft/mdfixer 四容器均 `healthy`，端口仅 127.0.0.1:18081-18084。
- 固定样例四容器 E2E 第一轮 `work/e14-compose-sample-241880555-01`：官方 Debian 源 apt 索引超时，draft `DRAFT_TIMED_OUT ... 600.0s`（E11 ADR-001 同因，job `job-f9ff11eb46c54e8c944e12f3b165461c`）。失败目录保留。
- 复跑（沿用 E11 派生的 `e12-b1.json`，候选 `candidate-mirror.Dockerfile` 清华源）→ `work/e14-compose-sample-241880555-02` 退出码 0：job `job-d005a90e60e9471eba7f938db8a671bb` / trace `trace-1f66630f3748435a8416504f39a7d126`，五阶段全部 SUCCEEDED。
  - 关联核验脚本断言通过（`E14_COMPOSE_SAMPLE_EVIDENCE_CHECK=PASS`）：五阶段同 job/trace、incremental 报告传输 SHA 一致、repair 补丁 SHA 一致且 `validation.accepted=true`、recheck `remaining_missing=0`、全部 162 个产物字节哈希与 `result.json` 一致。
  - 四角色日志（`work/e14-compose-241880555/compose-services.log`）：mdfixer/echecker/draft/buildchecker 各角色处理记录均含 `role`、`job_id`、`trace_id`、`status`、`elapsed_ms`（本轮 mdfixer 1140ms、echecker 24ms、draft 1097ms、buildchecker 三次 517/131/130ms）。
- 受控故障恢复（B1 主注入）：
  - 注入：`data/e14-fault-request-b1.json`（`build_timeout: 0.01`）→ `work/e14-compose-fault-241880555-01` 退出码 1，draft HTTP 422 `DRAFT_TIMED_OUT ... 0.01s`，job `job-6c33413d098f47a19550e8d978a6448c` / trace `trace-fb4cb6cb741b4b24b107505dd1d865d2`。
  - 残留核查（`residue-check/`）：`NO_DOCKER_BUILD_CLIENT`；`docker ps` 仅四个 healthy 服务容器与他人长驻容器，无本轮任务残留。
  - 恢复：原时限新目录 `work/e14-compose-recovery-241880555-01` 退出码 0 五阶段 SUCCEEDED，job `job-91cd65a0adf544fb9664f8e16fa240e5` / trace `trace-a729cc06544146aa9cb6a9b74c2d8e0c`。
  - 隔离核验（`E14_FAULT_RECOVERY_ISOLATION=PASS`）：失败与恢复任务 job/trace 不同；恢复任务五阶段同 job/trace、recheck 无 MISSING、全部产物哈希一致——失败任务标识未污染恢复任务。
- 运行日志 Secret 扫描（`labs/e13e14/scan_runtime_logs.py`）：本轮 7 个证据目录 + `compose-services.log` 全部退出码 0（hits=0 errors=0）。
- 四容器运行状态：固定样例与受控故障恢复完成后保持 `up` 供复核；round2 配对真实项目 E2E（§6-4）复用同一 `-p e14-241880555` 项目运行，收尾时 `docker compose -f labs/e13e14/compose.yaml -p e14-241880555 down` 关闭，容器与网络无残留。

## 5. 已知问题与记录

1. **H 项目/e12 模式候选必须含 strace**：main 版 pipeline 在 e12 模式经 `DraftExecutor` 做 traced full-check。教师三项目候选只装 build-essential，首轮必然 `FULL_CHECK_FAILED`（容器内 `strace: not found`）。已按"失败留证→候选副本补装→复测"路径处理（A2 在 H1 亦然）。建议 A3/组长评估：是否在项目包 README 或 workflow 文档中明示该前置，避免每位执行者重复消耗一轮 600s 级失败运行。
2. ~~四容器 service.py 不支持 project profile~~：已于 round2 解决——`service.py` 三个角色分支（buildchecker/echecker/mdfixer）均接入 `e12-profile.json`，`orchestrate.py` 传递 profile make 目标与扫描目标（见 §6-4）。
3. **orchestrate.py 固定样例默认候选在本人网络环境超时**：与 E11 ADR-001 同因，非代码缺陷；使用换源候选复跑通过，两轮证据均保留。

## 6. Round 2 交付（2026-11-24）：round2 CI 修复、组内交叉与配对真实项目四容器 E2E

### 6-1. round2 CI 错误修复（PR #29）

- 根因 1：早前 `3e9e5e5` 合并冲突解决出错，分支版 `.github/workflows/e13e14.yml` 出现重复 `on:`/`jobs:` key 与步骤错乱，`E13-E14 integration gate` 直接解析失败。恢复为 main 版 workflow（含 A3 已合入的 contracts/four-services 结构）。
- 根因 2：CI 的 secret 历史扫描命中 B2（52ceaef）引入的凭据读取 helper——以凭据名为键的映射单参 lookup，被"密钥赋值"正则误判为字面量。按 A 侧先例 `b376720`（AST 判定单参映射 lookup 放行，literal/fallback 仍拒绝）把 `credential_lookup` 例外移植到 B-draft 与 E11-E12 版扫描器（`189fcbc`）、A-buildchecker 版（`1b268ed`）。
- 修复提交 message 自身含代码示例被历史扫描命中 → amend 后 `--force-with-lease` 重推（`189fcbc`）。
- 修复后 CI 全绿（run `45331060021`/`45331060057`/`45331060245`/`45331060074`/`45331060165`：E7 A/B gate、E8-E10、E11-E12、E13-E14 contracts/four-services 全部 success）。
- round2 文档提交（`759c4c2`）后的分支最新 run `45337643247`/`45337642989`/`45337643073`/`45337643004`/`45337643012` 亦全部 success。

### 6-2. Cross-pair C1 复核（A 侧实际项目 transfer-eta，B1 复核执行）

- 输入 `data/e13-pair-b1/`：从主仓库 `projects/transfer-eta` 子树以 `git worktree` 提取构造 standalone repo（profile 模式要求 target-project 根目录布局），`base = adf19dc421c99eb44f9be2d2fcc8f2addbd89318` / `target = 1b1b0c4712e67e38c703ef6e310776e0c4ce4cb9`，候选沿用 A1 报告对应候选。首轮用主仓库全树提交 `e7414083…` 报 `INVALID_PROFILE`，失败记录在此，改用 standalone repo 后通过。
- 复核运行 `work/e13-c1-pair-b1-01`（退出码 0）：job `job-2142b70849d846d7b90efda22022f410` / trace `trace-1bba9b525cde40ea940ab5a3707377b1`，draft→full-check→incremental-check→repair→recheck 五阶段同 job/trace。
- incremental 发现 `MISSING(eta_cli.o → defaults.h)`，与 A1 报告 §C1 结论一致；recheck `commit=target` 且 MISSING=0。

### 6-3. partner-project C4 正式交叉（A 侧实际项目，B1 主跑）

- 请求同项目（base/target 同 §6-2），`build_timeout: 0.01` → `work/e13-c4-pair-b1-01`（退出码 1）：job `job-467195f13de645508c98d2328edc270e` / trace `trace-0211ec9f22f740df9b0cb6c9b9674810`。
- 外层 `FAILED` / `DRAFT_FAILED`，message `Docker client command exceeded 0.01s`，内层 `TIMED_OUT`；`residue-check/summary.txt` 结论 `NO_RESIDUE`（`docker ps -a` 无本轮构建容器、`ps` 无 buildkit 进程，容器未及启动）。

### 6-4. 配对真实项目四容器 E2E（E14 Test plan 最后一项）

代码适配（5 个提交，每轮失败根因即提交 message）：

| 提交 | 内容 |
| --- | --- |
| `ba83663` | orchestrate `read_profile`/`snapshot` 校验 profile targets 源文件、E2E 请求 `data/e13-pair-b1/request-e14.json` |
| `b97f3ee` | base revision 早于 profile 引入，snapshot 对无 profile 的 base 改为弱校验（有 C 源即可） |
| `b2e444f` | `service.py` buildchecker/echecker/mdfixer 三分支读 `e12-profile.json`：make 目标、扫描 target 映射、`lab.validate` 传 profile |
| `ea50ceb` | baseline 无 profile，orchestrate 从 target profile 推导 `clean/build` 命令经 payload 传给 baseline buildchecker |
| `a69c763` | mdfixer 内 `project_profile` 以 `importlib.util` 按文件路径加载（容器 sys.path 无该目录） |

- 排错 4 轮失败以修复提交留证（Unsupported teaching project profile → Traced build failed `make app` → baseline 同因 → `ModuleNotFoundError: project_profile`）；新增 `labs/e13e14/test_profile_targets.py` 6 用例（服务器运行 OK），覆盖 profile 接受/缺源拒绝/无效拒绝/教学项目接受/无 profile base 接受/无 C 源拒绝。
- 最终运行 `work/e14-real-pair-b1-01`（退出码 0）：job `job-1d2b684354074d169be9870b0e270cf2` / trace `trace-2e54016d9d6a4115b5549f4989304a84`，五阶段全部 SUCCEEDED，全部 187 产物字节哈希与 `result.json` 一致（0 mismatch），stage envelope 逐一核对无 mismatch，recheck MISSING=0。
- 收尾证据：`compose ps` 四容器 healthy（`work/e14-real-pair-b1-01-compose-ps.txt`）；四角色日志 653 行（`work/e14-real-pair-b1-01-services.log`）；`scan_runtime_logs.py` 扫描 E2E 证据目录（176 个文本文件）与服务日志均 hits=0 errors=0；`compose down` 清理后无 e14 容器/网络残留。

## 7. 待组内协调（B1 未执行，不作"通过"声明）

- C2/C3/C5/C7/C8 中 B1 作为复核人的项（依赖 A2/A3/B2/B3 主跑产出）。
- `v0.9-rc` 标签与 Release（组长）；E13 整组门禁判定（A3/B3 汇总）。

## 8. 归档

- 服务器：`/root/devops-submissions/241880555/E13-E14-20261121-B1.tar.gz`（排除 .git；SHA256 见归档命令输出）。
- 本机副本：`work-backup-e13b/`（关键 JSON/日志/核验脚本）。
