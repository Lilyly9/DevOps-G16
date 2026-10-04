# DRAFT 样本:Tiny Greeting

B1 用于 DRAFT 基线的最小 C 项目。目标:同一个样本既能验证"构建成功 + 功能正确"双层判据,也能提供一条可定位的失败构建日志。

来源:课程人工样例 Tiny Greeting(PPT E3/30、E3/33)。课程实验包 `E3实验包/fixtures/draft/` 未取得,本目录为按 PPT 口径手工等价构造,来源标注见 `expected/draft-sample.md`(`MANUAL_EXPECTED`)。

## 输入

| 文件 | 说明 |
| --- | --- |
| `main.c` | 源码,标准输出 `hello E3` |
| `Makefile` | 构建 `hello` 可执行文件 |
| `Dockerfile.broken` | 失败候选:基础镜像无 make/C 工具链 |
| `Dockerfile.reference` | 参考成功:安装 `gcc make libc6-dev` 后构建 |

## 构建与验证(本机或容器内同一判据)

```bash
make
./hello
```

预期:

- 第一层(编译通过):`make` 退出码 **0**,生成可执行文件 `hello`
- 第二层(功能验证):`./hello` 标准输出 **`hello E3`**,进程退出码 **0**

一条命令判据:`make && ./hello` 输出 `hello E3` 且整体退出码 0。

## 失败候选与参考成功(需要 Docker)

```bash
# 失败候选:构建应非零退出,日志可定位到 make: not found
docker build -f Dockerfile.broken -t nju-e3-draft-broken:20261004 .

# 参考成功:构建成功,容器输出 hello E3
docker build -f Dockerfile.reference -t nju-e3-draft-reference:20261004 .
docker run --rm nju-e3-draft-reference:20261004
```

失败日志是后续"修复方法"的输入,不要删除。

## 复现说明

- 任一含 GNU Make 与 C 编译器(cc 或 gcc)的环境按上面"构建与验证"执行;本仓库 B1 的实测记录在 `../work/` 对应 run 目录(`commands.json` 里有确切 argv、cwd、退出码与日志路径)。
- Docker 两步使用 Docker 官方或发行版 Docker Engine;镜像 tag 中的日期为运行日期,可自行改名,但日志里应保留当时的完整命令。
- 环境与工具版本见 `../env/toolchain-B1.txt`;项目版本即本目录文件内容,对应提交 SHA 见 `../docs/B1_CONTRIBUTIONS.md`。
