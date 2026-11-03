# E8 阶段索引

共用代码在仓库根 `run_lab.py` 与 `labs/e8e10/`；原 E4–E7 保留。所有实验在个人克隆的 Git 根运行。

| 主责 | 轨道 | 交付重点 | 状态/证据 |
| --- | --- | --- | --- |
| A1 | A | 真实基线/复用 | 标准/扩展实测通过，8项容器测试OK；[证据](evidence/A1-241880485/index.md)、[报告](../docs/students/241880485/e8-e10/个人报告.md)；个人远程CI待PR |
| B1 | B | 固定MD/候选/旧报告拒绝 | 待本人填 |

个人分支 `student/<学号>/e8-e10`；个人报告/ADR/AI_USAGE 位于 `docs/students/<学号>/e8-e10/`。完整原件在本人 `work/`，阶段精选证据/索引放本目录 `evidence/<角色>-<学号>/`。

个人测试新建 `labs/e8e10/test_student_<学号>.py`；本地和新 CI 统一 `python3 -m unittest discover -s labs/e8e10 -p 'test_*.py' -v`，保留原7项。

## A1 本轮实测

源码 `9ee3242f8d7ea1b6bb4091e2947d85d33a37aa8a`；标准 OUT `work/e8-A-manual.vwDixM`，扩展 `work/e8-A-manual.jA7ZjJ`。真实 BuildChecker 基线得到 MD config.h / RD unused.h；未变化时复用 main.o/helper.o、无刷新。

A1 自主测试修改 config.h 间接包含 extra.h；新 OUT 中两个对象刷新、新增 MD extra.h，增量/全量/动态图一致。原7项+A1新增1项，本人云机容器实际8项OK。资源3.5GiB低于建议，未抄旧doctor结论或假称达到4GiB。

公共导入 [PR #13](https://github.com/Lilyly9/DevOps-G16/pull/13) 已正常合并；个人PR/CI按 [CI记录](../docs/students/241880485/e8-e10/CI记录.md) 补真实结果。E9/E10仍由相应成员按分工完成。
