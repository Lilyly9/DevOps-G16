# 原始 trace 索引（A2 · E6 before）

本次 `e6` 采集共 7 个 trace 文件（按进程 pid 分文件，`strace -ff -s 4096 -e trace=%file,%process`）。

| 文件 | 角色 | 是否入库 | 说明 |
| --- | --- | --- | --- |
| `t.12` | `make` 派生链 | 否 | 构建驱动进程 |
| `t.13` | `cc` | 否 | 编译驱动 |
| `t.14` | `cc1` | **是** | 第 579 行 `openat(AT_FDCWD, "config.h", O_RDONLY)` —— MD 的直接证据 |
| `t.15` | `as` | **是** | 第 23 行 `openat(AT_FDCWD, "main.o", O_RDWR\|O_CREAT\|O_TRUNC)` —— 目标写出的归属证据 |
| `t.16`–`t.18` | 链接链（`collect2` / `ld` 等） | 否 | 生成 `app` 的读取与写出 |

- 关键进程归属：`cc1`（读 `config.h`）与 `as`（写 `main.o`）同属 `cc` 派生的一个构建任务 → 该读取记在目标 `main.o` 上。
- 未入库文件在原始运行目录 `e5-7/A-buildchecker/work/e6-before-A2/evidence/trace/`，重跑可完整重建。
- 完整原始目录约 112 KB/次，为控制仓库体积只保留两条直接证据；结论不依赖被裁掉的文件（声明侧由 `make-db.txt` 佐证）。
