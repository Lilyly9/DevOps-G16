# B2 E3 MDFixer 交付与复现

B2-1～B2-6 的独立材料和实测见 [验收报告](docs/B2_REPORT.md)。本次为课程任务的手工等价基线，人工答案与实际日志严格分开；不表示 MDFixer 服务已实现或全组已完成互查。

## 产物

- [冻结输入与四种补丁](fixtures/mdfixer/README.md)，根目录 `reference.patch` 对应 Target。
- [人工参考答案](expected/mdfixer-reference.md)，带 `MANUAL_EXPECTED`。
- [运行器](scripts/b2_run_mdfixer_baseline.py)，隔离运行并保存真实证据。
- [离线证据检查器](scripts/b2_verify_evidence.py)，仅使用 Python 标准库和 Git。
- [2026-10-04 Linux 实测](work/20261004-095323-B2-ae7679/observations.json)、[Linux 复跑](work/20261004-100021-B2-642335/observations.json)、[Windows 实测](work/20261004-100113-B2-803cdd/observations.json)；[最新环境摘要](env/toolchain-B2.txt) 对应 Windows，各轮环境以本轮 environment.json 为准。
- [AI 使用记录](docs/B2_AI_USAGE.md)、[个人贡献记录](docs/B2_CONTRIBUTIONS.md)。

## 一键重跑

在仓库根目录执行，Linux 需 Python 3.9+、Git、GNU Make、GCC/Clang；本次 WSL Ubuntu 22.04 的版本为 Python 3.10.12、Git 2.34.1、GNU Make 4.3、GCC 11.4.0。脚本不依赖课程实验包，不依赖第三方 Python 包。

```bash
python3 e3/scripts/b2_run_mdfixer_baseline.py
python3 e3/scripts/b2_verify_evidence.py
```

Windows PowerShell 可以直接复用 WSL（发行版名称按本机实际情况替换）：

```powershell
wsl -d Ubuntu-22.04 --cd "$((Get-Location).Path)" -- python3 e3/scripts/b2_run_mdfixer_baseline.py
python e3/scripts/b2_verify_evidence.py
```

原生 Windows 有 MinGW 时可显式指定工具，无需修改全局 PATH；以下路径替换为本机安装位置：

```powershell
python e3/scripts/b2_run_mdfixer_baseline.py --make 'C:/mingw64/bin/mingw32-make.exe' --cc 'C:/mingw64/bin/gcc.exe'
```

每轮创建 `work/<北京时间日期-时间-B2-编号>/`，结束时打印 `EVIDENCE_DIR` 和 `STATUS`。运行目录中的 `runtime/` 含私有 Git 根与临时编译产物，已通过该目录的 `.gitignore` 排除；保存输入、源码快照、日志、状态和哈希，不提交二进制。

只检查某一轮：

```bash
python3 e3/scripts/b2_verify_evidence.py --run 20261004-095323-B2-ae7679
```

## 手动验证单个补丁（Linux）

在仓库根目录执行，使用全新的临时目录；三个其他风格将 `target` 替换为 `macro/hybrid/implicit` 即可：

```bash
repo="$PWD"
sample="$(mktemp -d)"
cp e3/fixtures/mdfixer/main.c e3/fixtures/mdfixer/config.h e3/fixtures/mdfixer/unused.h "$sample/"
cp e3/fixtures/mdfixer/styles/target/Makefile.before "$sample/Makefile.before"
cp e3/fixtures/mdfixer/styles/target/reference.patch "$sample/reference.patch"
cd "$sample"
git init --quiet .
cp Makefile.before Makefile
make && ./app                         # 1
sleep 2
sed -i 's/VALUE 1/VALUE 2/' config.h
make && ./app                         # 仍为 1，MD 后果
make clean
git apply --check reference.patch
git apply reference.patch
make clean && make && ./app           # 2
sleep 2
sed -i 's/VALUE 2/VALUE 3/' config.h
make && ./app                         # 3，不 clean
cd "$repo"
```

完整命令、退出码和原始日志由一键运行器保存；手动片段用于理解实验。Implicit 构建后可查看 `main.d`。参考补丁保留 RD 声明，失败候选和恢复步骤由运行器在另一个副本完成。

## E2 接口与交接

`contracts/mdfixer/` 已在现有仓库中是目录，包含 request.json、response.json、专有 Schema、补丁和校验器，因此无需再次替换。其 E2 人工接口样例不混入 E3 实测，不更改公共任务 Schema。E2 校验需要 `jsonschema>=4.18,<5` 与其依赖，E3 运行器与检查器不需要它们。

B3 可将 [B2_REPORT.md](docs/B2_REPORT.md) 的七列表纳入公共 `e3/README.md`。公共 README、全员确认及姓名/Git 作者/最终提交 SHA 由对应本人和共同维护者补齐；本交付不代填身份，也不把工作区材料写成已提交记录。
