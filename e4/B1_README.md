# E4 B1 运行与交接入口

成员：郭德林；学号：待本人补填；小组：B16。

本组继续使用 [DevOps-G16](https://github.com/Lilyly9/DevOps-G16)，B 模板在 [B-draft](B-draft/README.md)。该模板来自课程 E4 实验包，由 B1 接入共享仓库（模板提交可用 `git log --oneline -- e4/B-draft` 查询），仅适配共享仓库的子目录运行、全仓库密钥检查与环境证据的模板 SHA，适配方式与 A 组模板一致。冒烟样例 `fixtures/draft/` 与 B1 在 E3 完成的 `e3/fixtures/draft/` 同源：同一 Tiny Greeting 项目、同一 `Dockerfile.broken`（缺 `make`）与 `Dockerfile.reference` 判据，仅 `FROM` 改为镜像站固定 digest。

## 在 B 组服务器运行

```sh
mkdir -p ~/<B1学号>
cd ~/<B1学号>
git clone https://github.com/Lilyly9/DevOps-G16.git
cd DevOps-G16
git config --local user.name <B1学号>
git config --local user.email <B1学号>@localhost
git rev-parse HEAD
cd e4/B-draft
make doctor
make all
```

服务器登录入口使用老师提供的当前凭据（B 组服务器与 A 组不是同一台）。Docker 已可用时跳过服务器初始化；若尚无 Docker，由有权限的负责人在确认 Ubuntu 22.04/24.04 后从共享仓库根目录执行一次 `sudo bash e4/setup/bootstrap_ubuntu.sh`。

B 组有两种基础镜像，运行前先按 B 组手册第 4 节核验 digest 与 `linux/amd64`：

```sh
docker buildx imagetools inspect 'm.daocloud.io/docker.io/library/python@sha256:f82c96458eedc847b233e582eb31336f4954b39cae020b6dcf5b3ed0e5cbcd74'
docker buildx imagetools inspect 'm.daocloud.io/docker.io/library/docker@sha256:9190b0613792e658a7783cf14b2d5ace5941bb68ede7276922ea36ee457d76ad'
```

成功证据位于 `e4/B-draft/work/<时间>/`，应包括 env.json、build.log、image.json、toolchain.lock、test.log、smoke.json、secret-scan.txt。该目录和 `.env` 保持本地、不进入 Git。E4 分工文档 §10 填写本人目录、完整模板 SHA 和成功证据路径。

## B 组验收口径

- `test.log`：4 passed。
- `smoke.json`：`docker_server` 有版本（宿主机引擎，容器内只是 Docker 客户端）；`build_exit_code` 非零；`make_error_line` 含 `make: not found`；`passed: true`。**`build_exit_code` 非 0 与 `passed: true` 同时成立，是因为冒烟样例 `Dockerfile.broken` 故意缺 `make`，DRAFT 服务成功识别并记录了这次预期失败——判据是"识别正确"，不是"构建成功"。**
- `secret-scan.txt`：未发现问题；`git ls-files .env` 无输出。
- `env.json`：`problems` 为空，`template_sha` 为本入口记录的完整 SHA。

注意：以 root 登录 ECS 时 `make shell` 按宿主机 UID 进容器，不能用它证明默认 `app` 用户有 Docker 权限；该权限由 `make smoke` 以默认 `app` 用户执行来证明。

## 与 B2 的对照

B2 在自己的学号目录独立克隆后，先在共享仓库根目录执行 `git checkout --detach <B1记录的完整SHA>`，用 `git rev-parse HEAD` 核对，再设置自己的 local Git 身份并进入 `e4/B-draft/` 运行 `make all`。工具版本（`toolchain.lock`）、单测结论和冒烟四项判据应一致；镜像 ID、运行时间、日志行数允许不同。B2 另做假 Key 验证扫描器（不提交、不与 `make all` 证据混用），并记录宿主机引擎与容器内 Docker 客户端的版本差异（E5 的差异记录输入）。

## 与 E5 的衔接

E4 的 `smoke.json` 只保留退出码、关键错误行与构建日志末尾 8 行，不是 E5 要求的完整原始证据。E5 在同一镜像里用 `docker build --progress=plain` 重新采集完整输出进 `work/`。`make shell` 会把宿主机 `work/` 挂到容器 `/app/work`，E5 的复现在那里保存。
