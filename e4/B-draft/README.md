# DRAFT 服务（E4 骨架）

本仓库在 E4 中建立可重复环境，E5 起在 `services/draft/` 中实现论文方法。

## 第一次使用

```sh
mkdir -p ~/<学号> && cd ~/<学号>
git clone https://github.com/Lilyly9/DevOps-G16.git
cd DevOps-G16
git config --local user.name  "<学号>"
git config --local user.email "<学号>@localhost"
git rev-parse HEAD
cd e4/B-draft
make all
```

`git remote -v` 应指向真正的本组远程仓库。课堂试跑所用的 `/root/E4实验包/B-draft` 只是本地模板；从它克隆不会自动同步到课程平台。共享服务器上的学号目录与 Git 身份只隔离个人工作和标记未来的提交，运行 `make all` 本身不会产生 Git 提交。

本组沿用 E2/E3 的共享仓库，B 模板位于 `e4/B-draft/`。以下所有 `make` 命令均在这个子目录运行，构建上下文也为这个子目录。该目录使用父级仓库的 Git 身份和完整 HEAD，不要另行 `git init`。

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

预期：`make test` 的 4 个测试全部通过；`make smoke` 输出 `"passed": true`，`Dockerfile.broken` 故意构建失败，`build_exit_code` 非零，`make_error_line` 保留含 `make: not found` 的关键行；`make scan` 显示"未发现问题"。`log_tail` 只保留末尾几行，不保证包含这条关键行。E5 仍须重新保存完整原始构建日志和退出码。

## 约定

- Python 基础镜像、Docker 客户端镜像和冒烟样例均通过镜像站按 digest 固定；更换时须核验 digest 与架构，并在提交说明中写明来源。服务镜像从 `docker:cli` 复制客户端，不在容器里另装 Docker 引擎；`docker_server` 记录的是宿主机引擎版本。
- ECS 到 Debian 默认源下载缓慢。本组在 Dockerfile 中仅将 `debian.sources` 的 Debian 包源改为 `https://mirrors.aliyun.com/debian`，安全更新源改为 `https://mirrors.aliyun.com/debian-security`。两处地址使用 HTTPS，原有 `Signed-By`、发行版及组件保持不变，`apt` 继续验证 Debian 签名；基础镜像 digest、`requirements-dev.lock` 和工具版本记录方式不变。这是组级网络配置修订，需形成新的模板提交，不属于个人运行日志。
- 新增 Python 依赖：写进 `requirements-dev.in`，执行 `make lock`，两个文件一起提交。
- 密钥只放在 `.env`（权限 600），不提交、不进镜像、不打印到日志。
- E4 每名组员各自在学号目录运行一次 `make all`，记录成功的 `work/<时间>/` 和所测源码 SHA，再与另一名组员对照。`work/` 默认不提交；E4 不要求个人创建分支、提交或合并。后续课程若要求提交原始证据，另按当时要求处理。
- `env.json` 的 `template_sha` 和 `template_subdirectory` 将运行证据对应到共享仓库版本；B1/B2 需使用相同的完整 SHA。
- B2 在自己的独立克隆中执行 `git checkout --detach <B1记录的完整SHA>`，核对 HEAD 后再进入 `e4/B-draft/` 运行 `make all`，以同一模板版本对照结果。
- `make scan` 检查共享仓库全部已跟踪文件和 Git 历史，以及本人的服务镜像；同时检查 B 子目录本地 `.env` 的权限。
- B 组验收：单测 `4 passed`；冒烟的 `docker_server` 有版本、`build_exit_code` 非零、`make_error_line` 含 `make: not found`、`passed=true` 同时成立——样例故意缺 `make`，服务成功识别并记录这次预期失败；密钥扫描未发现问题。
- 服务容器通过挂载的 `/var/run/docker.sock` 使用宿主机 Docker。这等同于宿主机 root 权限；容器的资源限制管不到它发起的构建。只构建课程指定的项目，不开放 Docker API 2375/2376 端口，不清理其他组员的镜像与缓存。

## Git 历史含旧编码日志

2026-10-05 A3 跨组重跑发现历史扫描因 Windows 旧编码日志产生 UnicodeDecodeError。扫描器现以 UTF-8 替换解码读取 Git 输出，保留原有密钥规则；应同步此修正版后在新的 RUN 目录完整执行 make all。旧版本构建、单测和冒烟通过但扫描崩溃的记录应保留为失败尝试，临时副本补充扫描不能冒充原命令成功。
