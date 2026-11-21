# ADR-001：服务器网络受限下派生换源候选（candidate-mirror）

编号、日期、作者：ADR-001 / 2026-11-13 / B1 郭德林（241880555）

问题：
E11-B/E12 在阿里云 ECS 上执行时，`prepare.py` 生成的候选 `candidate.Dockerfile` 使用官方 `deb.debian.org` 源安装 build-essential。实测 `apt-get update` 下载 trixie/main 索引（9.6MB）178s 未完成，`build_timeout=600` 耗尽后两轮工作流在候选构建阶段 TIMED_OUT，E11-B 无法完成（OUT=work/e11-b-241880555-20261113a，iter-01 仍正确复现 MISSING_MAKE）。

候选方案：
1. 调大 `build_timeout` 重试官方源——网络丢包依旧，耗时长且不稳定，每次构建都重复受罪。
2. 修改 `prepare.py` 生成的候选/样例生成逻辑——动了课程公共物料和共享代码，需 A1 协调，超出 B1 组件范围。
3. 保留原候选不动，派生 `candidate-mirror.Dockerfile`（仅新增一条 apt 换清华源 RUN 行），请求文件单独派生指向它——原样例物料可继续供其他成员在网络较好的环境使用。

采用方案与原因：
方案 3。理由：候选即"模型生成的修复方案"，B1 是候选来源与构建上下文的负责人（任务表 §4.1 构建输入与执行环境主责）；在候选内加入换源 RUN 行属于对候选的合法适配——`prepare_candidate` 校验要求仅新增 RUN 行、FROM 与基线指令不变，mirror 候选满足全部校验并通过两轮构建。原候选 SHA256 与 mirror 候选 SHA256 均登记于 index.md，来源可追溯；其他成员复用原候选不受影响。

输入输出字段：
- 输入：`data/integration-sample/candidate-mirror.Dockerfile`（= 原候选 + `RUN sed -i … /etc/apt/sources.list.d/debian.sources` 换清华源），请求 `e11-b-b1.json`、`e12-b1.json`、`e11-b-mismatch.json` 的 `candidate` 字段指向它。
- 输出：draft 阶段 `image_id`（E11-B：`sha256:8ad0bfcf…`；E12：`sha256:4d021749…`；mismatch：`sha256:3ae46247…`）与两轮构建/运行日志，字段格式与原候选完全一致，下游 A1/A2/B2 无感知。

兼容性与测试：
- `auto_build` 的 `prepare_candidate` 校验原样通过（未放宽任何规则）；E11-B 7 项判据、E12 五阶段判据、mismatch 预期失败全部满足。
- 原候选在官方源可达的环境（如 GitHub Actions runner）仍可直接使用，CI 无需改动。
- 固定样例回归：`run_e11e12.py test` 15 用例全过；B1 新增 5 用例见 report.md。
