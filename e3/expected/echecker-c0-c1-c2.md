# EChecker C0 / C1 / C2 人工预期与判断依据

- 成员：A2（万宇 / `adscfe`）
- `provenance`：`MANUAL_EXPECTED`（本组人工预期，**不是**检测器输出，也不计入工具准确率）
- `sample_origin`：`MANUAL_FIXTURE`
- 依据：E3 PPT《并行测试基线》A 组步骤 9（页脚 E3/24）与 `E3_TASKS.md` 的 A2-1~A2-5
- 机器可读版本：[`echecker-c0-c1-c2.json`](echecker-c0-c1-c2.json)
- 实际运行记录：`e3/work/<run-id>/`（与本文件严格分开）

本机没有课程 E3 实验包（无 `fixtures/commits/`、无 `scripts/run_lab.py`），所以按 PPT 的 C0/C1/C2 描述**手工等价搭建**同构小项目，没有声称运行过课程脚本。

## 1. 固定版本与环境

| 项 | 值 |
| --- | --- |
| 仓库 | `https://github.com/Lilyly9/DevOps-G16` |
| 被检测项目 | `e3/fixtures/commits/lab` |
| C0 | `ca57cfb89643e19f0c2ab73637ae2f962f8f7658`（tag `C0`） |
| C1 | `ef88dd77c8a452fb4f11b2978d0e1157f425e1db`（tag `C1`） |
| C2 | `900d64c1a60d81d106beb84e4c4593cb576e5a92`（tag `C2`） |
| 基线配置 | `configuration_id = a2-windows-gcc-default`（`MODE` 默认 0） |
| 编译命令 | C0/C1：`-O0`；C2：`-O0 -DMODE=7` |
| 构建命令 | `make clean` / `make`；运行 `./app`（Windows 为 `./app.exe`） |
| 范围 | 只针对 `main.o` 与本项目头文件，**不含系统头文件** |

增量与全量对照必须使用同一配置、同一提交、同一规范化方式；否则 E10 的“增量 vs 全量”不可比。

## 2. 人工预期（六列，实际值不在本文件）

| 版本 | 配置 | 命令 | 人工预期 | 依据 | 出处 |
| --- | --- | --- | --- | --- | --- |
| C0 | `MODE=0`，`-O0` | `make clean && make && ./app` | 输出 `10`；声明正确 | `main.c` 只读取 `config.h`，而 Makefile 已声明 `main.o: main.c config.h` | `fixtures/commits/C0/` |
| C1 | 同上 | `make`（复用 C0 产物） | 输出 `12`；**不能据此判定无 MD** | C0→C1 改了 `main.c`，一定会重编译 | `fixtures/commits/C1/` |
| C1 | 同上 | 只把 `feature.h` 的 `FEATURE` 改成 `3`，不 clean，`make` | **不重新编译**，程序仍输出 `12`（漏重建） | `main.o` 的声明缺 `feature.h` | `expected/echecker-c0-c1-c2.json` → `expected_missing_dependency_evidence` |
| C1 | 同上 | `make clean && make && ./app` | 输出 `13` | 重新编译才纳入 `FEATURE 3`；`12` vs `13` 证明此前结果过时 | 同上 |
| C2 | `-O0 -DMODE=7` | 复用 C1 产物，`make` | **增量 = 12**（不重建） | 目标依赖只有 `main.o`，普通 make 的时间戳检查看不到 `CFLAGS` 变化 | `fixtures/commits/C2/` |
| C2 | 同上 | `make clean && make && ./app` | **clean = 19**（`10 + 2 + 7`） | 只有全量重建才会用上 `-DMODE=7` | 同上 |

对照 PPT E3/28 的表述：C0 `clean = 10`；C1 预期发现 MD `main.o → feature.h`、`clean = 12`；C2 上述 MD 仍存在、`增量 = 12`、`clean = 19`。

## 3. 每条预期的判断依据

1. **C0 无 MD/RD（本例范围）**：`main.c` 只 `#include "config.h"` 并使用 `BASE`；Makefile 声明 `main.o: main.c config.h`。实际读取集合与声明集合一致，因此没有缺失；`config.h` 被真正使用，因此也没有冗余。
2. **C1 的 MD**：`main.c` 新增 `#include "feature.h"` 并使用 `FEATURE`，而声明仍是 `main.o: main.c config.h`。判据不是“构建失败”（C1 构建成功并输出 12），而是**单独修改 `feature.h` 后没有任何编译动作、程序继续输出旧值**；`make clean` 后才变成 13。这条差异就是 MD 的可核验依据。
3. **C2 的命令变化**：`make -n -B main.o` 的命令快照是 C1 = `-O0 -c main.c -o main.o`、C2 = `-O0 -DMODE=7 -c main.c -o main.o`。普通 `make` 只比较时间戳，命令变了也不重建，所以增量 12、全量 19；两者差异说明“命令变化未被普通重建捕获”。

这三种判据都不依赖检测器实现，别人换一台机器照做应得到同样的观察。

## 4. 复现命令

```powershell
# 1) 校验冻结快照与 tag 字节一致
python e3/scripts/a2_export_commits.py --check

# 2) 跑基线（每次新建 work/<run-id>/，不覆盖旧证据）
python e3/scripts/a2_run_echecker_baseline.py --make <make> --cc <cc> --python <python>
```

手工复现（任意装有 GNU Make 与 C 编译器的环境）：

```bash
cp -R e3/fixtures/commits/C0 /tmp/e3-c0 && cd /tmp/e3-c0
make clean && make && ./app                 # 10
cp ../C1/main.c ../C1/feature.h . && make && ./app   # 12
# 改 feature.h 的 FEATURE 2 -> 3（注意让 mtime 晚于 main.o），不要 clean
make && ./app                               # 仍为 12（漏重建）
make clean && make && ./app                 # 13
cp -R ../C2 /tmp/e3-c2 && cd /tmp/e3-c2     # C2 增量/clean 对照
```

## 5. 实际观察去哪里看

本文件只保存人工预期。真实命令、退出码、stdout/stderr、文件 hash 与 mtime 在：

- `e3/work/<run-id>/commands.json`：每条命令的 argv、cwd、退出码与日志路径
- `e3/work/<run-id>/observations.json`：实测输出与结论
- `e3/work/<run-id>/logs/`：原始日志，含 `*-main-o-command` 命令快照与 `*-make-pn.declared.txt` 声明快照
- `e3/work/<run-id>/snapshots/`：六个阶段状态（只存源码与 `state.json`，不存二进制）
- 本人汇总（含实测值）：`e3/docs/A2_REPORT.md`

## 6. 边界

- 不实现 EChecker 检测器（E8）；不做真实增量/全量报告一致性与耗时对照（E10）；不接入 B 组真实数据（E12）。
- 三人复核与总表汇总由 A3/B3 组织，本文件不替他们填写完成状态。
- 人工 oracle 与真实日志分离，人工预期不计入工具准确率。
