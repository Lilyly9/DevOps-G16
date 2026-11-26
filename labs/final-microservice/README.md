# A16 期末微服务实验

在 Linux 课程服务器上复验教师样例、真实 E12 集成及 `transfer-eta` 四服务停机恢复。请在自己的检出中运行。需要 Git、Python 3.10 或更新版本、Docker Engine、Docker Compose v2 和 `curl`。`run-e12.sh` 与 `run-sample.sh` 读取课程发放的 `Microservice_Lab.zip`。

## 教师样例

```bash
lab_zip=/absolute/path/Microservice_Lab.zip
bash labs/final-microservice/run-sample.sh "$lab_zip"
```

默认使用 `python:3.13-slim`、`prom/prometheus:v3.5.1` 与 `grafana/grafana:13.3.0`。可用 `PYTHON_IMAGE`、`PROMETHEUS_IMAGE`、`GRAFANA_IMAGE` 指定可取得的同版本镜像引用。脚本在新的临时目录运行，实际镜像和状态写入该次归档。可设置 `FINAL_WORK_ROOT` 选择已有的工作目录。

## A2 真实 E12 与错误补丁

```bash
lab_zip=/absolute/path/Microservice_Lab.zip
E12_IMAGE=course-e11e12:241880496 bash labs/final-microservice/run-e12.sh "$lab_zip"
```

镜像名按实验环境替换。脚本读取本次检出的已提交 HEAD，在新目录启动只绑定回环地址的 E12 API。教师客户端应通过五阶段验收。脚本另外复算所有产物哈希和字节数，验证项目命令使用 DRAFT 候选镜像，最后实跑错误补丁拒绝。输出目录和归档 SHA256 见 `RUN_ROOT` 和 `EVIDENCE`。

## A3 四服务和监控

```bash
docker pull prom/prometheus:v3.5.1
docker pull grafana/grafana:13.3.0
E14_IMAGE=course-e11e12:241880464 FINAL_DEMO=1 bash labs/final-microservice/run-real.sh
```

准备本地课程镜像和两个监控镜像。使用镜像代理时，拉取同版本镜像并在执行时设置 `PROMETHEUS_IMAGE` 和 `GRAFANA_IMAGE` 为实际引用。脚本在 `data/` 及 `work/` 下创建本轮输入和输出，随机分配回环端口，启动独立 Compose 项目。依次执行正常任务、停止本轮 EChecker 后的故障任务、恢复后的新任务。演示模式会暂停并打印 Grafana 的服务器端口。通过 SSH 将本地端口转发到该端口。Grafana 用户为 `admin`，本轮密码在 `RUN_ROOT/.env`，仅在本人终端查看。归档中有 Grafana 面板、Prometheus 查询、阶段日志与产物。移除 `FINAL_DEMO=1` 可自动走完三阶段。

## 验收证据

三条线路共用来源可追溯的输入。E12 使用 DRAFT 候选运行项目命令。E14 以独立四角色及其健康探测验证故障和恢复。同一条线路内可用 `job_id` 找结果、用 `trace_id` 找调用日志。

[复验任务、证据与回传格式](../../docs/final/a16/README.md) · [组内分工](../../docs/final/a16/assignment.md) · [AI 使用记录](../../docs/final/a16/AI_USAGE.md)
