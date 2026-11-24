# AI 使用记录（E13–E14，A1 焦龙 241880485）

## 1. 总体原则

AI 用于**起草、比对、排错建议与文档整理**；所有“通过/失败”结论都来自本人在 A16 云机、本机或 GitHub Actions 上的实际执行输出。凡未实际运行的项目一律写“未执行/阻断”，未用 AI 生成任何日志、哈希或 job/trace。

## 2. 使用明细

| 场景 | AI 参与 | 本人动作 | 验证方式 |
| --- | --- | --- | --- |
| 开工核验 | 建议“先 fetch 再判断远程”，提示检查 `pushed_at` | 执行 `git fetch`、比对 `origin/main`、发现 PR #25/#28 与两个新分支 | `git rev-parse`、`ls-remote`、GitHub API |
| 课程资料核对 | 建议按名称在全工作区检索缺失输入 | 执行检索，确认 H1–H3 与运行指南 0 命中 | 递归文件名检索 |
| C7 校验器 | 起草实现与测试用例骨架 | 修正 `stages[]` 结构假设；在真实两份 `result.json` 上跑出 `C7_ISOLATION=PASS` | 本地 18 项单测、服务器 482 项检查 |
| C6 扫描器测试 | 建议假 Key 用运行时拼接，避免命中仓库扫描 | 采纳并补测试 | `secret_scan.py .` 退出码 0 |
| CI 工作流 | 建议把 compose 校验、四容器、C7、日志扫描串成一个作业 | 按仓库实际路径改写（`labs/e13e14` 测试在目录根、扫描器在 `labs/e11e12/environment/scripts`） | 3 轮真实 CI：`44971776247` 失败 → `1a824ff` → `980e1a5` 全绿 |
| Docker Hub 不可达 | 提出“同 digest 换镜像前缀”“apt 换清华源” | 实测 daocloud pull（镜像 ID 与 digest 一致）、实测清华可达后落地 | `docker image inspect`、构建日志 |
| SSH 断连 | 建议改后台运行 + 哨兵文件 | 编写 `setsid` 启动脚本并轮询 | `e13e14-a1-e14.done` 与日志 |
| 文档 | 起草报告/ADR/证据索引结构 | 填入全部实测数值，逐项核对 job/trace/SHA | 与 `evidence/` 中 JSON 对照 |

## 3. AI 建议被否决或修正的地方

- AI 初版 C7 校验器假设 `stages[]` 带 job/trace，与仓库实际输出不符 → 改为按产物 URI 归属校验。
- AI 建议在 compose 的 `x-common` 里加 `safe.directory` → 实际会被各服务的 `environment` 覆盖，改在 `service.py` 内设置。
- AI 建议用 `pkill -f` 清理进程 → 首次调用匹配到自身 shell，导致启动失败；改为“上传脚本再 `bash <path>`”。
- AI 一度建议改 `prepare.py` 生成适配版固定样例 → 否决，改为另建 `data/e13-mirror`，保留教师原始样例不被修改。

## 4. 未使用 AI 的部分

- 所有真实运行、退出码、job_id/trace_id、SHA-256 均来自机器输出。
- 教师隐藏测试、H1–H3：没有输入，未生成任何“预期结果”。
- 未生成或推测任何他人（A2/A3/B1/B2/B3）的运行结论；队友成果仅按仓库提交与 PR 引用。
