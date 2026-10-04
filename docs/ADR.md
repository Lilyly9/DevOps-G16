# 架构决策记录

## ADR-001：使用异步 Job 模型

- 状态：Accepted（契约层）

### Context

DRAFT、BuildChecker、EChecker、MDFixer 都可能执行镜像构建、依赖分析、修复和重新验证，耗时可能超过普通 HTTP 请求生命周期。同步连接也会把客户端生命周期与执行过程耦合。

### Decision

四类服务共用 `contracts/task.schema.json` 定义的异步 Job：客户端通过 `POST` 创建任务，服务端以 HTTP 202 返回含 `job_id`、`trace_id`、`job_type` 和 `QUEUED` 状态的受理结果；客户端通过 `GET /v1/jobs/{job_id}` 查询完整 Job。可查询记录统一包含 `schema_version`、`job_id`、`trace_id`、`job_type`、`status`、`input`、`output` 和 `error`。

### Alternatives

- 在单次 HTTP 请求中同步等待任务完成。
- 为每个服务设计互不兼容的任务状态对象。

### Consequences

- 服务需要持久化任务状态并提供查询接口。
- 调用方需要轮询，或在未来另行约定回调机制。
- 客户端与长时间执行过程解耦，四个服务可共享生命周期处理。
- 需要通过 `trace_id` 维持跨服务追踪；是否跨增量检查继续使用同一 trace 仍需两组确认。

## ADR-002：通过产物引用访问大型结果

- 状态：Accepted（离线样例）；生产存储方案待定

### Context

依赖图、MD/RD 报告、构建日志和 Patch 可能较大，不适合全部内联在 Job 响应中；下游仍需可靠定位产物并核对生产任务。

### Decision

Job 的 `artifacts` 数组保存 `artifact_id`、`type`、`uri`、`media_type`、`producer_job_id` 和可选 `sha256`。业务输出通过 `*_artifact_ref` 或 `*_uri` 引用这些产物。仓库内离线样例使用 `repo://`，相对仓库根目录解析；公共契约不指定 S3、OSS 或其他尚未确定的平台。

### Alternatives

- 将所有产物完整内联到 `output`。
- 在公共契约中预先绑定某个对象存储产品。

### Consequences

- Job 查询响应保持较小，产物可独立保存、校验和复用。
- 消费方需要解析 URI，并用 `producer_job_id`、repository、commit、configuration 等元数据核对来源。
- 生产环境采用何种 URI scheme、权限和保留策略，需要 A/B 两组在实现前确认。

## ADR-003：系统执行错误与检测发现分离

- 状态：Accepted

### Context

Missing Dependency（MD）和 Redundant Dependency（RD）是检测服务的正常业务结果。如果把它们当成任务失败，下游将无法区分“分析成功且发现问题”和“分析器没有完成”。

### Decision

- 正常完成分析但发现 MD/RD：`status: SUCCEEDED`、`error: null`，发现放入 `output.findings` 或其报告产物。
- 镜像构建失败、任务超时、分析器异常等系统执行问题：使用 `FAILED` 或 `TIMED_OUT`，并在 `job.error` 提供至少含 `code`、`message` 的对象，可选 `details`。
- 参考错误码为 `ENV_3002`、`EXEC_4002`、`ANALYSIS_5001`；为兼容服务已有错误码，公共 Schema 不将其限制为封闭枚举。

### Alternatives

- 只要发现 MD/RD 就令 Job 进入 `FAILED`。
- 把系统异常和业务发现混放在同一个 findings 数组。

### Consequences

- 调用方先根据 Job 状态判断执行是否完成，再根据 findings 判断代码/构建依赖问题。
- MDFixer 可以只筛选 `type == MISSING` 的发现，不会把 RD 或系统异常当作修复输入。
- `ERROR_REPORT` 是现有产物类型名称，不等于公共字段 `job.error`；两者语义必须在实现和文档中保持分离。

## ADR-004：E3 测试基线采用手工等价样本与人工/实际分离

- 状态：Accepted（E3 基线层）

### Context

E3 需要为四个服务各准备一份"能判断对错、别人能重跑"的测试基线。但课程实验包（`E3实验包/` 的 `run_lab.py` 与 `fixtures/`）未取得，且检测器（BuildChecker/EChecker/MDFixer）在 E3 尚未实现，人工预期答案有被误当工具输出的风险。

### Decision

- 样本按 PPT 口径手工等价构造（A2 自建 C0/C1/C2 真实提交链；B1 自建 Tiny Greeting；B2 自建四种声明风格的 Makefile 与补丁），并在来源处标注 `MANUAL_EXPECTED` 或 `WORKING_TREE_SNAPSHOT`，不冒充课程原始产物或已提交文件。
- 人工预期放在 `expected/`，实际运行放在 `work/<run-id>/`，两者严格分列；`observations.json` 标注 `ACTUAL_RUN`，人工答案不得计入工具准确率。
- 每次运行新建 `work/<日期-时间-成员-编号>/`，不覆盖旧证据；构建产物由各 run 目录的 `.gitignore` 排除。
- 环境记录各自保存版本号，不同工具链（Linux/Windows/WSL）不混作同一次配置的性能对照。

### Alternatives

- 等待课程实验包取得后再开工。
- 把人工预期与实际日志混在同一文件。

### Consequences

- 基线不依赖课程实验包即可重跑，人工/实际分离使后续准确率评估不被污染。
- 手工样本与课程样例可能不完全一致，需在 README 标注"手工等价"；换机器重跑时工具链版本差异需另建 run 目录。
- 真实检测器实现后（E5/E8），以同构真实数据替换手工样本并保留人工/实际分离约定。
