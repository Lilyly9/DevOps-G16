# A2 · E6 最终 main 复核（2026-10-26）

在 `main`（`36047e31deaaddd767957b6fd151003d1debd545`）上重跑 A2 的 E6 交付，确认 A1/B1/A3/B3 的代码改动合入后，E6 判据仍然成立。

| 项 | 值 |
| --- | --- |
| 角色 / 学号 | A2 / 241880496 |
| 复核基线 | `36047e31deaaddd767957b6fd151003d1debd545`（`main`） |
| 服务镜像 | `course1020-buildchecker:241880496` → `sha256:7b7a4387292a936d0ac9be9bd59aa29e5f4c048a56238edc3eea54d82d2323cf` |
| 主机 | Ubuntu 26.04 LTS on WSL2，x86_64，4 CPU，7.8 GiB，Docker 29.5.2 |

## 命令

```bash
cd e5/A-buildchecker
python3 scripts/lab_cloud.py build --out work/build-A2-recheck-01 --image course1020-buildchecker:241880496 --build-timeout 1200
python3 scripts/lab_cloud.py e6 --out work/e6-before-A2-recheck --image course1020-buildchecker:241880496
python3 scripts/lab_cloud.py e6 --fixed --out work/e6-after-A2-recheck --image course1020-buildchecker:241880496
python3 scripts/verify_e6_evidence.py --before work/e6-before-A2-recheck/evidence/findings.json --after work/e6-after-A2-recheck/evidence/findings.json
python3 scripts/lab_cloud.py gate --out work/e7-A2-recheck --image course1020-buildchecker:241880496
```

## 预期 vs 实际

| 步骤 | 预期 | 实际 |
| --- | --- | --- |
| `build` | 通过 | 退出码 0，**19 passed**（原始 15 + A2 2 + A3 1 + 门禁演示 1） |
| `e6`（原始） | 退出码 1，2 条错误 | 退出码 1，`findings` 恰为 `MISSING(main.o, config.h)` + `REDUNDANT(main.o, unused.h)` |
| `e6 --fixed` | 退出码 0，`findings=[]` | 退出码 0，`findings=[]` |
| `verify_e6_evidence` | `passed=true`，仅 Makefile 变化 | `passed=true`，`changed_inputs=["Makefile"]` |
| `gate`（自证） | 退出码 0，8/8 | 退出码 0，8/8 `passed=true` |

## 文件

| 路径 | 内容 |
| --- | --- |
| `before/findings.json`、`before/make-db.txt` | 原始检测报告与 Make 声明（`trace_id=e6-1114ff2d004f4fe1b0120fe798d8237d`） |
| `before/trace/t.14`、`t.15` | MD 的读取与目标写出锚点 |
| `after/findings.json` | 修复复检（`trace_id=e6-6dbd29621dd743d0bb2d50eb7fc51dbc`，`findings=[]`） |
| `verify-e6.json` | 前后一致性校验输出（`passed=true`） |
| `build/tests-19-passed.log` | 最终 main 上的单测输出 |
| `gate/gate-result.json`、`gate/results.csv` | 自证门禁 8 项结果 |

## 与首次运行（2026-10-23）的差异

| 项 | 首次 | 本次 | 说明 |
| --- | --- | --- | --- |
| 基线 | `c343b5b`（仅 A 包入库） | `36047e3`（全组已合入） | 本次覆盖 A1/B1/A3/B3 的改动 |
| 单测数 | 17 passed | 19 passed | 新增 A3 的 1 项与门禁演示 1 项 |
| `trace_id` | `e6-d4fd…` / `e6-23a2…` | `e6-1114…` / `e6-6dbd…` | 每次运行必然不同 |

判据结论（错误集合、修复后清空、仅 Makefile 变化）两次一致。正式 gate 与 CI 由 A3 执行，见 `e6/reports/A2-241880496.md` 的 CI 段。
