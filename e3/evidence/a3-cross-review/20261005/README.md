# A3 对 B 组的 E3 实际复现（2026-10-05）

执行者 A3。来源为独立克隆的已发布版本 c3d1284；完整源码 SHA 见 reviewer-environment.json。
commands.json 和 docker-commands.json 保存真实命令与退出码，logs/ 保存原始输出。behavior-reruns.json 保存两个行为运行器的原始文本文件和哈希（排除 runtime 编译产物），不是人工答案。published-input-hashes.json 保存审核时的 B1 材料和人工预期快照哈希。

B1 本机构建退出 0，hello E3；Docker broken 退出 127、make: not found；reference 构建与容器运行均退出 0，hello E3。新参考镜像 ID 为 sha256:1a4050b3189b255b8cc7f96f84296918b095536a2c8d5c7ed7ddedbd9a5c374a。使用 A3 专属标签，没有覆盖 B1 镜像。
B2 四种风格、无效候选拒绝及恢复复跑通过；运行器和离线检查器均退出 0。

运行器中的 B1/B2 字段表示样本归属，本次执行者均是 A3。B1 原运行器写死原 WSL 环境，本轮归档保留其原输出，真实 A3 系统以 reviewer-environment.json 为准；已修正共享运行器以后采集实际 OS。
B1 原件的 source_commit=8f5ca88 是实验时仓库 HEAD 上下文，该提交尚未包含新增 B1 文件；文件随 a7291b5 发布。本轮按发布后的源码复跑并保存输入 hash，不宣称旧 SHA 已包含那些未提交文件。B2 原件显式标注 WORKING_TREE_SNAPSHOT，按其 source-manifest 核查。
