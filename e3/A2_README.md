# E3 A2 完成材料入口

成员：万宇 / `adscfe`。沿用队友的 `e3/` 目录与 A1 的命名习惯；公共 `e3/README.md` 与校验脚本由 A3/B3 汇总。

- [实验报告与七列基线条目](docs/A2_REPORT.md)
- [人工预期与判断依据](expected/echecker-c0-c1-c2.md)（机器可读：[JSON](expected/echecker-c0-c1-c2.json)）
- [C0/C1/C2 样本与复现命令](fixtures/commits/README.md)
- [本轮实测观察](work/20261002-182617-A2-e1d9d6/observations.json) / [命令与退出码](work/20261002-182617-A2-e1d9d6/commands.json)
- [环境摘要](env/toolchain-A2.txt)
- [AI 使用记录](docs/A2_AI_USAGE.md)
- [个人贡献记录](docs/A2_CONTRIBUTIONS.md)

在仓库根目录运行下面两条命令可离线核验已有产物（不需要重新构建）：

```bash
python e3/scripts/a2_export_commits.py --check
python e3/scripts/a2_run_echecker_baseline.py --make <make> --cc <cc> --python <python>
```

真实提交：`C0` = `ca57cfb89643e19f0c2ab73637ae2f962f8f7658`、`C1` = `ef88dd77c8a452fb4f11b2978d0e1157f425e1db`、`C2` = `900d64c1a60d81d106beb84e4c4593cb576e5a92`。
