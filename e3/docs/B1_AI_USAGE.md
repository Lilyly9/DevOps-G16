# B1 E3 AI 使用记录

### 工具与任务

- 成员:郭德林(Git 作者 `DelinGuo`)。
- 工具:Claude Code(Anthropic Sonnet 4.6 CLI)。
- 任务:阅读 `E3_TASKS.md` 与《E3_并行测试基线_20260910.pptx》B1 相关页面(E3/30–33 等),在本仓库完成 DRAFT 样本、失败/成功双层判据的实测证据、样本清单与本人文档,并按两段式提交。

### 提示摘要

- 用户唯一指令:"阅读E3_TASKS.md与E3PPT,完成角色B1对应的任务"。
- AI 解析出的工作范围:B1-1~B1-6;随后就"本机与 WSL 均无 Docker,B1-4/B1-5 如何处理"向用户提问,用户选择"WSL 里安装 Docker(推荐)"。

### AI 建议

- 读取仓库既有 A 组材料后,建议 B1 证据完全沿用 A 组口径:`work/<日期-时间-B1-<sha6>>/` 的 run-id、`commands.json`/`observations.json`/`environment.json` 三件套、`* -text` 字节保护与 `/runtime/` 忽略规则。
- 样本按 PPT 口径手工等价构造(课程实验包未取得),`expected/draft-sample.md` 标注 `MANUAL_EXPECTED` 并注明"PPT 行为目标为给定验收口径"。
- 编写可重跑的运行器 `e3/scripts/b1_run_draft_baseline.py`(分 build/docker 两阶段,幂等,按命令 id 覆盖),而非一次性命令堆砌。
- 执行细节建议:用 `wsl -u root` 完成 apt 安装与 docker 层;为 make 层建立 `runtime/` 副本避免污染冻结样本;Docker Hub 直连失败后配置 NJU/DaoCloud registry mirror。

### 人工采纳、修改与拒绝

- 采纳:全部产物位置、命名、`provenance` 标注与两段式提交顺序(先样例与证据,后文档),与 E2 以来的仓库纪律一致。
- 采纳用户选择:在 WSL 安装 Docker(apt 安装 docker.io),而不是放弃实测或改用其他环境。
- 修改:AI 初版脚本把 `make: not found` 判据只写在 stderr 检索上,实际日志证明 legacy builder 把详细输出写入 stdout;按实际观察把判据改为 stdout+stderr 联合文本,并修正重跑时 `failures` 条目残留的问题。
- 修正:AI 首次填写 `toolchain-B1.txt` 时凭印象写了 git 版本(2.51.0),核对 `env-git.stdout.log` 后改为实际值 2.53.0——版本号一律以运行日志为准。
- 未做:不修改 A1/A2/A3/B2/B3 的任何文件或记录段;不把人工预期写成工具输出;不声称四服务总表或全组确认已完成(那是 B3/A3 的汇总职责)。

### 验证

- 双层判据逐条核对:`make` 退出 0、`./hello` 输出 `hello E3` 退出 0;broken 构建退出 127 且 `make: not found` 可检索;reference 构建与容器运行均退出 0 且输出 `hello E3`;镜像 ID 与 Dockerfile diff 已保存(见 draft-sample.md 对照表)。
- 在仓库根目录运行 `python e3/validate_e3.py`,结果 PASS(4 个 run;该校验声明不检查 B 组,但确认 B1 的 run 目录未破坏 A 组校验)。
- 抽查 `commands.json` 与日志文件的一致性(stdout/stderr 路径均存在、退出码与状态记录一致)。
- `git status` 复核仅新增 B1 自有文件,未触碰他人记录。
