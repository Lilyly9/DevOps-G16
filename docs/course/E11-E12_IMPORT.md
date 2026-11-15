# E11—E12 公共导入说明

本分支从课程 E11—E12 包导入共享运行器与固定样例，未复制旧 E8—E10 实现：

- 导入来源：课程实验包（与 `00c7ed9` 共享导入一致）
- 导入内容：`run_e11e12.py`、`labs/e11e12/environment/`、`labs/e11e12/vendor/`、`labs/e11e12/pipeline.py`、`labs/e11e12/server.py`、`labs/e11e12/prepare.py`、`labs/e11e12/test_contract.py`、`.github/workflows/e11e12.yml`
- 未导入：其他同学的 `test_student_*.py`、个人证据目录
- 保留：`run_lab.py`、`labs/e8e10/`、旧 E8—E10 证据与已通过的检查；`labs/e8e10/lab.py` 未修改

A2 在导入基线上新增：

| 文件 | 说明 |
| --- | --- |
| `labs/e11e12/project_config.py` | `e11e12-project.json` 配置加载与校验 |
| `labs/e11e12/ecache.py` | 配置化 EChecker、逐目标复用、配置化 patch/validate |
| `labs/e11e12/draft_exec.py` | DRAFT 镜像内执行全量/增量命令并留证 |
| `labs/e11e12/test_student_241880496_e11e12.py` | 个人测试（避免与 `labs/e8e10/test_student_241880496.py` 同名冲突） |
| `labs/e11e12/pipeline.py` | 配置、`project_path`、同镜像执行、阶段上下文 |
| `labs/e11e12/prepare.py` | 固定样例配置与可复现候选 |
| `projects/tokenstat/` | 本人维护的 C/Make 真实项目（故障提交与候选 Dockerfile） |

`data/` 与 `work/` 由根 `.gitignore` 忽略，不随仓库提交；共享样例通过 `python3 labs/e11e12/prepare.py` 生成。
