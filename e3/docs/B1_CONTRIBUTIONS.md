# B1 E3 贡献记录

- 姓名:郭德林。
- Git 作者:DelinGuo。
- 工作范围:DRAFT 样本(Tiny Greeting)、失败/成功双层判据实测(本机 make/hello + Docker broken/reference)、样本清单与本人文档。
- 样本目录:e3/fixtures/draft/(main.c、Makefile、README.md、Dockerfile.broken、Dockerfile.reference、.gitattributes)。
- 人工预期:e3/expected/draft-sample.md(`MANUAL_EXPECTED`,行为目标为 PPT E3/30–33 给定口径)。
- 运行脚本:e3/scripts/b1_run_draft_baseline.py(build/docker 两阶段,幂等)。
- 实际证据:e3/work/20261004-115744-B1-8f5ca8/(commands.json 17 条、observations.json、environment.json、原始 stdout/stderr 日志;构建产物 runtime/ 按 A 组惯例不提交)。
- 环境记录:e3/env/toolchain-B1.txt(Ubuntu 26.04 LTS/WSL2、GNU Make 4.4.1、GCC 15.2.0、Docker 29.1.3)。
- 本人文档:e3/docs/B1_REPORT.md、B1_AI_USAGE.md、本文件及 e3/B1_README.md。
- 环境准备记录:本机原无 Docker;经用户确认后在 WSL 内 apt 安装 docker.io 29.1.3;Docker Hub 直连被重置后配置 registry mirrors(docker.nju.edu.cn、docker.m.daocloud.io)。详见 B1_REPORT 的卡点记录。
- A3/B3 后续汇总入口:本文件与 B1_REPORT 的任务对照表;四服务总表与全组确认由 B3/A3 组织,本人不代填。

## 可追溯提交

| 真实提交 SHA | 内容 |
| --- | --- |
| `a7291b5a2f0373f6aece7c0cdb228baace300cf6` | B1 样本、运行器、双层判据实测证据、样本清单与环境记录(`feat(e3): add B1 DRAFT sample with double-layer baseline evidence`,作者 DelinGuo) |

本文档提交(第二段)可用 `git log --oneline --author=DelinGuo -- e3/docs/B1_CONTRIBUTIONS.md` 查询;提交信息为 `docs(e3): record B1 contribution and progress`。

## 验证结论

- 本机双层:`make` 退出 0 且生成 `hello`;`./hello` 输出 `hello E3`、退出 0(behavior_status= PASSED)。
- Docker 双层:broken 构建退出 127 且日志可定位 `make: not found`;reference 构建退出 0,`docker run --rm` 输出 `hello E3`、退出 0;镜像 ID `sha256:7d1ee809dfd00f4c9572000810e1d114c15e1673d490b9c884abec676788985a`(docker_status= PASSED)。
- `python e3/validate_e3.py` 通过(该脚本声明只检查 A 组,B1 run 目录未破坏任何既有校验)。
- 人工预期与实际运行分列;构建产物未提交;未修改其他成员的文件与记录段;未声称四服务总表已获全组确认。
