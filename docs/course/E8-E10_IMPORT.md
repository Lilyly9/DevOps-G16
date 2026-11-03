# E8–E10 公共代码接入

来源：助教发布的 `DevOps_E8_E10` 2026-10-31 版，`03_实验包`。课程参考实现不是个人自主开发成果。

## 导入范围

- 根 `run_lab.py`、`labs/e8e10/`、根 `.github/workflows/e8e10.yml`。
- 保留 E4–E7 代码、原工作流和已有必需检查；本 PR 不修改分支保护。
- 根 `.gitignore` 只追加缺少的 work/凭据规则；原已跟踪证据不移除。
- `e8/e9/e10` 只有阶段索引，不复制三份实验代码。

## 明确适配

1. 新工作流测试发现从 `test_profile.py` 改为 `test_*.py`，使每人独立的 `test_student_<SID>.py` 被 CI 收集；本地命令相同。
2. 本次新增源码用局部 `.gitattributes` 固定 Python/Dockerfile/锁文件的 LF 换行。
3. 不复制老师备课、演示日志或参考运行 ID 作为本组成果；未改检测/修复核心逻辑和环境下载源。

## 使用

组长合并导入 PR 后，每人同步 main；设置 Git `--local` 数字学号与本人邮箱，建立 `student/<SID>/e8-e10`。
在仓库根执行 `python3 run_lab.py build`，镜像自动命名 `course-e8e10:<SID>`。
按外部材料中的 `classroom_helpers.sh` / 对应阶段手册执行分步路线；每次 OUT 唯一，不能把 helper 已建 OUT 交给要求目录不存在的一键入口。

源 `lab.py`/个人测试挂载运行，未改变环境时无需重建镜像。每人完成自己主责阶段的自主用例和个人报告，真实原件与 CI 记录独立保存。

新检查名 `e8e10-quality-gate`，工作流验证 A/B 六条阶段路线；是否加入分支保护由组长按教师规则决定，保留旧 E7 检查。检查结果以真实当前 SHA 的 Actions 为准。
