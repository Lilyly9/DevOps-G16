# A3 CI记录

本人的PR #22持续更新，依赖A1 PR #21，个人分支student/241880464/e11-e12。原E7 A/B及E8–E10 workflow保留，新增e11e12-integration的真实HTTP E12、报告出口、下载哈希和源码/镜像身份留证。

首次完整PR事件绿色run 43679389787绑定442fcfa0a54f815293574d260cfacb0610402407，当时36测，四个workflow都成功。后续新增TimeoutError归因独立测试，共37测，云端和本机均通过。CLI/API实际运行版本分别在本人报告中明确。

最终报告提交后，以实际最终head查询四个PR事件workflow，下载e11e12-evidence artifact并核对student-source-commit.txt，另保留checkout-commit.txt的临时合并SHA。最终run URL/headSha/结论/artifact下载记录在仓库外完整包的交付状态.json及最终交付状态.md，避免将旧绿色冒充新提交验证。

本轮没有替组长修改main保护或合并PR。B侧独立消费及新项目课程认可在交接清单中保留。
