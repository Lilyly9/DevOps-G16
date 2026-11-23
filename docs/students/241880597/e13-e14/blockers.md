# E13-E14 阻断 Issue 清单（B3 · 241880597）

> B3 主责维护。三个阻断点中的两个已解除，仅剩远端 CI/RC 发布。状态更新于 2026-11-23。

## BLOCK-1 真实项目四容器 E2E 被编排器 profile 硬编码阻断 —— 已解除

- 严重度：阻断（Blocking）→ 已解除
- 现象：`labs/e13e14/orchestrate.py::snapshot()` 校验写死 `{main.c, helper.c}` + `config.h`，真实教学项目（含 `stats.c`、`stats.h`、`Makefile` 等多文件 profile）命中 `Unsupported teaching project profile`，直接抛 `ValueError`。
- 解除：B2（241880543）在 PR #32 中为 `orchestrate.py`/`service.py` 接入 `project_profile`，支持 `profile=true` 动态识别源/头文件与 clean/build 目标。
- B3 复核：配对真实项目（B1 `data/e13-b-project`，profile=true）四容器 E2E 通过，五阶段 SUCCEEDED、recheck 无 MISSING；证据 `evidence/e14-real/`。

## BLOCK-2 H1/H2/H3 教师输入包缺失 —— 已解除

- 严重度：阻断（Blocking）→ 已解除
- 现象：教师发放的 `e13-upstream-student.zip` 与操作手册缺失，H3 tiny-AES-c 无法执行。
- 解除：已取得 `e13-upstream-student.zip` 并解压至云机 `/root/241880597/e13-upstream-student/`（H1-jsmn / H2-inih / H3-tiny-aes）。
- 现状：H1 jsmn（A2）、H2 inih（B1）、H3 tiny-AES-c（B3）均已执行五阶段通过。B3 H3 见 [cross-test-record.md](cross-test-record.md)。

## BLOCK-3 云机访问 GitHub 不通，远端 CI 无法触发 —— 仍阻断

- 严重度：阻断（Blocking，对 RC 发布）
- 影响：云机 `git fetch/clone https://github.com/...` 报 TLS 超时，远端必需 CI 无法在云机跑通；RC 发布「必需 CI 绿色」判据不满足。
- 现象：`GnuTLS recv error (-110)`、`curl 16 HTTP2 framing layer`。
- 绕过：云机用本地 remote（`/root/241880555/DevOps-G16`）绕过 TLS，见 [ADR.md](ADR.md)；本地 Windows 可访问 GitHub，`push` 需在本地完成。
- 责任：需组长/A3 在可访问 GitHub 的机器上完成 push + PR + CI，或排查云机出网策略。

## 已排除项

- 固定样例四容器 E2E 正常（B3 端口 18181-18184 通过）。
- 配对真实项目四容器 E2E 正常（BLOCK-1 解除）。
- H1/H2/H3 教师输入包齐全，三项目五阶段均通过（BLOCK-2 解除）。
- C7 B 侧、C4 复核、日志扫描均通过，无新增阻断。
