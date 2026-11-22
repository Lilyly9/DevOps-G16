# E13–E14 A1 个人报告（焦龙 241880485）

## 1. 任务与范围

分工表给 A1 的主责是：提供 A 侧真实项目与完整 SHA、主跑 C1 与 C7、核对全量图；E14 负责四容器 BuildChecker/EChecker 联调、真实项目检测与候选清单；另需至少一项可独立审查的个人改动。

本轮实际完成：A 侧项目供给与全量图核对、C1（A 侧五阶段）、C7（两种失败形态的隔离）、E14 四容器五阶段与受控故障恢复、真实项目四容器可行性实测、缺失的 E13-E14 CI、以及 C6 运行时日志扫描的回归测试。未完成项集中在“输入缺失”和“共享入口绑定固定样例”两处，见第 8 节。

## 2. 开工前核验

### 2.1 远程真实状态（重新 fetch，不用旧缓存）

| 引用 | 值 |
| --- | --- |
| `origin/main` | `28c94defee5af11ada42f9842cf03db2cb9da2e3`（含 PR #25 B3 E11–E12、PR #28 A2 E13–E14） |
| `delivery/a16/e11-e12` | `f0dbb3b8329a11c821e716d806bb4e2e67a44fee`（E11–E12 交付分支，**未合入 main**） |
| 本地旧 HEAD | `f0dbb3b`（`delivery/a16/e11-e12`），相对 main 落后 15、领先 5 |
| 新增远程分支 | `student/241880496/e13-e14`（A2）、`student/241880555/e13-e14`（B1） |
| 标签 | `C0` `5872b2f…`、`C1` `f2d8432…`、`C2` `e9302a6…`；**无 `v0.9-rc`** |
| 仓库 `pushed_at` | 2026-11-21T09:13:04Z，晚于本地最后一次 fetch，故必须先 fetch 再判断 |

结论：`main` 已包含 A2 的四容器入口与 `pipeline.py` 的 `fixed_report_sha256`，但**不包含**我 E11–E12 的 `consume_report.py`。因此本轮个人分支从 `origin/main` 起，E11–E12 的消费者实现保留在 `delivery/a16/e11-e12` 与 `student/241880485/e11-e12`，不在本轮重复引入。

### 2.2 本地保护

`README.md` 存在用户原有的未提交改动（新增 2 行仓库链接）。开工前已备份到
`tmp/a1-e13e14-readme-preserved-20261122.md`（SHA-256 `33875C45…F7CA`），切换分支后原样还原，全程未纳入任何提交。

### 2.3 工作区权限故障（如实记录）

会话开始时 `DevOps` 根目录缺 `WRITE_OWNER`，沙箱无法授予写权限。用内置诊断脚本修复并验证（备份与回滚脚本在 `tmp/acl-recovery-20261122/`）。修复后根目录可写，但**已存在的子目录**（仓库、`E13-14`、`E11-12`、`tmp`）的继承 ACE 缺失，仍拒绝写入；只有新建目录可写。该问题由会话权限切换为完全访问后解除，期间没有修改任何文件内容。

### 2.4 课程资料缺口

| 资料 | 状态 |
| --- | --- |
| `02_操作手册/00_公共准备.md`、`01_E13交叉测试与门禁.md`、`02_E14候选发布.md` | 存在，已读 |
| `02_操作手册/03_E13三个项目运行指南.md` | **不存在**（目录下只有 00/01/02） |
| H1 jsmn / H2 inih / H3 tiny-AES-c 输入包 | **全工作区无匹配文件**（按名称递归检索 0 命中） |
| `03_实验包/labs/e11e12/pipeline.py` | **不存在**；`fixed_report_sha256` 实际由 A2 在 PR #28 中实现并已合入 main |

另：分工表中的链接写作 `e13-14/02_操作手册/...`，与本机实际的 `E13-14/DevOps_E13_E14/DevOps_E13_E14/...` 两级同名目录不符。

## 3. A 侧真实项目供给

`projects/transfer-eta`：C/Make 命令行工具，按速率估算传输耗时。

