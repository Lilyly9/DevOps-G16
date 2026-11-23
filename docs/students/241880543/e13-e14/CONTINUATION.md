# B2 本轮续验说明（2026-11-23）

E7 A/B 失败共同来源是凭据读取代码被通用赋值规则误报，历史扫描也重复匹配该行。两个扫描器现在仅忽略 AST 确认的单参数映射 get 调用，参数必须是常用凭据字段名；没有删除文件扫描或历史扫描。强格式密钥仍独立检查，字面量、带默认值的 get 调用和伪装成字符串的调用均有拒绝回归。

E14 原入口仅支持 main.o/helper.o。新增复用 E12 项目配置及 project_path 的路径，以 target 的 e12-profile.json 为同一基准校验 base/target 源文件，让缺少配置文件的历史基线也能运行。BuildChecker 的构建目标、EChecker 的对象映射和 MDFixer 的输出/头文件变化验证都使用这份配置。路径越界和真实快照保真回归均通过。

## 本轮独立任务

| 项目 | job | trace | base → target |
| --- | --- | --- | --- |
| H1-jsmn | `job-28ea8e8320154730abbfaf2262513516` | `trace-1bc4328fc6f24041b5badba2890f38bb` | `66a6dafcc20cea76bf017923d3db725d78407845` → `948a1d30cd758d32d45a50f788e5a95fb1d89c69` |
| H3-tiny-aes | `job-741caccbe8c941cf9797fc9e1a9c9fa6` | `trace-4baccc3190784001a3c5cc51ac271aa4` | `dc8099306d7023b7337328d718149973e7b17978` → `5640bb69a01e64559207e9f74d15a9ae71a4d0f3` |
| C1-B | `job-a551c109139047baaa9a9d5d459e92d5` | `trace-73c87219c4064d88be182b1deb9f3b57` | `5ef9d829e2f893af23f60399dcb67095800d121e` → `e7414083c4f1760cb234f96a9d75f2d0255e3f57` |
| C1-A-handoff | `job-7d0b00237b694805bce1b039c97220c0` | `trace-6087b825fa5b4286b1a5e0911262da00` | `报告交接` → `原清单中的目标` |
| E14-H1 | `job-8e17cff1cb304ec7ab742496f5efee66` | `trace-ceda5b87083240cb8a62c1f8d7cac27c` | `66a6dafcc20cea76bf017923d3db725d78407845` → `948a1d30cd758d32d45a50f788e5a95fb1d89c69` |
| E14-fixed | `job-1db2ebdb94c84a639260c5c9ea34571e` | `trace-f2fb3a1915254f31b33dc364b53d6d41` | `db5cdc945e5bb985980b2db46d4df45b5bd60c86` → `1a84ab873b39a74900fa6321679fa448384fd024` |
| E14-H3-tiny-aes | `job-640b1273d6ed4ec1812e2c5f66b167b5` | `trace-9558fecab8834da3abac1afafa19238b` | `dc8099306d7023b7337328d718149973e7b17978` → `5640bb69a01e64559207e9f74d15a9ae71a4d0f3` |
| E14-transfer-eta | `job-aa567da45f2b442a98213440824f9071` | `trace-e82f0e54b9cc43439e87f0903fc2c455` | `5ef9d829e2f893af23f60399dcb67095800d121e` → `e7414083c4f1760cb234f96a9d75f2d0255e3f57` |

## 证据与环境

`verified-runs.json` 逐一校验成功任务的五阶段顺序、产物 SHA/字节数、job/trace、最终无 MISSING；H1/H3/C1 同镜像执行分别核对请求镜像、实际镜像和容器退出码。四容器分别检查四个独立 ID、相同运行镜像、四个健康响应、角色日志中的相同 job/trace 及清理退出码。

本轮教学镜像构建成功日志为 `../e14-image-host-20261123.log`，原失败日志继续保留。Git 适配只影响测试进程和独立容器镜像，不修改宿主全局 Git 配置。通过 core.filemode=false 处理 DrvFS 权限位；原件字节摘要仍逐项核对。

C1 使用 A1 提供的 transfer-eta 完整提交，不沿用旧报告。本机重新执行 A 侧检测并导出当次报告，保留来源 job/trace、源报告 SHA 和 fixed-md SHA；B2 读取后重新构建和验证。首次 B 构建因清华 HTTP 软件源不可达失败，派生 HTTPS 候选成功，保留原候选、派生候选和原 base/target 身份。

四容器测试是个人隔离复验；本轮没有据此申报整组 E13 门禁或 RC 发布。

受控 DRAFT 超时：失败任务 `job-23e009fabdf94d15a7a50f90af3d4320` / `trace-0cbaed03501d4992a14533b9617eff0f`；HTTP 422 TIMEOUT，原始结果 TIMED_OUT。核对超时前后源摘要、全部容器 ID 清单相等；后续任务 `job-c9287c8c48d1466d923e55efba23c2fc` / `trace-35e536ddb0074deeab24aac87570a5c9` 完成五阶段，与失败任务标识不同。恢复原件见 `e14-fault-recovery.zip`。
