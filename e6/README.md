# E6 · 论文1 MVP

本目录只放 E6 的证据与报告；实验包代码在 [`../e5/A-buildchecker`](../e5/A-buildchecker)、[`../e5/B-draft`](../e5/B-draft)。

> 任务分工与判据由组长私下分发，不随仓库提交；`work/` 不提交。

## 状态

| 角色 | 状态 | 关键判据 | 证据 |
| --- | --- | --- | --- |
| A2（E6-A） | **完成（本地 WSL2）** | before 2 条 → after 0 条；仅 Makefile 变化；17 passed；自证 gate 8/8 | [`evidence/A2-241880496/`](evidence/A2-241880496/index.md) |
| B2（E6-B） | **环境阻塞（2026-10-25，Windows 无 Docker）** | 本地 24 passed；两轮真实构建、同镜像运行及输入哈希待 Linux 云服务器验证 | [`evidence/B2-241880543/`](evidence/B2-241880543/index.md) |

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

- 分支：`e5-7/B2-241880543`；个人服务镜像：`course1020-draft:241880543`。
- 当前环境为 Windows，`python3` 商店别名不可用，且未找到 Docker；使用可用 Python 执行课程 doctor/build/e6 均被 Linux 平台检查拒绝（退出码 2）。
- 本地现有 B 包单测 **24 passed**；课程证据校验因缺少 `result.json` 返回 **1 / passed=false**。未将单测中的 Docker 桩当作真实构建证据。
- 报告：[源码解释与五项核对表](reports/B2-241880543.md)；证据：[索引](evidence/B2-241880543/index.md)；待执行：[Linux 续跑步骤](reports/B2-241880543-linux.md)。
- 本次不标记 E6-B 完成，不涉及 B3 门禁、CI 或合并演示。
