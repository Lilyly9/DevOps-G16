# DevOps-G16

南京大学 DevOps 课程项目，A16 / B16 共用仓库（G16）。包含接口契约、测试基线、容器化及 E5–E7 实验。

服务流程：`DRAFT → BuildChecker → EChecker → MDFixer → 构建、测试与复检`。

## 目录导航

| 阶段 | 内容与入口 |
| --- | --- |
| E2 | [公共任务模型](contracts/task.schema.json)；[DRAFT](contracts/draft/README.md)、[BuildChecker](contracts/buildchecker/README.md)、[EChecker](contracts/echecker/README.md)、[MDFixer](contracts/mdfixer/README.md) 接口 |
| E3 | [四服务测试基线与证据校验](e3/README.md) |
| E4 | [容器化实验](e4/)：[A 轨道](e4/A-buildchecker/README.md)、[B 轨道](e4/B-draft/README.md) |
| E5 | [复现实验、候选与报告](e5/README.md) |
| E6 | [自动检测 / 构建验证、状态与报告](e6/README.md) |
| E7 | [测试、CI 与合并门禁](e7/README.md) |

E5–E7 共用一份代码：A 轨道在 `e5/A-buildchecker/`，B 轨道在 `e5/B-draft/`；E6、E7 目录仅存阶段材料。

## E5–E7 开始实验

在具备 Docker、Git 和 Python 3 的 Linux 云服务器执行，从仓库根目录进入对应实验包：

```bash
cd e5/B-draft  # A 轨道改为 e5/A-buildchecker
python3 scripts/lab_cloud.py doctor
python3 scripts/lab_cloud.py --help
```

使用 `lab_cloud.py`；包内旧 Makefile / Compose 属于 E4。具体步骤和验收状态见对应阶段 README，不以本地单测代替真实 Docker 实验。

## 协作约定

- 使用个人分支与学号镜像标签：`course1020-buildchecker:<学号>` / `course1020-draft:<学号>`。
- 每次运行使用新的 `work/` 子目录，不覆盖已有证据；选取证据归档到对应阶段的个人 `evidence/` 目录。
- 只修改本人负责内容；新增测试独立命名，保留其他成员的测试和证据。
- 在 [AI_USAGE.md](AI_USAGE.md) 和 [CONTRIBUTIONS.md](CONTRIBUTIONS.md) 记录本人的 AI 使用与贡献；验收结论以实际日志和报告为准。

设计与待办：[ADR](docs/ADR.md) · [Backlog](docs/Backlog.md) · [接口集成检查](docs/INTEGRATION_CHECK.md)。
