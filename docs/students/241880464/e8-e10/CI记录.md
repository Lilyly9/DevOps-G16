# A3 GitHub / CI 记录：本人三阶段

## 按助教要求补齐三阶段的当前记录

每位成员必须完整完成自己的轨道三阶段，旧阶段主责安排不再替代个人实验。本人E8/E9标准与扩展的实际源码为00f4fe22ba53d5b3da45363ea8d1285845684daa；E10旧原件实际源码4cf51fa继续保留。

[三阶段代码PR事件run 41631873650](https://github.com/Lilyly9/DevOps-G16/actions/runs/41631873650)绑定00f4fe22ba53d5b3da45363ea8d1285845684daa，conclusion=success；原7项加本人3项共10测、A/B六路线、本人E10五次宏场景及E8/E9真实动态扩展均成功。artifact与run元数据保存work/ci-e8e10/41631873650，并随完整包双端交付。

后续仅补报告/原件/范围更正文档，最终PR head的真实CI与artifact在仓库外“A3-E8-E10-全阶段-20261103”包旁交付状态.json登记；绝不使用旧head的绿色替代最终提交。个人PR仍为#16，助教要求组长审核验证后的贡献再合入main，实际合并结果另按GitHub记录登记。

以下为前一次E10阶段的历史记录，保留失败/恢复和旧artifact身份区别，不能当成本次补齐后的最新提交：

[个人 PR #16](https://github.com/Lilyly9/DevOps-G16/pull/16)，分支student/241880464/e8-e10。正式实验源码与本次成功PR事件head为 `4cf51fa78bc856c9b0c3c559c8e10ebf6a4c64a2`。

## 已完成的源码检查

- [E8–E10 PR run 41570994117](https://github.com/Lilyly9/DevOps-G16/actions/runs/41570994117)，headSha完全匹配上述源码，conclusion=success；检查名e8e10-quality-gate。原7+本人1项共8测，A/B六路线和自主五次场景均运行。
- artifact `e8e10-evidence-41570994117`，ID13201850167，132645字节；已下载至work/ci-e8e10/41570994117/artifacts，元数据在本人的e10证据目录。expires_at=2026-11-17T03:15:59Z（北京时间11月17日11:15:59）；保留14天，归档已包含下载副本。
- [原E7 A run](https://github.com/Lilyly9/DevOps-G16/actions/runs/41570993936)、[原E7 B run](https://github.com/Lilyly9/DevOps-G16/actions/runs/41570994054)均为相同head的PR事件success；未改原E7工作流。
- 本次PR事件实际checkout为临时merge提交 `8ef3e5fa1899e5de5dc861464b2b15921ff89aff`，run.headSha仍为4cf51fa。旧artifact的student-source-commit.txt记录的是checkout；不能改写旧原件。后续workflow已经分成student-source-commit.txt（PR head）与checkout-commit.txt（实际checkout）两项，消除歧义。

## 真实失败与恢复

[早先push run 41570631270](https://github.com/Lilyly9/DevOps-G16/actions/runs/41570631270)绑定源码955fcf37a6e70997a5e28966755a714e330cadb8，构建阶段镜像源返回unexpected media type application/octet-stream而失败，未进入单测或矩阵。日志与run.json均保留。后续4cf51fa的push与PR事件在未更改基础digest/锁文件的条件下成功；没有把环境下载失败当成实验断言失败，也没有把失败记录删除。

## 当前报告提交与保护边界

随后增加报告、原件、索引与CI元数据字段，产生新的PR head。最终交付前再次按该head核对真实PR事件CI，并在仓库外交付包的“最终交付状态.md / 交付状态.json”保存最终head、run、artifact和PR状态；不以旧run冒充新head的验证，也不为把CI链接写回自身提交而无限循环提交。本文明确的4cf51fa是已执行实验源码与上述历史run。

公共导入PR #13，main合入SHA f1653557d066f7a17b2d2dce020126c34b8f6fcf；统一发现模式test_*.py已由A1导入。A3后续维护只新增留证/自主场景，不移除任何轨道。main protection API本次返回HTTP404，已保留原响应，不能确认必需检查配置；未PUT、未关闭保护。新门禁是否追加必需项由教师/组长决定。个人PR由组长审核后正常合并；不自行伪造MERGED或合并SHA。
