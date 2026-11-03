# E9 阶段索引

共用代码在仓库根 `run_lab.py` 与 `labs/e8e10/`；原 E4–E7 保留。所有实验在个人克隆的 Git 根运行。

按最新助教要求，每人须在个人分支完整完成本组轨道 E8、E9、E10。角色的阶段讨论安排不能替代本人运行；A16 ↔ B16 的跨组交换与联调留至 E11—E12。

| 成员 | 轨道 | 交付重点 | 状态/证据 |
| --- | --- | --- | --- |
| A1 / 241880485 | A | 本人 C0–C3、真实构建、变化驱动图更新、间接 include 独立测试 | [本人 E9 证据](evidence/A1-241880485/index.md) |
| A2 | A | C0-C3图更新 | 待本人填 |
| B2 | B | 三种风格候选 | 待本人填 |

个人分支 `student/<学号>/e8-e10`；个人报告/ADR/AI_USAGE 位于 `docs/students/<学号>/e8-e10/`。完整原件在本人 `work/`，阶段精选证据/索引放本目录 `evidence/<角色>-<学号>/`。

个人测试新建 `labs/e8e10/test_student_<学号>.py`；本地和新 CI 统一 `python3 -m unittest discover -s labs/e8e10 -p 'test_*.py' -v`，保留原7项。
