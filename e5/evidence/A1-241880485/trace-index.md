# A1 本次 trace 索引

实际执行：A1 焦龙 / 241880485；时间：2026-10-24 08:32:46 UTC（北京时间 16:32:46）。源码 `ac7a040ec615c13bca7d2ec2b79347108631237a`，镜像 `sha256:a8c15fd4391437a3f5497e9feee0d4e3053d4a488e2d1576cb8c12d65c9edc23`。

| 原文件 | 关键原始行 | 解释 | 本归档 |
| --- | --- | --- | --- |
| t.14 | 1、55、66 | make；派生编译 cc=15，稍后另派生链接 cc=18 | 保留 |
| t.15 | 1、64、84 | `cc -c main.c -o main.o`；派生 cc1=16、as=17 | 保留 |
| t.16 | 1、67、580 | 成功执行 cc1；成功只读打开 main.c、config.h | 保留 |
| t.17 | 5、23 | as 成功 exec；以创建/截断方式打开 main.o，返回 fd=3 | 保留 |
| t.18 | 1、129 | 链接 app 的 cc；不是 main.o 的编译 recipe | 仅索引 |
| t.19 | 1、96 | collect2→ld，属于 app 链接 | 仅索引 |
| t.20 | 1、82–83 | ld 读取 main.o，属于 app 链接 | 仅索引 |

原始行号保持不变；文件复制未删行或脱敏重排。全部 7 份原始 trace 的大小/哈希在 `trace-inventory.json`。按分工归档 main.o 判断所需四个关键进程；另三份仍在本人服务器原目录，不把此裁剪目录直接传给 E6 `analyze`（完整分析会检查所有 child trace）。A2/E6 应自己运行入口重新采集。

完整原件位于 `/root/241880485/DevOps-G16-e5-A1-20261024/e5/A-buildchecker/work/e5-A1-20261024-01/evidence/trace/`；本机私有备份 tar 的 SHA-256 为 `4896e11f04bb4d4e7e2b8505d6f23f70541e22a633903f4250006234c3d1585a`，未把完整 trace 压缩包或 app/main.o 二进制入库。

`clone3=-1 ENOSYS`、as 路径探测的 `execve=-1 ENOENT` 都是失败尝试，不建立额外父子关系；成功 clone/exec 和打开返回的非负 fd 才作为本次证据。`strace -e trace=%file,%process` 记录打开与创建，不记录实际 read/write 字节。
