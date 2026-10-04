# B2 复核记录（2026-10-04）

observation_type: `ACTUAL_RUN`

本目录保留实际校验命令、退出码、stdout/stderr 原始字节与 SHA256；`summary.json` 是结果摘要，`commands.json` 中 recorded_at 是结果记录时间。

检查覆盖：

- 既有 E2 MDFixer 合约：原 Windows 环境缺 jsonschema，WSL 系统版过旧；两次依赖失败保留原始日志。在独立临时虚拟环境安装 jsonschema>=4.18,<5 后，既有校验通过，没有修改 E2 文件或公共 Schema。
- A 组既有 E3 离线校验通过，B2 修改未破坏既有材料。
- 三轮 B2 实测（两轮 Linux，一轮 Windows/MinGW）均通过离线核验；四种参考 Patch 均可应用，增量输出 3、4，生成 .d，无效候选被拒绝并恢复。
- 当前 Windows 进程的 platform.machine() 返回空。GetNativeSystemInfo 补录真实架构 AMD64；原始 environment.initial.json 留在 Windows 运行目录，environment.json 注明补录来源，未覆盖原始缺项记录。
- 在临时隔离克隆中，以有效材料为对照，分别篡改增量原始输出、删除实际 .d、将失败候选标记为已接受、破坏恢复后的 Makefile；四个反例均被检查器以非零退出拒绝，恢复材料后校验重新通过。原仓库证据未被故障注入修改。

初次开发检查还纠正了两个证据校验问题：Windows Git 的自动换行转换通过临时目录的 LF 属性约束处理；失败候选在 clean 后不应要求 main.o 存在，检查器改为要求它不存在。这些是校验器修正，主 Linux 构建实验没有因此失败。

本复核不声称全组签字、真实 MDFixer 服务已实现或检测器重检通过。完整交付见 [B2_README](../../../B2_README.md)。
