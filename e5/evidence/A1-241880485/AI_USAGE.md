## A1：E5 复现与补测（2026-10-24）

- 成员：焦龙 / 241880485；工具：OpenAI Codex。用户要求阅读最新第5–7次材料并按分工完成 A1，特别区分助教包中的额外资料。
- AI 核对三份 PPT、私发分工与学生包，复用最新 main 已有代码；没有把外层助教演示、E6/E7 参考实现或 B 模型候选认领为 A1 成果。
- AI 提出“Make 自身打开头文件不应归给编译 recipe”的独立回归，在唯一 test_extra_241880485.py 实现；读取原始 PID/行号编写手工 MD/RD 解释，不以人工小样冒充实际 trace。
- 实际在本人 A16 新克隆构建新镜像，容器 pytest 18 passed，E5 新 run 退出 0；Docker Hub frontend 超时后在本人工作目录复用 E4 网络构建副本，固定 digest/依赖锁未变，未改共享 Dockerfile或 daemon。
- 原环境自检因 3.5 GiB < 4 GiB 退出 1，保持失败原件与 ENVIRONMENT_BLOCKED 状态；没有降低标准后宣称通过。A1 报告/证据含来源、源码 SHA、镜像 ID、真实命令、行号及文件哈希。
- 结果见 [A1 报告](e5/reports/A1-241880485.md) 和 [证据入口](e5/evidence/A1-241880485/index.md)。本记录描述 AI 协助执行，不伪造人工签名或全员确认；未贴密码、Key 或 GitHub 凭据。
