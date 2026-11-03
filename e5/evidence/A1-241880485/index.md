# A1 E5 证据入口

执行者：焦龙（A1，241880485，A16）；2026-10-24；云端独立克隆 `/root/241880485/DevOps-G16-e5-A1-20261024`。

**结论：E5 原始复现及容器 18 项单测通过；原始环境自检仍因 3.5 GiB < 4 GiB 退出 1，整体 A1 DoD 未标全通过。**详见 [报告](../../reports/A1-241880485.md) 与 [summary.json](summary.json)。

| 材料 | 用途 |
| --- | --- |
| `program-output.txt:1` | 实际输出 1 |
| `make-db.txt:1061` | 实际声明 main.o: main.c unused.h |
| `trace/t.14`～`t.17`、`trace-index.md` | 原始父子进程与目标读/创建关系；不是 E6 完整 trace 输入 |
| `AI_USAGE.md`、`CONTRIBUTIONS.md` | A1 本阶段个人记录，避免重写共享根记录或他人行尾 |
| `Makefile`、`main.c`、`config.h`、`unused.h` | 从实际镜像复制的四份输入 |
| `A1-run-metadata.json` | 真实 UTC、源码 SHA/干净状态、输入源码哈希、不可变镜像 ID、argv/退出码 |
| `runner/`、`invocation.json`、`service-container-id.txt` | E5 原始命令、输出、退出码与容器标识 |
| `doctor/` | 原始环境自检失败及其余工具版本/学号身份，未放宽门槛 |
| `build/` | 成功构建、18 passed、镜像 inspect、toolchain.lock 原输出、构建副本 |
| `failures/dockerhub-frontend/` | 直连 Docker Hub 在 Dockerfile frontend 超时，未达到编译阶段 |
| `image-provenance/` | 实际镜像内 fixture/新增测试/依赖锁哈希及仓库、历史、镜像扫描通过原件 |
| `verification.json` | 原件一致性检查通过；整体环境门槛仍未通过 |
| `trace-inventory.json`、`files.sha256.json` | 原 trace 全量清单和本归档逐文件 bytes/SHA-256 |

## 命令与重跑

源码运行提交：`ac7a040ec615c13bca7d2ec2b79347108631237a`；分支 `e5-7/A1-241880485`。只用本人镜像 tag `course1020-buildchecker:241880485`，实际 E5 参数固定为镜像 ID `sha256:a8c15fd4391437a3f5497e9feee0d4e3053d4a488e2d1576cb8c12d65c9edc23`。本次原始 `work/e5-A1-20261024-01` 不能复用。

从仓库根目录开始，Linux/Git/Docker 已就绪：

```sh
git checkout --detach ac7a040ec615c13bca7d2ec2b79347108631237a
git config --local user.name 241880485
git config --local user.email 241880485@localhost
cd e5/A-buildchecker
python3 scripts/lab_cloud.py doctor
python3 scripts/lab_cloud.py build --out work/build-A1-new --image course1020-buildchecker:241880485 --build-timeout 1200
python3 scripts/lab_cloud.py e5 --out work/e5-A1-new --image course1020-buildchecker:241880485
```

doctor 若报资源不足，保留原输出并联系助教确认/调整资源，不用实验成功覆盖此项。若直连 Docker Hub 同样超时，本次使用如下只影响本人构建的替代入口（新 tag 允许复用本人 tag，不操作别人 tag）：

```sh
docker build --progress=plain -f ../evidence/A1-241880485/build/Dockerfile.A16 -t course1020-buildchecker:241880485 .
docker run --rm --network none course1020-buildchecker:241880485 pytest
docker run --rm --network none course1020-buildchecker:241880485 cat /opt/toolchain.lock
python3 scripts/lab_cloud.py e5 --out work/e5-A1-new-mirror --image course1020-buildchecker:241880485
```

归档文件位于后续证据提交，若检出上述运行提交时看不到 `evidence/`，先从归档所在分支复制该构建副本再切运行提交，或在最新证据提交上运行并记录新的 SHA。Dockerfile 的服务/fixture/依赖锁都来自运行提交，网络副本复用 E4 已有镜像站与 apt 下载地址，基础镜像 digest、锁文件/签名校验均未更改。未修改共享 E5 Dockerfile 或服务器 daemon 配置。

服务代码、E6/E7 参考实现及原 15 测来自课程学生包；A2 的 2 测已在 main。A1 只新增 `test_extra_241880485.py` 的 1 测（独立人工 syscall 单元输入），合计 18 passed。没有复制外层助教演示日志、调用模型 API 或生成 B 组候选。
