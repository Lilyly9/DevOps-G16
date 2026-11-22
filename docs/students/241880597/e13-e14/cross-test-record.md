# E13-E14 交叉测试记录（B3 维护 · 241880597）

> 本表为 B3 主责的交叉测试记录与阻断 Issue 清单汇总。所有「通过」必须由本人实际运行留证，不代他人填写。B3 本人执行项标 `[B3]`，复核项标 `[B3 复核]`；他人状态仅记录已知提交/证据，不代表 B3 验收。

## 交换项目与报告

| 项目 | 提供人 | 执行/复核 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| A 项目（tokenstat） | A1/A2 | A2 导出，B3 接收 | 已交接 | B 接收 fixed-md `1036c895...` 与 A2 一致 |
| B 项目（data/e13-b-project） | B1 郭德林 241880555 | B1 提供，B3 消费 | 已就绪 | `repo.bundle` + `candidate.Dockerfile` + `exchange.json` |

## C1-C8 状态

| 编号 | 内容 | 主责 | 执行人 | 状态 | B3 复核 | 证据/结论 |
| --- | --- | --- | --- | --- | --- | --- |
| C1 | 正常链路 | A1 供项目，B2 修，B3 汇总 | A1/B2 | 未闭环 | 待汇总 | A1 分支 `student/241880485/e13-e14` 未合并；B2 未开始 |
| C2 | 旧报告/错误目标 | A2 | A2 | 已执行 | — | `STALE_REPORT`（A2 index） |
| C3 | 篡改产物哈希 | A2、A3 | A2 | 已执行 | — | `ARTIFACT_HASH_MISMATCH`（A2 index） |
| C4 | 超时 | B1 | B1 | 已执行 | `[B3 复核]` 通过 | 超时失败、无残留、恢复 SUCCEEDED |
| C5 | 错误补丁回滚 | B2 | B2 | 未开始 | — | 待 B2 |
| C6 | 假 Key 与日志扫描 | A3 | A3 | 未开始 | 待复核 | 待 A3 |
| C7 | 任务失败隔离 | A1 和 B3 各一端 | B3 | B 侧已执行 | `[B3]` | 见下，PASS 404 checks |
| C8 | 幂等冲突 | A2 | A2 | 已执行 | — | 相同请求同 job，不同 target HTTP 409 `IDEMPOTENCY_CONFLICT` |

### C7 B 侧详情

- 失败任务（超时）：job `job-2f34ced3761c46f5b6a66a3d66caaa18` / trace `trace-c9c219419a1c4a2d8dc15564127e8dcf`，status `FAILED`。
- 成功任务（五阶段）：job `job-e6c737fe87b0460689950c7f9cde39db` / trace `trace-2521e36143534fb2938e79ba6ef24097`，status `SUCCEEDED`，artifacts 196。
- `verify_c7_isolation.py`：status `PASS`，404 项检查通过（失败状态、成功状态、job/trace 互不相同、产物 URI/SHA、字节数、退出码等），确认失败任务未污染成功任务。

## H1-H3 未知三项目

| 项目 | 主执行 | 复核 | 状态 | 说明 |
| --- | --- | --- | --- | --- |
| H1 jsmn | A2 + B2 | A1、B1 | A2 已执行 | A2 index：隔离候选补装 `strace` 后五阶段通过 |
| H2 inih | A1 + B1 | A3、B3 | B1 已执行 | 见 B1 报告；`[B3 复核]` 待 B1 证据归档 |
| H3 tiny-AES-c | A3 + B3 | A2、B2 | 未执行 | 输入包 `e13-upstream-student.zip` 缺失 |

## 阻断 Issue 清单

见 [blockers.md](blockers.md)。

## 结论

- B3 本人可独立审查的完成项：B 接收、C7 B 侧、C4 复核、固定样例四容器 E2E、受控故障恢复核验、日志扫描。
- 阻断项：真实项目四容器 E2E（profile 硬编码）、H3（输入包缺失）、RC 发布与远端 CI（全组门禁未绿 + 云机网络）。
- 不声明整组 E13/E14 验收通过。
