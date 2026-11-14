# transfer-eta

`transfer-eta` 用于估算传输实验原始证据包或构建产物需要的秒数。用文件大小（MiB）除以观测到的传输速率（MiB/s），结果向上取整。它不读取文件或发起网络连接。

```sh
make
./transfer-eta 100
# eta_seconds=13
./transfer-eta 100 5
# eta_seconds=20
make test
```

省略速率时使用 `defaults.h` 中的默认值 8 MiB/s。显式传入速率可覆盖默认值。大小和速率均使用正十进制整数，最大值取决于平台的 `uintmax_t`。输入无效时退出码为 2。传输耗时还会受实际速率变化影响。

`Dockerfile.broken` 保留了精简镜像缺少 Make 的实验输入。`candidate.Dockerfile` 固定同一基础镜像的摘要，补装构建工具和 `strace`。两者使用相同构建命令和启动参数。

此版本增加了可配置默认速率。同一提交保留基线的 `eta_cli.o` Make 依赖声明，供 E12 验证漏声明新头文件时的实际影响。将默认速率从 8 改为 5 后，修复过依赖的增量构建应将默认输出从 13 改为 20 秒。`e12-profile.json` 描述了这项验收。
