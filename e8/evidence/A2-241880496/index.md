# E8-A 证据索引（A2 / 万宇 / 241880496 / G16 / 轨道 A）

轨道 A 手册《8_E8_A组.md》第 0—7 步的**实际运行**结果。运行时间 2026-11-10，宿主机 Windows 11 + Docker Desktop（WSL2 后端，4 vCPU / 8 GiB），实验容器 `course-e8e10:241880496`（linux/amd64，Debian 13，gcc 14.2.0、make 4.4.1、strace 6.13、python 3.13.14）。

## 身份

| 项 | 值 |
| --- | --- |
| 学生源码 SHA | `adf0421e61575869c2f3cca9c908ef6f07620633`（[student-source-commit.txt](student-source-commit.txt)） |
| 环境镜像 ID | `sha256:0a3e46d733048835ae762a5c309618db438d559abedb9bfa96b07d3018c05f84`（[environment-image-id.txt](environment-image-id.txt)） |
| 原始 OUT | `work/e8-A-manual.myt4ld`（服务器/本机工作目录，不入库；本目录为精选副本） |
| 内部受测项目 C0 | `5d82db6 C0 baseline`（[project-git-log.txt](project-git-log.txt)） |

## 复现命令

Windows 宿主上用 `run_stage.ps1 -Stage e8 -Track A`（[脚本副本](../../../docs/students/241880496/e8-e10/run_stage.ps1)）逐条执行手册第 1—7 步，每步等价于手册的 `lab_python "$OUT" <<'PY' ... PY`（`docker run ... python3 - $OUT`），并把 `STEP_EXIT_CODE` 追加到 `steps/*.log`。手工等价命令：

```bash
python3 run_lab.py build            # 建 course-e8e10:<学号>
# 第 1 步 fixture；第 3 步 gcc -MM 基线；第 4 步真实 BuildChecker；第 6 步未变化复用
```

## 关键结果

| 检查 | 预期（先写） | 实际 | 结论 |
| --- | --- | --- | --- |
| 第 3 步 gcc -MM 投影 | `main.o=[config.h, main.c]`，`helper.o=[helper.c]`；恰好两条 MD/RD | 一致，`BASELINE_PASS` | PASS（[baseline.json](baseline.json)） |
| 第 4 步真实 BuildChecker | 与 gcc 投影在对象目标上一致 | `BUILDCHECKER_BASELINE_PASS`，status=SUCCEEDED | PASS（[buildchecker/findings.json](buildchecker/findings.json)） |
| 第 5 步回溯原始证据 | MD 有系统调用证据，RD 有 Make 数据库证据 | `trace/t.14:579` `openat(...,"config.h",O_RDONLY)`；`make-db.txt:1044` `main.o: main.c unused.h` | PASS |
| 第 6 步未变化复用 | 两目标复用、刷新为空、图与发现相同 | `REUSE_PASS ['main.o','helper.o'] []` | PASS（[incremental.json](incremental.json)） |
| 第 7 步内部工作区干净 | `git status --short` 为空 | 无输出（`*.o`/`app` 被样例 `.gitignore` 忽略） | PASS |

历史图来源：`baseline_source = BuildChecker actual-graph.json projected to object targets`；`baseline.json` 保留本次 strace 采集的真实图，不是教师示例。

## 目录内容

- `baseline.json` / `incremental.json` / `结论.txt`：本阶段两份报告与结论。
- `buildchecker/`：真实 trace（`trace/t.12`—`t.21`）、`make-db.txt`、`actual-graph.json`、`declared-graph.json`、`findings.json`、`processes.json`、clean/build 日志。原始 `buildchecker/project/` 的编译产物未入库。
- `steps/`：7 份逐步容器日志，末行 `STEP_EXIT_CODE=0`。
- `main.c` `helper.c` `config.h` `extra.h` `unused.h` `Makefile` `.gitignore`：C0 输入副本；完整内部历史见 `project-git-log.txt`（内部 `.git` 不入库）。
- 个人扩展与单元测试证据见 [E10 证据](../../../e10/evidence/A2-241880496/unit-tests.log)。
