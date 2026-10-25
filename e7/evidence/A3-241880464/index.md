# A3 E7-A 证据索引

本目录保留首轮记录。**最新结果见 [云端索引](cloud-20261024/index.md)、[本地补齐索引](course-recheck-20261024/index.md) 与 [验收记录](验收记录.csv)**；两轮记录对应不同源码提交，不能互相替代。

角色 A3；林涵；241880464。运行日期：2026-10-24（北京时间）。来源：**ACTUAL_RUN**，由本地 CachyOS Linux + Docker 实际执行，不是课程云主机运行，也不是人工答案。源码提交 `6c12a45c6a0ad111f077cb5234c3bd7f5a8d3a73`；所有服务、脚本与测试 Python 源码哈希见 `verification.json`。

## 命令与重跑

从已同步 main 的个人分支进入 `e5/A-buildchecker`，确认 `docker buildx version` 可用并设置本人 Git 本地身份。`NN` 替换成新的编号，输出目录不得复用：

```sh
python3 scripts/doctor.py --out work/doctor-A3-NN.json
python3 -m unittest discover -s tests/e7 -v
python3 scripts/lab_cloud.py build --out work/build-A3-NN --image course1020-buildchecker:241880464 --build-timeout 1200
python3 scripts/lab_cloud.py gate --out work/e7-A3-NN --image course1020-buildchecker:241880464
```

本次成功目录为 `work/build-A3-03`、`work/e7-A3-01`。宿主机缺 buildx 的前两次构建失败保留原目录，未作为成功证据；本次使用下载并校验官方 SHA256 的 v0.38.1 插件，`DOCKER_CONFIG=<TASK_DOCKER_CONFIG>`。临时目录重启后可能消失，重跑请先安装/准备 buildx；不修改共享实验脚本掩盖缺失工具。

## 文件与关键结果

| 路径 | 应查看的内容 |
| --- | --- |
| `doctor.json`、`doctor.log` | 环境与工具版本，`problems=[]`；全局身份/镜像加速建议仍保留 |
| `oracle-tests.log` | 6 tests OK |
| `build/unit-tests/stdout.log` | 18 passed：原始 15 + A2 的 2 + A3 的 1 |
| `build/image/stdout.log` | 本次真实镜像 inspect |
| `gate-result.json`、`results.csv` | 8/8 通过；CSV 为表头 + 八条场景行 |
| `driver/exit-code.json` | gate 总退出码 0 |
| `cases/<场景>/evidence/findings.json` | 状态、findings、trace_id、输入哈希与耗时 |
| `cases/<场景>/evidence/trace/` | 发现引用的关键原始 trace 文件；锚点含文件及行号 |
| `cases/<场景>/evidence/trace-index.md` | 完整 trace 原始路径、总数、已归档文件及重采方法 |
| `verification.json` | 原始三次错误集合一致、trace_id 独立、仅 Makefile 哈希变化的额外核验 |

人工判据来自实验任务要求，写在报告中；这里的 JSON/CSV/日志均为真实输出，不把人工预期写成工具发现。完整原始 trace 保存在本机原始 work；CI artifact 包含对应远程运行的完整 trace。未提交编译产物或完整 trace 大包。

预期与实际一致：原始三次都是 `MISSING(main.o, config.h)`、`REDUNDANT(main.o, unused.h)`，检测成功但 CLI 退出 1；修复后 findings 空、退出 0，输入只有 Makefile 变化。构建失败为 FAILED/CHECK_FAILED，超时为 TIMED_OUT/TIMEOUT；多输出是 **status=FAILED、error_code=UNSUPPORTED**，并非 status=UNSUPPORTED。

## 公开副本的脱敏说明

本目录是实际运行证据的公开脱敏副本。宿主机名、本人邮箱、宿主机绝对仓库路径和临时 Docker 配置路径已替换为明确占位符；被替换的 command.json 仅供说明，重跑请使用上文命令并代入实际路径。没有改变判据、退出码、findings、trace_id、输入哈希和测试数量。

未脱敏原件保存在本机忽略目录 `e5/A-buildchecker/work/A3-private-delivery-originals/`，不推送。`redaction.json` 记录脱敏范围及原始文件哈希；`SHA256SUMS.json` 对应当前公开副本。CI 原始 artifact 可按 run ID 从 GitHub 下载，原始 artifact 文件哈希清单仍对应下载原件。

## 新增课程材料补齐后的验证

最新本地结果请先阅读 [本轮索引](course-recheck-20261024/index.md) 与 [验收记录](验收记录.csv)。前面的日志和旧 CI 仍对应原始提交，不能用来声称新工作流已经在 GitHub 运行。所有本轮结果仍只保留本地。


## 2026-10-25 最新 CI 验收

[官方失败拒绝、恢复和普通合并证据](../../ci/A/official-protected-20261025/index.md)：A 项已通过，完整共享配置与资源门槛仍待确认。
