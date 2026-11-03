# A1 E9-A 本人完整实验索引

焦龙 / 241880485 / A16；配对 B16。本人完整执行 E9-A 分步手册，OUT 为 `work/e9-A-manual.eqLOHp`。外层源码 `18a79582672a71d486abc656bc9007d4aebdceab`，镜像 `sha256:7461c2bbd458c9a1955c9cfd502d435f8213a8e15b59f952eca833edcfe4e691`。真实环境 2 CPU、3.5 GiB 内存，低于手册 4 GiB 建议，镜像环境未变并核验后复用。

[个人报告](../../../docs/students/241880485/e8-e10/个人报告.md)、[ADR](../../../docs/students/241880485/e8-e10/ADR.md)、[CI记录](../../../docs/students/241880485/e8-e10/CI记录.md)。公共 CI 参考路线不替代本目录本人运行；跨 A/B 联调留至 E11—E12。

| 内层版本 | 被测项目真实提交 | 图复用 | 图刷新 |
| --- | --- | --- | --- |
| baseline | `a817cc09960456b4eac8762d10d69037bf4aa767` | 无 | main.o, helper.o |
| C1 | `8e337b25d26c32f231f711f447c2d6399b435d4d` | main.o, helper.o | 无 |
| C2 | `02e714436272025bcce1ec9983a2be57a0a93e93` | 无 | main.o, helper.o |
| C3 | `35785ee1fa73e80c22a6c4f1067ec303c0a5fb05` | main.o, helper.o | 无 |

C0 精确发现 `MD(main.o, config.h)`、`RD(main.o, unused.h)`。C1 只改表达式：真实 make 日志重编 main.o 并链接 app，helper.o 不重编；依赖扫描仍复用两目标。C2 新增直接 include：保守刷新两目标、新增 `MD(main.o, extra.h)`。C3 只补声明：复用实际图，消除 config.h 与 extra.h 两项 MD，RD unused.h 保留。程序实际输出 1。

| 保存位置 | 内容 |
| --- | --- |
| [standard/baseline.json](standard/baseline.json)、[C1](standard/C1.json)、[C2](standard/C2.json)、[C3](standard/C3.json) | 完整实际图、声明图、发现、added/resolved、复用/刷新、内部 commit |
| [C0-build.log](standard/C0-build.log)、[C1-build.log](standard/C1-build.log)、[C2-build.log](standard/C2-build.log)、[C3-build.log](standard/C3-build.log) | 真正构建命令输出；C3 补充核对为 up to date |
| [project-history.txt](standard/project-history.txt)、[bundle](standard/project-history.bundle)、[完整变更](standard/project-history.patch.log) | C0—C3 四版本，可通过 bundle 在临时目录恢复；外层源码 SHA 与此内部历史不同 |
| `standard/project/`、`standard/*-commit-input.txt` | 最终输入及各版本 Makefile/main.c 快照；最终输入哈希另存 |
| `standard/steps/`、[execution/A1-E9-route-20261103.log](execution/A1-E9-route-20261103.log) | 手册容器步骤及外层命令的真实合并输出和退出码 |
| [execution/e9-a1-route.sh](execution/e9-a1-route.sh) | 原手册十个操作代码块与额外 A1 显式断言；脚本记录实际执行路径 |
| `provenance/`、`unit-tests/` | 源码/镜像/环境、命令、哈希、敏感信息扫描；现有原7项+A1独立1项，8项通过 |
| [archive-scope.json](archive-scope.json) | 原始下载包的 SHA256、路径及 Git 精选排除清单；完整本机备份保留原二进制 |
| `verification/`、`files.sha256.json` | 下载后独立审查与逐文件完整性清单 |

E9 当堂自主任务沿用已提交的 [A1 间接 include 独立测试](../../../labs/e8e10/test_student_241880485.py) 及 [E8 新 OUT 的实际扩展证据](../../../e8/evidence/A1-241880485/extension/extension-check.json)：主文件不变，config.h 新增 extra.h include，旧图失效、两目标刷新，新增 extra.h MD，完整增量/全量与动态图吻合。测试内容未变，本轮在当前源码下重新发现并通过；不为数量复制测试，也不把该扩展代替本次 C0—C3。

按最新助教要求，A1 同时有本人 [E8](../../../e8/evidence/A1-241880485/index.md)、[E10](../../../e10/evidence/A1-241880485/index.md)。本目录不代填其他成员状态。

下载后独立审查：[完整结果](verification/remaining-independent-audit.json)、[审查脚本](verification/audit_remaining.py)。199 项核验通过，errors 为空；内部历史恢复、输入推导集合、逐次计时/统计和三套动态原件重解析均核对，原下载文件哈希未变化。审查的限制在结果内单独列明，不以离线审查重新生成计时。

本人三阶段交付提交 `e835d187fa964d75ffecfd5779dda928526e0560` 已通过 E7-A、E7-B、E8–E10 三门禁；[PR事件run 41610392056](https://github.com/Lilyly9/DevOps-G16/actions/runs/41610392056) 与该SHA精确对应，artifact ID 13217844477 已下载。后续仅归档的最终文档SHA另在本机备份绑定实际CI；个人PR仍待组内审查。
