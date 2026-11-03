# B1 · 241880555（郭德林）E8-B 证据索引

- 日期：2026-11-03；角色：B1（B 组 E8 主责：固定 MD 报告、候选生成、旧报告拒绝）
- 环境：Aliyun ECS（Ubuntu 22.04，x86_64，实测可见内存 3.5Gi、磁盘可用 65G）；个人镜像 `course-e8e10:241880555` = sha256:8b8cba482ea52745fcd4514c719084d4561be82209834fc3cec73771389be276
- 镜像构建日志：`work/environment-build-20261103-123353.log`（ENV_BUILD_EXIT=0）
- 外层学生源码 SHA：f1653557d066f7a17b2d2dce020126c34b8f6fcf（`OUT/student-source-commit.txt`）
- 内部样例 C0 SHA：8763e4fe56206179d0f352b1d67023e38ad840fa（`OUT/project` HEAD；报告 commit 同值）
- 本次 OUT：`work/e8-B-manual.qsW6Xo`（完整原件保留于本人克隆 `work/`，被 .gitignore 忽略不提交）

## 完整命令与重跑步骤

服务器仓库根 `/root/241880555/DevOps-G16`（分支 `student/241880555/e8-e10`）：

```bash
E8_PACK=$HOME/devops-materials/DevOps_E8_E10/03_实验包
source "$E8_PACK/classroom_helpers.sh"
lab_ready                # 仓库/学号/镜像确认
lab_new_run e8 B         # 新建唯一 OUT（重跑会得到新目录）
OUT=$(cat work/last-e8-B.path)
# 步骤1：lab_python "$OUT" → fixture(out/'project')
# 步骤2：cat $OUT/project/{Makefile,main.c,config.h,helper.c}; git -C $OUT/project log -1 --oneline
# 步骤3：lab_python → scan() → fixed-md-report.json
# 步骤4：lab_python → assert r['commit']==HEAD
# 步骤5：lab_python → patch() → candidate.patch + patch-plan.json
# 步骤6：lab_python → git apply --check + 工作区干净断言
# 步骤7：lab_python → STALE_REPORT 拒绝 + 字节不变断言
# 步骤8：写结论.txt
```

断线恢复：`OUT=$(cat work/last-e8-B.path)`，查看 `$OUT/steps/` 最后一份日志后从下一步继续。

## 关键结果（steps/ 日志一一对应）

| 手册步骤 | 日志（steps/） | 关键输出 |
| --- | --- | --- |
| 1 fixture | 20261103-124450-1.log | CREATED，STEP_EXIT_CODE=0 |
| 3 scan | 20261103-124800-1.log | MISSING(main.o,config.h) + REDUNDANT(main.o,unused.h) |
| 4 报告身份 | 20261103-124816-1.log | COMMIT_MATCH 8763e4fe… |
| 5 生成补丁 | 20261103-124901-1.log | style=direct，只增 config.h，PATCH_GENERATED_SOURCE_UNCHANGED |
| 6 apply --check | 20261103-124930-1.log | APPLY_CHECK_PASS_SOURCE_CLEAN |
| 7 旧报告拒绝 | 20261103-125025-1.log | EXPECTED_REJECTION STALE_REPORT + SOURCE_BYTES_UNCHANGED |

## 本目录精选产物（字节复制自 OUT）

- `fixed-md-report.json`：固定报告输入（commit=8763e4fe…；findings 两条：MISSING/REDUNDANT）
- `candidate.patch`：唯一改动行 `+main.o: main.c unused.h config.h`
- `patch-plan.json`：`[{"target":"main.o","dependency":"config.h","style":"direct"}]`
- `expected-failure.json`：`{"error":"STALE_REPORT"}`
- `结论.txt`、`steps/`（6 份完整步骤日志）
- `unit-tests-241880555-20261103-125346.log`（Ran 9 tests OK）
- `environment-build-20261103-123353.log`（镜像构建）

## 个人扩展（labs/e8e10/test_student_241880555.py，类 StudentB1_241880555）

| 用例 | 独立预期 | 实际 |
| --- | --- | --- |
| test_unknown_target_rejected_and_source_intact | target=phantom.o → ValueError('UNSUPPORTED_TARGET')，Makefile 字节不变 | 通过 |
| test_redundant_only_report_generates_no_deletion | 纯 RD 报告 → diff=''、edits=[]、unused.h 保留 | 通过 |

## 归档与备份

- 服务器：`~/devops-submissions/241880555/E8-E10-<时间戳>.tar.gz`（提交手册 §9，排除 .git/.env/密钥）
- 本机：`D:\Users\nmh\Desktop\DevOps-G16\work-backup-e8b\`（scp 下载副本）
- GitHub：PR #17（`student/241880555/e8-e10` → `main`，https://github.com/Lilyly9/DevOps-G16/pull/17）；CI 见 `docs/students/241880555/e8-e10/CI记录.md`（e8e10-quality-gate run 41582298352 success，headSha=8a3986d 对应报告提交）
- 完整 work 原件不在 Git 中：从上述归档或本人克隆 `work/e8-B-manual.qsW6Xo/` 获取
