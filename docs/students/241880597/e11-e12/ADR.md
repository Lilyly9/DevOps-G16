# ADR-001：消费侧不信任生产方字节，独立校验下载拒绝路径

编号、日期、作者：ADR-001 / 2026-11-16 / B3 吴佳静（241880597）

## 问题

E12 里 B3 作为 B 侧独立消费方，要从 A3 维护的 API 宿主经 SSH 转发取得增量检查报告，核对后交给 B2 修复入口。A3 的 `test_student_241880464.py` 已覆盖生产方（`export_report`）的拒绝与下载 happy path，但消费方自己下载时的校验路径——交接清单 schema/身份/类型、三处哈希、内层 commit——没有独立覆盖。消费方若默认信任生产方字节，任何中间人篡改、传输错误或过期报告都可能被接受并进入修复。

## 候选方案

1. 复用 A3 的真实 loopback server 起服务测消费——依赖 A 侧环境与真实 task 产物，且真实 server 自带正确哈希，无法模拟「清单与字节不一致」这类篡改场景。
2. 不新增测试，直接信任共享 `download_report`——无法证明消费侧校验有效，B3 无独立可审查贡献。
3. 用 `unittest.mock` 回放 `download_report` 的两段 HTTP 响应（交接清单 + 增量封装字节），逐点注入篡改，断言每个拒绝分支的错误码。

## 采用方案与原因

方案 3。理由：契约（`contracts/e11e12.md`）要求「B3 从另一端取得清单，核对三处哈希、外层 commit 与 data.commit」；这些校验发生在消费方下载时，mock 是唯一能精确注入每个篡改点的可控方式，也不依赖 docker socket 或 A 侧 server，CI 可直接跑。测试只回放共享 `report_exchange.download_report` 已实现的逻辑，不修改共享代码，符合任务表「B3 优先在独立模块实现消费逻辑」的边界——独立体现在测试文件与消费侧校验视角，而非重写 A 侧共享入口。

## 输入输出字段

- 输入（交接清单 `e11e12-transfer-1`）：`schema_version`、`kind`、`job_id`、`trace_id`、`commit`、`report{uri,sha256,bytes}`、`download_path`。
- 输入（增量封装 `e11e12-1`）：`schema_version`、`kind`、`status`、`commit`、`job_id`、`trace_id`、`data{commit,findings}`。
- 输出（消费校验结论）：`manifest.report.sha256`、响应头 `X-Content-SHA256`、实际字节 sha256 三处一致 + 字节大小一致；外层 `commit` 与内层 `data.commit` 均为 target；`job_id`/`trace_id` 与清单一致；通过后保存 `verification.json`（passed/sha256/uri）并把原始字节交给 B2。
- 拒绝码：`OUTPUT_EXISTS` / `SCHEMA_MISMATCH` / `REPORT_IDENTITY_MISMATCH` / `ARTIFACT_TYPE_MISMATCH` / `ARTIFACT_HASH_MISMATCH` / `STALE_REPORT`。

## 兼容性与测试

- 未改 `report_exchange.py` / `server.py` / `pipeline.py` 共享代码，其他成员无感知。
- `test_student_241880597.py` 13 用例本地全绿；与 `test_contract.py` 合并 23 用例通过。
- 云端仍以真实 SSH 转发下载 + `report_exchange.py --job/--target` 独立消费留证（见 index.md）；mock 测试只覆盖消费侧校验逻辑，不替代真实联调。
