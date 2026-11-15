# 决策记录（A2 / 241880496 / 轨道 A，E8—E10）

## 背景与约束

参考实现 `labs/e8e10/lab.py` 用 `scan()` 计算"实际读取图（gcc -MM）"与"声明图（Makefile）"的差集，并用 `key` 判断历史图能否复用。`key` 把**全部** `.c`/`.h` 的行首预处理行、Make 配方行、`CFLAGS` 和编译器首行聚合为一个整体：任一处变化，`scan()` 就刷新全部对象目标。

个人实验要求"至少一个独立预期的用例或一项实现改动"，同时不能改变他人（A1/A3 与其他轨道）依赖的既有口径。

## 选择与替代方案

**选择：只做可解释性扩展，不改刷新语义。**

1. `lab.py:48` 新增 `invalidation(key, old)`：返回导致历史图失效的具体文件名列表，或因配方/编译配置/编译器变化返回 `recipes`/`flags`/`compiler`；无历史返回 `['NO_HISTORY']`。
2. `lab.py:81` 在 `scan()` 返回值中追加 `'invalidation'` 键。
3. 新增 `labs/e8e10/test_student_241880496.py` 三项用例（间接 include 边集、仅源码文件失效原因、纯函数体变化不失效）。

替代方案与不选理由：

- **按目标失效（更省）**：以目标自身的源码文件 + 历史实际集合构造签名，仅刷新受影响目标。收益明显（`helper.c` 改 include 时 `main.o` 可复用），但会改变 `refreshed` 的既有期望：`test_profile.py:test_include_added_invalidates_cache` 断言 `len(refreshed)==2`，E9-A 手册第 7 步断言 `set(refreshed)=={'main.o','helper.o'}`，CI 六个一键入口也会随之变化。这属于跨阶段口径调整，应先与组长统一，本次保留为扩展计划。
- **只加用例不改实现**：可以做，但 `invalidation` 让 E10 的六场景表能给出"为什么刷新"，直接支撑报告里复用/刷新逐条解释，成本仅一个纯函数，故一并落地。

## A：缓存何时失效、配置身份如何绑定

- 失效判据：任一项目内 `.c`/`.h` 的行首预处理行集合变化（含新增/删除文件、间接 include、宏定义），或 Make 配方行、`CFLAGS`（仅 `-O0`/`-O1`/`-O0 -DMODE=1` 合法）、编译器首行变化。
- 配置身份：`profile='GCC_LOCAL_HEADERS_EXPLICIT_MAKE'`、`schema_version='e8e10-1'` 写在报告中；`key.compiler` 取 `gcc --version` 首行，保证换镜像/换 gcc 时历史图不再被信任。
- 实测：`include→['main.c']`、`flags→['flags']`、`header→['config.h']`、`body`/`declaration`/`unchanged→[]`。

## B：共享变量怎样处理、失败怎样保证原目录不变

（本人轨道为 A；B 轨道的 `patch()`/`validate()` 只做只读确认，未修改其行为。）观察结论：`patch()` 对 `$(DEPS)` 形式修改变量定义、对混合形式改目标行末尾、对直接形式追加到目标行；`validate()` 在 evidence 沙箱中应用补丁并构建，只有全部 checks 通过才把 `Makefile` 字节写回原目录，失败时 `rollback=True` 且源文件逐字节不变。

## 代价与覆盖范围

- 代价：`scan()` 返回值多一个键（体积可忽略），每次扫描多一次字典遍历。
- 覆盖范围：只报告"哪些输入变了"，不改变刷新粒度；样例只有两个对象目标，收益不体现在墙钟时间上（`full/inc` 0.74–1.18）。
- 兼容性：`actual`/`declared`/`findings`/`added`/`resolved`/`reused`/`refreshed` 语义未变，原 7 项测试与三条手册路线断言全部仍通过。

## 验证命令与实际证据

```bash
docker run --rm --network none -e HOME=/tmp -e PYTHONPATH=/course/labs/e8e10:/app \
  -v "$PWD:/course" -w /course course-e8e10:241880496 \
  python3 -m unittest discover -s labs/e8e10 -p 'test_*.py' -v     # Ran 10 tests, OK
```

- 单测日志：[unit-tests.log](../../../e10/evidence/A2-241880496/unit-tests.log)
- 六场景失效原因：[E10 证据索引](../../../e10/evidence/A2-241880496/index.md)
- 三条路线逐步日志：`e8/e9/e10/evidence/A2-241880496/steps/*.log`（均以 `STEP_EXIT_CODE=0` 结束）
