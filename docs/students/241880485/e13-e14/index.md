# A1 焦龙 241880485 · E13–E14 个人记录

- **角色**：A1 · BuildChecker（A16 组，配对 B16）
- **仓库**：<https://github.com/Lilyly9/DevOps-G16>（共用原仓库，未新建仓库）
- **个人分支**：`student/241880485/e13-e14`，基线 `origin/main` = `28c94defee5af11ada42f9842cf03db2cb9da2e3`
- **代码提交**：`980e1a5f3c4e33520e4b9c0ac2a7c68f8262d460`（本记录的证书 SHA；实测运行在 `1a824ff6ef038787acb29fb290a8361429b6f408`，差异仅为扫描器解码修复，不参与 C1/C7/E14 执行路径）
- **镜像**：`course-e11e12:241880485` = `sha256:40b15f7e375e5bbbb5929f2f22f52f4a194a340b1970d340512af444f69320a5`（207 440 588 B）
- **执行宿主**：课程云机 A16（2 vCPU、MemTotal 3 710 080 kB、Docker 29.1.3、Compose 2.40.3、宿主 Python 3.10.12、Git 2.34.1、`/var/lib/docker` 剩余 59.4 GiB）
- **记录时间**：2026-11-22（Asia/Shanghai）

## 1. 结论摘要

| 项目 | 结论 | 关键标识 |
| --- | --- | --- |
| A 侧真实项目供给（全量+增量） | **完成** | `projects/transfer-eta`；base `5ef9d829…`、target `e7414083…`、修复版 `2efac598…` |
| C1 正常链路（A 侧供给与验证） | **通过（本人实际执行）** | `job-789dec04cba24db690ace58ecbe0f868` / `trace-ef57b1b5364d49b7b1f9357f4a5075b1`，235 产物 |
| C7 失败隔离（A 侧） | **通过（本人实际执行，两变体）** | 变体 A `job-fce3110d…`→`job-802afa93…`；变体 B `job-434f0696…`→`job-802afa93…` |
| E14 四容器五阶段（固定样例，镜像源适配版） | **通过（本人实际执行）** | `job-fc8b5db6f2b1408ea987ec29e4b0bd06` / `trace-cd0649b63f074cda968916ea55951966`，162 产物 |
| E14 受控故障与恢复 | **通过（本人实际执行）** | 故障 `job-b99f47f8…`（TIMEOUT）→ 正常任务 `job-fc8b5db6…` 成功 |
| E14 真实项目四容器 | **阻断（已实测拒绝，未擅自改共享入口）** | `job-8d42debc0ba549e3901f86318acb8a92` → `Unsupported teaching project profile` |
| 本人代码/测试改动 | **完成** | `verify_c7_isolation.py`、`test_c7_isolation.py`、`test_scan_runtime_logs.py`、`e13e14.yml`、`service.py`/`secret_scan.py` 两处修复 |
| 远端必需 CI | **全绿（目标提交实跑）** | `980e1a5` 上 6 项检查全部 success，E13-E14 run `44973427821` |
| H1 jsmn / H2 inih / H3 tiny-AES-c | **未执行：输入缺失** | 全工作区与仓库均无三项输入包，见 §5 |
| 教师隐藏测试 | **未执行** | 未收到任何用例、编号或反馈，未编造结果 |
| `v0.9-rc` | **未发布（组级动作）** | 远端无该标签；按分工由组长/有权限同学执行 |

**本文件不代表 E13/E14 整组验收通过。** 只声明 A1 本人实际执行并可回溯到原件的工作。

## 2. 归因：本人动作 vs 队友成果

| 内容 | 执行人/来源 | 本人本轮动作 |
| --- | --- | --- |
| `labs/e13e14/` 四容器入口（`service.py`、`orchestrate.py`、`compose.yaml`、`handoff_a_to_b.py`、`scan_runtime_logs.py`、`test_handoff.py`） | **A2 万宇**，PR #28 合入 main | 只读核验、与课程包逐文件比对，未重写 |
| `labs/e11e12/pipeline.py` 的 `fixed_report_sha256` 机制 | **A2 万宇**（课程包未提供该文件） | 核实已在 main 生效，未重复实现 |
| E11–E12 消费者拒绝测试、`docs/students/241880597/…` | **B3 吴佳静**，PR #25 | 只读核验 |
| B2 报告内层 commit 校验与补丁作用域修复 | **B2 李敏君** | 只读核验 |
| C1 五阶段实跑、C7 两变体、E14 四容器实跑与故障注入 | **本人 A1** | 全部本人执行 |
| 真实项目 `projects/transfer-eta` 及 base/target/修复版 | **本人 A1**（E12 建立） | 本轮复用并重跑 |
| `verify_c7_isolation.py`、`test_c7_isolation.py`、`test_scan_runtime_logs.py`、`e13e14.yml` | **本人 A1** | 本轮新写 |
| `service.py` 的 `safe.directory`、`secret_scan.py` 的解码修复 | **本人 A1** | 本轮新写（CI 暴露的真实缺陷） |

## 3. 证据目录

```
docs/students/241880485/e13-e14/
├─ index.md          # 本文件
├─ report.md         # 个人报告
├─ ADR.md            # 决策记录
├─ AI_USAGE.md       # AI 使用记录
├─ evidence-index.md # 证据索引（文件 → 来源 → 说明）
└─ evidence/
   ├─ logs/          # 环境、源码 SHA、65 项契约测试、prepare
   ├─ c1/            # 请求、提交核对、运行日志、五阶段信封、summary.json
   ├─ c7/            # 两组请求、三个 result.json、隔离校验、退出码
   └─ e14/           # 四容器 health/ps/logs、扫描、样例/故障 summary、真实项目拒绝
```

## 4. 可复现的最小步骤

```bash
# 云机 A16，仓库根目录
python3 run_e11e12.py test                     # 65 项契约测试
python3 run_e11e12.py prepare                  # 生成 data/integration-sample
python3 run_e11e12.py run --request data/e13-c1-a1-01/request.json --out work/e13-c1-a1-01
python3 labs/e13e14/verify_c7_isolation.py work/e13-c7-a1-01-failed work/e13-c7-a1-01-success
E14_ROOT=$PWD E14_IMAGE=course-e11e12:241880485 \
  docker compose -f labs/e13e14/compose.yaml -p e14-241880485 up -d --wait
python3 labs/e13e14/orchestrate.py --request data/e13-mirror/request.json --out work/e14-sample-a1-02
```

`data/` 与 `work/` 均被 `.gitignore` 忽略，属本机生成物；请求、日志、summary 已复制进 `evidence/`。

## 5. 已知缺口

1. **H1 jsmn、H2 inih、H3 tiny-AES-c 输入包缺失**：工作区、仓库、队友交付中均无相关文件；分工表引用的 `02_操作手册/03_E13三个项目运行指南.md` 亦不存在。
2. **E14 真实项目四容器阻断**：`orchestrate.py::snapshot()` 硬编码 `{main.c, helper.c}` 与 `config.h`，`service.py` 的 echecker 角色硬编码 `main.o/helper.o`；真实项目 `transfer-eta` 被 `Unsupported teaching project profile` 拒绝（已实测）。
3. **教师隐藏测试未执行**：未获得任何用例或反馈。
4. **C2/C3/C4/C5/C6/C8** 不由 A1 主责，本轮未替队友填写结论。
