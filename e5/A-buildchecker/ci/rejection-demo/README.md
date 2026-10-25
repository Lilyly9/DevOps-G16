# A3 CI 演示测试

当前两个模板已从新增官方学生包原样复制，来源与 SHA256 见 course-source.json。

- `A/test_ci_reject_demo.py`：故意把 `main(["version"])` 的退出码预期写成 1。
- `fixed/test_ci_reject_demo.py`：恢复正确预期 0；不改算法。

将对应版本复制到 `services/buildchecker/tests/test_ci_reject_demo.py` 后重建镜像。模板目录不会进入正常服务测试。

此前 GitHub PR #4 使用的是 A3 自写的依赖声明等价样例（错误预期 unused.h，正确预期 config.h）。其已归档 run 记录继续保留，不能改称官方模板运行证据。后续启用保护后的正式验收使用这里的官方模板。
