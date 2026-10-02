# A2：EChecker 的 C0 / C1 / C2 增量基线

成员：万宇 / `adscfe`。按 E3 PPT《E3 并行测试基线》A 组步骤 9（页脚 E3/24）与 `E3_TASKS.md` 的 A2-1~A2-5 手工等价搭建。**本机没有课程 E3 实验包**，因此没有运行课程 `scripts/run_lab.py`，而是按 PPT 的 C0/C1/C2 描述自建同构小项目。

本目录同时保存两种东西：**真实的连续提交**（`lab/` 的三个 tag）和**冻结的三版本快照**（`C0/`、`C1/`、`C2/`）。

## 三个版本与真实 SHA

| tag | 提交 SHA | 变化 | 声明 | 预期发现 | 程序行为（增量 / clean） |
| --- | --- | --- | --- | --- | --- |
| `C0` | `ca57cfb89643e19f0c2ab73637ae2f962f8f7658` | 初始版本（声明正确） | `main.o: main.c config.h` | 本例范围内无 MD/RD | 10 / 10 |
| `C1` | `ef88dd77c8a452fb4f11b2978d0e1157f425e1db` | 新增 `#include "feature.h"`，Makefile 未同步 | `main.o: main.c config.h` | MD：`main.o → feature.h` | 12 / 12 |
| `C2` | `900d64c1a60d81d106beb84e4c4593cb576e5a92` | 只改编译命令 `CFLAGS = -O0 -DMODE=7` | `main.o: main.c config.h` | C1 的 MD 仍存在 | 12 / 19 |

三个 tag 都是本仓库真实的、可 checkout 的提交；`git diff --name-only C0 C1` 得到 `feature.h`、`main.c`，`git diff --name-only C1 C2` 得到 `Makefile`，与 PPT 叙述一致。

```bash
git tag -l C0 C1 C2
git diff --name-only C0 C1          # feature.h  main.c
git diff --name-only C1 C2          # Makefile
git checkout C1 -- .                # 或者：git checkout --detach C1
```

## 为什么同时保留快照

`git checkout <tag>` 会把整个仓库切到那个版本，不方便三个人并行；因此 `e3/scripts/a2_export_commits.py` 用 `git cat-file blob` 把每个 tag 的 `lab/` 目录**按原始字节**导出成 `C0/`、`C1/`、`C2/` 三个快照，并写入 `commit.json`（含每个文件的 `git_blob_sha1`、`sha256`、字节数）。

```bash
python e3/scripts/a2_export_commits.py          # 导出（幂等，重跑只写同样的字节）
python e3/scripts/a2_export_commits.py --check  # 只校验快照与 tag 一致
```

`--check` 会重算每个快照文件的对象 ID（`sha1("blob <len>\0" + content)`）并与 tag 中的 blob 比较，因此“快照 = 提交内容”可离线核验。

## 复现行为对照（Windows 实测命令）

```powershell
& 'C:/Users/hydl/AppData/Local/Programs/Python/Python311/python.exe' e3/scripts/a2_run_echecker_baseline.py `
  --make 'C:/msys64/usr/bin/make.exe' --cc 'C:/Users/hydl/mingw64/bin/gcc.exe' `
  --python 'C:/Users/hydl/AppData/Local/Programs/Python/Python311/python.exe'
```

运行器在 `e3/work/<run-id>/` 新建目录，不覆盖旧证据；它先校验三个快照与 tag 的字节一致，再在隔离副本里跑真实构建。手工复现步骤与判据见 `e3/expected/echecker-c0-c1-c2.md`。

## 说明

- 快照与证据按 LF 保存：`e3/fixtures/commits/.gitattributes` 为 `* text eol=lf`；`e3/work/<run>/` 用 `* -text` 保留日志原始字节。
- `lab/` 是「当前」工作副本（内容等于 C2）；三个 tag 才是版本存档。
- Makefile 里的 `PYTHON` 变量只用于 `make clean`，让 Windows 与 Linux 都能复跑，不改变依赖声明本身。
- 人工预期与真实日志分开保存：预期在 `e3/expected/`，真实输出在 `e3/work/`。
