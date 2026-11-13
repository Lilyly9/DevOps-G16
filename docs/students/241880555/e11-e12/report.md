# E11–E12 个人报告（B1 郭德林 241880555）

学号/小组/轨道：241880555 / G16 / B16（DRAFT → MDFixer）
仓库与提交 SHA：Lilyly9/DevOps-G16，分支 `student/241880555/e11-e12`，代码提交 `00c7ed9`（基于 main `aecdbb3`），文档提交见本目录 git 历史。

## E11 轨道集成

- 上游（B1 · DRAFT）：`vendor/draft/autobuild.py` 两轮构建。第 1 轮用 broken 基线 Dockerfile 必须失败且 `failure_class=MISSING_MAKE`；第 2 轮用候选构建，`docker image inspect` 取 `image_id`，`docker run` 验证程序输出等于 `expected_output`。
- 下游（B2 · MDFixer）：消费 `fixed-md.json`（E11-B 固定输入），输出 `candidate.patch`、`repair-plan.json`、`validation/validation.json`；最终 `final-full` 重检无 MISSING（RD 可保留）。
- 字段映射：`auto_build` 报告的 `attempts[].build_exit_code / failure_class / image_id` 与 `verification.output_matches` 进入 `draft-build/result.json`，再由 `pipeline.py` 原样放入 `draft` 阶段信封 `data`；`image_id` 是 B1 交给 A1/A2（检测）与 B2（复验）的执行环境字段。
- 固定样例结果（OUT=work/e11-b-241880555-20261113b，job `job-f3ee0480c2f844e598988e4df3d9bca7`，trace `trace-cd1721468046474d857cfbbb029de5f7`）：
  - 首轮 `MISSING_MAKE`（exit 1）；候选构建 exit 0；`image_id=sha256:8ad0bfcffc89c097b0d38cf6912eaba0183978c97f2af171ec492c044f4cf37d`；镜像运行输出 `1`（构建与运行同一镜像，verify 命令即引用该 image_id）。
  - `fixed-md.json` 信封 `commit` 与 `data.commit` 均为 target `e611292b4f83fbb0060d46d034c543cac113865b`。
  - 修复 `MD(main.o, config.h)`、`MD(main.o, extra.h)`（固定样例新增项），`accepted=true`；重检仅剩 `RD(main.o, unused.h)`。
- 本人代码修改：新增 `labs/e11e12/test_student_241880555.py`（5 用例，见下）。未改共享 pipeline/server/vendor 源码；候选适配通过派生候选文件实现（见 ADR-001）。

## E12 联调

- CLI 五阶段全链（OUT=work/e12-241880555-20261113a，job `job-bc6cc1019eb3442c87a4f1f58b3be0a1`，trace `trace-4f1747cd8ced4e3a8222e179ac1d00c9`）：`draft → full-check → incremental-check → repair → recheck` 全部 SUCCEEDED，五阶段同一 job_id/trace_id；`full-check` 属 base `6af2be9cbfc431c313b325183467742766348ace`，其余四阶段属 target `e611292b4f83fbb0060d46d034c543cac113865b`。
- `repair.json` 的 `data.input_report` 指向本轮 `artifact://job-bc6cc1019…/incremental-check.json`（SHA256 d8871727…），未再使用固定 MD 文件。
- DRAFT 镜像交接（B1 主责，回应课件第 16–18 页"同镜像执行"补齐项）：对 e12 运行所得 `image_id=sha256:4d0217491191b5568e1bbf088764cb8fde0c981068c74b92468b4cbe9a3dfc89` 做了三项实际执行对照（命令、镜像 ID、退出码、输出见 `draft-execution/execution-log.txt`）：
  1. `docker image inspect`：Id 与 draft 报告完全一致；
  2. `docker run --rm --network none <image_id>`：默认 CMD 输出 `1`，exit 0；
  3. 同镜像内 `rm -f app && make app && ./app`：重新链接成功并输出 `1`，exit 0 —— 证明该镜像可作为检测/复验的实际执行环境，不只是 JSON 字段传递。
- `mode=e12` 共享 API（POST /v1/jobs、SSH 转发联调）：A3 维护入口、B3 实现独立消费，为 A3/B3 主责；B1 留待与其对齐后复用同一任务核验五阶段，本轮未单独执行 API 提交，避免重复归属。

