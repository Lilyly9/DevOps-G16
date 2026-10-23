# E5 论文1复现——证据与报告

目录结构见 `E5-7_TASKS.md` §8。实验包代码在 `A-buildchecker/`(A 轨)与 `B-draft/`(B 轨),各一份;`evidence/<角色>-<学号>/` 为本人证据,`reports/<角色>-<学号>.md` 为本人报告。

## B1(郭德林,241880555)

- 证据:`evidence/B1-241880555/`(index.md 为入口);报告:`reports/B1-241880555.md`
- 关键判据:服务镜像单测 **24 passed**;E5 采集脚本退出码 **0**;`build_exit_code=**1**`,`build-retry.log` 第 30/34 行 `make: not found`;候选构建 **BUILD_EXIT_CODE=0**;同镜像 `--network none` 运行 **VERIFY_EXIT_CODE=0**、输出精确 `hello E3`
- 镜像:`course1020-draft:241880555`(服务)、`course1020-draft-e5:241880555`(候选复建,`sha256:b5fc01af…`)
- 候选来源:Claude Sonnet 4.6(2026-10-23),两类提示全文独立生成,非 replay;最终候选 sha256 `ede21b0f…` 与包内 DeepSeek-E5.Dockerfile 逐字节一致(趋同,非复制),详见 `evidence/B1-241880555/candidate/候选来源记录.json`
- 运行环境:阿里云 B 组 ECS(ecs.c9i.large);docker.io 直连被 DNS 污染,daemon.json 配 mirror+dns,apt 经 squid 走内网镜像;过程故障与处理见报告 §3
