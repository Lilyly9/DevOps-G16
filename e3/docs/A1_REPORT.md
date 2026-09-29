# A1 E3 实验报告：MD/RD 测试基线与 Linux 原始跟踪

成员：焦龙 / illusiri。日期：2026-09-29。依据：E3_TASKS.md 的 A1-1—A1-9，以及 E3 PPT 实际第 15—22、28 张（页脚 E3/16—23、29）。

## 结果

Windows 与 Ubuntu 两套环境都真实完成行为对照：首次输出 1；仅将 config.h 中 VALUE 改为 2 后，普通 make 仍输出 1；相同源码 clean 后输出 2；只改 unused.h 注释会触发重新编译和链接，程序输出仍为 2。Ubuntu 另完成 strace 和 make -pn 原始取证。

这证明本小样本存在漏重建和多余重建，可作为后续 BuildChecker 的可判定测试基线。尚未实现检测器，人工报告不计入工具准确率。相互复跑/全组验收由 A3/B3 后续执行，本记录不替他们填写完成状态。

## 固定版本与环境

- 仓库：https://github.com/Lilyly9/DevOps-G16。
- 原始故障样本提交：`9c36984236b97115f44daa24c5274a90dd905b37`。
- Linux 使用的运行器提交：`f94237f996c8e0ade467f9ab180d469942b6356b`，已在导出 manifest 中锁定。
- 本机未取得课程实验包，因此按 PPT 手工等价搭建；没有调用课程 run_lab.py，也没有代做 A2 的 C0/C1/C2。
- 每轮均记录配置、实际工具路径和版本；Windows/Linux 的结果分别保存，不进行跨环境性能比较。

| 环境 | GNU Make | C 编译器 | Python | strace |
| --- | --- | --- | --- | --- |
| Windows / x86_64 | MinGW GNU Make 4.4.1 | MinGW GCC 14.2.0 | 3.13.5 | 不可用；不承担 Linux 取证 |
| Ubuntu / x86_64 / Linux 6.8.0-138 | GNU Make 4.3 | GCC 11.4.0 | 3.10.12 | 5.16 |

Ubuntu 使用已有 VMware Workstation Pro 虚拟机，通过 VMware Tools 认证并传入源码副本，未要求课程服务器、Docker、SSH 或共享文件夹。虚拟机中所需工具已存在，本轮没有安装新依赖。认证信息不进入项目或证据；保留的准备记录只含源码导出哈希、命令结果和运行器版本。

## 证据入口

| 运行 | 目录 | 状态 |
| --- | --- | --- |
| Windows 行为实验 | [20260929-110310-A1-4e5f8e](../work/20260929-110310-A1-4e5f8e/observations.json) | 行为通过；Linux 跟踪在此轮明确为 NOT_RUN |
| Ubuntu 行为及跟踪 | [20260929-110948-A1-00d164](../work/20260929-110948-A1-00d164/observations.json) | 行为和 Linux 跟踪均通过 |
| Ubuntu 原始跟踪 | [linux-verified/A1 运行目录](../evidence/linux-verified/20260929-110948-A1-00d164/README.md) | trace.log.*、make-pn.txt、访问/进程摘录均已保存 |
| 人工预期 | [buildchecker-md-rd.json](../expected/buildchecker-md-rd.json) | MANUAL_EXPECTED，与真实日志分离 |

每个 work 目录有 environment.json、source-manifest.json、commands.json、observations.json、logs/ 和六个 snapshots/。每步命令都有 stdout、stderr 文件及真实退出码。运行中的 app/main.o 只留在被忽略的 runtime 副本，不作为交付文件；hash/mtime 和源码状态进入证据。

各 A1 证据目录使用局部 .gitattributes 禁止 Git 转换换行，以保持日志和快照原始字节；make -pn 自带的行尾空格也保留。样本源码固定 LF 换行，便于 Windows/Linux 复跑。

## 可供 A3 汇总的七列基线条目

