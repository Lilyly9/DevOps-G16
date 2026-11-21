# B2 实验与提交证据

李敏君 · `241880543` · `student/241880543/e11-e12`

[个人报告](个人报告.md) · [ADR](ADR.md) · [PR #26](https://github.com/Lilyly9/DevOps-G16/pull/26)

## 源码与契约测试

- B2 实现提交为 `5d22086`。验证使用运行器 `bd65f4e3672c03bce73389ceafcc99d681896ccc`，其中包含 A3 的测试发现修复 `bf81c94`（[PR #24](https://github.com/Lilyly9/DevOps-G16/pull/24)）。下文的 base 与 target 指被测项目的提交。
- 本机环境为 Ubuntu 22.04 WSL2，Python 3.10，使用 GNU Make、GCC 和 strace。环境版本、原始日志和退出码保存在仓库下 `work/b2-tests-241880543-20261116-1938/`。

| 实际命令 | 退出码 | 结论与原件 |
| --- | --- | --- |
| `python3 -m unittest discover -s labs/e11e12 -p 'test_*.py' -v` | 0 | 48 项通过，含 B2 三项。原件 `e11e12.log` 和 `e11e12.exit`。 |
| `python3 -m unittest discover -s labs/e8e10 -p 'test_*.py' -v` | 0 | 21 项通过，包含上一轮共享宏的既有契约。原件 `e8e10.log` 和 `e8e10.exit`。 |

## B2 本机 MDFixer 与动态重检

命令 `PYTHONPATH=labs/e11e12:labs/e8e10:labs/e11e12/vendor python3 work/b2-mdfixer-host.py data/b2-241880543-20261116-1945 work/b2-host-241880543-20261116-1948` 退出 `0`。运行使用真实 Make、GCC、Git 和 strace，报告、补丁、构建和重检产物见 `work/b2-host-241880543-20261116-1948/`。该次运行的执行环境是 Ubuntu 主机。

| 用例 | 被测 base / target | 实际结果 |
| --- | --- | --- |
| 固定 | `db5cdc945e5bb985980b2db46d4df45b5bd60c86` / `1a84ab873b39a74900fa6321679fa448384fd024` | 固定报告内外提交均匹配 target。补齐 `main.o` 的 `config.h` 和 `extra.h`，复验接受，重检仅余 `RD(main.o, unused.h)`。[结果](evidence/host/fixed/result.json) · [补丁](evidence/host/fixed/candidate.patch) |
| 共享 macro | `fa3f37f249f2708a5855a92549c0fd2b1d59141f` / `2bde2fe977570c979994ed8ae1f223e846a5d885` | 仅 `main.o: $(DEPS)` 改为 `main.o: $(DEPS) config.h extra.h`。对比 `helper.o` 展开依赖相同，复验接受，动态重检 0 条 MD。[结果](evidence/host/macro/result.json) · [补丁](evidence/host/macro/candidate.patch) |
| 旧报告 | 同上 | 独立报告外层为 target、内层为 base，返回 `STALE_REPORT`。目标 Makefile 未改动，补丁和验证目录未生成。[结果](evidence/host/stale/result.json) |
| transfer-eta | `5ef9d829e2f893af23f60399dcb67095800d121e` / `e7414083c4f1760cb234f96a9d75f2d0255e3f57` | `make test` 通过。修改头文件后，`./transfer-eta 100` 从 `eta_seconds=13` 变为 `eta_seconds=20`，补丁被接受，动态重检集合为空。[结果](evidence/host/transfer-eta/result.json) · [补丁](evidence/host/transfer-eta/candidate.patch) |

固定、共享 macro、旧报告三个输入的 SHA256 及外层、内层 commit 记录在各自的 `result.json`。环境、执行脚本、输入引用、`validation/build.log`、`validation/incremental.log`、`final-full/findings.json` 和原始 strace 保存在 `work/b2-host-241880543-20261116-1948.zip`，归档 SHA256 为 `4ec9b1574b8854578fca8922732f15abd6dd9c891ed373f8af29e54037dd07a8`。

本机的首次 Docker 运行 `python3 docs/students/241880543/e11-e12/run_evidence.py --backend native --out work/b2-241880543-20261116-1945` 在固定样例的 DRAFT 首轮拉取镜像层时连接 Docker CDN 超时。该用例退出 `1`，DRAFT 分类为 `INFRASTRUCTURE`，日志原件在 `fixed/draft-build/iter-01/build-stderr.log`。该次失败没有复现 `MISSING_MAKE`。

## B2 独立 Docker 与 API 复验

为完成实际容器复验，在 B2 个人分支的 Ubuntu 24.04 GitHub runner 上构建个人镜像 `course-e11e12:241880543`，并执行 `python3 docs/students/241880543/e11-e12/run_evidence.py --out work/b2-personal`。运行器源提交为 `012c7423f49459af3b0b90bdda57d0d02c35af13`，脚本退出 `0`。四组正例各自成功，隔离的旧报告用例按预期退出 `1`。独立流程已从 PR 的最终 diff 移除。[B2 实际 Docker 运行](https://github.com/Lilyly9/DevOps-G16/actions/runs/43861390605)

| 个人用例 | job / trace | 验收结果 |
| --- | --- | --- |
| E11-B 固定 | `job-379da593c6d74ef08f1380e8fe4b0526` / `trace-fc5ac2fdc00c4b24bb91dd261bdd8018` | 首轮 `MISSING_MAKE`，候选镜像实际运行输出 `1`。固定报告内外 commit 匹配 target。补丁与重检通过，仅余 `RD(main.o, unused.h)`。[补丁](evidence/docker/fixed/candidate.patch) · [计划](evidence/docker/fixed/repair-plan.json) |
| E11-B 共享 macro | `job-2712fbecc37848748881ce9c9dee4713` / `trace-fe072442902446deb4ed1d9858727ff9` | 候选镜像实际运行输出 `1`。补丁只改 `main.o` 规则，两个 edit 均为 `mixed`。`accepted=true`，动态重检 0 条 MD。[补丁](evidence/docker/macro/candidate.patch) · [计划](evidence/docker/macro/repair-plan.json) |
| E11-B 旧报告 | `job-170b992e85184f95a1325421f086a1a6` / `trace-a7a5b5801ae246d38f59a5b3ec52eff4` | 只保留 `draft` 阶段，`STALE_REPORT`，无补丁、计划和验证目录。 |
| E12 固定 CLI | `job-ebf3fd554fa649c193aef2bd3a1d5188` / `trace-cadf1aa3b88f492584c24a37fdacaae1` | 五阶段标识一致。修复引用本轮增量报告 SHA256。8 条验证命令和最终动态构建在 DRAFT 镜像中退出 `0`，重检仅余 RD。 |
| E12 transfer-eta CLI | `job-37fc6a2a89f04578b4fa17fe0295bf47` / `trace-7675e2efe97e4b37936c72fc2ac9ebd8` | 修复 `MD(eta_cli.o, defaults.h)`。9 条验证命令和最终动态构建在 DRAFT 镜像 `sha256:53f343a6e159cc5847e2b196c064213b095589a2a136abd2e2798a8b9a1edd1a` 中退出 `0`。输出从 `eta_seconds=13` 变为 `eta_seconds=20`，`accepted=true`，重检为空。[补丁](evidence/docker/transfer-eta/candidate.patch) · [验证](evidence/docker/transfer-eta/validation.json) |

CLI 每次的完整 base/target、报告 URI/SHA256、镜像 ID 和结论记录在[个人 Docker 摘要](evidence/docker/summary.json)。HTTP 配套运行使用 `python3 run_e11e12.py serve --port 18086` 及 `labs/e11e12/api_probe.py`。固定任务为 `job-f297048b14104603bfcf0bcbd2eabba9` / `trace-b4277ee68af541fa9fa3e4d3aab3d5c8`，真实项目任务为 `job-a0c401338e314e408c0a51852dea0d51` / `trace-7404e32b70414a0aae9b54e071c4faf8`。两次均重新下载六份原件，核对报告清单、响应头、文件与修复记录的 SHA256。同键重放返回同一 job，改 target 返回 `409`。A3 执行的共享云端任务另见[个人报告](个人报告.md)。

原件下载到 `work/b2-docker-241880543-43861390605/`。归档 `14223278359.zip` SHA256 为 `4c3d880bef4f728d815673c40bca94721787d1867a243054608b00ba665b6609`，`logs.zip` SHA256 为 `83fd7b7560e41208fb585b192d6e1cdabcfad81eea8fb8228c2f79db81e5c8a1`。归档的 `work/b2-personal/<用例>/` 保存 `result.json`、DRAFT 两轮构建日志以及各正例的 `repair.json` 和 `final-full/`。E12 的实际镜像执行记录位于 `validation/execution/`，HTTP 请求、轮询、下载与哈希核验位于 `work/b2-personal/api-*`。[Docker 与 API 原始产物](https://github.com/Lilyly9/DevOps-G16/actions/runs/43861390605/artifacts/14223278359)

## GitHub Actions 公共回归

- PR 事件运行 `43859823876` 对应源提交 `bd65f4e3672c03bce73389ceafcc99d681896ccc`，CI 实际检出合并提交 `c1b4a34e4b0d4b4bc7558438a35b01b8163e7fa8`。`e11e12-integration` 成功，48 项契约通过，固定样例 CLI 和在线 E12 API 报告交接通过。[E11–E12 Actions](https://github.com/Lilyly9/DevOps-G16/actions/runs/43859823876)
- 同一 PR 提交的 E7 A、E7 B 和 E8–E10 三项检查均成功。[E7 A](https://github.com/Lilyly9/DevOps-G16/actions/runs/43859823797) · [E7 B](https://github.com/Lilyly9/DevOps-G16/actions/runs/43859823802) · [E8–E10](https://github.com/Lilyly9/DevOps-G16/actions/runs/43859823964)
- Artifact `e11e12-evidence-43859823876`（ID `14222503513`）及构建日志已下载到 `work/b2-ci-241880543-43859823876/`。归档 `14222503513.zip` 的 SHA256 为 `5173d8cae10e82d7b5a62aeb1454965db8315c42996128198dcd5583589dd4ac`，`logs.zip` 的 SHA256 为 `f89d6d988af8eca45194f1e7eeadd5ce4cee464dbb7adf68dd03f2bac8ab9928`。[CI 产物](https://github.com/Lilyly9/DevOps-G16/actions/runs/43859823876/artifacts/14222503513)

| CI 运行 | job / trace | 归档相对路径 |
| --- | --- | --- |
| 固定 E11-B | `job-a37844fc9afc4e4b8eb04040f19cf01a` / `trace-67bdf0b903ea4bfcbf9546331e1fb437` | `ci-e11-b/{result.json,draft-build/,candidate.patch,repair-plan.json,validation/,final-full/}` |
| 固定 E12 CLI | `job-fe1fda6a749d4b6ea6f86a2a666ca336` / `trace-89d817129eec428a9c4dbfec0c399dbf` | `ci-e12/{incremental-check.json,repair.json,recheck.json,validation/execution/}` |
| 固定 E12 API | `job-c4d2c8a4b5124a9a8a6a4cbf3d38eeea` / `trace-37df6b1466f5413ab1308c4e5f758f58` | `ci-api-e12/{result.json,downloads/,report-transfer/,verification.json}` |

CI 固定样例的 base 为 `bbf8068386d9c33131a48a621f49297c01ec7e0d`，target 为 `811f08aa765e75adc12b6b8a5884e4431b1eb606`。A3 的云端固定与真实项目任务及 B2 离线复核见[个人报告](个人报告.md)。
