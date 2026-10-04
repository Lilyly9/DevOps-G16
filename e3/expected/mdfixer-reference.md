# B2 MDFixer 人工参考答案

provenance: `MANUAL_EXPECTED`

来源：用户粘贴的《E3 并行测试基线——任务分配》§6 B2-1～B2-6 和四种声明风格表。课程 PPT/实验包原文件未提供；本答案为手工等价基线，不是 MDFixer 或 BuildChecker 的实际输出，不计入工具准确率。

## 固定输入与修复边界

配置为 `b2-gcc-O0-project-headers`，CFLAGS 为 `-O0 -Wall -Wextra`，只判断项目头文件。`main.c` 包含 `config.h`，VALUE 初始为 1；原 Makefile 没有声明这个头文件，也没有生成、加载 `.d` 文件，因此 `main.o` 缺少 `config.h`。每份 `md-report.json` 固定一个 `MISSING` 发现，并绑定源码与 Makefile.before 的 SHA256。

源码来源是 A1 提交 `9c36984236b97115f44daa24c5274a90dd905b37`；B2 Makefile 为新样本。每轮实际版本以 `work/<run>/inputs/` 和 `source-manifest.json` 的哈希为准，不能将上下文 base_commit 当作未提交样本的 Git 版本。

`unused.h` 的冗余声明不属于本次修复目标。补丁保留它，避免将 MD 修复扩大为 RD 删除。

## 四种期望补丁

| 风格 | 原声明 | 参考修复 | 补丁 |
| --- | --- | --- | --- |
| Target | `main.o: main.c unused.h` | 在该目标的依赖列表末尾加入 `config.h` | [reference.patch](../fixtures/mdfixer/styles/target/reference.patch) |
| Macro | `DEPS = main.c unused.h`；`main.o: $(DEPS)` | 将 DEPS 改成 `main.c unused.h config.h`，保留宏引用 | [reference.patch](../fixtures/mdfixer/styles/macro/reference.patch) |
| Hybrid | `HEADERS = unused.h`；`main.o: main.c $(HEADERS)` | 将 HEADERS 改成 `unused.h config.h`，保留直接源码项 | [reference.patch](../fixtures/mdfixer/styles/hybrid/reference.patch) |
| Implicit | `%.o: %.c`；另保留 `main.o: unused.h` | 编译加 `-MMD -MP`，末尾加 `-include main.d`；clean 同时移除 `.d` | [reference.patch](../fixtures/mdfixer/styles/implicit/reference.patch) |

Implicit 编译命令应为 `$(CC) $(CFLAGS) -MMD -MP -c $< -o $@`。人工预期 `.d` 核心内容是：

```make
main.o: main.c config.h
config.h:
```

`-MP` 生成头文件空目标，`-include` 允许首次构建时 `.d` 不存在。`.DEFAULT_GOAL := all` 固定默认目标；生成的实际文件保存在 `work/<run>/implicit-main.d` 和 implicit-patched 快照中。

## 修复有效性的判据

| 操作 | 人工预期 | 判断依据 |
| --- | --- | --- |
| 原 Makefile，VALUE=1，make 后运行 | stdout=1，退出 0 | 初始基线能构建、能测试 |
| 仅改 config.h 为 VALUE=2，确认 mtime 晚于 main.o，再 make | 仍为 1；main.o 的哈希和 mtime 不变 | 缺失声明导致结果过时；构建退出 0 并不能证明依赖正确 |
| git apply --check 后应用参考补丁，clean、make、运行 | stdout=2，退出 0 | 与上一行使用同一 VALUE=2 源码，补丁可应用且项目可构建 |
| 再改 config.h 为 VALUE=3，不 clean，make、运行 | stdout=3，退出 0；编译命令执行、main.o 更新 | 修复后的声明能够触发增量重建，这才是关键验收 |
| 继续改为 VALUE=4，不 clean，make、运行 | stdout=4，main.o 再更新 | 排除只成功一次的候选 |
| 不改任何文件，再 make、运行 | 仍为 4，main.o 哈希和 mtime 不变 | 排除每次强制编译伪装成依赖修复 |

**不能只靠 clean build 成功证明 MD 已修复。** 必须保留再改头文件、不 clean 仍自动重编译的证据；本基线比较真实输出、命令、mtime 与对象哈希。

## 无效候选、拒绝与恢复

在独立 Target 副本验证：原始 Makefile 构建和测试输出 1 → 应用 `invalid-candidate.patch` → clean 后 make 执行注入命令，打印 `B2_INVALID_CANDIDATE` 并返回非零 → 标记候选未接受 → 在 finally 中恢复原 Makefile 字节 → clean、make、运行再次输出 1。

注入命令自身退出 23；GNU Make 的顶层退出码以实际日志为准，不能假设等于 23。恢复判据包含原文件 SHA256 相同和构建/测试通过。恢复原副本仍保留原 MD，这代表回滚成功，不代表修复成功。

本阶段仅提供人工参考补丁与行为证据。真实 MDFixer 的候选生成、BuildChecker 重检和 `remaining_missing=0` 留待后续服务实现与联调；这里不伪造重检结果。