## 真实数据

- 真实 C/Make 项目由 A1 牵头筛选（任务表 §7），截至 2026-11-13 未选定；登记缺项。
- B1 后续责任：项目与 base/target 双 SHA 定下后，为目标提交准备候选、构建上下文与镜像交接，并把固定样例的 `candidate-mirror` 网络适配迁移到真实项目构建。

## 故障与处理

1. **候选构建超时（TIMED_OUT）**：第一次 E11-B（OUT=work/e11-b-241880555-20261113a，原候选，官方 apt 源）第 1 轮正常复现 `MISSING_MAKE`，第 2 轮 `apt-get` 下载 `deb.debian.org` 9.6MB 索引 178s 未完成，600s `build_timeout` 耗尽，整体 FAILED。处理：按 ADR-001 派生换清华源候选 `candidate-mirror.Dockerfile`（原候选保留不动），重跑成功。证据：`e11-b-241880555-20261113a/draft-build/iter-02/build-stderr.log`。
2. **退出码误读**：首次核对用 `python3 run_e11e12.py run … | tail`，`$?` 取到 tail 的退出码误判为成功；改为输出重定向文件后 `echo $?` 取真实退出码（mismatch 实验正确得到 EXIT 1）。
3. **测试容器无 Docker socket**：`run_e11e12.py test` 不挂载 socket，真实 docker 命令无法在 CI 单测执行；测试改为以可脚本化 fake 替换 `draft.autobuild.execute`，真实 Docker 行为由 E11-B 固定样例与 mismatch 实验覆盖。

## 独立贡献与测试

`labs/e11e12/test_student_241880555.py`（B1 独立贡献：候选构建成功与运行输出不符时的不同结论，对应任务表 §5 B1 方向）：

| 用例 | 预期 |
| --- | --- |
| test_build_ok_output_matches_records_image_id | SUCCEEDED，`attempts[1].image_id` 与 `verification.output_matches` 记录（交接契约） |
| test_build_ok_but_wrong_output_fails_verification | FAILED "Program verification failed"，`build_exit_code=0` 且 `image_id` 仍记录（构建成功可追溯） |
| test_repair_build_failure_is_a_different_conclusion | FAILED "Repair candidate build failed"，无 `image_id` |
| test_first_iteration_must_reproduce_missing_make | 首轮未复现 MISSING_MAKE 即拒绝，`failure_class=OTHER_BUILD_ERROR` |
| test_classify_failure_separates_make_from_infrastructure | MISSING_MAKE / INFRASTRUCTURE / OTHER_BUILD_ERROR 三分类 |

真实 Docker 交叉验证：`data/integration-sample/e11-b-mismatch.json`（expected_output=2，程序实际输出 1）→ EXIT 1，pipeline `DRAFT_FAILED`，draft `attempts[1].build_exit_code=0`、`image_id=sha256:3ae46247047a2ebaceb364317a11f7ea2e44985e017387dfe8a2dc4105a42cc3`、`output_matches=false`（OUT=work/e11-b-241880555-mismatch-20261113）。全套测试 15 个（原 10 + B1 5）通过。

## 交付索引

|任务|文件/URL|结果|
|---|---|---|
|E11-B 固定样例|work/e11-b-241880555-20261113b（服务器）/result.json、draft-build/、candidate.patch、validation/validation.json|SUCCEEDED，7 项判据全过|
|E12 CLI 五阶段|work/e12-241880555-20261113a/result.json、recheck.json、draft-execution/execution-log.txt|SUCCEEDED，五阶段同 job/trace，同镜像执行对照通过|
|自主 mismatch 实验|work/e11-b-241880555-mismatch-20261113 + test_student_241880555.py|FAILED(DRAFT_FAILED) 符合预期，三结论区分留证|
|故障记录|work/e11-b-241880555-20261113a/draft-build/iter-02/、ADR-001|超时→换源候选→成功|
|PR / CI|见 PR 正文（分支 student/241880555/e11-e12）|CI run 待 push 后回填|
|归档|/root/devops-submissions/241880555/E11-E12-*.tar.gz|SHA256 见 index.md|
