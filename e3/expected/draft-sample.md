# DRAFT 样本清单(Tiny Greeting)

- `provenance`: `MANUAL_EXPECTED`(课程实验包 `E3实验包/fixtures/draft/` 未取得,B1 按 PPT E3/30–33 的口径手工等价构造;"输出 hello E3、退出码 0、make: not found 可定位"这些行为目标为 PPT 给定的验收口径)
- 人工预期不计入工具准确率;实际运行见 [work/20261004-115744-B1-8f5ca8/observations.json](../work/20261004-115744-B1-8f5ca8/observations.json)

| 项目项 | 本实验示例 |
| --- | --- |
| 项目项 | Tiny Greeting:单文件 C 程序,构建产物 `hello` |
| 来源 | 课程人工样例 Tiny Greeting(PPT E3/30、E3/33);手工等价构造,说明见 [fixtures/draft/README.md](../fixtures/draft/README.md) |
| 输入 | `main.c`、`Makefile`、`README.md`、Dockerfile 两份;项目版本 = 仓库内文件内容 + `source_commit`(见 observations.json) |
| 命令 | 构建 `make`;验证 `./hello`;容器内同一判据 `make && ./hello` |
| 失败候选 | `Dockerfile.broken`(`FROM python:3.13-slim`,无 make/C 工具链):构建非零退出,日志可定位到 `make: not found` |
| 参考成功 | `Dockerfile.reference`(增加 `RUN apt-get install gcc make libc6-dev`):构建成功,`docker run --rm` 输出 `hello E3`,退出码 0 |

## 预期判据(双层)

1. **第一层(编译通过)**:`make` 退出码 0,生成可执行文件 `hello`。
2. **第二层(功能验证)**:`./hello` 标准输出 `hello E3`,进程退出码 0。

失败候选判据:`docker build -f Dockerfile.broken` 非零退出(实测 127),构建日志可定位 `make: not found`——该日志是后续"修复方法"的输入,不得删除。

参考成功判据:`docker build -f Dockerfile.reference` 退出码 0;`docker run --rm nju-e3-draft-reference:20261004` 输出 `hello E3`、退出码 0;同时保存 Dockerfile diff、build 日志与镜像 ID。

## 实际观察(2026-10-04,B1,Ubuntu 26.04 LTS / WSL2 + Docker 29.1.3)

| 判据 | 预期 | 实测 | 出处 |
| --- | --- | --- | --- |
| `make` 退出码 | 0 | 0 | `work/20261004-115744-B1-8f5ca8/logs/draft-build.*.log` |
| `./hello` 输出 | `hello E3` | `hello E3` | 同上 `draft-run.stdout.log` |
| broken 构建退出码 | 非零 | 127 | `logs/docker-broken-build.*.log` |
| broken 日志含 `make: not found` | 是 | 是(stdout,legacy builder) | 同上 |
| reference 构建退出码 | 0 | 0 | `logs/docker-reference-build.*.log` |
| `docker run --rm` 输出 | `hello E3` | `hello E3` | `logs/docker-reference-run.stdout.log` |
| 参考镜像 ID | 保存 | `sha256:7d1ee809dfd00f4c9572000810e1d114c15e1673d490b9c884abec676788985a` | `logs/docker-reference-image-id.stdout.log` |
| Dockerfile diff | 保存 | 新增 `RUN apt-get …` 段 | `logs/dockerfile-diff.stdout.log` |

复现命令、确切 argv/cwd/退出码见同目录 `commands.json`;环境版本见 `environment.json` 与 [env/toolchain-B1.txt](../env/toolchain-B1.txt)。

已知限制:broken 构建使用 Docker legacy builder,`make: not found` 的详细输出出现在 stdout(BuildKit 会在错误摘要中给出同类行);换 builder 重跑时按 stdout+stderr 联合文本检索关键词。
