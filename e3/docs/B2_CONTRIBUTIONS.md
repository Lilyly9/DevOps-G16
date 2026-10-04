# B2 E3 个人贡献记录

- 角色：B2（MDFixer）。
- 姓名：待本人填写。
- Git 作者：待本人填写。
- 最终提交 SHA：待本人提交后填写；本次生成的材料当前在工作区，尚未创建或推送 Git 提交。
- 工作范围：固定 MD 报告、四种声明风格的参考修复、隐式依赖文件、增量行为实测、失败候选拒绝与恢复、人工答案及个人记录。

| 负责文件/目录 | 内容 |
| --- | --- |
| `e3/fixtures/mdfixer/` | 冻结源码、四份固定报告、原 Makefile、参考 Makefile 与 Patch、无效候选、人工 .d 示例 |
| `e3/expected/mdfixer-reference.md` | 人工参考答案、来源、修复与回滚判据 |
| `e3/scripts/b2_run_mdfixer_baseline.py` | 隔离副本运行器、命令和日志保存 |
| `e3/scripts/b2_verify_evidence.py` | 冻结输入、补丁、输出、对象变化及恢复的离线校验 |
| `e3/work/*-B2-*/` | 实际输入、原始日志、命令、源码快照与观察，runtime 构建产物被忽略 |
| `e3/env/toolchain-B2.txt` | 本次 Linux 环境和版本摘要 |
| `e3/evidence/b2-review/` | 本次校验命令、依赖问题与复核记录 |
| `e3/B2_README.md`、`e3/docs/B2_*.md` | 复现入口、验收报告、AI 记录与贡献记录 |

上游源码归属 A1：`main.c/config.h/unused.h` 来自真实提交 `9c36984236b97115f44daa24c5274a90dd905b37`，不将其原创归属改写为 B2。E2 接口目录此前已完整存在，本次只复核，不记为新建贡献。

每轮 source-manifest 中的 base_commit 是运行时仓库上下文；新 B2 样本标记 WORKING_TREE_SNAPSHOT，准确版本由冻结输入 SHA256 确定。它不是用户最终提交 SHA。

提交时仅选择本人文件，提交后用下列命令取得真实 SHA，补入本文件与任务表；不要代填其他成员信息：

```bash
git log -1 --format='%H %an <%ae>' -- e3/fixtures/mdfixer
```

根 `.gitignore` 的 `env/` 规则也匹配 `e3/env/`，因此提交环境摘要时应显式使用 `git add -f e3/env/toolchain-B2.txt`；不要把临时编译产物加入索引。
