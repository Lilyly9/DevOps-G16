# A3 E10-A 原件与交接索引

林涵 / 241880464 / A16；2026-11-03。本人[报告、ADR、AI及CI记录](../../../docs/students/241880464/e8-e10/个人报告.md)，[个人PR #16](https://github.com/Lilyly9/DevOps-G16/pull/16)。

## 正式运行身份

实际源码4cf51fa78bc856c9b0c3c559c8e10ebf6a4c64a2；镜像course-e8e10:241880464，完整ID sha256:a0bafc7c741bc8912adbc1b1797202c5bc0f220c67f8879b556627a521b3322c。云端独立克隆 /root/241880464/DevOps-G16-e10-A3-20261103；标准OUT work/e10-A-manual.dAyEb0，扩展OUT work/e10-A-manual.1v1wdC。Ubuntu22.04.5 / x86_64 / 2CPU / 3.5GiB / 64GiB空余；内存低于4GiB建议，未宣称环境达标。

标准项目内部C0 93ffbab6fafd7cdfe17c09a6d08af83441f2fe92至header 505681419cbce2039526279d5a1d19ea04aedbb5；扩展2892851857387cf279341865b3c4c2bde6e8f052至e4975164422e44cdfecf46bb0bcdfbf68e49145c。两个project-history.bundle保存各自历史；它们是内层测试输入，不含外层登录信息。

## 原件位置与判据

- standard/matrix/：独立输入、baseline、六类末次JSON、60份逐次JSON、30行results.csv、performance-summary.csv、gate.json。六类各5次、equal全True；复用/刷新与MD/RD完整集合见报告。
- standard/matrix/final-buildchecker/：完整文字trace、processes、实际/声明图、make-db与findings；status=SUCCEEDED，无MD，只保留RD main.o→unused.h。make-db.txt:1052、trace/t.14:596（config.h）、:101（extra.h）、:67（main.c）可直接回查。
- extension/extension/：expected.json先保存独立预期，再创建输入；宏启用新增mode.h，五次独立预期及完整集合比较均通过；10份原始JSON、5行CSV及统计。标准OUT没有覆盖。
- standard/steps、extension/steps：helper保存的真实容器日志，标准8步、扩展1步均STEP_EXIT_CODE=0；execution/保存本次完整运行脚本、官方helper、构建/会话/单测日志、宿主环境和工具锁。独立预期另在e10/ci/241880464/自主预期.md。
- evidence-audit.json：分别核对本机/云端30行、独立图集、逐次原始计时与统计；扩展5次单独核查。evidence-audit-command.py为实际审查命令原件，含本机路径，异机需适配。
- ci/：绑定真实head的run/artifact元数据与早期失败原日志；完整下载artifact留在work与双端归档，未全量塞入Git。
- selection-scope.json：精选排除项，只去掉编译二进制/缓存；project-history.bundle保留。trace/数据库原件按字节复制，不裁剪、不改空白或行号；files.sha256.json逐文件复核。
- backup-record.json：真实原始归档双端路径/大小/哈希；最终包的实际哈希/大小另存包旁交付状态.json。本机云端原始包SHA一致。

## 完整命令与重跑

原标准执行脚本execution/cloud-manual-run.sh逐字保留本次手册命令。先在本人的仓库根配置数字身份，python3 run_lab.py build；source execution目录的classroom_helpers.sh后lab_ready、lab_new_run e10 A，按官方E10-A §1–13依次执行。script内E8_PACK适配到实际helper所在目录；写入步骤只运行一次，不把已创建OUT交给一键入口。

扩展新OUT的实际调用：

```bash
source e10/evidence/A3-241880464/execution/classroom_helpers.sh
lab_ready
lab_new_run e10 A
lab_python "$OUT" <<'PY'
from pathlib import Path
import sys
from student_241880464 import measure
measure(Path(sys.argv[1])/'extension')
PY
```

单测采用unittest discover -s labs/e8e10 -p 'test_*.py' -v，在本人镜像中执行，完整docker命令见个人报告。test_student_241880464.py为本人唯一测试文件；不改他人文件或课程原7项。

## 交接限制

本机预检另存work/e10-A-manual.aVwovS与PChVAq，源码955fcf37a6e70997a5e28966755a714e330cadb8。正式报告只统计上述云端运行，未把不同环境计时混合。后续文档提交的CI另见最终交付状态。本人的E8/E9现已分别在e8/evidence/A3-241880464与e9/evidence/A3-241880464补齐，按助教要求独立完成三阶段。main保护读取404、组长合并及全组每人三阶段证据仍分别登记。

助教要求更新：本E10目录原始8测记录保留；新增E8/E9自主测试后当前统一发现共10测。本人三阶段总报告见同一docs路径，最终完整包使用“全阶段”命名，旧E10阶段包仅供历史追溯。