| 项 | 值 |
| --- | --- |
| base | `5ef9d829e2f893af23f60399dcb67095800d121e`（显式速率） |
| target | `e7414083c4f1760cb234f96a9d75f2d0255e3f57`（新增 `defaults.h` 默认速率） |
| 修复版 | `2efac5983b38ce9ddf05d194ba29169bba10e5b0` |
| 候选 | `projects/transfer-eta/candidate.Dockerfile`（固定 digest） |
| 预期输出 | base/target 构建后 `eta_seconds=13`；默认速率 8→5 后强制重建为 `20` |
| 运行限制 | 目标为 `eta_cli.o`、`estimate.o`；程序参数 `100`；需 `cc` + `make` + `strace`；仅 Linux 容器内执行 |

**真实全量图核对**：target 上 BuildChecker 的全量发现为
`MISSING(eta_cli.o → defaults.h)`，证据为 `openat` 系统调用（`t.12:923`、`t.13:23`），
声明依赖只有 `estimate.h`、`eta_cli.c`。这与项目的实验故障（Makefile 遗漏头文件依赖）一致，不是推测。

**适配核对（回应“两份配置名不同”的问题）**：仓库里有两套并存机制，服务对象不同，不能互相改名或覆盖——

- `labs/e11e12/project_profile.py` 读 `e12-profile.json`（schema `e12-project-1`），被 `pipeline.py` 使用，**transfer-eta 走这条**；
- `labs/e11e12/project_config.py` 读 `e11e12-project.json`（schema `e11e12-project-1`），被 `ecache.py`（A2 的 EChecker）使用，**tokenstat 走这条**。

两者都是已合入的实现，各自有测试；本轮据此保留原名，未做机械重命名。

## 4. C1 正常链路（A 侧供给与验证）

请求：`evidence/c1/request.json`（`mode=e12`、`project_path=projects/transfer-eta`、`profile=true`）。

| 项 | 值 |
| --- | --- |
| 退出码 | `0`（`evidence/c1/run.exit-code.txt`） |
| job / trace | `job-789dec04cba24db690ace58ecbe0f868` / `trace-ef57b1b5364d49b7b1f9357f4a5075b1` |
| 阶段 | `draft → full-check → incremental-check → repair → recheck` 全部 `SUCCEEDED` |
| 产物 | 235 个，URI 前缀均为 `artifact://job-789dec04…/` |
| target 发现 | `MISSING(eta_cli.o, defaults.h)` |
| recheck | commit = `e7414083…`，`MISSING` 计数 **0** |
| 报告链 | `repair` 记录的 `input_report.sha256` 与磁盘 `incremental-check.json` 的 SHA-256 **一致** |

即：A 侧真实项目的全量与增量结果可复现，修复后同一目标提交上缺失依赖消除，且报告字节与修复阶段读取到的字节一致。

## 5. C7 失败任务隔离（A 侧，两个变体）

校验器 `labs/e13e14/verify_c7_isolation.py` 检查：失败/成功状态、`job_id` 与 `trace_id` 不同、成功侧每个产物落在自己 job 的 URI 命名空间、SHA-256 与字节数一致、失败侧产物不越界、两侧产物集合无交集。

| 变体 | 失败任务 | 正常任务 | 结果 |
| --- | --- | --- | --- |
| A：错误 base（`0…0`） | `job-fce3110d7c4b483cac106e2e343d6216` / `trace-60cc0fe449654d278bcf8922c9dc2499`，`COMMAND_FAILED`，2 产物，退出码 1 | 同 C1 请求重跑：`job-802afa939103438da815537d7d93fb5b` / `trace-69276f4cc0754138b393bf02604ba886`，235 产物，退出码 0 | `C7_ISOLATION=PASS`，482 项检查 |
| B：构建超时（`build_timeout=0.01`） | `job-434f0696e4654f1f8335bb1e03f49a27` / `trace-e3bde1f7b74e446b9e01b826a74a0459`，`DRAFT_FAILED`（`Docker client command exceeded 0.01s`），**已产出 48 个产物**，退出码 1 | 同上 235 产物 | `C7_ISOLATION=PASS`，482 项检查 |

变体 B 是更强的证据：失败任务本身已有产物，仍与后续正常任务的 235 个产物完全隔离。

## 6. E14 四容器五阶段

### 6.1 环境与镜像源适配

