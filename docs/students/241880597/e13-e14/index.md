# B3 E13-E14 个人交付索引（241880597）

- 姓名：吴佳静
- 学号：241880597
- 分支：`student/241880597/e13-e14`
- 角色：B3 / B 消费与联调
- 阶段状态：B 接收、C7 B 侧隔离、C4 复核、C8 幂等复核、固定样例四容器 E2E、配对真实项目四容器 E2E、H3 tiny-AES-c 五阶段、受控故障恢复核验、运行日志扫描、候选发布说明与回滚验证均已完成并留证。RC 发布与远端 CI 仍受 BLOCK-3（云机 GitHub 不通）阻断，因此不代表整组 E13/E14 验收通过。

## 本轮交付

| 项目 | 证据 | 结果 |
| --- | --- | --- |
| A→B 当次报告交接（B 接收） | [fixed-md.json](evidence/b-receive/fixed-md.json) | A2 当次 E11-A 报告经 `handoff_a_to_b.py` 转 fixed-md，SHA256 `1036c8955fe4bae6664a1bf88879113cc2be48b6d7cd358a0c20b70a505737af`，与 A2 导出值一致 |
| C7 任务失败隔离（B 侧） | [c7-isolation-report.json](evidence/c7-b3/c7-isolation-report.json) | 失败/成功两个独立 job/trace，`verify_c7_isolation.py` → PASS（404 checks，无污染） |
| C4 超时复核 | 核验 B1 证据 | B1 超时失败、无进程/容器残留、恢复重跑成功 |
| C8 幂等冲突复核 | [test_student_241880597_e13e14.py](../../../labs/e11e12/test_student_241880597_e13e14.py) | 独立 Store+HTTP 三层测试 3 passed；同 key 同请求复用 job，同 key 异 target HTTP 409 `IDEMPOTENCY_CONFLICT` |
| 固定样例四容器 E2E | [result.json](evidence/e14-sample/result.json) | 五阶段 SUCCEEDED，recheck 无 MISSING |
| 配对真实项目四容器 E2E | [result.json](evidence/e14-real/result.json) | profile=true 五阶段 SUCCEEDED，recheck 无 MISSING |
| H3 tiny-AES-c 五阶段 | [result.json](evidence/h3-tiny-aes/result.json) | 五阶段 SUCCEEDED，MISSING(helper.o, extra.h) 修复后 recheck 空 |
| Compose 健康与角色日志 | [services.log](evidence/e14-sample/services.log) | 四服务 healthy，日志含 role/job/trace/status/耗时 |
| 受控故障恢复核验 | 核验 B1 证据 | 超时失败、无残留、恢复 SUCCEEDED，两次任务标识不污染 |
| 运行日志 Secret 扫描 | 见下 | 408 个文本文件 0 hits / 0 errors |
| 候选发布说明 | [candidate-release.md](candidate-release.md) | 两轨 SHA、镜像、E13 门禁、CI、已知问题 |
| 回滚验证 | [rollback.md](rollback.md) | 复现命令、回退步骤、回退后验证、已知问题 |

## 环境

- 服务器：`root@47.97.103.111`（云机，paramiko 密码 SSH）
- 本地：Windows 11（git、文档整理与定向测试）
- 镜像：`course-e11e12:241880597`（image ID `98c22b63fa7e`）
- 四容器端口：`18181-18184`（避让 B1 正在运行的 `18081-18084`）

## 关键字段