| 版本 | 配置 | 命令 | 预期 | 实际 | 依据 | 出处 |
| --- | --- | --- | --- | --- | --- | --- |
| 原始 fixture 9c36984 | 本轮 GCC，-O0 -Wall -Wextra | make；app | 1 | 两环境均 1 | VALUE=1 的初始源码 | logs/md-rd-clean* |
| 同 SHA 加 config.h 的记录改动 | 同一配置 | 普通 make；app | 仍为 1 | 两环境均 1，main.o 未更新 | config.h mtime 晚于旧 main.o，但声明没有它 | snapshots/02、03；touch-header 日志 |
| 完全相同 VALUE=2 源码 | 同一配置 | make clean；make；app | 2 | 两环境均 2 | 重新编译才纳入新头文件值 | snapshots/03、04 hash 对照；clean-rebuild 日志 |
| 仅改 unused.h 注释 | 同一配置 | 普通 make；app | 多余编译、仍为 2 | 两环境均重新编译/链接，输出 2 | 声明包含 unused.h，源码没有使用它 | snapshots/05、06；redundant 日志 |
| 原始 fixture 9c36984 的独立副本 | Ubuntu GCC 11.4.0 | strace -ff ... make；make -pn | 编译进程读取 config.h，声明漏掉它 | PID 11091 读取；声明为 main.c unused.h | compiler 与 make 进程身份、实际访问及声明 | linux-verified trace 与 make-pn |

工作副本改动没有伪装成新 Git 提交。各快照保存修改后的内容，commands 继续引用原始源码 SHA，source-manifest 与 state.json 同时记录实际状态。

## Linux 取证的具体解释

本轮 trace.log.11088 的 execve 表明它是 `/usr/bin/make`；它对 unused.h 的操作是 newfstatat（时间戳/属性查询）。trace.log.11089 为 `/usr/bin/cc`，其 vfork 创建 PID 11091；trace.log.11091 的 execve 表明它是 GCC 的 `cc1` 编译进程，同一进程随后成功 openat `config.h`。

`make-pn.txt` 中目标声明为 `main.o: main.c unused.h`，没有 config.h。结合 main.c 的 include 和行为对照，能够解释人工 MD/RD 依据。

**只看到 openat 还不足以直接判 MD。** 本阶段保留原始取证，不声称已经完成进程/路径归一化、间接依赖建图或完整错误推断。系统头文件不属于本人工答案集合。

## 复现与离线核验

从仓库根目录在已有 GNU Make/C 编译器/Python 的 Linux 上运行：

```bash
python3 e3/scripts/a1_run_baseline.py --require-linux-trace
```

需要 strace 且使用 Linux。每次创建新目录，不覆盖本次证据。Windows 可使用样本 README 中的 MinGW 命令执行行为部分。

只核对现有证据，不重新构建、不需要 strace：

```bash
python e3/scripts/a1_verify_evidence.py
```

此 A1 专用脚本检查真实源码 SHA、文件 hash、日志路径/退出码、程序输出、修改时间、增量/clean 源码一致性、编译与链接证据，以及 Linux 编译进程读取 config.h 的原始行。它不是 A3 的公共 validate_e3.py，不替其他服务验收。

## 与队友的交接

- A3：读取本报告七列基线条目、env/toolchain-A1.txt 和两轮 work，复跑后在公共文档记录自己的结论。
- B2：只消费人工报告中 MISSING/config.h，使用同一源码提交的 Makefile.before，在自己的副本修复；REDUNDANT 不作为 MD 修复。
- A2：C0 必须声明正确。本故障 fixture 已故意包含 MD/RD，不作为 A2 的正确 C0。
- B3：可汇总 A1_AI_USAGE.md、A1_CONTRIBUTIONS.md，保留来源区分和独立运行状态。
- 本人任务已完成；相互检查及总表汇总待队友执行。没有修改公共 Schema、队友接口或其 E3 负责目录。
