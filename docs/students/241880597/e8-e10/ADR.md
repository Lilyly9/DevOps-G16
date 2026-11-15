  # 决策记录

  背景与约束：
  E10-B 要把 Patch 生成与「接受」分离：候选必须先在一个隔离 sandbox 内通过全部检查（应用、构建、程序测试、头文件变化增量、无 MISSING），全部通过后才写回源 Makefile；任一检查失败或 Patch
  无法应用都必须拒绝且不污染源目录。

  选择与替代方案：
  A（选用）：validate() 在 evidence/sandbox 副本上应用候选、构建并跑测试，全绿才把 sandbox 的 Makefile 写回源 project；拒绝时 rollback=True、source_unchanged=True，源文件逐字节不变。
  替代1：直接在源 project 上应用候选再撤销（git reset）。缺点：先污染再回滚，无法保证「源文件始终未变」，易残留中间态。
  替代2：只做 git apply --check 就接受。缺点：只证明格式可应用，不能证明构建/测试/头文件变化正确，可能放过错误候选。

  代价与覆盖范围：
  代价：每次验证要在 sandbox 上真实编译（含 sleep 1.05 触发头文件变化增量），比纯静态检查慢。覆盖范围：受限显式 Makefile（direct/macro/mixed 三类声明）；复杂隐式规则、DIS/LLM
  属于扩展，不在本版最低交付内。

  验证命令与实际证据：
  lab_new_run e10 B → work/e10-B-manual.LcfdFB；三场景 validation.json（reject-test/accept/reject-patch）passed=True；source-before.Makefile 与 source-after-accept.Makefile 字节副本；cmp 退出
  0；recheck-buildchecker 无 MISSING。
  EOF

  ③ AI_USAGE.md（务必按你真实使用情况核对/修改，别照抄——尤其「采纳/拒绝」「人工修改」要如实）：

  cat > "docs/students/241880597/e8-e10/AI_USAGE.md" <<'EOF'
  # AI使用记录

  工具/模型/日期：Claude Code（Anthropic 助手）/ 2026-11-08 ~ 2026-11-09

  输入上下文与问题：用于逐步指导 E8/E9/E10 B 轨实验流程（环境准备、git 同步、lab_new_run/lab_python 步骤、独立测试编写、报告/ADR 起草）；未调用外部模型 API。

  模型建议：给出各阶段手册命令的执行顺序、heredoc 顶格注意事项、编译失败拒绝的独立测试用例，以及报告/ADR/AI_USAGE 的填写草稿。

  采纳/拒绝及理由：采纳命令顺序与独立测试方向（编译失败拒绝，补第三种拒绝原因）；所有断言与预期来自手册与实际运行，模型草稿经本人逐条核对后才落盘。

  人工修改：独立测试输入（main.c 非法 C）、报告中的 OUT/SHA/镜像ID 等真实数据由本人填写核对；报告措辞与论文机制理解由本人确认。

  实际验证命令/输入/结果：docker run ... unittest discover -p 'test_*.py' -v → Ran 8 tests OK；E8/E9/E10 三阶段 OUT 各自 STEP_EXIT_CODE=0 与结果文件。
  EOF

