# ADR：E13–E14 A1 关键决策

## ADR-1 个人分支从 `origin/main` 起，而不是从旧交付分支

**背景**：`delivery/a16/e11-e12` 领先旧 main 5 个提交、落后新 main 15 个；重新 fetch 后 main 已含 A2 的 `labs/e13e14` 与 `pipeline.py` 的 `fixed_report_sha256`（PR #28）、B3 的消费者测试（PR #25）。

**决定**：`student/241880485/e13-e14` 以 `origin/main` = `28c94de` 为基线。

**理由**：E13/E14 的公共代码以 main 为准，避免把上一轮的等价提交再合并一遍（`1ccdf36`/`ef4931c`、`a1c1fc0`/`b282a5a` 等成对重复）；我的 E11–E12 消费者实现保留在原分支，不在本轮扩大范围。

**代价**：main 不含 `consume_report.py`。已写进报告，未声称 main 已包含该实现。

---

## ADR-2 C7 做成可复用校验器，而不是一次性脚本

**背景**：E13 手册给出的 C7 断言是一段内联 Python，只能人工判断一次，无法进 CI。

**决定**：新增 `labs/e13e14/verify_c7_isolation.py`（结构化报告 + 退出码 0/1/2）与 7 项回归测试，并在 `e13e14.yml` 的 `four-services` 作业里对真实的两份 `result.json` 执行。

**理由**：C7 的判据（不同 job/trace、产物命名空间、SHA/字节一致、无共享产物）是机械的，适合固化；固化后才能防止后续改动悄悄放宽。

**实施中修正**：初版假设 `result.json` 的 `stages[]` 带 `job_id`/`trace_id`，实际 E11–E12 只有 `{name, artifact}`，首轮真实运行因此误报 5 条失败。改为按 stage 产物的 URI 归属校验，并把两种形状都写进测试。

---

## ADR-3 镜像源替换：保留 digest，只换前缀

**背景**：A16 上 `registry-1.docker.io` 不可达，固定样例的 `FROM python:3.13-slim@sha256:70729b…` 直接超时；deb.debian.org 约 50 kB/s。

**决定**：基础镜像改为 `m.daocloud.io/docker.io/library/python:3.13-slim@<同一 digest>`；候选 Dockerfile 追加一条 `RUN sed -i` 把 apt 源换成清华；`tag` 保持不变。原始 `data/integration-sample` 不动，另建 `data/e13-mirror` 并重算 base/target。

**理由**：`autobuild.prepare_candidate` 要求候选与破损 Dockerfile 的**镜像 tag 相同**、且只允许**新增** `RUN`。保留 tag 才能让 DRAFT 的校验仍然有意义；digest 不变才能保证用的是同一个镜像。替换前后的 SHA-256 都写入 `evidence/e14/mirror-adaptation.txt`。

**代价**：E14 固定样例的 base/target 与教师版本不同，已在报告与证据里显式标注为“镜像源适配版”，没有冒充原始固定样例。

---

## ADR-4 允许四角色信任受限路径（`safe.directory`）

**背景**：CI 上容器以 root 运行，工作区属 runner，`git rev-parse HEAD` 报 `dubious ownership`，echecker 阶段 422。

**决定**：在 `service.py` 里设置 `GIT_CONFIG_COUNT/KEY_0/VALUE_0 = safe.directory=*`。

**理由**：四角色本来就被 `local()` 限制在 `/course/data` 与 `/course/work` 内，容器内又是本次运行专属；与其要求 CI 改变用户映射，不如让服务信任自己已被约束的路径。值写 `*` 是 git 唯一支持的写法，实际暴露面由 `local()` 兜底。

**替代方案（未采用）**：在 compose 里给每个服务加 environment —— 会与 `x-common` 锚点里被覆盖的 `environment` 语义纠缠，且要改四处。

---

## ADR-5 重写本人当天新建的未合并分支

**背景**：首推 `836c6c2` 在 `test_scan_runtime_logs.py` 里写了密钥形状字面量，仓库的 `secret_scan.py --history` 扫全部历史，导致 E7 双门禁与我新增的 contracts 作业同时变红；历史一旦留存，团队后续所有分支都会继续红。

**决定**：改为运行时拼接密钥后，删除该远程分支并以 `1a824ff` 重推同一分支名。

**理由**：该分支是本人当天新建、只有一个提交、尚未开 PR、无他人引用；不清除历史就无法让任何人的门禁转绿。操作范围严格限于本人分支，未触碰 main、他人分支或标签，也未使用 `reset --hard`。

**记录**：旧 SHA `836c6c2` → 新 SHA `1a824ff` → 后续 `980e1a5`；三次 CI 结果都写进报告第 9 节，失败的 run `44971776247` 同样保留。

---

## ADR-6 E14 真实项目阻断时不改共享入口

**背景**：`orchestrate.py::snapshot()` 硬编码 `{main.c, helper.c}` + `config.h`，`service.py` 的 echecker 硬编码 `main.o/helper.o`；真实项目必被拒。

**决定**：本轮只做实测留证（`Unsupported teaching project profile`），不改这两处。

**理由**：四容器入口是 A2 在 PR #28 合入的跨人契约，`orchestrate.py` 的 payload 与 `service.py` 的角色语义要和 B 侧对齐；单人改会把“真实项目支持”变成未经验证的声明。正确做法是提出 Issue、按 profile 适配并同步测试，这需要 A2/A3 与 B 侧确认。

**代价**：E14 真实项目四容器记为阻断，不写“通过”。
