# E11–E12 证据索引（B1 241880555）

更新：2026-11-13。所有 OUT 均在服务器 /root/241880555/DevOps-G16/ 下；`work/`、`data/` 不入 Git，原件在服务器保留并另打 tar 归档。

## 环境

- 服务器：root@47.97.103.111（Aliyun ECS，Ubuntu 22.04，x86_64，3.5Gi 内存）。
- 仓库：/root/241880555/DevOps-G16，分支 `student/241880555/e11-e12`，git `user.name=241880555`。
- 运行器：`run_e11e12.py` @ 代码提交 `00c7ed9`（labs/e11e12、workflow 一并导入）。
- 镜像：`course-e11e12:241880555`（`python3 run_e11e12.py build`，BUILD_EXIT_CODE=0）。
- 样例：`python3 run_e11e12.py prepare`（PREPARE_EXIT_CODE=0）；base=`6af2be9cbfc431c313b325183467742766348ace`（C0），target=`e611292b4f83fbb0060d46d034c543cac113865b`（C1）。
- 候选：原候选 `data/integration-sample/candidate.Dockerfile`（SHA256 `c2f7a9f70caf44bbf4852a1c61e262203de9f28cd6fbe3aa2dec5adf6d34c6da`）；B1 派生 `candidate-mirror.Dockerfile`（SHA256 `e0107367f1501dcd2e3f8737affee3c317cd3144717e5069ae0b07c6927cc125`，仅新增 apt 清华源 RUN 行，ADR-001）。

## 运行记录（命令 → 退出码 → OUT）

| # | 命令 | 退出码 | OUT | 结论 |
| --- | --- | --- | --- | --- |
| 1 | `python3 run_e11e12.py test`（导入后） | 0 | - | 10 tests OK |
| 2 | `run --request data/integration-sample/e11-b.json --out work/e11-b-241880555-20261113a` | 1 | e11-b-241880555-20261113a | FAILED：iter-01 MISSING_MAKE ✓，iter-02 apt 官方源 600s 超时（故障证据） |
| 3 | `run --request data/integration-sample/e11-b-b1.json --out work/e11-b-241880555-20261113b` | 0 | e11-b-241880555-20261113b | SUCCEEDED，E11-B 判据全过 |
| 4 | `run --request data/integration-sample/e12-b1.json --out work/e12-241880555-20261113a` | 0 | e12-241880555-20261113a | SUCCEEDED，五阶段同 job/trace |
| 5 | `run --request data/integration-sample/e11-b-mismatch.json --out work/e11-b-241880555-mismatch-20261113` | 1 | e11-b-241880555-mismatch-20261113 | FAILED(DRAFT_FAILED) 预期内，输出不符结论 |
| 6 | `python3 run_e11e12.py test`（加 B1 测试后） | 0 | - | 15 tests OK（10 原 + 5 B1） |
| 7 | DRAFT 同镜像执行对照（宿主 docker，见 #8） | 0/0/0 | e12-241880555-20261113a/draft-execution/ | inspect 一致 + 默认运行输出 1 + 镜像内重构建输出 1 |

## 关键字段（E11-B 成功运行 #3）

- job_id `job-f3ee0480c2f844e598988e4df3d9bca7`，trace_id `trace-cd1721468046474d857cfbbb029de5f7`。
- stages：draft → fixed-md → repair → recheck；draft 信封 commit = target。
- attempt1：exit 1，`MISSING_MAKE`；attempt2：exit 0，`image_id=sha256:8ad0bfcffc89c097b0d38cf6912eaba0183978c97f2af171ec492c044f4cf37d`。
- verification：`docker run --rm --network none … <image_id>` exit 0，actual `1\n`，output_matches true（构建与运行同一镜像）。
- fixed-md：信封 commit 与 `data.commit` 均为 `e611292b…`；findings：MISSING(main.o,config.h)、MISSING(main.o,extra.h)、RD(main.o,unused.h)。
- validation `accepted=true`；final-full 仅 RD(main.o,unused.h)。
- 原件：OUT 下 `result.json`、`draft-build/result.json`、`fixed-md.json`、`candidate.patch`、`repair-plan.json`、`validation/validation.json`、`final-full/findings.json`、`draft-build/iter-0{1,2}/build-*.log`。

## 关键字段（E12 CLI #4）

- job_id `job-bc6cc1019eb3442c87a4f1f58b3be0a1`，trace_id `trace-4f1747cd8ced4e3a8222e179ac1d00c9`（五阶段一致）。
- full-check commit=`6af2be9c…`（base）；draft/incremental-check/repair/recheck commit=`e611292b…`（target）。
- `repair.json data.input_report` = `artifact://job-bc6cc1019…/incremental-check.json`（sha256 `d88717272823bcbb…` 完整值见文件）。
- recheck：`accepted=true`，仅 RD 保留。
- draft `image_id=sha256:4d0217491191b5568e1bbf088764cb8fde0c981068c74b92468b4cbe9a3dfc89`；同镜像执行对照原件：`draft-execution/execution-log.txt`（inspect Id 一致、CMD 输出 1、镜像内 make 后输出 1，三条命令退出码 0/0/0）。

## 自主实验（#5）与测试

- 输入：`data/integration-sample/e11-b-mismatch.json`（= e11-b-b1.json 但 expected_output=2）；候选同 mirror 版。
- 实际：EXIT 1；pipeline error `{code: DRAFT_FAILED}`；draft error `Program verification failed: nonzero exit or unexpected output`；attempt2 `build_exit_code=0`、`image_id=sha256:3ae46247047a2ebaceb364317a11f7ea2e44985e017387dfe8a2dc4105a42cc3`；verification `{exit 0, expected 2, actual "1\n", output_matches false}`。
- 结论区分：构建成功+输出不符 ≠ 构建失败（后者无 image_id，见测试用例 3）；与 E11-B 成功样例构成三态对照。
- 单测：`labs/e11e12/test_student_241880555.py`（fake 替换 `draft.autobuild.execute`，CI 无 docker socket 可跑）。

## 归档与校验

- tar：/root/devops-submissions/241880555/E11-E12-20261113-*.tar.gz（含 4 个 OUT、candidate/请求副本、执行对照日志；排除 .git）。SHA256 见归档命令输出，与远端 `sha256sum` 核对。
- 本地副本：D:\Users\nmh\Desktop\DevOps-G16\work-backup-e11b\（E11-B 与 E12 关键 JSON）。
- Git 内小件：本目录（report.md、index.md、adr-001）与 `labs/e11e12/test_student_241880555.py`。

## 分工边界（本轮未做、待对齐）

- `mode=e12` 共享 API 提交/轮询/下载与 SSH 转发联调：A3（入口）/B3（消费）主责，B1 未单独执行，待对齐后复用同一任务核验。
- 真实项目候选/构建适配：待 A1 牵头选定项目与双 SHA 后执行。
