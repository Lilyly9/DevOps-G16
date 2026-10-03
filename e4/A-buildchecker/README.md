# BuildChecker 服务（E4 骨架）

本仓库在 E4 中建立可重复环境，E5 起在 `services/buildchecker/` 中实现论文方法。

## 第一次使用

```sh
mkdir -p ~/<学号> && cd ~/<学号>
git clone https://github.com/Lilyly9/DevOps-G16.git
cd DevOps-G16
git config --local user.name  "<学号>"
git config --local user.email "<学号>@localhost"
git rev-parse HEAD
cd e4/A-buildchecker
make all
```

`git remote -v` 应指向真正的本组远程仓库。课堂试跑所用的 `/root/E4实验包/A-buildchecker` 只是本地模板；从它克隆不会自动同步到课程平台。共享服务器上的学号目录与 Git 身份只隔离个人工作和标记未来的提交，运行 `make all` 本身不会产生 Git 提交。

本组沿用 E2/E3 的共享仓库，A 模板位于 `e4/A-buildchecker/`。以下所有 `make` 命令均在这个子目录运行，构建上下文也为这个子目录。该目录使用父级仓库的 Git 身份和完整 HEAD，不要另行 `git init`。B 组模板可由 B1 在 `e4/B-draft/` 独立接入。

## 命令

| 命令 | 作用 | 证据（work/<时间>/） |
| --- | --- | --- |
| `make doctor` | 服务器与 Git 身份自检 | env.json |
| `make build` | 构建服务镜像 | build.log、image.json、toolchain.lock |
| `make test` | 容器内运行单元测试 | test.log |
| `make smoke` | 用 E3 样例做冒烟测试 | smoke.json |
| `make scan` | 密钥检查（工作区、Git 历史、镜像） | secret-scan.txt |
| `make all` | 以上五步 | 同一个证据目录 |
| `make shell` | 进入服务容器；仓库的 `work/` 挂到容器的 `/app/work`，在那里保存的文件退出后仍保留 | — |
| `make lock` | 修改 requirements-dev.in 后重新生成锁文件 | requirements-dev.lock |

预期：`make test` 全部通过；`make smoke` 输出 `"passed": true`，strace 记录中能看到 `config.h` 被打开，`app_output` 为 `1`；`make scan` 显示"未发现问题"。

## 约定

- 基础镜像按 digest 固定，升级时只改 `services/buildchecker/Dockerfile` 的 `ARG BASE_IMAGE` 一行，并在提交说明中写明新 digest。
- A16 ECS 到 Debian 默认源下载缓慢。本组在 Dockerfile 中仅将 `debian.sources` 的 Debian 包源改为 `https://mirrors.aliyun.com/debian`，安全更新源改为 `https://mirrors.aliyun.com/debian-security`。两处地址使用 HTTPS，原有 `Signed-By`、发行版及组件保持不变，`apt` 继续验证 Debian 签名；基础镜像 digest、`requirements-dev.lock` 和工具版本记录方式不变。这是组级网络配置修订，需形成新的模板提交，不属于 A1 个人运行日志。
- 新增 Python 依赖：写进 `requirements-dev.in`，执行 `make lock`，两个文件一起提交。
- 密钥只放在 `.env`（权限 600），不提交、不进镜像、不打印到日志。
- E4 每名组员各自在学号目录运行一次 `make all`，记录成功的 `work/<时间>/` 和所测源码 SHA，再与另一名组员对照。`work/` 默认不提交；E4 不要求个人创建分支、提交或合并。后续课程若要求提交原始证据，另按当时要求处理。
- `env.json` 的 `template_sha` 和 `template_subdirectory` 将运行证据对应到共享仓库版本；A1/A2 需使用相同的完整 SHA。
- 网络配置修订后，以新模板提交的完整 `git rev-parse HEAD` 为准。A1 记录其成功运行的 SHA；A2 在自己的独立克隆中执行 `git checkout --detach <A1记录的完整SHA>`，核对 HEAD 后再进入 `e4/A-buildchecker/` 运行 `make all`，以同一模板版本对照结果。
- `make scan` 检查共享仓库全部已跟踪文件和 Git 历史，以及本人的服务镜像；同时检查 A 子目录本地 `.env` 的权限。
- A 组验收：单测 `3 passed`；冒烟的 `make_exit_code=0`、`app_output="1"`、`config_h_opened` 非空、`passed=true` 四项均满足；密钥扫描未发现问题。

## A3 核查入口

[A3 的证据链与交叉检查记录](../A3_REVIEW.md)汇总 A1/A2 已提交的交接说明、模板 SHA、复现顺序及尚待核验的服务器原件和 B 组重跑。按成功运行输出选择 `work/<时间>/`；额外的 `make scan` 会产生更晚的目录，不能据此判断 `make all` 的结果。

## 已核验的 A 组运行记录

A3 本人的成功目录为 `/root/241880464/DevOps-G16/e4/A-buildchecker/work/20261003-174027`，SHA 为 `fa5ae8fa45ea0fed943c94f9a1523a602aa96ce6`。前一个 doctor-only 目录和后一个 scan-only 目录都不是完整成功证据。

A1/A2 的同 SHA 重跑对照已由 A3 读取原件核验。A3 本人整仓版本较新，A 服务模板 Git tree 与 A1/A2 相同；详细对照和原件 hash 见 [A3 核查记录](../A3_REVIEW.md)。注意两次 make scan 若在同一秒执行，旧模板可能共用目录并覆盖报告；为独立扫描明确指定不同的 `RUN=work/<唯一编号>`。A3 新核查脚本的输出拒绝覆盖已有文件。

相邻 B 组尚未准备，跨组重跑结果为未通过，后续按 B 组发布的真实模板和 README 再核验。
