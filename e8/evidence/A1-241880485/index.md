# A1 E8-A 原件与交接索引

焦龙 / 241880485 / A16；2026-11-03。源码 `9ee3242f8d7ea1b6bb4091e2947d85d33a37aa8a`；镜像 `sha256:7461c2bbd458c9a1955c9cfd502d435f8213a8e15b59f952eca833edcfe4e691`。

**本轮标准路线、间接 include 扩展和 8 项容器单测均通过。**完整图/发现/进程已由匹配源码离线重解析核对。个人远程 CI 见 [CI记录](../../../docs/students/241880485/e8-e10/CI记录.md)，公共导入7测与个人8测分别记账。

报告：[个人报告](../../../docs/students/241880485/e8-e10/个人报告.md)；决策与AI使用在同一个人文档目录。

| 路径 | 内容/核查入口 |
| --- | --- |
| `baseline/` | `work/e8-A-manual.vwDixM` 的文字原件；`baseline.json`、`incremental.json`、完整 `buildchecker/trace/`、图、进程、数据库、输入、程序输出、steps、内部历史bundle |
| `baseline/baseline-gcc-projection.json` | 覆写真实基线前保存的GCC投影，与最终真实对象图分清来源 |
| `extension/` | `work/e8-A-manual.jA7ZjJ`；独立人工预期、间接include变更、增量/全量和动态前后原件、steps、历史bundle |
| `unit-tests/` | 原7项+A1新增1项，`stderr.log` 的 `Ran 8 tests`/`OK`，退出0；工具锁和运行后镜像 |
| `preparation/` | 本次环境、工具版本、Git身份/干净状态、构建命令与退出码 |
| `provenance/` | 源码/镜像/输入哈希、实际命令、课程锁、仓库/历史/本人镜像扫描通过原件 |
| `execution/` | 本次实际执行脚本、原helper、构建与整体路线日志。脚本是原执行记录，带实际路径；异机按下方命令适配 |
| `verification/` | 独立原件审查、三套trace重解析比对；保存其真实检查范围/限制 |
| `ci/import/` | 公共导入PR/merge/run/artifact元数据，不能冒充个人新增测试CI |
| `backup-record.json` | 双端原始备份、大小/SHA、内容范围；本轮个人源码/CI备份另行生成 |
| `archive-scope.json` | 原完整备份路径、大小、哈希与Git精选排除清单 |
| `files.sha256.json` | 精选文件逐个大小/SHA-256，清单自身除外 |

## 关键原始证据

- 标准 `baseline/buildchecker/make-db.txt:1044`：`main.o: main.c unused.h`。
- 标准 main.o 作业：make13→gcc14→cc1=15 / as=16；`trace/t.15:579` 成功只读打开config.h，`trace/t.16:23` 创建main.o。第二指针是目标写出，不是又读一次头文件。
- `baseline/baseline.json` 的 actual 已用真实BuildChecker对象图投影，baseline_source明确；`incremental.json`同key复用main.o/helper.o，refreshed为空，MD/RD完整集合不变。
- 扩展后 cc1=66 的 `trace/t.66:579–580` 打开config.h/extra.h；同作业 as=67 在`t.67:23`创建main.o。增量/全量和动态对象投影都新增MD extra.h。
- 每套动态原件的10份trace都保存，未像前次E5那样只裁剪关键PID。动态目录去掉的只是编译二进制；完整备份保留它们，详见排除清单。

## 三种SHA不要混用

1. 学生实验实现源码：`9ee3242f8d7ea1b6bb4091e2947d85d33a37aa8a`。
2. 标准内部C0：`288876b0f535833a83e76c7526f5df0a4d8ec303`。
3. 扩展内部：`683b6b05d97233fe2c81f6697662e346a5cefd0b` → `20094b5a4d105c72ecbead91d3302b3834d47254`。

两个 `project-history.bundle` 可恢复内层历史；它们不是外层学生仓库的认证/配置。

## 如何重跑

使用包含公共导入的原G16仓库；Linux、Docker、Git/Python可用，个人数字学号身份。实际云端独立克隆为 `/root/241880485/DevOps-G16-e8-A1-20261103`，镜像`course-e8e10:241880485`。

```bash
# 在本人G16 Git根，切相应实现版本后运行；每次OUT必须新建
python3 run_lab.py build
source e8/evidence/A1-241880485/execution/classroom_helpers.sh
lab_ready
lab_new_run e8 A
```

然后依课程 `8_E8_A组.md` 的分步代码1–7执行，核对本次行号；本目录`execution/e8-a1-route.sh`保留了当时官方七代码块及扩展的完整调用，可据实际路径适配。不能把已经创建的OUT再传给要求目录不存在的一键入口。

```bash
docker run --rm --network none --user "$(id -u):$(id -g)" -e HOME=/tmp \
  -v "$PWD:/course" -w /course course-e8e10:241880485 \
  python3 -m unittest discover -s labs/e8e10 -p 'test_*.py' -v
```

个人新测试是`labs/e8e10/test_student_241880485.py`；它的人工小样不是实际trace。扩展另外用新OUT，旧标准基线保持原样。环境代码没变时复用镜像，挂载代码修改后用新OUT验证。

GitHub操作使用本机已有授权，云机接收同SHA的Git bundle并设置原origin，不存GitHub token。推送/个人PR的记录与原始运行源码SHA用途不同，不能把随后写报告的新提交伪称当时运行版本。

实际资源为2 CPU / 3.5 GiB，可见内存低于材料4 GiB建议，未宣称达标；本轮无旧doctor输出或强制改阈值。没有完成/认领A2的E9或A3的E10个人任务；CI双轨六条参考路线属于公共回归。
