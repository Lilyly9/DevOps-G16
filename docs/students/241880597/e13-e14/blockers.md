# E13-E14 阻断 Issue 清单（B3 · 241880597）

> B3 主责维护。三个阻断点分别阻碍配对真实项目 E2E、H3 未知项目和远端 CI/RC 发布。状态更新于 2026-11-22。

## BLOCK-1 真实项目四容器 E2E 被编排器 profile 硬编码阻断

- 严重度：阻断（Blocking）
- 影响：E14「配对真实项目四容器 E2E」无法执行；候选发布缺少真实项目证据。
- 现象：`labs/e13e14/orchestrate.py::snapshot()` 校验写死 `{main.c, helper.c}` + `config.h`，真实教学项目（含 `stats.c`、`stats.h`、`Makefile` 等多文件 profile）命中 `Unsupported teaching project profile`，直接抛 `ValueError`。
- 关联：`labs/e13e14/service.py` 不支持 project profile（A1 已实测复现）。
- 复现：
  ```bash
  python3 labs/e13e14/orchestrate.py --request <real-project-request.json> --out work/e14-real-01
  # -> ValueError: Unsupported teaching project profile
  ```
- 期望：编排器按 project profile 动态识别源文件与头文件，或 service 层支持真实项目 profile。
- 责任：需 A1（BuildChecker 联调）与 A3（四容器入口）确认修法；B3 复核。当前无合并修复。

## BLOCK-2 H1/H2/H3 教师输入包缺失

- 严重度：阻断（Blocking）
- 影响：H3 tiny-AES-c（A3+B3 主责）无法执行；H 三项结果不全，E13 门禁不满足。
- 现象：教师发放的 `e13-upstream-student.zip` 与 `02_操作手册/`（`01_E13交叉测试与门禁.md`、`02_E14候选发布.md`、`03_E13三个项目运行指南.md`）均未提供。
- 现状：A2 已完成 H1 jsmn（自带隔离候选补 `strace`）；B1 已完成 H2 inih；H3 无输入包，未执行。
- 责任：需教师补发输入包，或 A3/B3 依据 A2 的 H1 流程自行构造 H3 输入。

## BLOCK-3 云机访问 GitHub 不通，远端 CI 无法触发

- 严重度：阻断（Blocking，对 RC 发布）
- 影响：云机 `git fetch/clone https://github.com/...` 报 TLS 超时，远端必需 CI 无法在云机跑通；RC 发布「必需 CI 绿色」判据不满足。
- 现象：`GnuTLS recv error (-110)`、`curl 16 HTTP2 framing layer`。
- 绕过：云机用本地 remote（`/root/241880555/DevOps-G16`）绕过 TLS，见 [ADR.md](ADR.md)；本地 Windows 可访问 GitHub，`push` 需在本地完成。
- 责任：需组长/A3 在可访问 GitHub 的机器上完成 push + PR + CI，或排查云机出网策略。

## 已排除项

- 固定样例四容器 E2E 正常（B3 端口 18181-18184 通过）。
- C7 B 侧、C4 复核、日志扫描均通过，无新增阻断。
