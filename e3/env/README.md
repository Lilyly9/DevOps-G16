# E3 A 组环境记录

- `toolchain-A1.txt`：A1 的 Linux x86_64、Git 2.34.1、GNU Make 4.3、GCC 11.4、Python 3.10.12、strace 5.16；对应 `work/20260929-110948-A1-00d164/`。
- `toolchain-A2.txt`：A2 的 Windows AMD64、Git 2.45.1、GNU Make 4.4.1、GCC 15.2、Python 3.11.9；对应 `work/20261002-182617-A2-e1d9d6/`。

两份环境不可混作同一性能基线。成员版本记录由各自运行产出；A3 负责汇总，不代填成员身份。新的运行使用新的 `work/<run-id>/`，保留命令、退出码、原始 stdout/stderr 和环境快照。

- `toolchain-A3.txt`：2026-10-03 在本地进行证据复核时实际采集的环境；用途是 A3 校验，不代表 ECS 服务运行，也不参与 A1/A2 的性能比较。

新成员记录模板：`member`、`run_id`（如有）、`recorded_date`、`purpose`、`os`、`architecture`、`versions`；每项工具注明实际版本、退出码或未安装状态。若记录构建基线，还须附 `source_commit`、`configuration_id`、编译参数和对应 `work/` 路径。
