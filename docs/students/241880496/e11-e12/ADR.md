# ADR-001：E12 项目配置、逐目标复用与同镜像执行

- 编号：ADR-001
- 日期：2026-11-15
- 作者：A2 / 万宇 / 241880496
- 状态：已采纳
- 相关：E11-A EChecker、E12 A 侧检测与报告交接
- 输入输出字段：`e11e12-project.json`（targets/commands/program/header_change）→ `incremental-report.json`（commit/actual/declared/findings/refreshed/reused）→ `incremental-check.json`（schema_version/job_id/trace_id/kind/commit/data/artifacts）
- 兼容性与测试：无配置时保留 `main.c/helper.c/config.h` 固定契约；`Ran 18 tests ... OK`；CI run 43683416564 success

## 问题

课程参考实现把对象目标 `main.o/helper.o`、程序 `./app`、输出 `1→2`、头文件 `config.h` 和 Make 变量都写死在 `labs/e8e10/lab.py`。真实项目接入需要：

1. 目标、源文件、Make 规则可配置，不修改共享 E8—E10 代码；
2. 能说明哪些目标刷新、哪些复用，而不是任一预处理行变化就全部刷新；
3. 检测与复验必须实际运行在 DRAFT 构建出的镜像里，而不是只在 JSON 里传 `image_id`。

## 候选方案

1. 直接扩展 `labs/e8e10/lab.py`，把项目差异写进共享代码：改动最小，但污染旧 E8—E10 路线，且多人并行时冲突大。
2. 在请求 JSON 中传全部目标/命令：不改代码，但配置不随 commit 版本化，报告无法自证。
3. 项目根部 `e11e12-project.json`，按提交读取（采用）：配置与源码同版本，兼容旧固定契约。

## 采用方案与原因

### 1. 项目配置放在目标提交根部：`e11e12-project.json`

由 `labs/e11e12/project_config.py` 加载并校验；base 和 target 两个提交必须都包含该文件（防止用配置差异掩盖源码差异）。字段包含 `targets`、`clean_target/build_target/test_target`、`program`、`expected_output`、`header_change`、`include_dirs`。

理由：

- 配置随项目版本走，base/target 快照各自可复现；
- 不修改 `labs/e8e10/lab.py`，旧 E8—E10 路线保持原样；
- 无配置时退回课程固定契约，旧固定样例继续可用。

替代方案：请求里直接传 JSON。被否决，因为报告无法说明配置属于哪个 commit，且容易在两次运行间漂移。

### 2. 缓存复用按“目标依赖闭包”判定，而不是全局 key

`ecache.scan` 的 key 仍包含 directives、recipes、flags、compiler、targets、config。当 recipes/flags/compiler/targets/config 变化时全部刷新；当仅预处理行变化时，对每个目标检查：

```text
affected = source in changed_files or (historical_actual_deps & changed_files)
```

未受影响目标复用历史 `gcc -MM` 结果。

理由：原实现任一 `.c/.h` 变化刷新全部目标，无法完成“说明哪些目标刷新、哪些复用”的验收；逐目标判定在固定样例上得到 `main.o` 刷新、`helper.o` 复用，在真实项目上得到 `stats.o` 刷新、`main.o` 复用。

风险与缓解：如果漏掉某个实际依赖会导致复用错误，因此复用只在该目标历史实际集合（`gcc -MM` 投影）上判定，并始终用目标全量检测做集合级交叉核对；集合不一致即 `FINDINGS_MISMATCH`。

### 3. DRAFT 镜像执行器：挂载同一仓库并在镜像内跑命令

`labs/e11e12/draft_exec.py` 用 DRAFT 产出的 `sha256:…` 镜像启动容器，挂载宿主仓库根，`-w` 指向同一项目目录，执行：

- BuildChecker 全量检测（容器内 python + strace）；
- EChecker 增量扫描（容器内 `gcc -MM`、`gcc --version`）；
- 补丁验证的 `make`、程序运行与动态重检扫描。

每条命令记录镜像 ID、argv、cwd、退出码和输出。`git rev-parse` 不放进候选镜像（候选镜像不保证有 git），由编排侧读取并传入报告，报告仍绑定 target commit。

风险与缓解：嵌套 Docker 需要 Docker socket、宿主路径 `E11E12_DOCKER_HOST_ROOT` 和 `SYS_PTRACE`。缺失时显式失败 `DRAFT_EXECUTION_UNAVAILABLE`，不会静默退回宿主执行。

## 后果

- 固定样例与 `projects/tokenstat` 都能通过同一套流水线，五阶段使用同一 job/trace，阶段信封带 `profile_sha256` 与 `image_id`；
- 报告可以逐条回答“为什么刷新/为什么复用”，并能把基线边回查到 strace 行号；
- 代价是多一层 Docker 启动、候选镜像需要 `build-essential` 和 `strace`，构建时间增加约 1—2 分钟；
- 尚未支持 pattern 规则、order-only 依赖和多输出 recipe，遇到时显式报 `UNSUPPORTED_*`。
