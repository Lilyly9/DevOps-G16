# 实际运行命令与退出码

所有命令均在仓库根目录执行。WSL2 主机路径为 `/mnt/c/Users/hydl/OneDrive/Desktop/codeing/DevOps-G16`，容器内挂载为 `/course`。

| 步骤 | 命令 | OUT | 退出码 |
| --- | --- | --- | --- |
| 工具链 | `mkdir -p /tmp/strace-bin && printf '#!/bin/sh\nLD_LIBRARY_PATH=/tmp/strace-deps/usr/lib/x86_64-linux-gnu exec /tmp/strace-local/usr/bin/strace "$@"\n' > /tmp/strace-bin/strace && chmod +x /tmp/strace-bin/strace` | `/tmp/strace-bin` | 0 |
| 单测 | `PYTHONPATH=labs/e11e12:labs/e8e10:labs/e11e12/vendor python3 -m unittest discover -s labs/e11e12 -p 'test_*.py' -v` | [unit-tests.log](unit-tests.log) | 0（18 tests OK） |
| 样例生成 | `PYTHONPATH=labs/e11e12:labs/e8e10:labs/e11e12/vendor python3 labs/e11e12/prepare.py` | `data/integration-sample` | 0 |
| E11-A 固定样例 | `PYTHONPATH=... python3 labs/e11e12/pipeline.py --request data/integration-sample/e11-a.json --out work/e11a-standard-final-20261115` | `work/e11a-standard-final-20261115` | 0 |
| E11-A 官方入口 | `E11E12_DOCKER_HOST_ROOT=<repo> python3 run_e11e12.py run --request data/integration-sample/e11-a-container.json --out work/e11a-runner-20261115` | `work/e11a-runner-20261115` | 0（[日志](runner-e11a.log)） |
| E12 官方入口 | `E11E12_DOCKER_HOST_ROOT=<repo> python3 run_e11e12.py run --request data/integration-sample/e12-container.json --out work/e12-runner-20261115` | `work/e12-runner-20261115` | 0（[日志](runner-e12.log)） |
| E11-A 自主项目 | `PYTHONPATH=... python3 labs/e11e12/pipeline.py --request data/e11a-tokenstat.json --out work/e11a-tokenstat-final-20261115` | `work/e11a-tokenstat-final-20261115` | 0 |
| 服务镜像 | `docker build --build-arg BASE_IMAGE=python:3.13-slim@sha256:f82c96458eedc847b233e582eb31336f4954b39cae020b6dcf5b3ed0e5cbcd74 -f labs/e11e12/environment/services/buildchecker/Dockerfile -t course-e11e12:241880496 labs/e11e12/environment` | `course-e11e12:241880496` | 0 |
| E12 固定样例 | `docker run ... course-e11e12:241880496 python3 labs/e11e12/pipeline.py --request data/integration-sample/e12-container.json --out work/e12-standard-final3-20261115` | `work/e12-standard-final3-20261115` | 0 |
| E12 真实项目 | `docker run ... course-e11e12:241880496 python3 labs/e11e12/pipeline.py --request data/e12-tokenstat-container.json --out work/e12-tokenstat-final-20261115` | `work/e12-tokenstat-final-20261115` | 0 |
| API 服务 | `docker run -d --name e11e12-api-241880496 ... -p 127.0.0.1:18080:8080 course-e11e12:241880496 python3 labs/e11e12/server.py --host 0.0.0.0 --port 8080` | `work/api-jobs` | 0 |
| API 联调 | `python3 /tmp/api_client.py`（POST → 轮询 → 下载核对） | `work/api-e12-241880496` | 0 |
| API 幂等 | `python3 /tmp/api_idem.py` | `work/api-e12-241880496/idempotency.json` | 0（同任务 / 409） |

E12 的完整 `docker run` 参数见 [index.md](../index.md) 的复现命令；`--group-add` 使用 `/var/run/docker.sock` 的 gid，`E11E12_DOCKER_HOST_ROOT` 指向宿主仓库路径。

`work/` 与 `data/` 已在根 `.gitignore` 中忽略；仓库只保留本索引引用的选择件，带 `result.json` 全量产物清单的目录仍留在本机 `work/`。
