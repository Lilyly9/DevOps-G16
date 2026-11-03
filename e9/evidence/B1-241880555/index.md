# B1 · 241880555（郭德林）E9-B 证据索引

- 日期：2026-11-03；角色：**B1**（B 组 E8 主责；本次按任务要求额外完整执行 E9-B 参考路线，**非 B2 主责交付**，B2 本人交付以其学号证据为准）
- 环境：Aliyun ECS（Ubuntu 22.04，x86_64）；镜像 `course-e8e10:241880555` = sha256:8b8cba482ea52745fcd4514c719084d4561be82209834fc3cec73771389be276（与 E8-B 同一镜像，未重建）
- 外层学生源码 SHA：ee84236f41a658fb4d779f2d2bf6f1aa11e03c87（`OUT/student-source-commit.txt`）
- 内部样例 C0 SHA：direct=a8f41880883655e80a408a7ec5917e7fb41f34a2、macro=c581bc1a907920954c02ccb75a589240f25b4354、mixed=385cd048d9d8bb05b7f5f421f5fedd90bd8a3fbe（各自独立 fixture + 内部 Git）
- 本次 OUT：`work/e9-B-manual.KUAgZz`（完整原件保留于本人克隆 `work/`，被 .gitignore 忽略不提交）

## 完整命令与重跑步骤

服务器仓库根 `/root/241880555/DevOps-G16`（分支 `student/241880555/e8-e10`）：

```bash
E8_PACK=$HOME/devops-materials/DevOps_E8_E10/03_实验包
source "$E8_PACK/classroom_helpers.sh"
lab_ready
lab_new_run e9 B          # 新建唯一 OUT（重跑会得到新目录）
OUT=$(cat work/last-e9-B.path)
# 步骤1-3：lab_python → fixture(style)+scan+patch → 各风格 input.json/patch/plan
#          断言 style 命名、Makefile 字节不变、git apply --check 通过
# 步骤4：for STYLE in direct macro mixed; do cat patch/plan; git status --short; done
# 步骤5：lab_python → copytree(macro→apply-demo, 忽略 .git)→ git init/apply
#          断言 demo 含 config.h 且原 macro 项目无 config.h
# 步骤6：grep 定位 lab.py patch()，写结论.txt
```

断线恢复：`OUT=$(cat work/last-e9-B.path)`。

## 关键结果（steps/ 日志一一对应）

| 手册步骤 | 日志（steps/） | 关键输出 |
| --- | --- | --- |
| 1 direct | 20261103-191803-1.log | `+main.o: main.c unused.h config.h`，style=direct，STYLE_PASS |
| 2 macro | 20261103-191803-2.log | `+DEPS = main.c unused.h config.h`，目标行保持 `$(DEPS)`，style=macro |
| 3 mixed | 20261103-191804-3.log | `+main.o: main.c $(HEADERS) config.h`，保留宏引用，style=mixed |
| 5 apply-demo | 20261103-191923-1.log | APPLY_TO_COPY_PASS：demo 的 DEPS 含 config.h，原 macro 项目无 config.h |

步骤 4（并排查看）与步骤 6（结论定位）为只读 shell，无 steps 日志；`patch()` 位于 `labs/e8e10/lab.py:76`，拒绝类型定位：UNSUPPORTED_RULE(L40)、UNSUPPORTED_DECLARATION(L44)、UNSUPPORTED_FLAGS(L50)、STALE_REPORT(L77)、UNSAFE_PATH(L82)、UNSUPPORTED_TARGET(L85)、UNSUPPORTED_MACRO(L89)。

## 本目录精选产物（字节复制自 OUT，SHA256SUMS.txt 全量校验）

- `{direct,macro,mixed}-input.json`：三种风格的固定报告（均含 MISSING(main.o,config.h)+REDUNDANT(main.o,unused.h)）
- `{direct,macro,mixed}.patch`：三种风格候选补丁——均只增 config.h，不删 unused.h、不改配方
- `{direct,macro,mixed}-plan.json`：三个 plan，各一条 edit，style 分别为 direct/macro/mixed
- `结论.txt`、`steps/`（4 份完整步骤日志）
- `unit-tests-241880555-20261103-193600.log`：**预期修正前**的失败日志（Ran 11 tests，1 failure）——保留作为"先写独立预期再看结果"的证据
- `unit-tests-241880555-20261103-193709.log`：修正后通过（Ran 11 tests OK）

## 个人扩展（labs/e8e10/test_student_241880555.py，类 StudentE9B_SharedDeps_241880555）

| 用例 | 独立预期 | 实际 |
| --- | --- | --- |
| test_macro_patch_shared_variable_expands_helper_declaration | helper.o 改为引用 $(DEPS) 后，scan 产生两条 MISSING（main.o→config.h、helper.o→helper.c）；patch 对每条 MISSING 依次追加到共享变量定义，最终 `DEPS = main.c unused.h config.h helper.c`；两个目标行保持 $(DEPS) 字节不变，helper.o 声明被动扩大（含 config.h）；重检无 MISSING | 通过（初版预期只写一条 edit，实测第二条 MISSING 后修正预期——声明改为引用变量时，原字面依赖 helper.c 从展开结果中消失） |

共享变量影响结论：`patch()` 的 macro 修复修改的是变量定义本身，**所有引用该变量的目标**的声明集合都会变化；参考实现不分析跨目标影响范围（手册原文同此限制），本用例以实际扫描结果如实演示该影响。

## 归档与备份

- 完整 work 原件不在 Git 中：从归档或本人克隆 `work/e9-B-manual.KUAgZz/` 获取
- 归档路径见 `docs/students/241880555/e8-e10/个人报告.md` 与服务器 `~/devops-submissions/241880555/`
- GitHub：PR #17（`student/241880555/e8-e10` → `main`）；CI 见 `docs/students/241880555/e8-e10/CI记录.md`
