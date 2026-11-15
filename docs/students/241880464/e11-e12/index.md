# A3 E11–E12 交付索引

林涵 / 241880464 / A16，2026-11-15。[个人报告](个人报告.md)、[ADR](ADR.md)、[AI使用](AI_USAGE.md)、[CI记录](CI记录.md)，[PR #22](https://github.com/Lilyly9/DevOps-G16/pull/22)。

本机项目/home/perilla/Projects/devops，云端/root/241880464/DevOps-G16-e11-e12-A3-20261115，个人分支student/241880464/e11-e12。开工干净，从最新main建立，公共依赖A1 PR #21 c14876d。CLI源码3ea1e566bcd60a8133df768a833230e4917fcf71，API/37测源码cea3986e4317fd53c0886f028d306f4caa01fe69，环境镜像完整ID/工具锁/实际资源在evidence/execution，内存3.5GiB低于前期4GiB建议。

## 本人原件

- evidence/e11-standard与e11-autonomous保留真实图→缓存、目标增量/全量完整集合、阶段封装、请求、版本/URI/哈希。新提交的独立预期和输入历史在execution/inputs。
- evidence/cli-fixed、cli-real、api-fixed、api-real保存四次E12阶段原件与逐命令镜像执行记录，DRAFT真实两轮构建/程序运行、补丁、验证、最终图均可核查。
- evidence/http保留本机通过SSH转发取得的请求/响应、轮询、下载原字节/响应头/交接清单/验证。checks包含真实旧目标/短SHA拒绝和重启前后同任务记录，audit.json逐字节核查1148个引用、16套真实图和四份bundle恢复。
- execution保留实际脚本、命令、退出码、环境工具锁、构建失败/镜像源重试、37项测试与输入记录。Git只选必要小件，完整trace、项目副本、编译产物及CI artifact留在归档。

云端OUT根work/a3-20261115，标准/自主为e11-a-standard、e11-a-autonomous，E12 CLI为e12-cli-fixed-retry、e12-cli-real。API原件在work/api-jobs下对应job/evidence；具体job/trace与base/target见报告及audit。失败的e12-cli-fixed原件也保留在完整包。

## 备份与复跑

云端原件包/root/devops-submissions/241880464/A3-E11-E12-cloud-originals-20261115.tar.gz，本机副本位于Practices/E11/A3-20261115，大小/SHA见evidence/backup-record.json，两端已核对。含本机HTTP预跑、当前源码/文档和最终CI的完整个人包放在Practices/E11/提交材料/A3-E11-E12-20261115，最终实际路径/大小/哈希与当前CI在包旁交付状态.json登记，服务器另存一份。

复跑先在原仓库本人分支构建course-e11e12:学号，执行run_e11e12.py test、首次prepare，再按execution/cloud_run.sh/retry_cli.sh中的实际输入逐次使用新OUT。网络适配包含真实Git新提交和候选摘要，不能直接替换旧结果的commit。API用run_e11e12.py serve --port 18046，另一端SSH转发后调用labs/e11e12/api_probe.py，完整参数见contracts/e11e12.md。

## 交接状态

A侧出口、本人CLI/API/SSH预跑、错误拒绝和CI已做。B3还需本人从另一端下载并触发独立MDFixer消费/复验，组长审核公共依赖和本PR，课程方确认A1本轮新建transfer-eta的真实项目验收口径。具体入口见仓库e12/A3-B3交接.md。个人预跑与上述共同验收分别登记。
