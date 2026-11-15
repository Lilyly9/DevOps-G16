# AI 使用说明（E11—E12 / A2 241880496）

## 使用的工具

- GitHub Copilot（VS Code Chat / Agent 模式）：辅助阅读课程包、编写 `project_config.py`、`ecache.py`、`draft_exec.py`、个人测试和文档初稿；辅助排查 WSL/Docker 路径、Docker socket 权限和候选镜像 apt 源问题。
- 没有在流水线中调用任何大模型 API。DRAFT 的候选 Dockerfile 是手工编写的固定文件，`draft.autobuild` 只是两轮回放，报告中明确 `candidate_source` 为手工候选回放。

## 本人如何核对 AI 产出

1. 所有增量/全量集合、commit、镜像 ID 都来自实际运行文件，不是 AI 生成的值；报告中的数字逐项对照 `work/` 下的原件与归档到 `evidence/` 的选择件。
2. 新增测试先写独立预期（例如“改 core.c 只刷新 core.o”），再运行；`Ran 18 tests ... OK` 后仍用全新 OUT 重跑 E11-A、E12，避免用测试通过代替真实运行。
3. 每次 E12 都核对：同一 job/trace、阶段顺序、`image_id` 与 DRAFT 构建结果一致、下载文件三处 SHA256 一致。
4. AI 给出的命令在 WSL/Docker 中实际执行；失败的尝试（apt 503、候选镜像缺 git/strace、`host_root` 检查位置错误）保留在 `work/` 的失败 OUT 中，没有用成功结果覆盖。

## 未使用 AI 的部分

- 真实项目 `projects/tokenstat` 的 C 代码、Makefile、测试输入与两次故障提交由本人编写并本地编译验证。
- 最终的取舍（配置放项目根部、逐目标复用、镜像内执行）由本人确认并写入 ADR。
