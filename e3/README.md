# E3 并行测试基线

本目录按课程 `E3_TASKS.md` 中 A1/A2/A3/B1/B2 的职责组织四服务测试基线。人工预期放在 `expected/`（`MANUAL_EXPECTED`），实际运行放在 `work/<run-id>/`（`ACTUAL_RUN`），Linux 跟踪放在 `evidence/`；人工答案不得计入检测器准确率。A 组与 B 组的七列基线已并入本页；四服务总表待全员确认。

## A 组七列基线（BuildChecker / EChecker）

| 版本 | 配置 | 命令 | 人工预期 | 实际观察 | 判断依据 | 出处 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 MD/RD | `a1-linux-gcc-default` | 见 [A1 样本 README](fixtures/md-rd/README.md) | `main.o` 缺 `config.h`，多 `unused.h` | 首次 1，改 `config.h` 后仍 1，clean 后 2；改 `unused.h` 触发多余重编译 | `main.c` 包含前者，Makefile 仅声明后者；仅有 `openat` 不足以独立判 MD | [人工预期](expected/buildchecker-md-rd.json)、[实测](work/20260929-110948-A1-00d164/observations.json) |
| A2 C0 | `a2-windows-gcc-default` | `make clean && make && ./app` | 项目文件范围无 MD/RD | clean 10 | 声明包含 `config.h` | [人工预期](expected/echecker-c0-c1-c2.md)、[实测](work/20261002-182617-A2-e1d9d6/observations.json) |
| A2 C1 | 同上 | 修改 `feature.h` 后 `make && ./app`，再 clean 重建 | `main.o` 缺 `feature.h` | 增量 12，修改头文件后仍 12，clean 后 13 | 新增 include，但 Makefile 未补声明 | 同上 |
| A2 C2 | 同上；CFLAGS 改为 `-O0 -DMODE=7` | 复用 C1 产物 `make && ./app`，再 clean 重建 | 上述 MD 仍存在；编译命令变化 | 增量 12，clean 19 | 普通 Make 不追踪命令变化 | 同上 |

## B 组七列基线（DRAFT / MDFixer）

| 版本 | 配置 | 命令 | 人工预期 | 实际观察 | 判断依据 | 出处 |
| --- | --- | --- | --- | --- | --- | --- |
| B1 DRAFT | `b1-ubuntu-wsl2-docker` | `make && ./hello`；`docker build -f Dockerfile.broken\|.reference` + `docker run` | 双层：build 退出 0 且输出 `hello E3`；broken 非零且日志可定位 `make: not found`；reference 输出 `hello E3` | build 0、`hello E3`、退出 0；broken 127、`make: not found`；reference 0、`hello E3`、镜像 `7d1ee809…` | 同一源码唯一差异是 reference 安装 gcc make libc6-dev；失败日志是后续修复的输入 | [人工预期](expected/draft-sample.md)、[实测](work/20261004-115744-B1-8f5ca8/observations.json) |
| B2 Target | `b2-gcc-O0-project-headers` | `python3 e3/scripts/b2_run_mdfixer_baseline.py` | 1→旧 1→修复 clean 2→增量 3→增量 4 | 1/1/2/3/4，无变化不重编译 | 直接补 `config.h`；对象 hash/mtime 和编译日志支持重建 | [styles/target](fixtures/mdfixer/styles/target)、[实测](work/20261004-095323-B2-ae7679/observations.json) |
| B2 Macro | 同上 | 同上 | 同上 | 同上 | `DEPS` 增加 `config.h`，保留宏引用 | [styles/macro](fixtures/mdfixer/styles/macro)；同一轮 work |
| B2 Hybrid | 同上 | 同上 | 同上 | 同上 | `HEADERS` 增加 `config.h`，直接源码项保持 | [styles/hybrid](fixtures/mdfixer/styles/hybrid)；同一轮 work |
| B2 Implicit | 同上 | 同上 | 同上；首次没有 `.d` 也成功 | 同上，生成真实 `.d` | `-MMD -MP` 与 `-include main.d` 实际生效 | [styles/implicit](fixtures/mdfixer/styles/implicit)；work 下 `implicit-main.d` |
| B2 无效候选 | 同上，Target 副本 | 原始构建→候选验证→finally 恢复→重建 | 候选非零退出，不接受，恢复后输出 1 | 候选 make=2，恢复 make=0、app=0、输出 1 | 失败标记可定位；恢复后的 Makefile SHA256 与原输入相同 | [invalid-candidate.patch](fixtures/mdfixer/invalid-candidate.patch)；work 下 `rejection-*` |

## 目录、复现与校验

