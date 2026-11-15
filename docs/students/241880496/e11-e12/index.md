# E11—E12 证据索引（A2 / 241880496）

源码提交：`7fabf45ec98fb1b7ffe101b3621272b93f0be4d5`（分支 `student/241880496/e11-e12`）。
运行环境：Docker Desktop 29.5.2 / linux-amd64；编排在 WSL2 Ubuntu 内执行；服务镜像 `course-e11e12:241880496` = `sha256:dfa861b4…`。详见 [environment.txt](evidence/logs/environment.txt)。

## 1. 输入

| 文件 | 内容 |
| --- | --- |
| [e11a-standard-request.json](evidence/inputs/e11a-standard-request.json) | 固定样例 E11-A 请求（base `199580a4…` / target `473af31e…`） |
| [e11a-tokenstat-request.json](evidence/inputs/e11a-tokenstat-request.json) | 自主项目请求（base `74fd1f2a…` / target `7fabf45e…`，`project_path=projects/tokenstat`） |
| [e12-standard-request.json](evidence/inputs/e12-standard-request.json) | 固定样例 E12 容器内请求（`/course/data/...` 路径） |
| [e12-tokenstat-request.json](evidence/inputs/e12-tokenstat-request.json) | 真实项目 E12 请求（`projects/tokenstat`） |
| [standard-dataset.json](evidence/inputs/standard-dataset.json) | 固定样例生成信息、base/target SHA、候选来源 |
| [standard-history.txt](evidence/inputs/standard-history.txt) | 固定样例内部 Git 历史 |
| [tokenstat-base-target.diff](evidence/inputs/tokenstat-base-target.diff) | 真实项目 base→target 完整差异 |
| [tokenstat-base-target-stat.txt](evidence/inputs/tokenstat-base-target-stat.txt) | 真实项目差异统计 |

## 2. E11-A

| 文件 | 用途 |
| --- | --- |
| [e11a-standard/result.json](evidence/e11a-standard/result.json) | 固定样例整体结果、job/trace、base/target |
| [e11a-standard/incremental-report.json](evidence/e11a-standard/incremental-report.json) | 目标增量扫描：`main.o` 刷新、`helper.o` 复用、新增 `MD(main.o, extra.h)` |
| [e11a-standard/incremental-check.json](evidence/e11a-standard/incremental-check.json) | 带 commit / 产物 URI / SHA256 的阶段信封 |
| [e11a-standard/baseline-cache.json](evidence/e11a-standard/baseline-cache.json) | 真实图投影后的基线缓存 |
| [e11a-standard/cache-edge-provenance.json](evidence/e11a-standard/cache-edge-provenance.json) | `main.o → config.h` 回查 `t.9028:594` |
| [e11a-standard/target-full-findings.json](evidence/e11a-standard/target-full-findings.json) | 目标全量发现，用于完整集合对照 |
| [e11a-standard/baseline-actual-graph.json](evidence/e11a-standard/baseline-actual-graph.json) / [target](evidence/e11a-standard/target-actual-graph.json) | 真实 BuildChecker 图 |
| [e11a-tokenstat/incremental-report.json](evidence/e11a-tokenstat/incremental-report.json) | 自主项目：`stats.o` 刷新、`main.o` 复用、新增 `MD(stats.o, extra.h)` |
| [e11a-tokenstat/cache-edge-provenance.json](evidence/e11a-tokenstat/cache-edge-provenance.json) | `stats.o → config.h` 回查 `t.9105:692` |
| [e11a-tokenstat/target-full-findings.json](evidence/e11a-tokenstat/target-full-findings.json) | 自主项目全量对照 |

## 3. E12 五阶段

