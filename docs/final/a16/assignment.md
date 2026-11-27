# A16 期末分工与验收

组内建议 11 月 29 日 20:00 前提交复验文档。课程要求 12 月 1 日前按助教通知的小组入口提交。

本组统一使用 DevOps-G16 的 `projects/transfer-eta`。期末基础路线已在 A16 云机通过。请各自在独立环境复验负责的部分，记录自己实际运行的步骤。复用同一对提交，方便把 E12 结果与 Compose 故障演练对起来。

## 开始前

- 登录 A16 云机，确认能运行 `docker compose version`。在自己的目录检出期末分支 `student/241880485/final-microservice`。代码、运行条件和证据入口见 [期末实验 README](https://github.com/Lilyly9/DevOps-G16/tree/student/241880485/final-microservice/labs/final-microservice)。
- 共同输入为基线 `5ef9d829e2f893af23f60399dcb67095800d121e`，目标 `e7414083c4f1760cb234f96a9d75f2d0255e3f57`。目标版 `eta_cli.o` 缺少 `defaults.h` 的 Make 依赖。使用课程发放的 `Microservice_Lab.zip` 和各自的课程镜像。

## A2 万宇 241880496

1. 按仓库 README 运行 `run-e12.sh`，参数使用自己路径下的课程 ZIP。保存请求、五阶段结果和候选镜像核验。验收时核对基线和目标、同一 job/trace、报告和补丁 SHA，以及最终无缺失依赖。
2. 检查同次脚本中的错误补丁复验。确保干净构建和普通测试通过，修改 `defaults.h` 后仍得到 `eta_seconds=13`，预期是 `eta_seconds=20`。核对补丁被拒绝以及验证前后 HEAD、工作区和 Makefile 哈希一致。
3. 在复验文档中列出成功任务的 job/trace、候选镜像 ID、运行归档 SHA256，以及 `e12-image-and-artifacts.json`、`rejection.json` 和前后状态的证据位置。

## A3 林涵 241880464

1. 按仓库 README 准备三个镜像，运行 `run-real.sh`。先确认四个角色和监控就绪，再走正常、停 EChecker、恢复三个阶段。只操作这次脚本生成的 Compose 项目。
2. 验收两次成功均走完五阶段，停机任务在增量阶段报告 `DOWNSTREAM_UNAVAILABLE`。Grafana 显示 EChecker 探测 `1 → 0 → 1` 和成功 2、失败 1。用失败 job/trace 找到对应角色和错误。
3. 在复验文档中列出三个任务的 job/trace、运行归档 SHA256、故障日志位置，以及覆盖三阶段的 Grafana 截图或导出。

## 提交复验文档

- A2 写入 `docs/final/a16/A2-241880496.md`，A3 写入 `docs/final/a16/A3-241880464.md`，分别提交并推送到仓库中的个人分支。
- 文档顺序为**姓名和运行日期、源码 SHA 与镜像、执行命令、结果与任务编号、证据路径及本人完成的工作**。证据用仓库相对路径或可访问的链接引用，原始归档注明 SHA256。若运行失败，写明卡点并保留实际错误与日志位置。

提交材料排除 `.env`、密码、密钥和服务器登录信息。