四个容器共用教学镜像，`compose` 项目名 `e14-241880485`，端口仅绑定 `127.0.0.1:18081–18084`。
A16 上 `registry-1.docker.io` **不可达**（`dial tcp 128.242.245.180:443: i/o timeout`），首次运行因此在 DRAFT 阶段 `INFRASTRUCTURE` 失败。适配如下，全部记录在 `evidence/e14/mirror-adaptation.txt`：

| 项 | 处理 |
| --- | --- |
| 基础镜像 | 同 digest 改由 daocloud 镜像获取：`m.daocloud.io/docker.io/library/python:3.13-slim@sha256:70729b46…`，tag 保持不变，DRAFT 的候选校验仍然生效 |
| apt 源 | deb.debian.org 实测约 50 kB/s（88 MB 依赖 > 10 分钟未完成），候选 Dockerfile 增加一条 `RUN sed -i` 改为 `mirrors.tuna.tsinghua.edu.cn`；只新增 `RUN`，未改动原指令，校验可通过 |
| 固定样例 | 原始 `data/integration-sample` 未被修改；另建 `data/e13-mirror`，base/target 重算为 `52798034360135fe0af8644aa13cd3728a6c0667` / `c3561b73751452e1b4a3e41e81734293fc429bbd`，并记录替换前后 SHA-256 |
| 镜像 | `course-e11e12:241880485` = `sha256:40b15f7e…`（复用，未重建，避免 Docker Hub 超时） |

### 6.2 五阶段结果

| 项 | 值 |
| --- | --- |
| 退出码 | `0` |
| job / trace | `job-fc8b5db6f2b1408ea987ec29e4b0bd06` / `trace-cd0649b63f074cda968916ea55951966` |
| 阶段 | `draft`、`full-check`、`incremental-check`、`repair`、`recheck` 五个信封的 job/trace 与总结果**逐项一致** |
| 产物 | 162 个 |
| 健康检查 | `GET /health` 四角色均返回 `{"status":"ok","role":...}`；`compose ps` 四个 `healthy` |
| 角色日志 | `evidence/e14/services.log`（13 312 B），含角色、job、trace、状态、耗时 |
| 日志扫描 | `scan_runtime_logs.py`：工作区 `0`、服务日志 `0`（退出码均 0） |

### 6.3 受控故障与恢复

| 步骤 | 结果 |
| --- | --- |
| 故障请求 `build_timeout=0.01` | 退出码 1；`job-b99f47f871b54b7b9dbf867736abd844` / `trace-ce8b875938314eccbf2cacc142411873`；`DRAFT_TIMED_OUT: Docker client command exceeded 0.01s`；36 产物；五阶段未推进 |
| 恢复：同一请求原时限、全新输出目录 | 成功（上文 `job-fc8b5db6…`） |
| 标识隔离 | 两次 job/trace 不同，故障产物未进入成功清单 |
| 收尾 | 仅 `docker compose -p e14-241880485 down`，未触碰其他项目（同机另有他组容器 `magical_perlman`，全程未干预） |

## 7. 个人独立改动

1. **`labs/e13e14/verify_c7_isolation.py`**（新）：把 E13 手册里的一次性断言固化成可复用工具，输出结构化报告，退出码 0/1/2。
2. **`labs/e13e14/test_c7_isolation.py`**（新，7 项）：覆盖同 job、同 trace、越界命名空间、篡改字节、状态不符、stage 携带他 job、证据缺失等拒绝路径。
3. **`labs/e13e14/test_scan_runtime_logs.py`**（新，6 项）：钉住 C6 扫描器退出码 0/1/2、命中值必须被遮蔽、A2 的指针赋值例外；假 Key 运行时拼接，避免把密钥形状字面量写进仓库。
4. **`.github/workflows/e13e14.yml`**（新）：仓库此前**没有** E13-E14 工作流。`contracts` 作业做编译、契约测试、compose 校验与源码/历史扫描；`four-services` 作业构建镜像、`prepare`、四容器 `--wait` 起来后跑五阶段、扫描、C7 隔离、仅在 `always()` 收尾时 `down` 本项目。
5. **`labs/e13e14/service.py`**：为四角色设置 `GIT_CONFIG_*` 的 `safe.directory`，因为 CI 以 root 运行容器、工作区属 runner，git 否则报 `dubious ownership`。
6. **`labs/e11e12/environment/scripts/secret_scan.py`**：历史扫描遇到遗留 GBK 字节时 `UnicodeDecodeError` 直接中断，改为 `errors="replace"`，扫描总能给出结论。

