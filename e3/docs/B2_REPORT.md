# B2 E3 验收报告

角色 B2；日期 2026-10-04。本报告按用户提供的任务分配逐项验收，课程原始实验包未提供，采用手工等价样本。

## B2-1～B2-6

| 任务 | 交付和实测依据 | 结论 |
| --- | --- | --- |
| B2-1 固定输入 | 四份 md-report.json 只含 main.o 缺 config.h，绑定 Makefile.before 与源码哈希；修改 VALUE=2 后仍输出 1，原对象哈希和 mtime 不变 | 通过 |
| B2-2 四种风格 | Target 直接补依赖、Macro 更新 DEPS、Hybrid 更新 HEADERS、Implicit 生成并加载 .d；四份补丁均经 git apply --check 和实际应用 | 通过 |
| B2-3 应用与增量 | 四种均 clean 输出 2；再次修改头文件为 3，不 clean，自动编译并输出 3；继续改 4 后输出 4，无变化构建不重编译 | 通过 |
| B2-4 Implicit/.d | 首次 .d 不存在，修复后首次构建成功；实际 main.d 含 main.o: main.c config.h 和 config.h:；再次改头文件自动重建 | 通过 |
| B2-5 拒绝与恢复 | 原副本输出 1；无效候选打印 B2_INVALID_CANDIDATE，GNU Make 返回 2；候选不接受；恢复 Makefile 原字节后构建、测试再次输出 1 | 通过 |
| B2-6 参考判据 | expected/mdfixer-reference.md 解释期望补丁、来源和行为；明确不能只靠 clean 成功证明 MD 修复 | 通过 |
| E2 遗留检查 | contracts/mdfixer 已是完整目录，无需重新替换；在独立依赖环境中复核既有接口与反例 | 通过 |

## 给 B3 的七列基线

| 版本 | 配置 | 命令 | 人工预期 | 实际观察 | 判断依据 | 出处 |
| --- | --- | --- | --- | --- | --- | --- |
| B2 Target | b2-gcc-O0-project-headers | b2_run_mdfixer_baseline.py | 1→旧1→修复clean2→增量3→增量4 | 1/1/2/3/4，无变化不重编译 | 直接补 config.h；对象 hash/mtime 和编译日志支持重建 | fixtures/mdfixer/styles/target；work/20261004-095323-B2-ae7679 |
| B2 Macro | 同上 | 同上 | 同上 | 同上 | DEPS 增加 config.h，保留原依赖 | fixtures/mdfixer/styles/macro；同一轮 work |
| B2 Hybrid | 同上 | 同上 | 同上 | 同上 | HEADERS 增加 config.h，直接源码项保持 | fixtures/mdfixer/styles/hybrid；同一轮 work |
| B2 Implicit | 同上 | 同上 | 同上；首次没有 .d 也成功 | 同上，生成真实 .d | -MMD -MP 与 -include main.d 实际生效 | fixtures/mdfixer/styles/implicit；work 下 implicit-main.d |
| B2 无效候选 | 同上，Target 副本 | 原始构建→候选验证→finally 恢复→重建 | 候选非零退出，不接受，恢复后输出 1 | 候选 make=2，恢复 make=0、app=0、输出1 | 失败标记可定位；恢复后的 Makefile SHA256 与原输入相同 | invalid-candidate.patch；work 下 rejection-* 日志/快照 |

## 实际证据

主实测目录：[20261004-095323-B2-ae7679](../work/20261004-095323-B2-ae7679/observations.json)。`commands.json` 记录每条 argv、cwd、SHA 上下文、开始时间、退出码、stdout/stderr 路径和日志 SHA256；`inputs/` 冻结输入，`snapshots/` 保存源码、Makefile 与对象状态；`environment.json` 和 `env/toolchain-B2.txt` 保存版本。

另有 [Linux 复跑](../work/20261004-100021-B2-642335/observations.json) 和 [Windows/MinGW 实测](../work/20261004-100113-B2-803cdd/observations.json)，三轮均通过。每轮 82 条命令，其中仅故意注入的 candidate build 非零；Windows 实测为 Python 3.10.10、GNU Make 4.2.1、GCC 8.1.0。环境摘要文件指向最新 Windows 轮次，Linux 工具版本以各轮 environment.json 为准；这些环境不作为跨平台性能对照。

Linux/WSL Ubuntu 22.04，x86_64，GNU Make 4.3，GCC 11.4.0，Git 2.34.1，Python 3.10.12。上下文仓库提交为 `8f5ca88c26bcdf23e76221639d752650f5cbad50`；B2 新样本未提交，明确标注 WORKING_TREE_SNAPSHOT，冻结字节由 SHA256 定位。未将新样本伪称存在于该提交。

`unused.h` 全程保留。实际 `.d` 在 [implicit-main.d](../work/20261004-095323-B2-ae7679/implicit-main.d)；失败日志在 [rejection-candidate-build.stderr.log](../work/20261004-095323-B2-ae7679/logs/rejection-candidate-build.stderr.log)。命令中的退出 23 属于注入的子进程，Make 顶层实测退出 2。

校验入口：`python e3/scripts/b2_verify_evidence.py`。复核的实际命令、日志、退出码及故障注入记录保存在 `e3/evidence/b2-review/`。

Windows 进程最初未提供 CPU 架构环境变量，platform.machine() 为空。通过 GetNativeSystemInfo 补录 AMD64，保留 environment.initial.json 和补录命令日志；运行器也已加入原生 API 回退，后续同类环境可直接记录架构。复核在临时克隆中独立验证四个反例：篡改输出、删除真实 .d、错误接受失败候选、破坏恢复文件，检查器均拒绝；材料恢复后再次通过。

## 失败、恢复与边界

已有 E2 合约校验首次在 Windows Python 缺少 jsonschema；WSL 系统版 jsonschema 过旧，不含 Draft202012Validator。本次在独立临时 Python 环境安装满足现有约束的依赖，再执行既有校验，不修改公共 Schema 或依赖约定。失败与重试均在复核记录中保留。

仅凭本实验不声称检测器准确率、MDFixer 服务已实现或真实重检已完成。人工参考答案与真实构建行为各自保存；全组互查、公共 README 汇总由 A3/B3 继续组织。姓名、Git 作者、最终提交 SHA 待本人补齐，当前未创建或推送提交。
