# E4 A2 运行与对照入口

成员：万宇；学号：241880496；小组：A16；日期：2026-10-02。

本组继续使用 [DevOps-G16](https://github.com/Lilyly9/DevOps-G16)，A 模板在 [A-buildchecker](A-buildchecker/README.md)。A2 的角色是**第二名重跑 + 对照 + 假 Key 验证**：在**自己的学号目录**独立克隆，切到 A1 记录的同一模板 SHA，重复 `make doctor` / `make all`，再与 A1 逐项对照。

## 服务器上的运行步骤（已实际执行）

```sh
mkdir -p /root/241880496
cd /root/241880496
git clone https://github.com/Lilyly9/DevOps-G16.git          # 直连 GitHub，首次即成功
cd DevOps-G16
git rev-parse HEAD                                           # f04ea266…（含 A2 的 E3 提交）
git checkout --detach 9feb7a5675083a8ad0ad9fa3645010ced7bf2ffd
git rev-parse HEAD                                           # 与 A1 记录的模板 SHA 一致
git config --local user.name 241880496
git config --local user.email 241880496@localhost
cd e4/A-buildchecker
make doctor
make all
```

- 只用 `--local` 设置身份；切换 SHA 之后就绪后才建身份。
- 服务器 Docker 已可用，没有重复执行 `bootstrap_ubuntu.sh`；没有删除 A1 的镜像与缓存，本次构建复用了同一台机器的 Docker 层缓存（只影响速度，不影响判据）。
- `work/` 与 `.env` 按约定留在服务器，不进入 Git；E4 不要求个人提交，本仓库只提交本记录文件。

## A2 实际结果

| 项目 | 值 |
| --- | --- |
| 模板 SHA | `9feb7a5675083a8ad0ad9fa3645010ced7bf2ffd` |
| 服务器成功证据目录 | `/root/241880496/DevOps-G16/e4/A-buildchecker/work/20261002-184355` |
| `make doctor` / `make all` 退出码 | `0` / `0` |
| 单元测试 | `3 passed in 0.01s` |
| 冒烟四项判据 | `make_exit_code=0`、`app_output="1"`、`config_h_opened` 非空、`passed=true`（`trace_lines=1206`） |
| 密钥扫描 | 未发现问题（文件 240 个，含 Git 历史，含镜像） |
| 服务镜像 | `e4-buildchecker:241880496`，`sha256:5929bb973f6e9bcf0435c3333ab78d7d2cf1940aad888ff1a48dc161a5b3fb5a`，`amd64` |
| 本地配置 | `.env` 权限 600、未被跟踪；运行前后 `git status --short` 均为空 |

宿主环境与 A1 相同（Ubuntu 22.04.5 LTS、x86_64、2 CPU、3.5 GiB 可见内存；Docker 29.1.3、Compose 2.40.3、buildx 0.30.1、git 2.34.1、GNU Make 4.3、Python 3.10.12）；资源低于建议值与未配置镜像加速只出现在 `env.json` 的 `warnings`。

## 与 A1 的对照结论（E4 要求的“两名组员重跑对照”）

A1 基准：`/root/241880485/DevOps-G16/e4/A-buildchecker/work/20261001-040329`（模板 SHA 相同）。

| 项目 | 结论 |
| --- | --- |
| `toolchain.lock`（容器内工具与 Python 依赖版本） | **完全一致**（`diff` 无输出） |
| `test.log` 结论 | **一致**：都是 `3 passed in 0.01s` |
| `smoke.json` | **完全一致**（`diff` 无输出），四项判据全中 |
| `env.json` 的 `problems` | 都是空 |

**允许不同、实际也不同的项**：镜像名与 ID（`e4-buildchecker:241880485` / `sha256:72d3cbea…` 对 `e4-buildchecker:241880496` / `sha256:5929bb97…`）、`work/<时间>/` 目录名与耗时、主机磁盘可见量（70.5 → 70.4 GiB）。**没有需要解释的意外差异。**

克隆传输方式与 A1 不同，也一并记录：A1 的直连克隆曾超时、改用了组级副本 `--no-hardlinks`；A2 **直连 GitHub 克隆首次即成功**，因此本次对照同时验证了“从正式远程仓库直接克隆 → 切同一 SHA → 跑 `make all`”这条路径。

## 假 Key 扫描验证（手册 §6，未提交，不作为 `make all` 证据）

| 步骤 | 目录 | 退出码 | 结果 |
| --- | --- | --- | --- |
| 暂存 `e4/A-buildchecker/leak-demo.txt` 后 `make scan` | `work/20261002-184924/` | **2** | 报出 2 处：`LLM/API Key sk-d***`、`密钥赋值 sk-d***` |
| `git rm --cached` 并删除文件后 `make scan` | `work/20261002-184926/` | **0** | 未发现问题 |
| 首轮尝试（两次扫描落在同一秒，报告被第二次覆盖） | `work/20261002-184915/` | — | 已被上面两次取代，不作为证据 |

清理后 `git status` 为空、文件已删除；本次还执行了 `git reflog expire --expire=now --all` + `git gc --prune=now`，`git fsck --unreachable` 在清理前只报出那个未提交的假 Key blob、清理后为空。**成功证据目录是 `work/20261002-184355/`（七份文件齐全），它比两个扫描目录早——最新目录不等于成功目录。**

## 给 A3 / B3 的核对入口

- 证据 ↔ SHA：`work/20261002-184355/env.json` 的 `template_sha` 与 `template-sha.txt`、`head.txt` 都指向 `9feb7a5675083a8ad0ad9fa3645010ced7bf2ffd`。
- 无泄露三项：`.env` 未被跟踪（`git check-ignore` 命中 `e4/A-buildchecker/.gitignore:2`）、Git 历史与镜像 history 由 `secret-scan.txt` 覆盖（含镜像）。
- 目录内容清单与哈希：同目录 `sha256-manifest.txt`；服务器侧另有 `A2_HANDOFF.md`、`A2_RESULT.json`（与人读记录同源）。
- 本记录不含服务器地址与登录凭据。

## 边界

- 未修改模板、未改公共 Schema、未替 A3/B 组填写任何内容；A3 的相邻组检查（查 B 组）与 §10 汇总仍由 A3 完成。
- E5 会在同一服务环境重新采集完整 `strace` 与 `make -p` 原始证据；E4 的 smoke 摘要不能代替 E5 原始跟踪。
