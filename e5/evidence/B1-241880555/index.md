# B1 E5-B 证据目录 index

## 谁 / 何时

- 角色:B1(郭德林,241880555,B16)
- 运行时间:2026-10-23 15:47 – ~22:30(UTC+8;服务器时钟为 UTC)
- 环境:阿里云 ECS `iZbp106a3t3mzz3nfabuarZ`(ecs.c9i.large,2 vCPU / 3.5 GiB / Ubuntu 22.04.5)
- 工具:Docker 29.1.3、Python 3.10.12、git 2.34.1(daemon.json 已配 registry-mirrors=docker.m.daocloud.io 与 dns=223.5.5.5/119.29.29.29,临时 4G swap /swapfile)
- 工作副本:`~/241880555/DevOps-G16`,分支 `e5-7/B1-241880555`(f8e1888,实验包入库提交)
- Git 本地身份:user.name=241880555,user.email=241880555@localhost(--local)

## 命令(可在服务器整段重跑)

```bash
cd ~/241880555/DevOps-G16/e5/B-draft
# B1-2 服务镜像与单测
python3 scripts/lab_cloud.py build --out work/build-B1-05 --image course1020-draft:241880555 --build-timeout 3600
# B1-3 E5 采集
python3 scripts/lab_cloud.py e5 --out work/e5-B1-01 --image course1020-draft:241880555 --build-timeout 600
# B1-7 候选手工复建与运行
docker build --progress=plain -f work/candidate/Dockerfile -t course1020-draft-e5:241880555 work/e5-B1-01/project
IMAGE_ID=$(docker image inspect --format '{{.Id}}' course1020-draft-e5:241880555)
docker run --rm --network none course1020-draft-e5:241880555
```

注:doctor 报内存 3.5 GiB 低于最低要求 4(必需项),实测可完成构建;资源信息按 §11 记录,不做功能判断依据。

## 预期 vs 实际

| 检查项 | 预期 | 实际 |
| --- | --- | --- |
| B1-2 单测 | `24 passed`,退出码 0 | `24 passed in 0.15s`,build/unit-tests exit_code=0 |
| B1-4 build_exit_code | 1 | 1(result-retry.json) |
| B1-4 make: not found | 日志含 | build-retry.log 第 30/34 行,共 2 处 |
| B1-4 脚本退出码 | 0 | E5_EVIDENCE_EXIT_CODE=0 |
| B1-7 候选构建 | BUILD_EXIT_CODE=0 | 0(build-e5-03.log) |
| B1-7 运行 | VERIFY_EXIT_CODE=0,输出 `hello E3` | 0,输出 `hello E3`;IMAGE_ID=`sha256:b5fc01afbda029bb3c26a9dfe52b4b42004046a4d2345e072d3b829cbd9bc9ab` |

两层退出码说明:被跟踪的候选构建失败(127/1)是"目标故障",DRAFT 流水线把它记录为证据;采集脚本(e5)退出码 0 表示"复现并保存失败"这一任务本身成功。两者含义不同,不矛盾。

## 候选来源

- 提示:两类全文(error-driven / context-driven)分别提交给对话模型
- 模型:Claude Sonnet 4.6(Claude Code CLI 会话),2026-10-23
- 原始回复:`candidate/model-response.txt`;两个候选 candidate-01/02
- 最终候选:`candidate/Dockerfile`(= candidate-02,build-essential),sha256 `ede21b0f…`(与包内 DeepSeek-E5.Dockerfile 逐字节一致,系独立生成的趋同,非复制/非 replay,详见 `candidate/候选来源记录.json`)

## 证据清单

| 文件 | 内容 |
| --- | --- |
| `iter-01/result-retry.json` | `{"build_exit_code": 1}` |
| `iter-01/build-retry.log` | 真实失败构建完整输出,第 30/34 行 `make: not found` |
| `iter-01/Dockerfile` | 故障 Dockerfile(FROM python:3.13-slim,sha256 b78528f9…) |
| `iter-01/error-localization.json` | 脚本定位的根因行(第 30/34 行)与关键词匹配 |
| `iter-01/prompt-error-driven.txt` | 错误驱动提示全文(62 行) |
| `iter-01/prompt-context-driven.txt` | 上下文驱动提示全文(73 行,多 README 段) |
| `candidate/Dockerfile` | 最终候选(修复 Dockerfile) |
| `candidate/candidate-01.Dockerfile` / `candidate-02.Dockerfile` | 两个模型候选 |
| `candidate/model-response.txt` | 模型原始回复(两次,verbatim) |
| `candidate/候选来源记录.json` | 模型/版本/日期/提示类型/选择理由/哈希 |
| `candidate/build-e5-02.log` | 第 2 次复建(加 swap 后)中途被终止的日志;第 1 次复建日志(build-e5.log)在第 3 次运行时被脚本命名失误覆盖,OOM(exit 137)证据以内核 dmesg oom-killer 记录与报告 §3.5 引用的错误文本为准 |
| `candidate/build-e5-03.log` | 第 3 次复建(squid 内网代理后)完整输出,BUILD_EXIT_CODE=0 |
| `candidate/run-e5-03.log` | 候选镜像运行输出 `hello E3`、VERIFY_EXIT_CODE=0、IMAGE_ID |
| `build-B1-05/unit-tests/stdout.log` | 服务镜像单测 `24 passed` |

## 重跑方法(从 main 出发)

1. `git switch main && git pull --ff-only`(若 B1 分支已合并则直接用 main)
2. `mkdir -p ~/241880555 && cd ~/241880555 && git clone https://github.com/Lilyly9/DevOps-G16.git && cd DevOps-G16`
3. `git config --local user.name 241880555 && git config --local user.email 241880555@localhost`
4. 基础镜像:直接 `docker pull`(需 daemon.json 配 mirror,直连 docker.io 被 DNS 污染)
5. 用上面"命令"一节的整段重跑,`--out` 全部换新目录(如 `work/build-B1-06`、`work/e5-B1-02`)
6. E5 的判据值应完全一致;镜像 ID、容器 ID、耗时允许不同
