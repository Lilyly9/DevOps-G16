# E4 A1 运行与交接入口

成员：焦龙；学号：241880485；小组：A16。

本组继续使用 [DevOps-G16](https://github.com/Lilyly9/DevOps-G16)，A 模板在 [A-buildchecker](A-buildchecker/README.md)。该模板来自课程 E4 实验包；本次仅适配共享仓库的子目录运行、全仓库密钥检查与环境证据的模板 SHA。

## 在 A16 服务器运行

```sh
mkdir -p ~/241880485
cd ~/241880485
git clone https://github.com/Lilyly9/DevOps-G16.git
cd DevOps-G16
git config --local user.name 241880485
git config --local user.email 241880485@localhost
git rev-parse HEAD
cd e4/A-buildchecker
make doctor
make all
```

服务器登录入口使用老师提供的当前凭据。基础镜像先按 A 组手册核验固定 digest 及 linux/amd64；Docker 已可用时跳过服务器初始化。

若本组服务器尚无 Docker，由有权限的负责人在确认 Ubuntu 22.04/24.04 后执行一次 `sudo bash e4/setup/bootstrap_ubuntu.sh`（从共享仓库根目录执行）。脚本来自课程实验包。

成功证据位于 `e4/A-buildchecker/work/<时间>/`，应包括 env.json、build.log、image.json、toolchain.lock、test.log、smoke.json、secret-scan.txt。该目录和 `.env` 保持本地、不进入 Git。A1 会在成功目录另存运行交接记录；分工文档 §10 填写本人目录、完整模板 SHA 和成功证据路径。

A2 在自己的学号目录独立克隆并使用 A1 记录的同一 SHA 重跑。工具版本、单测和冒烟结论应一致；镜像 ID、PID、trace 行数和耗时允许不同。A3 后续汇总和组织相邻组复跑，本入口不登记其他成员完成状态。

A2 克隆后先在共享仓库根目录执行 `git checkout --detach <A1记录的完整SHA>`，用 `git rev-parse HEAD` 核对，再设置自己的 local Git 身份并进入 `e4/A-buildchecker/` 运行 `make all`。这样后续 B 组或文档提交不会改变对照版本。

E4 的冒烟摘要用于验证环境；E5 在同一服务环境重新采集完整 strace 与 make -p 原始证据。
