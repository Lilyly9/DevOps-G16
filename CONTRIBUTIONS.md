# 成员贡献记录

每位成员记录本人负责的文件、提交说明和提交 SHA。未知信息不得由其他成员代填。

## A1

- 成员：焦龙；Git 作者：`illusiri`。
- 负责内容：BuildChecker 全量检测接口的请求、结果、MD/RD 表示和产物读取约定。
- 已完成：`contracts/buildchecker/request.json`、`response.json`、接口 README、服务专有 `contract.schema.json`、三份人工产物及 `validate.py`。
- 文档补充：README 中 A1 姓名/职责/进度、AI_USAGE 的 A1 部分、本贡献记录。
- 验证：五种合法生命周期消息、十个非法消息反例、三份产物实际读取及一致性检查、四个非法交接反例，均达到预期。
- 待协作：A2/B1/B2 交接互查、A3 独立字段复核、B3 汇总公共设计决定；尚未实施实际服务或声称全组已确认。
- 接口提交：`0370ef7111d582c05ac4f283ff033daa94971b84`（`feat(contracts): add A1 BuildChecker handoff examples`），作者 `illusiri`。
- 文档提交说明：`docs(e2): record A1 contribution and progress`；可通过 `git log --oneline --author=illusiri` 查到文档提交 SHA，避免在提交内部填写自身尚未生成的 SHA。

## A2

待 A2 填写。

## A3

- 负责内容：公共异步任务模型、A 组接口公共字段一致性检查、与 B3 共同维护 README。
- 已完成文件：`contracts/task.schema.json`
- Schema 提交：`381a951`（`feat(contracts): define shared job schema`）
- 本次文档：`README.md`、`AI_USAGE.md`、`CONTRIBUTIONS.md`
- 验证：JSON 语法、Draft 2020-12 元 Schema、两个合法样例和三个非法反例检查通过；A1/A2 接口文件尚未提交，一致性检查处于等待状态。

## B1

待 B1 填写。

## B2

待 B2 填写。

## B3

待 B3 填写并最终汇总。
