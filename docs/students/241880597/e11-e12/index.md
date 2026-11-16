# E11–E12 证据索引（B3 241880597）

更新：2026-11-16。本地测试已完成；云端 E11-B 抽查、E12 CLI 五阶段、API serve+幂等+独立消费下载、真实项目 transfer-eta 均已留证。CI 待跑。`work/`、`data/` 不入 Git，原件在服务器保留并另打 tar 归档。

## 环境

- 本地：Windows 11，Python 3.13.5（Anaconda），仅跑纯 mock 契约测试。
- 服务器：root@47.97.103.111（待 SSH 登录确认路径与仓库位置）。
- 仓库：Lilyly9/DevOps-G16，分支 `student/241880597/e11-e12`，git `user.name=241880597`。
- 运行器：`run_e11e12.py`（代码提交待填）。
- 镜像：`course-e11e12:241880597`（待云端 `build`）。
- 样例：`data/integration-sample/`（base/target 待 `prepare` 后确认）。

## 本地测试运行记录（命令 → 退出码 → 结论）

| # | 命令 | 退出码 | 结论 |
| --- | --- | --- | --- |
| 1 | `PYTHONPATH="labs/e11e12;labs/e8e10;labs/e11e12/vendor" python -m unittest labs.e11e12.test_student_241880597_e11e12 -v` | 0 | 13 用例全绿 |
| 2 | 同上，`test_contract` + `test_student_241880597_e11e12` | 0 | 23 用例全绿 |

> 说明：B1 的 `test_student_241880555.py` 在本地报 `Run inside the Linux service container`，因 `draft.autobuild` 含平台检查，需 Linux 容器（CI）运行，非本次改动引入。

## 云端运行记录

| 阶段 | 命令/对象 | 退出码/结论 |
| --- | --- | --- |
| build | 构建镜像 course-e11e12:241880597（含换源 candidate） | 0 |
| prepare | 生成 integration-sample（base/target） | 0 |
| run（E11-B） | `run_e11e12.py` 四阶段 | 0，draft→fixed-md→repair→recheck 全 SUCCEEDED |
| 抽查 | `validation/validation.json` + `final-full/findings.json` | accepted=true、无 MD、仅 RD 保留 |
| run（E12） | `run_e11e12.py run --request data/integration-sample/e12.json` | 0，draft→full-check→incremental-check→repair→recheck 全 SUCCEEDED |
| serve | `run_e11e12.py serve --port 8080`（后台），`/health` ok | 0 |
| submit（API 幂等） | `POST /v1/jobs`（key b3-e12-241880597-v1）→ job-7a94650e...，同 key 再提交同 job_id | 202，幂等通过 |
| download（独立消费） | `report_exchange.py --job job-7a94650e... --target 33a335ff...8f7c --out work/b3-download-241880597` | REPORT_TRANSFER_VERIFIED，三处 SHA 一致 |
| run（真实项目 transfer-eta） | `run_e11e12.py run --request data/integration-sample/e12-transfer-eta.json` | 0，五阶段 SUCCEEDED，MISSING(eta_cli.o, defaults.h)，accepted=true，无 MD |

> 待云端运行后补：CI run 与 artifact。

## 关键字段

- E11-B：job_id=`job-6a0ecd29018f4e96a6c02d19e42cc4a2`，trace_id=`trace-e35069abbe75488c96cdb4bd40bf5ee7`，base=`91de1706f242b026882bfd9fc5da37926a209661`，target=`33a335ff5269466022a1c5078c748cca640e8f7c`。
- E12 CLI 五阶段：job_id=`job-c7baefcaa6f44881a79bfef7a153fd26`，trace_id=`trace-6f0fc4df6d37499c885abad2cc0848d3`，顺序 `draft→full-check→incremental-check→repair→recheck`，full-check 对应 base=`91de1706f242b026882bfd9fc5da37926a209661`，其余四阶段对应 target=`33a335ff5269466022a1c5078c748cca640e8f7c`。
- E12 API 消费（独立消费）：job_id=`job-7a94650e554e42289376ecb884be82de`，trace_id=`trace-c5c8a3a78bc74e63ae9c01e4e3151e57`，三处 SHA 一致=`796ec26961ed1655c9bd45a18e70191c507e3a4bc1e8bfa662d8b815fee67601`，字节 3414。
- 真实项目 transfer-eta：job_id=`job-b3206ad827734ea9867cf3fecc333b1a`，trace_id=`trace-ccad58f4b473499aa396302a1e210d41`，base=`5ef9d829e2f893af23f60399dcb67095800d121e`，target=`e7414083c4f1760cb234f96a9d75f2d0255e3f57`，增量 `MISSING(eta_cli.o, defaults.h)`，accepted=true，final 无 MD。

## 归档与校验（待填）

> 待填：tar 路径、SHA256、本地副本位置。
