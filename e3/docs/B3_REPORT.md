# E3 B3 相互检查与 B 组汇总报告（2026-10-04）

角色 B3；范围是课程 `E3_TASKS.md` 的 B3-1～B3-5。本文只做汇总与检查，不代填他人身份，也不把离线材料写成已获全员确认。

## B3-1 目录与命名对齐

核对 B1/B2 的 `e3/` 产物位置、`work/<run-id>` 命名、日志与人工标签是否与 A 组一致：

| 检查项 | 结论 |
| --- | --- |
| 样本目录 | B1 `fixtures/draft/`、B2 `fixtures/mdfixer/` 与 A 组 `fixtures/md-rd/`、`fixtures/commits/` 同层；通过 |
| 运行目录命名 | B1 `work/20261004-115744-B1-8f5ca8/`、B2 `work/20261004-095323-B2-ae7679/` 等，均采用 `<日期-时间-成员-编号>` 格式；通过 |
| 人工标签 | B1/B2 的 `expected/` 均标注 `MANUAL_EXPECTED`，`work/` 标注 `ACTUAL_RUN`；通过 |
| 环境记录 | B1 `env/toolchain-B1.txt` 存在；**B2 `env/toolchain-B2.txt` 被文档引用但未创建/未入库**（受根 `.gitignore` 的 `env/` 规则影响，需 `git add -f`），已记 Backlog |

## B3-2 四服务七列总表

已将 A1 MD/RD、A2 C0/C1/C2、B1 DRAFT、B2 四种声明风格与无效候选并入 `e3/README.md` 的七列表格（版本/配置/命令/人工预期/实际观察/判断依据/出处）。B2 的七列由 [B2_REPORT.md](B2_REPORT.md) 的"给 B3 的七列基线"转录，B1 的七列由 [draft-sample.md](../expected/draft-sample.md) 的判据表转录。总表待全员确认。

## B3-3 文档沉淀

- `docs/Backlog.md`：新增"E3 B3 收尾后待协作项"，记录四服务总表确认、B2 环境摘要缺失、E3 B2 姓名/Git 作者、§10 相互检查汇总等未决项。
- `docs/ADR.md`：新增 ADR-004，记录"手工等价样本 + 人工/实际分离 + 运行目录不覆盖 + 环境不混作性能对照"的基线策略与理由。

## B3-4 相互检查（B 组查 A 组，§10 四问）

| §10 四问 | A 组检查结论 |
| --- | --- |
| 1. 别人能按 README 运行吗？ | 能。`e3/README.md` 给出仓库根命令；A1/A2 入口列出真实 SHA 与复现命令，A2 还给出缺 tag 的安全补齐步骤；A3 已在临时克隆独立复跑通过（`evidence/a3-review/20261003/`） |
| 2. 人工答案和实际日志分清了吗？ | 分清。`expected/` 全为 `MANUAL_EXPECTED`，`work/` 的 `observations.json` 标注 `ACTUAL_RUN`，未混写 |
| 3. 预期结果能说明依据吗？ | 能。A1 的 MD（`main.o→config.h`）与 RD（`main.o→unused.h`）各有一条可核验依据，并明确"只有 `openat` 不足以独立判 MD"；A2 C0/C1/C2 每个版本都有预期发现 + 行为（10/12/12→13/12 vs 19） |
| 4. 失败记录能定位到具体版本吗？ | 能。日志带版本名，`commands.json` 记录 argv/cwd/退出码，A1 样本 SHA `9c36984…`、A2 C0/C1/C2 三个真实 SHA 可 checkout |

B 组自身同样满足四问：B1 的卡点记录（Docker Hub 重置、legacy builder 输出分流、WSL safe.directory、sudo 密码）每条都带版本与下一步；B2 的三轮实测（Linux 复跑、Windows/MinGW）与 WORKING_TREE_SNAPSHOT 标注可定位。

## B3-5 贡献汇总

- `CONTRIBUTIONS.md`：追加 B3 的 E3 段（本文件对应的交付）。
- `AI_USAGE.md`：追加 B3 的 E3 段（见 [B3_AI_USAGE.md](B3_AI_USAGE.md)）。
- B1/B2 的 E3 贡献已在 `e3/docs/B1_CONTRIBUTIONS.md`、`B2_CONTRIBUTIONS.md` 由本人记录；E3 B2 姓名/Git 作者与最终提交 SHA 仍待其本人补齐，B3 不代填。

## 未决项（详见 Backlog）

1. 四服务七列总表待全员确认。
2. B2 环境摘要 `env/toolchain-B2.txt` 缺失。
3. E3 B2（Lilyly9）姓名/Git 作者待其本人补齐。
4. 待 A3 完成 A 组对 B 组的四问检查后汇总 §10 结论。