| 文件 | 用途 |
| --- | --- |
| [e12-standard/result.json](evidence/e12-standard/result.json) | 固定样例五阶段、同一 job/trace、`image_id` |
| [e12-standard/draft.json](evidence/e12-standard/draft.json) | DRAFT 首轮 `MISSING_MAKE`、次轮构建与运行输出 |
| [e12-standard/draft-build-result.json](evidence/e12-standard/draft-build-result.json) | 两轮构建日志、`image_id`、验证输出 |
| [e12-standard/baseline-scan/](evidence/e12-standard/baseline-scan) | DRAFT 镜像内基线扫描命令与退出码 |
| [e12-standard/target-scan/](evidence/e12-standard/target-scan) | DRAFT 镜像内目标扫描命令与退出码 |
| [e12-standard/incremental-check.json](evidence/e12-standard/incremental-check.json) | 增量阶段信封（commit、镜像、产物） |
| [e12-standard/repair.json](evidence/e12-standard/repair.json) | `data.input_report` 指向本轮报告 |
| [e12-standard/candidate.patch](evidence/e12-standard/candidate.patch) | 最小补丁 |
| [e12-standard/validation.json](evidence/e12-standard/validation.json) | 补丁验证 `accepted=true` |
| [e12-standard/recheck.json](evidence/e12-standard/recheck.json) | 最终重检无 MD |
| [e12-standard/final-full-findings.json](evidence/e12-standard/final-full-findings.json) | 最终全量发现 |
| [e12-tokenstat/result.json](evidence/e12-tokenstat/result.json) | 真实项目五阶段 |
| [e12-tokenstat/draft-build-result.json](evidence/e12-tokenstat/draft-build-result.json) | 真实项目 DRAFT 两轮构建与输出 |
| [e12-tokenstat/target-scan/](evidence/e12-tokenstat/target-scan) | 真实项目镜像内扫描 |
| [e12-tokenstat/validation.json](evidence/e12-tokenstat/validation.json) | `config=1…` → 改头文件 `config=2…` |
| [e12-tokenstat/candidate.patch](evidence/e12-tokenstat/candidate.patch) | `stats.o` 补 `config.h extra.h` |
| [e12-tokenstat/recheck.json](evidence/e12-tokenstat/recheck.json) | 真实项目最终重检 |

## 4. 共享 API

| 文件 | 用途 |
| --- | --- |
| [api/submit.json](evidence/api/submit.json) | `POST /v1/jobs` 返回 202 与 job |
| [api/poll.json](evidence/api/poll.json) | 轮询状态序列至 `SUCCEEDED` |
| [api/result.json](evidence/api/result.json) | 五阶段、同一 job/trace、镜像 ID |
| [api/incremental-check.json](evidence/api/incremental-check.json) | 下载得到的增量报告 |
| [api/repair.json](evidence/api/repair.json) | 下载得到的修复阶段 |
| [api/recheck.json](evidence/api/recheck.json) | 下载得到的最终重检 |
| [api/candidate.patch](evidence/api/candidate.patch) | 下载得到的补丁 |
| [api/validation/validation.json](evidence/api/validation/validation.json) | 下载得到的验证结果 |
| [api/download-checks.json](evidence/api/download-checks.json) | 清单 / 文件 SHA256 / `X-Content-SHA256` 三处一致 |
| [api/idempotency.json](evidence/api/idempotency.json) | 同键同输入同任务；同键改 target → 409 |

## 5. 日志与复现

| 文件 | 用途 |
| --- | --- |
| [unit-tests.log](evidence/logs/unit-tests.log) | `Ran 18 tests ... OK` |
| [environment.txt](evidence/logs/environment.txt) | 系统、工具链、runner 镜像 ID |
| [source-sha.txt](evidence/logs/source-sha.txt) | 源码提交与最近提交 |
| [run-commands.md](evidence/logs/run-commands.md) | 实际命令、OUT 与退出码 |

### 复现命令（在 Linux/WSL 主机，仓库根目录）

```bash
export PATH=/tmp/strace-bin:$PATH
export PYTHONPATH=labs/e11e12:labs/e8e10:labs/e11e12/vendor:labs/e11e12/environment/services/buildchecker
python3 labs/e11e12/prepare.py
python3 labs/e11e12/pipeline.py --request data/integration-sample/e11-a.json --out work/<new-e11a>
python3 labs/e11e12/pipeline.py --request data/e11a-tokenstat.json --out work/<new-autonomous>
```

E12 在服务容器内运行（需要 Docker socket 和宿主仓库路径）：

```bash
docker run --rm --network bridge --group-add <docker-gid> \
  -v /var/run/docker.sock:/var/run/docker.sock --cap-add SYS_PTRACE \
  -e PYTHONPATH=/course/labs/e11e12:/course/labs/e8e10:/course/labs/e11e12/vendor:/app \
  -e E11E12_DOCKER_HOST_ROOT=<host-repo-path> \
  -v <host-repo-path>:/course -w /course course-e11e12:241880496 \
  python3 labs/e11e12/pipeline.py --request data/integration-sample/e12-container.json --out work/<new-e12>
```

API：同一镜像启动 `labs/e11e12/server.py --host 0.0.0.0` 并映射 `127.0.0.1:18080:8080`，再按 [api/submit.json](evidence/api/submit.json) 的输入提交。