- `env/toolchain-A1.txt`、`toolchain-A2.txt`、`toolchain-B1.txt` 记录 OS、架构、工具版本；详见 [环境说明](env/README.md)。B2 的环境摘要 `env/toolchain-B2.txt` 被文档引用但尚未入库，见 Backlog。
- `fixtures/md-rd/`、`fixtures/commits/C0|C1|C2/`、`fixtures/draft/`、`fixtures/mdfixer/` 保存四服务样本；C0/C1/C2 的真实 SHA 在 [A2 说明](A2_README.md)。
- 每次运行新建 `work/<日期-时间-成员-编号>/`，不覆盖旧记录；`commands.json` 保存命令、退出码和日志路径，日志名注明版本，`observations.json` 标注 `ACTUAL_RUN`。
- 人工答案在 `expected/` 标注 `MANUAL_EXPECTED` 或 `INSTRUCTOR_ORACLE`。本仓库各份答案均为 `MANUAL_EXPECTED`，不是工具输出。
- A 组校验：`python e3/validate_e3.py`、`python e3/scripts/a1_verify_evidence.py`、`python e3/scripts/a2_export_commits.py --check`（先执行下面的 tag 核对步骤；A3 校验器直接按 SHA 核对，无此依赖）。A2 的行为重跑命令见 [A2 说明](A2_README.md)。
- B 组校验：B1 运行器 `python3 e3/scripts/b1_run_draft_baseline.py`（见 [B1 说明](B1_README.md)）；B2 运行器与检查器 `python3 e3/scripts/b2_run_mdfixer_baseline.py`、`python3 e3/scripts/b2_verify_evidence.py`（见 [B2 说明](B2_README.md)）。

## E2 公共模型对齐

E3 文件是离线基线材料，不直接冒充 `jobRecord.artifacts`。如把文件登记为 E2 artifact，需补 `artifact_id`、`type`、`uri`、`media_type`、`producer_job_id`；`configuration_id` 应进入服务请求或报告的配置上下文，不能把 E3 本地 JSON 直接作为公共任务消息提交。`provenance`、运行命令、退出码等 E3 字段保留在材料或服务专有 payload 中；目前无需改 `contracts/task.schema.json`。

已知限制：A1 Linux 与 A2 Windows 工具链不同；A2/B1/B2 均未取得课程实验包，分别按 PPT 口径手工等价构造样本；B2 环境摘要 `env/toolchain-B2.txt` 缺失待补；E3 当前只验证人工样本和构建行为，尚无四服务检测器准确率或真实联调结果。

## 从仓库根目录复现（Linux，Python 3.9+）

先有 GNU Make、C 编译器和 Python 3；保存证据的离线检查只需要 Python 与 Git。下列操作从仓库根目录执行。A1 行为重跑时若没有 strace，Linux 跟踪会注明未运行；已经保存的 Linux 原始跟踪仍可离线检查。

```bash
python3 e3/validate_e3.py
python3 e3/scripts/a1_run_baseline.py
```

A2 原运行器依赖 C0/C1/C2 tag。某些克隆未取得 tag，可根据已验证的版本记录在本地补齐；已有 tag 若指向不同 SHA 则立即停止，先核实原因，不能覆盖。

```bash
python3 - <<'PYTHON'
import json, subprocess
from pathlib import Path
refs = json.loads(Path('e3/fixtures/commits/versions.json').read_text())['tags']
for tag in ('C0', 'C1', 'C2'):
    sha = refs[tag]['commit']
    subprocess.run(['git', 'cat-file', '-e', sha + '^{commit}'], check=True)
    current = subprocess.run(['git', 'rev-parse', '--verify', 'refs/tags/' + tag + '^{commit}'], capture_output=True, text=True)
    if current.returncode == 0:
        assert current.stdout.strip() == sha, f'{tag} does not match recorded SHA'
    else:
        subprocess.run(['git', 'tag', tag, sha], check=True)
PYTHON
python3 e3/scripts/a2_export_commits.py --check
python3 e3/scripts/a2_run_echecker_baseline.py
```

两个行为运行器均新建自己的运行目录并保存日志，退出成功后按其输出找到证据；不要在冻结样本目录直接修改头文件。Windows 的具体工具路径因机器而异，见各成员入口。

A1 样本 SHA：`9c36984236b97115f44daa24c5274a90dd905b37`；A2 C0/C1/C2 的 SHA 和配置见 [版本记录](fixtures/commits/versions.json)。A1 人工答案中的 `a1-project-headers-default` 表示样本配置，实际 Linux/Windows 环境分别使用 `a1-linux-gcc-default`、`a1-windows-gcc-default`；这些材料不能直接混作同一次配置的性能对照。

## A3 本人交付与共同验收

- [逐项核查报告](docs/A3_REPORT.md)、[AI 使用记录](docs/A3_AI_USAGE.md)、[个人贡献记录](docs/A3_CONTRIBUTIONS.md)。
- [本次命令及重跑证据](evidence/a3-review/20261003/README.md)：实际执行者 A3，在临时克隆验证 A1/A2 行为与缺 tag 时的复现步骤。
- A3-1～A3-6 的 A 组独立交付已核查；四服务总表已由 B3 并入本页，待全员确认，见根目录 Backlog。

## B3 本人交付与共同验收

- [相互检查与 B 组汇总报告](docs/B3_REPORT.md)、[AI 使用记录](docs/B3_AI_USAGE.md)、[个人贡献记录](docs/B3_CONTRIBUTIONS.md)。
- B3-1～B3-5 已核对 B 组目录/命名对齐、并入四服务七列总表、沉淀 Backlog/ADR、按 §10 四问检查 A 组产物并汇总 B 组贡献。
- 未决项：B2 环境摘要 `env/toolchain-B2.txt` 缺失、E3 B2 姓名/Git 作者待其本人补齐、四服务总表与 §10 相互检查待全员确认。
