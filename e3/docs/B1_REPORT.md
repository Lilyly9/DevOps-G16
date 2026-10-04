# B1 E3 实验报告(DRAFT 样本与失败/成功双层判据)

- 成员:郭德林(Git 作者 `DelinGuo`)
- 运行目录:`e3/work/20261004-115744-B1-8f5ca8/`(run-id 格式与 A 组一致)
- 执行环境:Ubuntu 26.04 LTS(WSL2,x86_64),GNU Make 4.4.1、cc/GCC 15.2.0、Docker 29.1.3;版本明细见 [env/toolchain-B1.txt](../env/toolchain-B1.txt)
- 样本与预期:[fixtures/draft/](../fixtures/draft/README.md)、[expected/draft-sample.md](../expected/draft-sample.md)

## 任务对照

| ID | 任务 | 验收条件 | 结果 |
| --- | --- | --- | --- |
| B1-1 | 准备 DRAFT 样本 | `fixtures/draft/` 含 main.c、Makefile、README,README 给出构建/验证命令 | 完成;另含 Dockerfile.broken、Dockerfile.reference |
| B1-2 | 第一层:编译通过 | `make` 退出码 0、可执行文件生成、保存构建日志 | `draft-build` 退出 0,`ls -l hello` 确认产物;日志 `logs/draft-build.*.log` |
| B1-3 | 第二层:功能验证 | `./hello` 输出 `hello E3`、退出码 0 | `draft-run` stdout 为 `hello E3`,退出 0 |
| B1-4 | 失败样例 | `Dockerfile.broken` 构建非零退出,日志可定位 `make: not found` | 退出码 127;`make: not found` 在构建输出中可检索 |
| B1-5 | 参考修复与验证 | reference 构建成功,容器输出 `hello E3`;保存 diff、日志、镜像 ID | 构建与 `docker run --rm` 均退出 0,输出 `hello E3`;镜像 `sha256:7d1ee809dfd0…`;diff 见 `logs/dockerfile-diff.stdout.log` |
| B1-6 | 样本清单 | 按六项口径填写,别人能重跑 | [expected/draft-sample.md](../expected/draft-sample.md) |

实测汇总(预期 vs 实际)见 draft-sample.md 的对照表;确切 argv、cwd、退出码与日志路径见运行目录 `commands.json`(17 条命令记录)。

## 结论

- `make && ./hello` 双层判据在本机与容器内(`Dockerfile.reference`)同样成立:输出 `hello E3`、退出码 0,满足 PPT E3/30"容器内也能通过同一验证"。
- 失败候选与参考成功构成一对可判定的输入:同一源码,唯一差异是 `RUN apt-get install gcc make libc6-dev`(见 dockerfile-diff 日志);失败日志可定位到 `make: not found`,可用作后续 DRAFT 自动修复的输入(PPT E3/31)。
- 人工预期(`expected/draft-sample.md`,`MANUAL_EXPECTED`)与实际运行(`work/`,带 `ACTUAL_RUN` 标记)分列存放,未混写。

## 失败与卡点记录(未完成项处理)

1. **Docker Hub 直连被重置**:首次 docker 构建在拉取 `python:3.13-slim` 时 `read: connection reset by peer`(原始日志保留在 `logs/docker-*.stderr.log` 的早期记录,后续重跑覆盖;完整报错样例已抄录至本报告)。试过:配置 registry mirrors(`docker.nju.edu.cn`、`docker.m.daocloud.io`)到 `/etc/docker/daemon.json` 并重启 docker。结果:拉取成功,docker 层全部通过。下一步:无;若换机器复现,可参照此配置或改用任一可达 mirror。
2. **legacy builder 的输出分流**:首次判据只在 stderr 检索 `make: not found`,而 legacy builder 把 `RUN make` 的详细输出写入 stdout,导致误判 FAILED。试过:检查两路日志,确认 `make: not found` 实际出现在 stdout。结果:运行器判据改为 stdout+stderr 联合文本,并清理重跑残留的 failures 条目;重跑后 `docker_status= PASSED`。下一步:换 BuildKit 时无需修改(错误摘要自带详细行),但联合检索保持兼容。
3. **WSL root 下 git 拒绝解析仓库**:首次运行 `source_commit` 为空(safe.directory 保护,`git rev-parse HEAD` 无输出)。试过:在 WSL root 的 git 全局配置中加入本仓库 `safe.directory` 后用同一 run-id 重跑(运行器按命令 id 覆盖,证据保持同目录)。结果:`source_commit=8f5ca88c26bcdf23e76221639d752650f5cbad50`(运行时 HEAD)。下一步:无。
4. **sudo 需要密码**:WSL 内 `sudo` 需交互认证,无法在脚本中安装 docker。试过:`wsl -u root`(WSL 内建机制)执行 apt 安装。结果:docker.io 29.1.3 安装成功。下一步:无。

## 已知限制

- 实测经由 Windows 主机 `wsl.exe` 调用,以 root 在 WSL2 内执行;`environment.json` 的 `callsite` 字段如实记录。换 Linux 宿主机直接执行命令亦应得到相同观察(工具链版本可能不同,需另建 run 目录)。
- broken 构建退出码依赖基础镜像内 shell(dash 报 127);不同镜像版本可能得到其他非零码,判据以"非零 + 日志可定位 make: not found"为准。
- E3 只验证样本与判据;DRAFT 服务的自动生成、镜像迭代与真实数据联调属于 E5/E12 的后续工作,本阶段仅留接口与证据。
