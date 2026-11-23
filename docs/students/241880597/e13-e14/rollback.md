# E14 回滚验证（B3 · 241880597）

> B3 主责记录候选回滚的复现命令、回退步骤、回退后验证与已知问题。回滚分两层：流水线内置的补丁回滚，与发布级的提交回退。

## 1. 流水线内置回滚（已验证）

`labs/e11e12/pipeline.py` 在 repair→recheck 阶段内置回滚：

- 补丁被 `validate` 拒绝时，不落盘，直接 `REPAIR_REJECTED`。
- recheck 发现仍存 `MISSING` 时，将工作区 `Makefile` 恢复为修复前内容（`pipeline.py:262`：`(target/'Makefile').write_bytes(before)`）再报 `RECHECK_FAILED`。

复现（C5 错误补丁回滚，B2 主责，B3 核验）：

```bash
# 以错误补丁候选触发，观察被拒绝且工作区未污染
python3 run_e11e12.py run --request <bad-patch-request.json> --out work/e13-rollback-bad
# 期望：status FAILED，error.code 为 REPAIR_REJECTED 或 RECHECK_FAILED
git -C <target-project> diff -- Makefile   # 应无残留改动
```

回退后验证：用正确候选重跑，五阶段 SUCCEEDED、recheck `findings: []`。

## 2. 发布级提交回退（v0.9-rc 出错时）

若 `v0.9-rc` 候选被判定不通过，回退至上一个验收提交并复验。

### 复现命令

```bash
# 定位当前候选与上一个已知良好提交
git -C <repo> rev-parse HEAD HEAD~1
# 在候选上复现失败（五阶段编排）
python3 labs/e13e14/orchestrate.py --request work/e14-real-request.json --out work/e14-rollback-repro
```

### 回退步骤

```bash
# 云机（47.97.103.111）回退到已知良好提交（此处仅示例，具体 SHA 以验收记录为准）
git -C /root/241880597 checkout <known-good-sha>
# 或对已发布标签回退：删除误打标签（需组长确认，不覆盖他人标签）
git tag -d v0.9-rc && git push origin :refs/tags/v0.9-rc   # 仅当标签确实误打
```

### 回退后验证

```bash
# 重建镜像并重跑固定样例 + 真实项目四容器 E2E
python3 run_e11e12.py build
python3 labs/e13e14/orchestrate.py --request <sample-request.json> --out work/e14-rollback-sample
python3 labs/e13e14/orchestrate.py --request <real-request.json> --out work/e14-rollback-real
# 期望：两条链路均 SUCCEEDED，recheck 无 MISSING
```

## 已知问题

- 远端 CI 未绿（BLOCK-3 云机 GitHub 不通），发布级回退中的 `push`/PR 需在本地 Windows 完成。
- `git tag -d` + 强制推送属破坏性操作，仅在标签确实误打且组长确认后执行；不得覆盖他人已有标签。
- 回滚仅作用于仓库提交与标签，不回收已推送到私有镜像仓的候选镜像；如需回收需另行清理镜像。

## 结论

流水线内置补丁回滚与发布级提交回退两条路径均已记录命令、步骤与复验判据。内置回滚由 C5/recheck 覆盖；发布级回退命令已备好，待 `v0.9-rc` 实际打出后可执行复验。
