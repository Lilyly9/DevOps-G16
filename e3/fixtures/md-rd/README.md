# A1：BuildChecker 的 MD/RD 测试基线

成员：焦龙 / illusiri。按 E3 PPT 的 main.o/config.h/unused.h 例子手工搭建，未取得课程实验包，没有运行课程的 run_lab.py。本目录保留 VALUE=1 的原始故障样本，运行器总是先复制到新的隔离目录。

主任务是实际展示漏重建和多余重建，另在 Linux 采集原始系统调用跟踪；本次尚不实现 BuildChecker。

## 复现（从 DevOps-G16 仓库根目录）

Linux / macOS，已有 GNU Make、C 编译器和 Python 3.9+：

```bash
python3 e3/scripts/a1_run_baseline.py
```

Linux 安装有 strace 时，运行器还会在独立副本执行跟踪并写入 `e3/evidence/linux-verified/<A1-run-id>/`。若无 strace，行为实验仍能执行，观察记录会将跟踪标为未完成。

本次 Windows 的可用工具及执行命令：

```powershell
& 'E:/Anaconda/python.exe' e3/scripts/a1_run_baseline.py --make 'E:/winlibs/mingw64/bin/mingw32-make.exe' --cc 'E:/winlibs/mingw64/bin/gcc.exe'
```

其他机器可用 `--make` 和 `--cc` 指定本机工具。命令运行后打印本轮工作目录，每次使用带时间及随机后缀的 A1 目录；不会覆盖其他成员的 work 文件。

## 可以手工核对的步骤

在独立副本中，以实际工具替换 make/cc；Windows 为 make 增加 `CC=gcc`、`PYTHON=python`：

1. `make` 后运行 `./app`（Windows 为 `./app.exe`），应输出 1。
2. 仅将 config.h 的 VALUE 改为 2，确保它的修改时间晚于 main.o；普通 `make` 后程序仍输出 1。
3. 同一源码执行 `make clean`、`make`，程序输出 2。
4. 仅修改 unused.h 的注释，确保修改时间更新，再 `make`；出现编译与链接命令，程序仍输出 2。

Makefile 第 18 行故意只声明 `main.c unused.h`。编译器从 main.c 第 2 行读取 config.h，但规则遗漏它，是 MD；unused.h 被声明而没有被该源码使用，是 RD。该人工答案只针对 main.o 和本项目文件，排除系统头文件。

## 交付内容与核验

- `Makefile.before` 是与 Makefile 相同的冻结故障版本，方便 B2 在独立副本使用；A1 不生成修复补丁。
- `e3/expected/buildchecker-md-rd.json` 标明 `MANUAL_EXPECTED`，保留判断依据与实际样本 SHA。人工报告不计入工具准确率。
- `e3/work/<A1-run-id>/commands.json` 记录真实命令、cwd、退出码及 stdout/stderr 文件；`observations.json` 记录实测结果。
- 每步保留修改前后头文件、文件 hash 和 mtime，证明增量和 clean 对照使用相同的 VALUE=2 源码。
- `e3/env/toolchain-A1.txt` 提供本轮环境摘要；每轮完整环境存入 work，不依赖可变摘要文件。
- Linux 跟踪记录单独保存；只看到 openat 还不足以直接判 MD，本阶段是原始证据，构图与归一化属于后续 BuildChecker。
- 公共 `e3/README.md` 和 `validate_e3.py` 属 A3/B3。A1 的运行报告、AI 使用和贡献记录放在 `e3/docs/A1_*.md`，供其汇总。

本样本的 CC、CFLAGS 和工具版本组成运行配置。Windows 的 MinGW 行为证据和 Linux 的系统调用证据分别记录，不混作同一环境的性能结果。
