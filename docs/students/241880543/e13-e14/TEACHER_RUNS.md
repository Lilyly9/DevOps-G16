> 2026-11-23 更新：H1 jsmn 主执行及 H3 tiny-AES-c 复核已在 Linux 官方 E12 入口跑通五阶段，各核对 20 条同镜像执行记录，最终无 MISSING。原始输入与 Git C0/C1 不变；本轮 [Linux 原件](evidence/continuation-20261123/teacher-linux.zip)、[逐项清单](evidence/continuation-20261123/verified-runs.json)。下文 Windows 阻断说明为历史记录。

# B2：新发教师项目 H1 / H3 实际记录

输入来自本次提供的 `学生发放包_20261116.zip`，已阅读随包操作手册及 E13/E14 课件。发放包 SHA256 为 `707cd09b37b69db0312fcef8292edac0c777b5a906bd1e82625bff53630481bc`；内部项目 ZIP 原样保存在 [e13-upstream-student.zip](evidence/teacher/e13-upstream-student.zip)，SHA256 为 `d9818c5f34d6ff5b6016222dabd7f56daca09ceaa5f525be214e146e3d485435`。保留原上游源码、许可与课程适配 Git 历史，没有使用教师预跑结果。

| 项目 / B2 角色 | C0 完整提交 | C1 完整提交 | 本轮结果 |
| --- | --- | --- | --- |
| H1 jsmn / 主执行 | `66a6dafcc20cea76bf017923d3db725d78407845` | `948a1d30cd758d32d45a50f788e5a95fb1d89c69` | GCC 编译、运行输出 1；生成修复补丁并通过 Git 适用性预检；完整 E12 阻断 |
| H3 tiny-AES-c / 复核 | `dc8099306d7023b7337328d718149973e7b17978` | `5640bb69a01e64559207e9f74d15a9ae71a4d0f3` | GCC 编译、运行输出 1；生成修复补丁并通过 Git 适用性预检；完整 E12 阻断 |

上游固定提交分别是 jsmn `25647e692c7906b96ffd2b05ca54c097948e879c` 和 tiny-AES-c `23856752fbd139da0b8ca6e471a13d5bcc99a08d`。上游提交与课程 C0/C1 是不同身份，不混用。

本轮独立目录为 `work/e13-241880543-teacher-20261122-01`、`-02`、`-03`。第一次 GCC 缺少汇编器 PATH 的失败保留；补齐本进程 CLion MinGW 路径后，第二、三次两项目均实际编译并输出 1。第三次由现有 `lab.scan()` 调用真实 GCC `-MM`，两项均发现 `MISSING(helper.o, extra.h)`；由 `lab.patch()` 生成候选并实际执行 `git apply --check`，退出 0。它们是静态依赖与补丁预检，不替代构建验证和动态复验。每次原始仓库均通过 `git fsck --full`，源文件前后摘要相同，Git 工作区保持干净。

每项目已生成独立的官方 E12 请求并实际调用 `run_e11e12.py run`。当前 Windows 入口返回退出码 2：`Run on the Linux cloud host after SSH login`，流水线尚未启动，没有生成该次 `result.json`、Docker 构建、validation 或 strace 结果，不能判定 H1/H3 五阶段通过。成功及失败原件见 [运行归档](evidence/teacher/teacher-runs.zip)，摘要见 [teacher-summary.json](evidence/teacher/teacher-summary.json)。

原教师候选只安装 build-essential；同镜像动态重检还需要 strace。第三次生成了独立的 `candidate-b2-strace.Dockerfile` 并记录原件与派生件 SHA256，只增补 strace 依赖，保留原候选。该派生候选尚未成功构建，不能填写镜像 ID。

在具有 GCC 和 Docker 的 Linux 仓库检出中，先构建本人的 E11/E12 教学镜像，再执行：

```bash
python3 docs/students/241880543/e13-e14/run_teacher.py \
  --execute --with-strace --out work/e13-241880543-teacher-new
```

入口使用归档内的原始项目，按实际 Git 历史重新生成请求；每轮生成新的 data/work 副本，保留完整退出码和输出。只有实际五阶段和动态复验成功后，才更新 H1/H3 完成状态。C1 的当次对手报告、四容器和整组门禁仍分别待完成。
