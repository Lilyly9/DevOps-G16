# E5–E7 归档（A16 / B16 · 共用仓库）

本目录存放 E5–E7 的**实验包代码**与**归档证据**。任务分工与判据见仓库根 [E5-7_TASKS.md](../E5-7_TASKS.md)。

- 仓库：`https://github.com/Lilyly9/DevOps-G16`（A16 + B16 共用）
- 实验包：`A-buildchecker/`（A 轨道）、`B-draft/`（B 轨道）
- 归档：`evidence/<角色>-<学号>/`、`reports/<角色>-<学号>.md`、`ci/<轨道>/`
- `work/` 不提交（实验包自带 `.gitignore` 已忽略 `work/`、`.env`、`*.pem`、`*.key`）

> 每人只追加自己那节，**顺序固定 A1→A2→A3→B1→B2→B3**；交接约定见 E5-7_TASKS.md §1。

## 总表

| 阶段 | 角色 | 状态 | 关键判据 | 证据 |
| --- | --- | --- | --- | --- |
| E5-A | A1 | 待填 | 输出 `1`；声明含 `unused.h`；trace 读到 `config.h` | 待填 |
| E6-A | A2 | **完成（本地 WSL2）** | before 2 条 → after 0 条；仅 Makefile 变化；17 passed；gate 8/8 | `evidence/A2-241880496/E6/` |
| E7-A + CI-A | A3 | 待填 | 6 tests OK；gate 8 项；CI 失败→恢复 | 待填 |
| E5-B | B1 | 待填 | `build=1` 且 `make: not found`；候选运行 `hello E3` | 待填 |
| E6-B | B2 | 待填 | 两轮构建；同 `image_id` 运行 `exit=0` | 待填 |
| E7-B + CI-B | B3 | 待填 | gate 6 项；五场景；CI 失败→恢复 | 待填 |

## A2 · E6 BuildChecker 自动检测与修复复检

- 分支：`e5-7/A2-241880496`
- 镜像：`course1020-buildchecker:241880496`
- 主机：Ubuntu 26.04 LTS on WSL2，x86_64，4 CPU / 7.8 GiB，Docker 29.5.2
- 命令（在 `A-buildchecker/` 下）：

```bash
python3 scripts/doctor.py --out work/doctor-A2-01/env.json
python3 scripts/lab_cloud.py build --out work/build-A2-01 --image course1020-buildchecker:241880496
python3 scripts/lab_cloud.py e6 --out work/e6-before-A2 --image course1020-buildchecker:241880496          # 退出码 1
python3 scripts/lab_cloud.py e6 --fixed --out work/e6-after-A2 --image course1020-buildchecker:241880496    # 退出码 0
python3 scripts/verify_e6_evidence.py --before work/e6-before-A2/evidence/findings.json --after work/e6-after-A2/evidence/findings.json
python3 scripts/lab_cloud.py build --out work/build-A2-02 --image course1020-buildchecker:241880496        # 17 passed
python3 scripts/lab_cloud.py gate --out work/e7-A2-selfcheck --image course1020-buildchecker:241880496     # 8/8
```

- 结论：`MISSING main.o → config.h`（`t.14`:579、`t.15`:23）、`REDUNDANT main.o → unused.h`（`make-db.txt`:1053）；修复后 `findings=[]`，`changed_inputs=["Makefile"]`。
- 新增测试：`services/buildchecker/tests/test_extra_241880496.py`（2 项：`# Not a target:` 跳过、order-only 被读取仍报 MISSING）。
- 自证门禁：`gate-result.json` 8/8 `passed=true`，`E7_GATE_EXIT_CODE=0`。
- 报告：[`reports/A2-241880496.md`](reports/A2-241880496.md)｜索引：[`evidence/A2-241880496/E6/index.md`](evidence/A2-241880496/E6/index.md)

## A1 · E5

待本人补充。

## A3 · E7 + CI

待本人补充。

## B1 · E5

待本人补充。

## B2 · E6

待本人补充。

## B3 · E7 + CI

待本人补充。
