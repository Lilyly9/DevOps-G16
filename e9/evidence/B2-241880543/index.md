# B2 / 241880543 · E9-B 证据索引

2026-11-03（Asia/Shanghai）。[个人报告](../../../docs/students/241880543/e8-e10/个人报告.md)、[ADR](../../../docs/students/241880543/e8-e10/ADR.md)、[AI_USAGE](../../../docs/students/241880543/e8-e10/AI_USAGE.md)、[CI记录](../../../docs/students/241880543/e8-e10/CI记录.md)。

## 环境与原件

- 学生源码 SHA：`3befe15c3912056474c359b7990b84048f53773f`；公共导入依赖 `7f6a448`。
- 交付PR=[#14](https://github.com/Lilyly9/DevOps-G16/pull/14)；其源码SHA=`883c7792c22752f4d9d35f57132e559beb91ae64` 的 [课程CI](https://github.com/Lilyly9/DevOps-G16/actions/runs/41568698562) 成功，原E7 A/B检查也成功。`ci/41568698562/` 保存原始API记录、artifact.zip、验证日志及verification.json，9项单测/六路线/30行矩阵/三项验证均已独立核验；属于公共回归，非本人代做他人阶段。
- WSL Ubuntu22.04 / x86_64 / Python3.10.12 / GCC11.4.0 / Make4.3 / Git2.34.1；本机无 Docker/image ID，环境原始记录见 `run-01/environment.json`。
- OUT（Windows）：`D:\LearningResources\大三上\DevOps\Project\DevOps-G16\work\e9-B-241880543-20261103-01`。
- OUT（Linux）：`/mnt/d/LearningResources/大三上/DevOps/Project/DevOps-G16/work/e9-B-241880543-20261103-01`。
- 原件内含 `direct/ macro/ mixed/` 三项目及内部 `.git`，`apply-demo/`、全部 `steps/`；`history/*.bundle` 可恢复各输入提交，备份排除 .git 时仍保留内部历史。

## 逐文件核查

`run-01/` 为精选原件按字节复制，非整个 OUT。`selected-manifest.json` 对本次精选实验文件记录 SHA-256；`.gitattributes` 禁止原件行尾转换和空白报错（原始patch有空格+TAB上下文，CSV有CRLF，失败日志有尾空格），不为静态检查改写实测字节。索引仍按普通文本检查。索引/文档与后续 CI 记录不属于该实验原件清单。

| 证据 | 看什么 / 实际结果 |
| --- | --- |
| `*-input.json` | commit=本次内部SHA；actual/declared/findings精确两项MD/RD；main.o实际config.h/main.c，helper.o仅helper.c |
| `*-expected.json` | scan之前冻结的独立集合与编辑行预期 |
| `direct.patch / macro.patch / mixed.patch` | 新增项分别在第8/5/8行，落在main.o直接列表、DEPS定义、main.o混合列表；原配方/变量引用保留 |
| `*-plan.json` | 各一项：target=main.o、dependency=config.h、style对应目录 |
| `*-before.Makefile` | 候选前原字节；三个原项目从未实际应用补丁 |
| `steps/*-apply-check/` | 三原项目及副本真实git apply --check，exit-code=0；argv/cwd与进程退出码可追溯 |
| `steps/*-source-clean/stdout.log` | 三原项目Git状态均为空，exit-code=0 |
| `apply-demo.Makefile` | 仅DEPS新增config.h，main.o仍引用$(DEPS) |
| `steps/demo-build/`、`demo-run/` | 副本构建退出0，首次程序输出1 |
| `steps/demo-incremental-build/stdout.log` | 第1行真实main.o编译，第2行真实链接；程序输出2见demo-incremental-run/stdout.log |
| `steps/final-source-audit/stdout.log` | 三个原Makefile字节与VALUE=1头文件全保持 |
| `steps/03-unit-tests/stderr.log` | 原7+本人2项，Ran 9 tests / OK；所有test_student名称确实出现 |
| `source-hashes.json`、`source-verification.json` | 三个实验源码文件原始字节与外层提交逐一吻合 |
| `results.csv`、`gate.json`、`结论.txt` | 三行apply_check/source_unchanged=True、edits=1；gate仅指E9范围，非E10接受门禁 |
| `regression-before/` | 真实修复前exit1、3个三风格子用例失败，plan实际3项而非1项 |
| `regression-after/` | 修复后exit0、9项通过；正式OUT中的单测又在已提交实现上通过 |

内部输入 SHA：direct=`7968c44a6f8311f5f444a650e962b1d2c4319152`；macro=`39f18b5b16fa373cb393f2ec535b39f86217340b`；mixed=`b2cd52cb01f4edc10492012b5303f673cdff873b`。它们不是外层学生源码SHA。

## 重跑

在有 Python>=3.9、Git、GCC、Make 的 Linux个人克隆Git根执行：

```bash
python3 -m unittest discover -s labs/e8e10 -p 'test_*.py' -v
python3 labs/e8e10/student_241880543_e9.py --out work/e9-B-241880543-<新唯一号>
```

预期9项通过；三个候选可检查，所有原项目干净；副本输出1→2；全部STEP_EXIT_CODE=0。脚本拒绝已有OUT。使用容器时需先准备个人课程镜像并挂载仓库；本次宿主实测没有伪造该步骤。

## 归档与交接

完整运行原件归档：[B2-241880543-e9-originals-20261103.tar.gz](B2-241880543-e9-originals-20261103.tar.gz)，39,584字节，SHA-256=`471ef745462c6f85e27f7711cc0e057400cf4a0237b01313c18d2ad113ba9cbb`。含本次OUT、修复前后日志、三份内部历史bundle，排除.git、环境凭据与缓存；257个归档文件均逐字节对比原件通过。源码/个人文档在同一仓库中单独交付。

仓库外本机副本：`C:\Users\Staris\.codex\visualizations\2026\11\03\01a19f31-73d7-7033-a9c4-1a38c5185dd4\B2-241880543-e9-originals-20261103.tar.gz`。实际大小、路径与核验说明另见 `backup.json`。该小型完整原件归档另复制到个人证据目录，随分支推送后B3可直接取得，无需访问本人电脑。没有把整个团队work或其他成员历史打包。

服务器第二副本、B3实际收件确认及组长合并仍需对应人员完成。本索引不把仅有本机路径写成已移交，也不把apply --check/副本构建写成E10已接受源文件。