- B 接收：来源 A2 报告 job `job-04e068ac15d547599a324dd56d1ee0f5` / trace `trace-d8277c2fbcb543c18448c79778c9c064`；target `7fabf45ec98fb1b7ffe101b3621272b93f0be4d5`；fixed-md SHA256 `1036c8955fe4bae6664a1bf88879113cc2be48b6d7cd358a0c20b70a505737af`。
- C7 B 侧：失败任务 job `job-2f34ced3761c46f5b6a66a3d66caaa18` / trace `trace-c9c219419a1c4a2d8dc15564127e8dcf`（超时，FAILED）；成功任务 job `job-e6c737fe87b0460689950c7f9cde39db` / trace `trace-2521e36143534fb2938e79ba6ef24097`（五阶段，SUCCEEDED，artifacts 196）。
- C8 幂等复核：`test_student_241880597_e13e14.py` 3 passed（Store 幂等/冲突 + HTTP 202/202/409），云机与本地均通过。
- 固定样例四容器 E2E：job `job-695e68fd67f04a22b6b2f01efa3adf13` / trace `trace-a3580ab57c5c484a9f3099ea7b1815b2`；base `91de1706f242b026882bfd9fc5da37926a209661`、target `33a335ff5269466022a1c5078c748cca640e8f7c`。
- 配对真实项目四容器 E2E：job `job-5afabf021a0a46ff8f19088c25c8a556` / trace `trace-11436bef785140c9bb56516b75c220db`；base `e9ce878b1e2c46bd7d86e463ff9115b2fc2e6158`、target `48b64156548b3fd8af1ed9ed25eee60d0f92371d`；候选镜像 `sha256:683694107f57eda5e7c84fe2416c61bd85a5a11d159c7c15f6124e5497407d2c`，验证输出 `2` 匹配。
- H3 tiny-AES-c：job `job-a5a567707aa748059d308ff7ff4e6c7f` / trace `trace-b7a3b182c65f454ead5128ade0027ef7`；base `dc8099306d7023b7337328d718149973e7b17978`、target `5640bb69a01e64559207e9f74d15a9ae71a4d0f3`；MISSING(helper.o, extra.h) → recheck 空；候选镜像 `sha256:ab14d2113ccf4b652651db281e8a960f844c200e3bf6b4fb2c4c7f2b09f19159`，验证输出 `1` 匹配。
- 日志扫描：`scan_runtime_logs.py` 扫描本轮证据与四服务日志，文本文件 408，0 hits / 0 errors，退出码 0。

## 证据命令

```bash
# 云机（47.97.103.111）上执行；详情见 cross-test-record.md、candidate-release.md、rollback.md 与 ADR.md
python3 labs/e13e14/handoff_a_to_b.py --a-result <a2-result.json> --target-sha 7fabf45ec98fb1b7ffe101b3621272b93f0be4d5 --out work/e13-b3-receive/fixed-md.json
python3 labs/e13e14/verify_c7_isolation.py --failed work/e13-c7-b3/failed --succeeded work/e13-c7-b3/success --out work/e13-c7-b3/c7-isolation-report.json
python3 labs/e13e14/orchestrate.py --request work/e14-b3-sample-01/request.json --out work/e14-b3-sample-01
python3 labs/e13e14/orchestrate.py --request work/e14-b3-real-request.json --out work/e14-b3-real-01
python3 run_e11e12.py run --request e13-upstream-student/H3-tiny-aes/h3-request.json --out work/h3-tiny-aes
python3 labs/e13e14/scan_runtime_logs.py work/
python3 -m unittest discover -s labs/e11e12 -p "test_student_241880597_e13e14.py" -v
```

## 未执行 / 阻断（见 [blockers.md](blockers.md)）

- RC 发布 `v0.9-rc`：需全组 C1-C8/H1-H3/日志扫描/远端必需 CI 全绿；BLOCK-3 云机访问 GitHub 不通，标签尚未打出，需在本地 Windows 完成 push + PR + CI。
- 全组 C1/C5/C6 未闭环前，不判定整组 E13/E14 验收通过。

本目录证据原件保留在云机 `/root/241880597/work/`（`e13-b3-receive`、`e13-c7-b3`、`e14-b3-sample-01`、`e14-b3-real-01`、`h3-tiny-aes`、`e14-b3-services.log`、`e14-b3-compose-ps.txt`），此处归档关键结果。
