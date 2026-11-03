# A3 新材料补齐后的本地验证

林涵 / 241880464 / G16 A16。源码提交 `a977ac905e7767ec4ec438fe3b4d84963b3dd824`；运行日期 2026-10-24（北京时间）。本目录是实际本地运行的脱敏副本，未推送；完整未脱敏原件保留在忽略的 `e5/A-buildchecker/work/course-recheck-A3-20261024T114803Z/`。操作系统为 CachyOS，**不是课程云主机，也不是新版 GitHub Actions 的运行记录**。

## 预期与实际

| 项目 | 实际结果 | 证据 |
| --- | --- | --- |
| doctor | problems=[]，退出 0 | environment.json、steps/doctor/ |
| Python 语法 | 退出 0 | steps/syntax/ |
| 独立判定测试 | 6 项通过 | steps/oracle-tests/ |
| 扫描回归 | 2 项通过；旧编码不崩溃，模拟密钥仍被检出且遮蔽 | steps/scanner-tests/ |
| 全仓库及全部 Git 历史扫描 | 未发现扫描规则覆盖的疑似密钥，退出 0 | steps/source-history-scan/ |
| 正常服务镜像 | 重建成功，18 passed | normal-build/ |
| 镜像扫描 | 退出 0 | steps/image-scan/ |
| 正式 gate | 退出 0，8/8 | gate-result.json、results.csv、cases/ |
| 官方错误测试 | Docker 构建 0；单测 1 failed / 18 passed；入口退出 1 | official-demo/bad/ |
| 官方修复测试 | 19 passed；入口退出 0；gate 8/8 | official-demo/fixed/ |
| 工作流静态检查 | actionlint 1.7.12，退出 0 | steps/workflow-lint/ |
| 路径门控 | 5 个本地场景通过：A 变更、仅文档、PR、手动、新分支 | steps/path-gating/ |
| 容器清理 | 本轮 16 个 gate 容器 ID 均已不存在 | steps/container-cleanup/ |
| A2 已交证据复核 | 校验通过，仅 Makefile 改变；不称为本人复跑 | steps/a2-reference-verify/ |

## 从个人分支重跑

进入 `e5/A-buildchecker`。确认 docker/buildx 可用；本机本轮临时插件使用 `DOCKER_CONFIG=/tmp/devops-a3-docker`，其他机器按自己的实际环境准备，不能假设临时目录存在。以下 NN 必须换成未使用的新编号：

```sh
python3 scripts/doctor.py --out work/doctor-A3-NN.json
python3 -m compileall -q services/buildchecker/buildchecker services/buildchecker/tests scripts tests
python3 -m unittest discover -s tests/e7 -v
python3 -m unittest discover -s tests/tooling -v
python3 scripts/secret_scan.py ../.. --history
python3 scripts/lab_cloud.py build --out work/build-A3-NN --image course1020-buildchecker:241880464 --build-timeout 1200
python3 scripts/secret_scan.py ../.. --image course1020-buildchecker:241880464
python3 scripts/lab_cloud.py gate --out work/e7-A3-NN --image course1020-buildchecker:241880464
```

官方失败/修复演示应在独立副本或演示分支中分别复制 `ci/rejection-demo/A/test_ci_reject_demo.py`、`ci/rejection-demo/fixed/test_ci_reject_demo.py` 到服务 tests，然后每次重建镜像。本轮两份副本保留于 raw/official-demo；未将故意失败测试放入正常服务 tests，也未修改算法。

`steps/*/command.json` 保存实际命令；原命令中本机绝对路径已替换成 `<REPO>` 等占位符，不能直接当作可复制命令。Docker 子步骤退出码见各自 exit-code.json。源码与输入哈希、三次独立 trace_id 和完整场景判据见 verification.json 和 findings.json。部分 trace 为节选，原始完整记录留在本机并备份到 ZIP。

本轮没有执行 GitHub 推送、PR 更新、保护配置或合并；这些项目仍为 PENDING。
