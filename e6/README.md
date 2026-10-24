# E6 · 论文1 MVP

本目录只放 E6 的证据与报告；实验包代码在 [`../e5/A-buildchecker`](../e5/A-buildchecker)、[`../e5/B-draft`](../e5/B-draft)。

> 任务分工与判据由组长私下分发，不随仓库提交；`work/` 不提交。

## 状态

| 角色 | 状态 | 关键判据 | 证据 |
| --- | --- | --- | --- |
| A2（E6-A） | **完成（本地 WSL2）** | before 2 条 → after 0 条；仅 Makefile 变化；17 passed；自证 gate 8/8 | [`evidence/A2-241880496/`](evidence/A2-241880496/index.md) |
| B2（E6-B） | 待填 | 第一轮 `MISSING_MAKE`、第二轮 `build=0`；同 `image_id` 运行 `exit=0`、`hello E3` | — |

## A2 · E6-A 自动检测与修复复检

- 分支：`e5-7/A2-241880496`
- 镜像：`course1020-buildchecker:241880496`
- 主机：Ubuntu 26.04 LTS on WSL2，x86_64，4 CPU / 7.8 GiB，Docker 29.5.2

```bash
cd e5/A-buildchecker
python3 scripts/doctor.py --out work/doctor-A2-01/env.json
python3 scripts/lab_cloud.py build --out work/build-A2-01 --image course1020-buildchecker:241880496
python3 scripts/lab_cloud.py e6 --out work/e6-before-A2 --image course1020-buildchecker:241880496          # 退出码 1
python3 scripts/lab_cloud.py e6 --fixed --out work/e6-after-A2 --image course1020-buildchecker:241880496    # 退出码 0
python3 scripts/verify_e6_evidence.py --before work/e6-before-A2/evidence/findings.json --after work/e6-after-A2/evidence/findings.json
python3 scripts/lab_cloud.py build --out work/build-A2-02 --image course1020-buildchecker:241880496        # 17 passed
python3 scripts/lab_cloud.py gate --out work/e7-A2-selfcheck --image course1020-buildchecker:241880496     # 8/8
```

- 结论：`MISSING main.o → config.h`（`t.14`:579、`t.15`:23）、`REDUNDANT main.o → unused.h`（`make-db.txt`:1053）；修复后 `findings=[]`，`changed_inputs=["Makefile"]`。
- 新增测试：`e5/A-buildchecker/services/buildchecker/tests/test_extra_241880496.py`（2 项）。
- 自证门禁：`gate-result.json` 8/8 `passed=true`，`E7_GATE_EXIT_CODE=0`（正式门禁与 CI 归 A3）。
- 报告：[`reports/A2-241880496.md`](reports/A2-241880496.md)｜索引：[`evidence/A2-241880496/index.md`](evidence/A2-241880496/index.md)

## B2 · E6-B 两轮构建与同镜像运行

待本人补充（命令与预期见私发的任务分工文档 §6 B2；默认 `--replay` 可直接开跑）。
