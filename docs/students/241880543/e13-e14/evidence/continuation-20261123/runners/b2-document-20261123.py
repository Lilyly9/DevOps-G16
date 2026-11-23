from pathlib import Path
import json
root=Path.cwd();doc=root/'docs/students/241880543/e13-e14';ev=doc/'evidence/continuation-20261123'
r=json.loads((ev/'verified-runs.json').read_text())
index='''# E13–E14 B2 交付记录

李敏君 · 241880543 · MDFixer · 更新于 2026-11-23

分支 `student/241880543/e13-e14`，基线 `28c94defee5af11ada42f9842cf03db2cb9da2e3`。[PR #32](https://github.com/Lilyly9/DevOps-G16/pull/32) · [Issue #31](https://github.com/Lilyly9/DevOps-G16/issues/31)。原未提交改动已纳入提交，原 stash 备份保留。

| 验证项 | 本轮实际结果 | 原始证据 |
| --- | --- | --- |
| E7 A/B 扫描修复 | 全仓库和历史扫描退出 0；读取凭据表达式不再误报，字面量密钥、含默认值的调用仍被拒绝 | `evidence/continuation-20261123/scanner-*.log`；远端修复提交四类 CI 均成功，见 `ci-scanner-fix.json` |
| Linux 回归 | E11/E12 75 项、E14 5 项、扫描回归 3 项均退出 0 | 同目录 `linux-e11e12.log`、`linux-e14.log`、`scanner-tests-linux.log` 及 exit |
| C5 | 真实损坏补丁拒绝、可构建但依赖错误的补丁拒绝回滚、正确补丁接受与 strace 最终重检通过 | [既有三路径原件](evidence/docker-c5.zip) |
| H1 jsmn / H3 tiny-AES-c | 本轮官方 E12 五阶段全部成功，同镜像命令各 20 条，最终无 MISSING，原始项目摘要和 Git 干净状态不变 | [本轮教师项目原件](evidence/continuation-20261123/teacher-linux.zip) |
| C1 A→B 正常链路 | A1 transfer-eta 新运行 A 侧检测、导出当次报告，B2 核对 SHA 后完成 E12 修复与动态复验，最终无 MISSING | [当次 A 报告和首次 B 尝试](evidence/continuation-20261123/c1-a-and-first-b.zip) · [B 成功重跑](evidence/continuation-20261123/c1-b-recovery.zip) |
| E14 四容器 | 固定样例、H1、H3、真实 transfer-eta 五阶段均成功；四个独立服务的 /health、角色日志、job/trace、报告 SHA、补丁接受及最终无 MISSING 均核对通过 | [H1](evidence/continuation-20261123/e14-four-services.zip) · [固定样例和 H3](evidence/continuation-20261123/e14-fixed-h3.zip) · [真实项目](evidence/continuation-20261123/e14-real-project.zip) |
| E14 超时恢复 | 状态以本轮恢复记录为准 | `evidence/continuation-20261123/verified-runs.json` |

[逐项 SHA、job/trace 与归档校验清单](evidence/continuation-20261123/verified-runs.json) · [本轮说明](CONTINUATION.md) · [报告](REPORT.md) · [ADR](ADR.md) · [教师项目来源](TEACHER_RUNS.md) · [历史记录](HISTORY.md)。最终 PR 提交的远端 CI 以 GitHub Checks 实际状态为准；已有绿色记录绑定具体源码提交，不能套用到后续提交。

## 复现与范围

本轮为 WSL Ubuntu 22.04 / Docker 29.1.3 实测。运行镜像由仓库课程 Dockerfile 的独立副本构建，使用可达的官方软件源及 host 构建网络；测试命令容器仍使用原有网络隔离。独立适配层记录了 Docker 构建网络包装脚本、Git 对挂载测试目录的信任和 core.filemode 配置。教师原始源码和 Git C0/C1 不变；C1 仅派生 HTTPS 安装候选，保留原候选摘要。

四服务使用课程 Compose 文件对应的端口、资源限制和挂载，以四条独立 docker run 命令部署。本轮验证的是四容器实际 HTTP 链路；没有执行 docker compose 命令。启动命令、容器 inspect、健康响应和退出码全部归档，各次仅清理本人容器。运行入口与构建副本保存在 `evidence/continuation-20261123/runners/`；每次需使用新的 OUT。

本页只申报上述 B2 实跑项目。整组 C1–C8、H2、E13 总门禁、跨机共享入口、RC 标签和 Release 仍须由对应成员及组长汇总，本人没有将整组 E13/E14 标记通过。失败尝试、旧 Windows 权限阻断和旧清单保留为历史证据，不能当作当前结果。
'''
(doc/'index.md').write_text(index,encoding='utf-8',newline='\n')
text='''# B2 本轮续验说明（2026-11-23）

E7 A/B 失败共同来源是凭据读取代码被通用赋值规则误报，历史扫描也重复匹配该行。两个扫描器现在仅忽略 AST 确认的单参数映射 get 调用，参数必须是常用凭据字段名；没有删除文件扫描或历史扫描。强格式密钥仍独立检查，字面量、带默认值的 get 调用和伪装成字符串的调用均有拒绝回归。

E14 原入口仅支持 main.o/helper.o。新增复用 E12 项目配置及 project_path 的路径，以 target 的 e12-profile.json 为同一基准校验 base/target 源文件，让缺少配置文件的历史基线也能运行。BuildChecker 的构建目标、EChecker 的对象映射和 MDFixer 的输出/头文件变化验证都使用这份配置。路径越界和真实快照保真回归均通过。

## 本轮独立任务

| 项目 | job | trace | base → target |
| --- | --- | --- | --- |
'''
for key,c in r['cases'].items():
 text+=f"| {key} | `{c['job_id']}` | `{c['trace_id']}` | `{c.get('base','报告交接')}` → `{c.get('target','原清单中的目标')}` |\n"
