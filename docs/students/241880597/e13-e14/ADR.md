# ADR：B3 云机用本地 Git remote 绕过 GitHub 网络不通

- 状态：已实施
- 日期：2026-11-22

## Context

E13-E14 需要在云机 `47.97.103.111` 上运行 B 接收、C7 隔离、四容器 E2E 等，并基于 `origin/main` 的某个提交（`28c94de`）建分支、拉取 B1 已推送但未合并的 `data/e13-b-project/`。但云机访问 GitHub 持续失败：`git fetch`/`git clone` 报 `GnuTLS recv error (-110)`、`curl 16 HTTP2 framing layer`（TLS 超时），无法直接 `git fetch origin` 或 `git clone https://github.com/...`。

## Decision

不依赖云机直连 GitHub，改为把云机上已存在的 B1 仓库 `/root/241880555/DevOps-G16` 注册为本地 remote（别名 `b1`），用本地文件路径 fetch：

```bash
git remote add b1 /root/241880555/DevOps-G16
git fetch b1
git checkout -b student/241880597/e13-e14 28c94de...
```

B 项目交换件（`repo.bundle` + `candidate.Dockerfile` + `exchange.json`）从 B1 的 `data/e13-b-project/` 取得；A2 服务器证据包同理通过已存在的本地路径取得。

## 原因

云机网络层（TLS/HTTP2）对 GitHub 不通，但同机不同成员仓库之间的本地 git 对象共享完全可用。本地 remote 走文件系统，绕过 TLS，无需任何代理或证书改动，也不改变提交内容与 SHA。

## 校验

- `git fetch b1` 成功取到 `28c94de` 及 B1 分支对象，随后 `git rev-parse 28c94de^{commit}` 通过。
- 拉取的 B 项目与 B1 分支内容一致，B 接收 fixed-md SHA 与 A2 导出值逐字节一致。

## 后果

- 云机上的提交最终仍需在可访问 GitHub 的机器（本地 Windows）上 `push` 到远端并触发 CI；云机只作为执行环境，不作为远端同步出口。
- 本地 remote 依赖同机成员仓库已存在，若 B1 仓库被清理需重新获取，属临时协作手段，不入库、不改公共契约。

## 不做

- 不在云机上配置代理、改 `~/.gitconfig` 全局或跳过 TLS 校验。
- 不把本地 remote 当作长期方案写入公共文档；仅作为本轮网络受限下的可复现操作记录。
