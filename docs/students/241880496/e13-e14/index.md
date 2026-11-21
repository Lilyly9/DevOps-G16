# A2 E13-E14 个人交付索引（241880496）

- 姓名：万宇
- 学号：241880496
- 分支：`student/241880496/e11-e12`
- 角色：A2 / EChecker
- 阶段状态：A2 定向回归、tokenstat 实际 E11-A、A→B 报告导出以及 C2/C3/C8 服务器验证已完成。H1 完整 E12 已在隔离候选中补装 `strace` 后通过；E14 固定样例和 H1 jsmn 五阶段也已在本机 Docker 中通过，报告哈希、阶段关联和日志扫描均核验通过。跨组 C1-C8 全集、H2/H3、故障恢复及远端 CI/RC 仍未完成，因此不代表整组 E13/E14 验收通过。

## 本轮交付

| 项目 | 文件 | 结果 |
| --- | --- | --- |
| A→B 当次报告适配 | [handoff_a_to_b.py](../../../../labs/e13e14/handoff_a_to_b.py) | 已接入，校验任务、目标 SHA、job/trace、产物 URI、内容 SHA 和大小 |
| C2 旧报告 | [A2 定向测试](../../../../labs/e11e12/test_student_241880496_e13e14.py) | 定向回归通过 |
| C3 篡改报告哈希 | [pipeline.py](../../../../labs/e11e12/pipeline.py) 和 [A2 定向测试](../../../../labs/e11e12/test_student_241880496_e13e14.py) | 传入 `fixed_report_sha256` 后校验字节哈希，不匹配返回 `ARTIFACT_HASH_MISMATCH` |
| C8 幂等冲突 | [A2 定向测试](../../../../labs/e11e12/test_student_241880496_e13e14.py) | 相同键相同请求复用任务，不同 target 被拒绝 |
| 实际 E11-A 与报告交接 | [交接适配器](../../../../labs/e13e14/handoff_a_to_b.py) | tokenstat 实际 E11-A 成功；导出 `fixed-md`，SHA256 为 `1036c8955fe4bae6664a1bf88879113cc2be48b6d7cd358a0c20b70a505737af` |
| E14 固定样例与 H1 jsmn | [E14 Compose 与编排](../../../../labs/e13e14/) | 本机 Docker 上两次完整五阶段通过；EChecker 报告 SHA、每阶段 job/trace 与产物 SHA 均核验 |

## 验证

执行于本机 Windows 11，使用 `python`：

- `labs/e13e14/test_handoff.py`：3 passed
- `labs/e11e12/test_contract.py`：10 passed
- `labs/e11e12/test_student_241880496_e13e14.py`：4 passed

合计定向回归：17 passed。

## 服务器真实执行（2026-11-21）

- 服务器：`47.96.152.132`
- 服务器测试：`labs/e11e12/test_*.py` 共 22 项通过。
- tokenstat E11-A：job `job-04e068ac15d547599a324dd56d1ee0f5` / trace `trace-d8277c2fbcb543c18448c79778c9c064` 成功；base `74fd1f2a86ea4e345245e41011f300aa94ae56c1`、target `7fabf45ec98fb1b7ffe101b3621272b93f0be4d5`，检测到 `MISSING(stats.o, extra.h)`。A→B `fixed-md` 交接来源 job/trace 一致。
- C2：job `job-f96371c35b2a492383d8506254cc8840` 返回 `STALE_REPORT`，按预期拒绝旧提交报告。
- C3：job `job-58279c8b00bd41958a30b54d3470cb44` 返回 `ARTIFACT_HASH_MISMATCH`，按预期拒绝篡改报告。
- C8：相同键相同输入两次 HTTP 202，返回同一 job `job-f7acb6ac4fe040aa934409e586322e1e`；不同 target HTTP 409，响应 `{"error":"IDEMPOTENCY_CONFLICT"}`。
- H1 jsmn 完整 E12：job `job-070b682748c64331afa1d7815439098e` / trace `trace-d39a25f8bae5477d9e80b82ac444d4a3`，base `66a6dafcc20cea76bf017923d3db725d78407845`、target `948a1d30cd758d32d45a50f788e5a95fb1d89c69`，五阶段 `draft/full-check/incremental-check/repair/recheck` 全部成功；候选镜像 ID `sha256:b34e18e15363ef86412b81a3d8800c7bc922714cfd1146be857ef0e1ecec10da`。为满足 EChecker 的运行时依赖，在独立副本 `candidate-a2-strace.Dockerfile` 中增加 `strace`；原课程候选未覆盖。
- 本机 Docker：Docker Desktop 29.5.2，拉取固定样例基础镜像成功（`python:3.13-slim` digest `sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90`；候选固定 digest 亦成功）。Compose 使用本机已有 `course-e11e12:241880496`，镜像 ID `sha256:dfa861b49a79b11fc10b3c58e3991c1760e985b5c58febc22194fa13ca0f5b83`；四服务均 healthy，完成后只关闭本轮 Compose 项目。
- E14 固定样例：job `job-207b9359db854f218e24d5043f4e0f9b` / trace `trace-08a07b593b98405fb1b7f8801fca0433`，五阶段全部成功；EChecker 报告 SHA256 `85ef73f7acdceae87a41dedc622850ee5c2fba24bf7dbbc649a61133a5acd459`。
- E14 H1 jsmn：job `job-9031e40cbcff42f1a5415e1b8eb4efa9` / trace `trace-47090f511ec44967ad6c2fc64f088581`，五阶段全部成功；EChecker 报告 SHA256 `b64a6f02a8e284f43c4b3fe1b802a74ae3c257174c4eb09bd2b6bde48795aa55`，recheck 无 MISSING。两次 E14 的阶段包 SHA 与同一 job/trace 逐项核对通过。
- 日志扫描：E14 两次成功运行共扫描 332 个文本文件，0 hits / 0 errors。第一次本机 E14 尝试因 Windows Git 自动转换 CRLF 导致 patch 无法应用；仅在该次编排进程设置 `core.autocrlf=false` 后重跑通过，未改动原始项目提交。
- 原始服务器尝试和本机成功结果分别见 [服务器证据目录](evidence/server-2026-11-21/) 与 [成功运行证据目录](evidence/successful-runs-2026-11-21/)；也可下载[成功运行压缩包](evidence/successful-runs-2026-11-21.zip)。归档包含完整请求、阶段产物、日志和候选差异。

未执行或未代做：

- 与 B 组实际项目交换的 C1
- 本人主责之外的 C4-C7 真实注入
- 与 B 组配对项目交换的 C1 消费验收；本人主责之外的 C4-C7 全矩阵/独立复核
- H2/H3 的真实项目运行；E14 受控故障恢复、真实配对组项目 E2E、RC 发布
- GitHub 远端必需 CI

## 证据命令

```powershell
python -m py_compile labs/e13e14/handoff_a_to_b.py labs/e11e12/pipeline.py
python -m unittest discover -s labs/e13e14 -p "test_*.py" -v
python -m unittest discover -s labs/e11e12 -p "test_contract.py" -v
python -m unittest discover -s labs/e11e12 -p "test_student_241880496_e13e14.py" -v
```