text+='''
## 证据与环境

`verified-runs.json` 逐一校验成功任务的五阶段顺序、产物 SHA/字节数、job/trace、最终无 MISSING；H1/H3/C1 同镜像执行分别核对请求镜像、实际镜像和容器退出码。四容器分别检查四个独立 ID、相同运行镜像、四个健康响应、角色日志中的相同 job/trace 及清理退出码。

本轮教学镜像构建成功日志为 `../e14-image-host-20261123.log`，原失败日志继续保留。Git 适配只影响测试进程和独立容器镜像，不修改宿主全局 Git 配置。通过 core.filemode=false 处理 DrvFS 权限位；原件字节摘要仍逐项核对。

C1 使用 A1 提供的 transfer-eta 完整提交，不沿用旧报告。本机重新执行 A 侧检测并导出当次报告，保留来源 job/trace、源报告 SHA 和 fixed-md SHA；B2 读取后重新构建和验证。首次 B 构建因清华 HTTP 软件源不可达失败，派生 HTTPS 候选成功，保留原候选、派生候选和原 base/target 身份。

四容器测试是个人隔离复验；本轮没有据此申报整组 E13 门禁或 RC 发布。
'''
(doc/'CONTINUATION.md').write_text(text,encoding='utf-8',newline='\n')
(doc/'REPORT.md').write_text('''# B2 MDFixer 个人报告

当验证通过后最终 BuildChecker 重检异常或超时时，旧流水线会失败却留下候选 Makefile。本修改把验证和最终重检纳入同一个恢复边界：只有全部成功且无 MISSING 才保留补丁；其他退出恢复原始 Makefile 字节并保存回滚阶段、job/trace、commit 和摘要。验证器补充执行异常落盘和补丁、源文件前后 SHA256。

新增 10 项 B2 契约，且已有真实 C5 三路径原件。本轮继续修复 E7 凭据读取误报，并为 E14 复用现有项目配置，使 A1 的 transfer-eta 能走四服务链路。

实际完成：Linux E11/E12 75 项、E14 5 项和扫描回归 3 项通过；H1/H3 官方 E12 全五阶段通过；C1 使用当次 A 报告完成 B2 修复和最终动态复验；固定样例、H1、H3、transfer-eta 四容器五阶段均成功。逐项 job/trace、完整 SHA、镜像、命令、产物哈希、日志和失败尝试见 [本轮说明](CONTINUATION.md) 和 [证据索引](index.md)。

E7 修复提交的远端四类检查均通过，后续 PR 提交以实际 Checks 结果为准。运行环境的构建网络、软件源、Git 适配以及 docker run 部署方式均在索引中明确记录。未申报整组 C1–C8、H2、总门禁或 RC 发布。
''',encoding='utf-8',newline='\n')
p=doc/'TEACHER_RUNS.md';s=p.read_text(encoding='utf-8');p.write_text('''> 2026-11-23 更新：H1 jsmn 主执行及 H3 tiny-AES-c 复核已在 Linux 官方 E12 入口跑通五阶段，各核对 20 条同镜像执行记录，最终无 MISSING。原始输入与 Git C0/C1 不变；本轮 [Linux 原件](evidence/continuation-20261123/teacher-linux.zip)、[逐项清单](evidence/continuation-20261123/verified-runs.json)。下文 Windows 阻断说明为历史记录。

'''+s,encoding='utf-8',newline='\n')
body='''最终 BuildChecker 重检异常或超时时，旧流程会留下候选 Makefile。此修改将验证和最终重检纳入同一恢复边界，仅全部成功且无 MISSING 才保留补丁；其余退出恢复原始字节并保存 rollback.json、job/trace 与 SHA256。

修复 E7 A/B 扫描对凭据读取表达式的误报，保留字面量及强格式密钥检测和完整历史扫描。E14 复用既有 e12-profile/project_path 支持真实项目，并对历史基线统一使用目标项目配置。

实际验证：

- Linux E11/E12 75 项、E14 5 项、扫描回归 3 项全部通过；已有 10 项 B2 契约及真实 C5 三路径原件。
- H1 jsmn、H3 tiny-AES-c 官方 E12 全五阶段成功，各 20 条同镜像执行记录通过核对，最终无 MISSING。
- C1：A1 transfer-eta 当次 A 侧报告经 SHA 校验交给 B2，B2 构建、补丁验证及动态复验通过；首次 HTTP 软件源失败和 HTTPS 派生候选均归档。
- 四个独立 HTTP 服务完成固定样例、H1、H3、transfer-eta 五阶段；健康、job/trace、报告 SHA、补丁接受和最终无 MISSING 均核验。
- E7 修复提交 b376720 的 E7 A/B、E8/E10、E11/E12 远端检查全部成功；最新提交以实际 Checks 为准。

证据：docs/students/241880543/e13-e14/index.md 与 evidence/continuation-20261123/verified-runs.json。四服务按课程 Compose 的设置使用 docker run 启动；构建网络和 Git 环境适配均留原件。整组门禁与 RC 未申报通过，PR 保持草稿。

Closes #31
'''
(doc/'PR_BODY.md').write_text(body,encoding='utf-8',newline='\n')
for name,content in [('AI_USAGE.md','- 2026-11-23 B2 续验：Codex 修复 E7 A/B 扫描误报并增加正反例；补齐 E14 真实项目配置复用，基线使用目标配置。实际执行 H1/H3、当次 C1 报告交接及四容器固定/未知/真实项目验证，逐项状态和原件见个人索引；不以健康响应代替五阶段或整组门禁。'),('CONTRIBUTIONS.md','- 2026-11-23 B2 续交付：E7 A/B 凭据读取误报修复及回归通过；H1/H3、A1 transfer-eta 当次 C1 修复和固定/H1/H3/真实项目四容器五阶段已有成功原件。新增 E14 project_path/profile 复用及基线配置兼容，详细证据见 docs/students/241880543/e13-e14/index.md。')]:
 p=root/name;p.write_bytes(p.read_bytes().rstrip()+b'\n\n'+content.encode('utf-8')+b'\n')
p=root/'E13-14_TASKS.md';original=p.read_bytes();lines=original.splitlines(keepends=True)
for i,line in enumerate(lines):
 if line.startswith(b'| B2   |'):
  end=b'\r\n' if line.endswith(b'\r\n') else b'\n'
  lines[i]='| B2   | 李敏君 / 241880543 | `student/241880543/e13-e14` | C5 真实三路径；H1/H3 官方 E12 五阶段；C1 A1 transfer-eta 当次报告交接、B2 修复与动态复验通过 | 固定、H1、H3、真实 transfer-eta 四容器五阶段通过，健康/角色日志/job/trace/报告 SHA 已核对；组门禁及 RC 待汇总 | [个人记录](docs/students/241880543/e13-e14/index.md) · [PR #32](https://github.com/Lilyly9/DevOps-G16/pull/32)；E7 修复提交四类 CI 成功，最新提交以实际 Checks 为准 |'.encode('utf-8')+end
p.write_bytes(b''.join(lines))
print('Updated B2 documentation from verified results')