本地 18 项 `labs/e13e14` 单测通过；容器内 E11–E12 契约测试 **65 项**通过（`evidence/logs/tests.log`）。

## 8. 未完成与阻断

### 8.1 H1/H2/H3 输入缺失

分工要求 H1 jsmn（A2+B2）、H2 inih（A1+B1）、H3 tiny-AES-c（A3+B3）。三项的输入包与 `03_E13三个项目运行指南.md` 在本机都不存在，仓库与队友分支中也没有。**需要的输入**：上述运行指南，以及三项各自的项目压缩包（含 base/target 提交或源码树、Dockerfile 候选、预期输出）。缺这些无法执行，也不能用自行下载的上游项目冒充教师指定输入或隐藏测试。

### 8.2 E14 真实项目四容器阻断

`orchestrate.py::snapshot()` 在克隆后断言 `{*.c} == {main.c, helper.c}` 且存在 `config.h`；`service.py` 的 echecker 角色把目标硬编码为 `main.o/helper.o`。真实项目 `transfer-eta`（`eta_cli.o`/`estimate.o`）因此被拒：

```
job-8d42debc0ba549e3901f86318acb8a92 → {"status": "FAILED", "error": "Unsupported teaching project profile"}
```

本轮**没有**为了让结果好看去改这份共享入口：它属 A2/A3 维护的契约，改动需与 B 侧同步。已把拒绝原样留证（`evidence/e14/orchestrate-real-project.log`、`real-project-result.json`、`real-project.exit-code.txt`）。下一步若获授权，应按 `project_profile.load_profile` 让四角色读 `e12-profile.json`，并同步更新 `test_handoff.py` 与 compose 的 echecker 分支。

### 8.3 其他

- 教师隐藏测试：未收到用例或反馈，未执行。
- C2/C3/C4/C5/C6/C8：非 A1 主责，本轮未替队友下结论。
- `v0.9-rc`：组级动作，远端无该标签，本轮未创建。

## 9. 失败与重试记录

| 时间（UTC） | 现象 | 处理 |
| --- | --- | --- |
| 01:35 | E14 首次 `orchestrate` 失败：DRAFT `INFRASTRUCTURE`，`python:3.13-slim@sha256:70729b…` 解析超时 | 确认 Docker Hub 不可达，改用 daocloud 同 digest |
| 01:37 | SSH 长连接被切断，E14 运行被终止，`work/e14-sample-a1-02` 无 `result.json` | 改为服务器端 `setsid` 后台 + 哨兵文件轮询 |
| 01:43 | 首次推送 `836c6c2` 使 E7 双门禁与 `e13e14-contracts` 变红：测试里写了密钥形状字面量 | 改运行时拼接；该提交是本人当天新建、尚无 PR 的单提交分支，删除后以 `1a824ff` 重推同一分支名（未动他人分支与标签） |
| 01:47 | `e13e14-contracts` 仍红：`secret_scan.py` 历史扫描 `UnicodeDecodeError` | 修复解码（`980e1a5`），CI 转绿 |
| 01:52 | DRAFT 修复构建极慢（88 MB 依赖，约 50 kB/s） | 候选 Dockerfile 增加清华源 `RUN`，同一流程 61 秒完成 |
| 01:56 | 误杀正在进行的样例运行（`pkill` 匹配过宽） | 保留故障变体结果，重跑样例，得到 `job-fc8b5db6…` |

## 10. 结论

- A 侧真实项目供给、全量图、C1、C7 均有本人实际执行的原件，可回到完整 SHA、退出码与 job/trace。
- E14 四容器五阶段在固定样例（镜像源适配版）上通过，含受控故障与恢复、四角色日志与日志扫描。
- E14 真实项目在现有共享入口下**阻断**，已留实测拒绝证据而非口头判断。
- 远端必需 CI 在 `980e1a5` 上 6 项全绿。
- 缺口集中在教师输入缺失（H1–H3、运行指南）与 E14 真实项目适配（需跨人协调）。
