# 本轮续验：2026-11-22

已保留原始改动及 stash，从最新 `origin/main`（`28c94de`）建立 `student/241880543/e13-e14`。以下为本轮实际结果，下方旧记录保留历史状态，不代表当前结论。

| 检查 | 结论 | 证据 |
| --- | --- | --- |
| E11/E12 全量 | 75 项通过，退出 0 | [Linux 日志](evidence/linux-full-tests-confirmed.log)，包含 B2 10 项契约 |
| E13/E14 报告交接 | 3 项通过，退出 0 | [日志](evidence/linux-handoff-tests-confirmed.log) |
| E8/E10 回归 | 21 项通过，退出 0 | [日志](evidence/linux-lab-tests-final.log)；首次模块路径冲突记录保留 |
| 真实 DRAFT | 通过 | [结果](evidence/draft-build-summary.json)、[原始日志及 Dockerfile](evidence/draft-build.zip)，首次缺 make、第二次成功且运行输出匹配 |
| C5 真实容器验证 | 三条路径通过 | [摘要](evidence/docker-c5-summary.json)、[原始证据](evidence/docker-c5.zip)：损坏补丁拒绝，语义错误补丁可构建但因依赖错误拒绝并回滚，正确补丁接受且 strace 最终复验无 MISSING |
| H1 / H3 / C1 对手项目 | 未完成，不申报通过 | main 有他人 H1 历史归档，但未取得本轮可复跑原始 Git 项目、H3 和对手输入，不计为本人运行 |
| E14 四容器 | 未通过 | 镜像构建尝试见 `evidence/e14-image-*.log`，尚无本轮四容器成功证据 |
| 远端发布 / CI | 待实际确认 | 只以 GitHub 实际结果为准 |

本轮 C5 使用 DRAFT 实际构建镜像 `sha256:1542170ad4477d3b2b3c48e6fa6abb75aac1a2c464e3ccf31308aaebd65eddda`，保存每次容器命令、镜像检查和文件摘要。原始目录：`work/e13-241880543-draft-20261122-01/`、`work/e13-241880543-c5-docker-20261122-04/`。前三次 C5 尝试遇到 WSL Git 所有权限制；最终使用仅本进程的 safe.directory 配置成功，未修改全局配置。

本轮清单见 [verification-current.json](evidence/verification-current.json)。旧 `verification.json` 与 Windows 日志均为同步 main 之前的历史证据，予以保留。

---

# E13–E14 B2 个人记录（历史记录及本轮续验）

李敏君 · 241880543 · MDFixer · 2026-11-22

本轮已完成本地回滚修复、10 项 B2 契约及 Git 错误补丁拒绝留证。当前分支仍为 `student/241880543/e11-e12`；当前会话禁止源仓库 `.git` 写入和终端联网，尚未创建个人 E13–E14 分支、push 或 PR。本轮不能标记为全部验收通过。

[个人报告](REPORT.md) · [ADR](ADR.md) · [PR 草稿](PR_BODY.md) · [留证入口](run_evidence.py)

| 交付 / 检查 | 当前结论 | 证据与范围 |
| --- | --- | --- |
| C5 回滚实现 | 本地完成 | `pipeline.validate_repair()` 对验证拒绝、重检异常、重检仍有 MD 恢复原 Makefile，并保存 `rollback.json`。 |
| B2 独立契约 | 10 项通过 | [测试日志](evidence/contract-tests.log)。重检、容器异常和成功路径使用明确注入的测试替身。 |
| 相关公共回归 | 21 项通过 | 同一日志中的公共报告契约、项目配置、A2 EChecker 测试；使用 CLion GCC 13.1.0。 |
| C5 实际 Git 拒绝 | 通过此子项 | [运行摘要](evidence/local/summary.json)、[错误补丁](evidence/local/malformed/candidate.patch)、[验证](evidence/local/malformed/validation.json)、[回滚](evidence/local/malformed/rollback.json)。实际调用 Git，未运行 Docker 或编译。 |
| C5 语义错误补丁、真实构建及最终动态复验 | 待运行 | 同一留证入口支持 `--draft-result`，需 Linux、Docker 和 DRAFT 构建结果。 |
| H1 jsmn 与 H3 复核 | 待运行 | 当前未取得教师项目包及本轮完整请求、SHA、原始报告。 |
| E14 MDFixer 四容器联调 | 待运行 | 需本轮共享四容器入口、E13 门禁和实际项目。孤立契约不能替代 E14 验收。 |
| 个人分支、Issue、push、PR、远端 CI | 阻断 | 终端联网被拒绝，源仓库 `.git/FETCH_HEAD` 写入被拒绝。PR 正文已准备；没有远端提交或新 PR。 |

源码起点、实现文件 SHA256、平台和测试命令见 [验证清单](evidence/verification.json)。修改尚未提交，复现时应同时核对文件哈希，不能只引用起点提交。

本轮原始 Git 留证目录为 `work/e13-241880543-c5-local-20261122-03/`；必要小件归档于 `evidence/local/`。前两次 OUT 予以保留：第一次受 Windows 默认编码影响失败；第二次开启 `PYTHONUTF8=1` 后通过；最终第三次针对当前实现重新生成证据。没有覆盖旧 OUT。

使用已有 GCC 13.1 后，最新全量测试共 58 项：1 failure、7 errors、1 skipped，退出码 1；[完整日志](evidence/full-tests.log)已保留。剩余原因包括终端连本机 HTTP 均被禁止、Git/MSYS 在受限进程中无法启动及 B1 的 Linux 平台检查。31 项相关测试通过；未改动他人的测试，也未将全量检查写成绿色。

## 旧记录的复跑入口

Windows 本地检查（从仓库根目录执行）：

```powershell
$env:PYTHONUTF8 = '1'
$env:PYTHONPATH = 'labs/e11e12;labs/e8e10;labs/e11e12/vendor'
python -m unittest discover -s labs/e11e12 -p test_student_241880543_e13e14.py -v
python docs/students/241880543/e13-e14/run_evidence.py --out work/e13-241880543-c5-new
```

Linux 在本轮 DRAFT 已成功构建之后，用其 `draft-build/result.json` 执行容器复验：

```bash
python3 docs/students/241880543/e13-e14/run_evidence.py \
  --out work/e13-241880543-c5-docker-new \
  --draft-result work/本轮成功任务/draft-build/result.json
```

后一命令目前未执行。入口将记录 DRAFT 结果文件 SHA256 和不可变镜像 ID，分别执行损坏补丁拒绝、可应用但遗漏真实依赖的补丁拒绝、正确补丁接受及真实 strace 重检。使用 `DraftExecutor` 检查实际容器镜像并保存命令记录。它只覆盖隔离 MDFixer C5，不代表四服务部署或对手项目交叉验收。

权限恢复后，应先 fetch 并与最新 `main` 对齐，在 `student/241880543/e13-e14` 提交本人的改动，再完成 Issue / push / PR 和远端检查；不能将当前未提交代码视作已发布版本。
