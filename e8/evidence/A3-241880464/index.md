# A3本人 E8-A 证据索引

林涵 / 241880464 / A16；2026-11-03。助教要求每人完整做三阶段，本目录是本人的实际运行，不由队友阶段材料替代。

[个人报告/ADR/AI/CI记录](../../../docs/students/241880464/e8-e10/个人报告.md)，个人分支student/241880464/e8-e10，[PR #16](https://github.com/Lilyly9/DevOps-G16/pull/16)。

实际源码00f4fe22ba53d5b3da45363ea8d1285845684daa；环境镜像course-e8e10:241880464，完整ID sha256:a0bafc7c741bc8912adbc1b1797202c5bc0f220c67f8879b556627a521b3322c。云端仓库/root/241880464/DevOps-G16-e10-A3-20261103；标准OUT work/e8-A-manual.EY0rdk，扩展OUT work/e8-A-manual.XkTQNp。Ubuntu22.04.5/x86_64/2CPU/3.5GiB；内存低于4GiB建议，如实保留。

## 结果与文件

真实BuildChecker基线精确MD config.h/RD unused.h；未改C0时两个对象复用；共享头在两个对象作业上的完整边/发现与增量/全量/真实动态结果一致。

standard/保存官方分步路线原件，extension/保存独立预期expected.json、本人扩展输入/报告与动态重检；完整trace、数据库、图、进程与history.bundle保留。project-history.txt逐一对应报告commit；bundle可恢复完整内部历史，和外层学生源码分开记录。execution/保存实际脚本、会话、环境与10项单测日志；standard/steps及extension/steps真实容器步骤均退出0。

audit.json记录标准图/发现/真实构建日志核对、四套动态原件重新解析和内部bundle恢复。selection-scope.json列明精选排除项，只排除.git/缓存和编译二进制；大归档保留编译产物，原始文字不裁剪、不改空白。files.sha256.json保存逐文件大小与哈希。

## 命令、独立预期与重跑

完整实际命令为execution/personal-e8-standard.sh和personal-e8-extension.sh；标准逐字采用原E8-A手册分步代码，额外留存GCC投影副本/内部历史。source路径改到实际官方helper位置，在本人仓库根按顺序执行，每次新建OUT，不能把已创建目录交给一键入口。

扩展使用lab_ready、lab_new_run e8 A后，在lab_python中调用student_241880464_followup.run_extension('e8', Path(sys.argv[1]))。函数在扫描前保存手写预期，独立断言全部actual/declared/findings及复用/刷新/added/resolved，再用真实BuildChecker对象投影核对。新增个人测试在labs/e8e10/test_student_241880464.py，原7项保留，共10项；本地/CI统一test_*.py发现。

## 归档与交接

补充完整原始归档服务器/root/devops-submissions/241880464/A3-personal-supplement-20261103.tar.gz，本机E8/A3-personal-supplement-20261103.tar.gz；SHA256 cb0a944091bd0bb13a7101515f89572adb9a23adbee20b8ba11b618d7ded14af，已两端核对。正式全阶段交付另取仓库外“A3-E8-E10-全阶段-20261103”包，实际路径/大小/SHA与最终当前head对应CI另见包旁“交付状态.json”，避免归档自包含哈希循环。仓库中可审查本目录精选原件与个人文档，完整work/CI原件由双端包交接。
