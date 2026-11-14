# A1 E11–E12 证据索引

焦龙（241880485），A16，BuildChecker，配对 B16。E11-A 实验于 2026-11-14 在 A16 Linux 完成。执行源码 `456a375221ee963140b68be4afd2b26a96cc0f19`，编排镜像 ID `sha256:40b15f7e375e5bbbb5929f2f22f52f4a194a340b1970d340512af444f69320a5`。云端原件根目录为 `/root/241880485/DevOps-G16-e11-A1-20261114/work/e11-a1-241880485-20261114.HTL9X4`。[个人报告](report.md) · [ADR](ADR.md)

| 验收项 | 实际判据与入口 |
| --- | --- |
| 编排镜像 | 首次拉取 Docker CLI 镜像 metadata 超时，退出 1；通过课程镜像站解析同一 digest 后构建退出 0。两次云端目录尾号 `8WOHXG`、`VR6DkD`。[环境构建记录](evidence/environment/) |
| E11-A 标准输入 | 课程 `prepare` 生成本次输入，数据清单与请求绑定两份完整提交，目标增加直接 include。[数据清单](evidence/inputs/standard-dataset.json) · [请求](evidence/inputs/standard-request.json) |
| E11-A 标准结果 | `SUCCEEDED`，两对象刷新、新增 `MD(main.o, extra.h)`。基线和目标阶段封装可核对提交、任务、跟踪与产物身份。[基线封装](evidence/standard/full-check.json) · [增量封装](evidence/standard/incremental-check.json) · [实际缓存边溯源](evidence/standard/cache-edge-provenance.json) |
| E11-A 自主版本 | E9 夹具的真实内部历史 C0 → C1。两对象复用，`config.h` MD、`unused.h` RD 维持，新增与消除均为空。[数据清单](evidence/inputs/autonomous-dataset.json) · [请求](evidence/inputs/autonomous-request.json) · [版本差异](evidence/inputs/autonomous-base-target.diff) · [增量封装](evidence/autonomous/incremental-check.json) · [实际缓存边溯源](evidence/autonomous/cache-edge-provenance.json) |
| 完整对照 | 标准与自主各自通过实际图、声明图、完整 MD/RD 三元组的比较。两次基线均保留原始 trace 和 Make 数据库。[实测汇总](evidence/summary.json) · [标准原件](evidence/standard/baseline-full/) · [自主原件](evidence/autonomous/baseline-full/) |
| `STALE_REPORT` | 实际标准封装的只改 commit 副本被拒，原件 hash 核对一致，验证中的下游标记未达。[拒绝记录](evidence/stale-report-result.json) |
| 运行与单测 | 标准、自主、溯源检查均退出 0。课程测试入口在 Linux 容器中运行 19 项，全部通过。[执行日志和退出码](evidence/logs/) · [新增个人测试](../../../../labs/e11e12/test_student_241880485.py) |
| E12 固定样例 CLI | 五阶段通过，共 162 个产物引用通过验证。修复消费本轮增量报告的实际 SHA256，检验 `accepted=true`，最终 0 MD、1 RD `unused.h`。[链路复核](evidence/e12/verification.json) · [修复封装](evidence/e12/repair.json) · [最终复验](evidence/e12/recheck.json) |
| E12 BuildChecker 镜像交接 | 基线、目标和最终全量的六个 clean/trace 容器均使用 DRAFT 构建的完整镜像 ID，每次全量含 10 份 trace。EChecker 扫描与 MDFixer 验证仍在编排容器，A2/B2 的同镜像执行待接入。[基线执行原件](evidence/e12/baseline-full/) · [目标执行原件](evidence/e12/target-full/) · [最终执行原件](evidence/e12/final-full/) |
| E12 组内联调 | 共享 API 与 B 侧独立下载、消费和复验仍待组内联调。 |
| 真实项目 | 等待组内提供符合要求的真实 C/Make 项目、两份完整 SHA 和对应构建输入。 |
| PR 与 CI | 个人草稿 PR #21 基于 B1 分支，等待 PR #20 合入。云端实验源提交 `456a375221ee963140b68be4afd2b26a96cc0f19` 的四项检查成功。E11–E12 的 PR run `43548159901` 产物 `14095027314`，push run `43548058094` 产物 `14094534869` 已下载。[PR #21](https://github.com/Lilyly9/DevOps-G16/pull/21) · [PR #20](https://github.com/Lilyly9/DevOps-G16/pull/20) · [PR CI](https://github.com/Lilyly9/DevOps-G16/actions/runs/43548159901) · [push CI](https://github.com/Lilyly9/DevOps-G16/actions/runs/43548058094) |
| 原件与备份 | 完整云端原件包为 178309 字节，SHA256 `4c6e0364ac295b65e8a6eb505740a439fd55397cc87dc32d709ba556c6ba0de3`。本机个人交付包路径为 `E11-12/A1-E11-E12-个人交付备份-20261114.tar.gz`，校验独立记录。 |

E12 云端运行目录为 `work/e12-a1-draft-image-241880485-20261114T024540Z`，辅助目录为 `work/a1-e12-proof-20261114T024540Z.TjTU9C`。编排 ID 为 `job-8a1ef46c976448698d0f004cbc89d5d2` / `trace-3cd6971ebf334b2788f6f31cd3660d36`。基线 `46fc6c1b74681d6f3746c7d9dff9fca722ca936e`，派生目标 `d5204f53b641173fd3f23c71ae37dda8ac6628e9`。从各全量目录的 `clean-execution.json` 和 `build-execution.json` 核对请求镜像、实际镜像、容器和退出码，再与 DRAFT 镜像 `sha256:c45a0b791b8cdc4cde2841d205fb123ef1e41f854dd7f405b6526758d1c55b1c` 对照。[固定样例验证](evidence/e12/verification.json)

## 复跑入口

在本人 Linux 检出目录中确认实验源码 SHA 与镜像身份。标准样例只需 `prepare` 一次，保留实际生成的请求与数据清单。每次执行使用新的 `work/` 子目录。

```bash
python3 run_e11e12.py test
python3 run_e11e12.py prepare
python3 run_e11e12.py run --request data/integration-sample/e11-a.json --out "work/e11-a1-$(date -u +%Y%m%dT%H%M%SZ)"
```

自主版本可从本人 E9 历史 bundle 恢复。它只公开 bundle 内的 `HEAD`，应恢复到独立仓库的本地分支并核验两份提交可解析。请求中的 `repo` 写为容器内该仓库的 `/course/data/.../repo` 路径，使用实际 base 和 target SHA。标准及自主模式固定为 `e11-a`。六项审查入口为请求、结果、缓存、阶段封装、对象目标全量发现及原始 trace。[原始自主输入与历史记录](evidence/inputs/)

E12 固定样例需准备本轮候选与独立请求，`mode=e12`，候选须提供 `make`、编译器与 `strace`。按环境可达性配置镜像源，保留候选实际哈希与目标提交。使用 `python3 run_e11e12.py run --request <仓库内请求路径> --out <新work子目录>`，完成后逐项核对镜像、阶段身份与修复复验。A1 本次采用课程生成样例及其镜像站派生提交，后续真实项目另换输入和适配配置。[本次 E12 原件](evidence/e12/)
