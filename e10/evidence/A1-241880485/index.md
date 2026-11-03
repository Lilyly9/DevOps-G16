# A1 E10-A 本人完整实验索引

焦龙 / 241880485 / A16，配对 B16。标准 OUT：`work/e10-A-manual.eVOOik`；自主删除场景 OUT：`work/e10-A-manual.n9BhPY`。外层源码 `18a79582672a71d486abc656bc9007d4aebdceab`，镜像 `sha256:7461c2bbd458c9a1955c9cfd502d435f8213a8e15b59f952eca833edcfe4e691`。环境未改、已核验复用；2 CPU、3.5 GiB 可见内存，低于建议 4 GiB。

本人执行结果：标准六类各五次，**30/30 完整 actual/declared/findings 集合一致**，保存全部 60 份逐次 JSON；自主任务另有五次、10 份 JSON。标准最终和扩展前后共三套真实 BuildChecker trace、数据库、图、发现均保留。结果不是教师演示或队友运行。

[个人报告](../../../docs/students/241880485/e8-e10/个人报告.md)、[ADR](../../../docs/students/241880485/e8-e10/ADR.md)、[AI_USAGE](../../../docs/students/241880485/e8-e10/AI_USAGE.md)、[CI记录](../../../docs/students/241880485/e8-e10/CI记录.md)。PR 的 CI 是公共回归，与本目录手册交付区分。

| 类别 | n | 增量中位数 ms | 全量中位数 ms | 增量范围 ms | 全量/增量 |
| --- | --- | --- | --- | --- | --- |
| unchanged | 5 | 1.751385 | 10.083498 | 1.733246–2.371456 | 5.7574 |
| body | 5 | 1.752061 | 10.217140 | 1.715209–2.161571 | 5.8315 |
| include | 5 | 10.148967 | 9.944403 | 10.008659–11.463852 | 0.9798 |
| declaration | 5 | 1.763683 | 10.198696 | 1.752740–2.160252 | 5.7826 |
| flags | 5 | 10.235706 | 10.032028 | 10.131463–11.393623 | 0.9801 |
| header | 5 | 10.127683 | 10.062317 | 10.051824–11.355276 | 0.9935 |

计时来自 [results.csv](standard/matrix/results.csv)，手册原始统计为 [performance-summary.csv](standard/matrix/performance-summary.csv)。`scan()` 包含解析、Git/编译器检查及必要的 gcc -MM；不是完整 clean build 的时间。刷新场景比值略低于 1，按原数记录，不推广为论文规模的加速结论。每次重复均从同一上一场景历史图开始，未将第一次刷新后的图作为第二次历史。

unchanged/body/declaration 复用两个目标；include/flags/header 保守刷新两个目标。include 新增 extra.h MD；declaration 消除两项 MD，RD unused.h 始终保留。标准 header 场景在已有直接 include extra.h 的基础上增加间接 include，所以签名失效，但完整依赖集合不再新增 extra.h 边。

| 保存位置 | 内容 |
| --- | --- |
| `standard/matrix/*-rN-incremental.json`、`*-full.json` | 六类各五对，含完整集合、commit、key、真实耗时与刷新/复用；CSV可逐行回查 |
| [standard/matrix/gate.json](standard/matrix/gate.json)、[显式核对](standard/matrix/a1-complete-check.json) | 手册 gate 与额外完整人工集合预期/动态对象图断言 |
| `standard/matrix/final-buildchecker/` | 原始 t.*、进程、make-db、图、发现，最终无 MD，保留 RD unused.h |
| [标准内部历史](standard/matrix/project-history.txt)、[bundle](standard/matrix/project-history.bundle) | 六个内部提交，C0 + body/include/declaration/flags/header，关联原输入及完整变更 |
| [扩展独立预期](extension/independent-expected.json)、[五次CSV](extension/results.csv)、[统计](extension/performance-summary.csv) | 先陈述删除场景的完整图/发现及差分预期，再执行五次 |
| [extension/gate.json](extension/gate.json)、`extension/buildchecker-before/`、`extension/buildchecker-after/` | extra.h MD 消除、两个目标刷新，增量/全量/独立预期/动态图一致，程序输出1 |
| [扩展内部历史](extension/project-history.txt)、[bundle](extension/project-history.bundle) | 三版本：C0、增加间接 include 的旧状态、移除 include 并删除 extra.h 的新状态 |
| `execution/`、`standard/steps/`、`extension/steps/` | 原手册13个操作块、独立场景脚本、helper、整体日志、步骤退出码与运行时间边界 |
| `provenance/`、`unit-tests/` | 元数据、源码与输入哈希、镜像与锁、敏感信息扫描、原7项+A1一项独立测试通过 |
| [archive-scope.json](archive-scope.json)、`verification/`、`files.sha256.json` | 原始下载包身份、二进制排除边界、下载后独立审查及逐文件校验 |

自主任务的输入先让 config.h 间接包含 extra.h，建立旧图；然后移除该 include 并删除 extra.h。显式预期为 main.o 实际依赖回到 `[config.h, main.c]`，helper.o 为 `[helper.c]`；声明仍是 main.c/unused.h；发现精确剩 MD config.h、RD unused.h，`resolved=[[MISSING,main.o,extra.h]]`，`added=[]`。五次均从同一旧图扫描，均刷新两个目标；删除的文件没有悬空 include，因此构建实际成功。该场景补充标准矩阵没有覆盖的删边与发现消除，不复制队友扩展。

原 E8 证据和本机旧 E8 包保留。完整新个人备份按用户选择仅保存在本机，另附 SHA256；它不是 A16 全组包。A1 本人 [E8](../../../e8/evidence/A1-241880485/index.md)、[E9](../../../e9/evidence/A1-241880485/index.md) 与本目录共同覆盖三个阶段；E11—E12 跨组联调未开展。

下载后独立审查：[完整结果](verification/remaining-independent-audit.json)、[审查脚本](verification/audit_remaining.py)。199 项核验通过，errors 为空；内部历史恢复、输入推导集合、逐次计时/统计和三套动态原件重解析均核对，原下载文件哈希未变化。审查的限制在结果内单独列明，不以离线审查重新生成计时。
