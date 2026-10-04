# B2 MDFixer 冻结输入（手工等价）

provenance: `MANUAL_EXPECTED`

本目录根据用户提供的 E3 任务分配 B2-1～B2-6 手工构造；未取得课程实验包或 PPT 原文件，不将这些文件称为课程原始产物。`main.c/config.h/unused.h` 逐字节复用 A1 真实提交 `9c36984236b97115f44daa24c5274a90dd905b37` 的 `e3/fixtures/md-rd/`；四种 Makefile 与补丁由 B2 单独准备。

| 输入 | 用途 |
| --- | --- |
| `md-report.json` | Target 固定报告，仅包含 `main.o → config.h` 的 MISSING；含源码和原 Makefile 的 SHA256 |
| `main.c/config.h/unused.h` | 初始 VALUE=1；程序实际包含 config.h，unused.h 未被源码使用 |
| `Makefile`、`Makefile.before` | 根目录 Target 原始副本，两者完全相同 |
| `reference.patch` | 根目录 Target 参考修复，只新增 config.h 声明 |
| `styles/{target,macro,hybrid,implicit}/` | 各自的 Makefile.before、Makefile.reference、reference.patch、md-report.json |
| `invalid-candidate.patch` | 故意插入打印 B2_INVALID_CANDIDATE 并退出 23 的编译前置命令 |
| `main.d.example` | 人工预期示例，实际生成的 main.d 保存在每轮 work 中 |

所有参考补丁都保留 `unused.h`；MDFixer 只消费 `MISSING`，不删除 RD。Implicit 的额外 `main.o: unused.h` 保留原声明，`%.o: %.c` 负责编译；补丁新增 `-MMD -MP` 和 `-include main.d`，缺少 `.d` 的首次构建不会因此失败。

不要在本冻结目录直接构建或改头文件。在仓库根运行：

```bash
python3 e3/scripts/b2_run_mdfixer_baseline.py
python3 e3/scripts/b2_verify_evidence.py
```

环境需 Python 3.9+、Git、GNU Make 与支持 `-MMD -MP` 的 GCC/Clang。完整复现、Windows/WSL 命令见 [B2 入口](../../B2_README.md)，判断依据见 [人工参考答案](../../expected/mdfixer-reference.md)。每轮记录 SHA 上下文、冻结输入哈希、命令、退出码、原始日志与源码快照；未提交的 B2 输入显式标为 WORKING_TREE_SNAPSHOT，不冒充 HEAD 内已有文件。
