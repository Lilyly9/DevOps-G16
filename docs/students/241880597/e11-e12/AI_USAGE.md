# AI 使用记录

日期 2026-11-16，B3 吴佳静 / 241880597。使用 Claude Code 协助阅读 E11-12_TASKS.md、contracts/e11e12.md、共享代码（pipeline.py / server.py / report_exchange.py）与 A3/B1 交付，梳理 B3 消费侧职责边界，编写本人独立契约测试 test_student_241880597.py 及文档。未选择或调用模型 API 生成 Dockerfile 候选。

复用 A3 已合并的 report_exchange.download_report 实现与接口契约；B1 的 DRAFT/MDFixer 报告仅作角色边界参考，未改动其代码与测试。本人改动集中在消费侧拒绝测试与个人文档，不改共享 pipeline/server/report_exchange 源码。

AI 帮助设计「消费侧不信任生产方字节」的独立预期：以 mock 回放两段 HTTP 响应，逐点注入清单 schema/身份/类型、三处哈希、内层 commit 过期等篡改，断言对应拒绝码。采纳契约「原字节交接、三处 SHA 核验」的要求。没有把 A3 的 export 拒绝测试或真实 loopback 下载写成 B3 本人独立消费；云端 SSH 转发下载与交给 B2 修复入口的实际动作待云端运行后由本人记录，不代写。

用户给出 B3 角色与材料路径。当前没有用户逐行改代码或独立完成云端运行的证据，不代写人工修改/签字。用户应阅读本人 report/ADR，解释消费侧字段映射、拒绝分支与云端联调边界。实际云端运行与核验见 index.md 及双端归档。
