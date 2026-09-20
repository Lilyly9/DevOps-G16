# MANUAL_FIXTURE: 人工教学样例，DRAFT 服务未实际运行。
# 表示 g16-example-draft-001 第 2 轮（最终）生成的构建环境；
# 仓库、镜像与提交均为 example.invalid 占位值，不可直接执行。
FROM gcc:12-bookworm
RUN apt-get update \
 && apt-get install -y --no-install-recommends make bison \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /src
# build.command 与 verify_command 在本环境内执行（DRAFT 验证轮挂载
# 指定 commit 的源码执行，下游检测同样如此），不烘焙进镜像；
# 本镜像即为 output.image 引用的可获取环境。
