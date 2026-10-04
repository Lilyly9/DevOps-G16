# E3 B1 完成材料入口

成员:郭德林 / DelinGuo。沿用 `e3/` 目录与 A 组约定,本文件仅覆盖 B1;公共 README、四服务总表和校验汇总由 A3/B3 维护。

- [实验报告与卡点记录](docs/B1_REPORT.md)
- [样本源码、Dockerfile 与复现命令](fixtures/draft/README.md)
- [样本清单(人工预期)](expected/draft-sample.md)
- [实测观察](work/20261004-115744-B1-8f5ca8/observations.json)
- [环境记录](env/toolchain-B1.txt)
- [AI 使用记录](docs/B1_AI_USAGE.md)
- [个人贡献记录](docs/B1_CONTRIBUTIONS.md)

## 一分钟复现

```bash
# 本机双层判据(任一含 GNU Make 与 C 编译器的 Linux 环境)
cd e3/fixtures/draft && make && ./hello   # 预期输出 hello E3,退出码 0

# Docker 失败/成功双层(需要 Docker)
cd e3/fixtures/draft
docker build -f Dockerfile.broken -t nju-e3-draft-broken:20261004 .    # 预期非零退出,日志含 make: not found
docker build -f Dockerfile.reference -t nju-e3-draft-reference:20261004 .
docker run --rm nju-e3-draft-reference:20261004                        # 预期输出 hello E3
```

重新采集完整证据(WSL/Linux,Docker 阶段需 daemon):

```bash
RUNID=$(date +%Y%m%d-%H%M%S)-B1-$(git rev-parse --short=6 HEAD) python3 e3/scripts/b1_run_draft_baseline.py --stage build --run-id "$RUNID"
RUNID=... python3 e3/scripts/b1_run_draft_baseline.py --stage docker --run-id "$RUNID"
```

注意:运行器应在 Linux 环境执行(本仓库实测经由 WSL2);构建产物只落在新建 run 目录的 `runtime/` 下,不会污染冻结样本。
