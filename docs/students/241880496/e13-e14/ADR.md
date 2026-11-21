# ADR：A2 的 E13 报告交接与哈希校验

- 状态：已实施
- 决策：A2 保留增量报告的原始结构，新增独立 `handoff_a_to_b.py` 转换为 B 可消费的 `fixed-md`；传输双方同时保存报告 SHA。
- 原因：旧版 E11-A 输出和旧版 E11-B 输入接口不一致，且字节级哈希校验是 C3 的必需判据。
- 校验：交接脚本核对目标 SHA、schema、status、job/trace、阶段 artifact 和内部产物；E11-B/E12 在读取固定报告前校验 `fixed_report_sha256`。
- 不做：不在本轮声称真实跨组 C1-C8 或 H1-H3 已通过；不代做 C4-C7 的实际注入。
