# E4 A3 运行与核查入口

成员：林涵；学号：241880464；A 组编号：A16（沿用仓库分组记录）。

本人已确认在服务器完成 E4 运行；克隆目录为 `/root/241880464/DevOps-G16/`，运行证据基目录为 `e4/A-buildchecker/work/`。成功目录已核验为 `work/20261003-174027/`；运行 SHA 为 `fa5ae8fa45ea0fed943c94f9a1523a602aa96ce6`。

- [A3 逐项核查与证据汇总](A3_REVIEW.md)
- [A 组模板操作说明](A-buildchecker/README.md)
- [本人 AI 使用记录](docs/A3_AI_USAGE.md)
- [本人贡献记录](docs/A3_CONTRIBUTIONS.md)

## 原件核查

证据核查脚本在共享仓库根目录执行，`--run` 指向已经成功的完整目录，不能直接传 `work/` 基目录。先核对七份文件齐全及 smoke/test 结论；额外的扫描运行不能代替 make all 成功记录。输出应选新的个人 work 路径，已有文件不会覆盖。

```sh
python3 e4/scripts/a3_check_evidence.py \
  --repo /root/241880464/DevOps-G16 \
  --run /root/241880464/DevOps-G16/e4/A-buildchecker/work/20261003-174027 \
  --scan \
  --out /root/241880464/DevOps-G16/e4/A-buildchecker/work/review-YYYYMMDD-HHMMSS/a3-review.json
```

A1/A2 的严格对照应另外执行一条命令，以两个 `--run` 分别指定他们的成功目录。本人整仓 SHA 不同，单独核验；不要将三份不同 SHA 的记录混作同 SHA 验收。`--scan` 会独立检查当前克隆的仓库/历史和原记录对应的镜像，若镜像已被覆盖或不可用则报告失败。

本脚本核查 A 组原件；相邻 B 组只看 README 的真实重跑必须单独留日志。原始 work 和 .env 保留在服务器，仓库只记录核查入口及必要结论。

本人单测 `3 passed`，冒烟四项通过，仓库/历史/镜像独立扫描通过。A1/A2 使用相同完整 SHA；本人整仓 SHA 较新但 A 模板 Git tree 相同。本人已在独立克隆完成 B 模板跨组重跑，详见 A3_REVIEW.md；B1/B2 双人对照仍待提供。

## B 模板跨组成功记录（2026-10-05）

- 完整 SHA：`26d23da933c4cd2e76c786fbc618a03b1dec70e0`。
- 成功目录：`/root/241880464/e4-cross-check/B-review-20261005-195556/e4/B-draft/work/20261005-201624-A3-cross-fixed`。
- 4 passed、冒烟 passed=true、仓库/历史/镜像扫描无发现；七份证据存在，.env 未跟踪且权限 600。
- 记录依据为本人提供的服务器终端输出，见 [转录索引](docs/A3_B_CROSS_RECORD.json)。B1/B2 双人同 SHA 对照不在本人的成功记录中替代。
- 首次历史扫描编码失败和临时补扫单独保留；最终成功以修复后新 RUN 为准。原始 work 不提交。
