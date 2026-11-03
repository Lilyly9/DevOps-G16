# B3 CI 演示测试

当前两个模板已从新增官方学生包原样复制，来源与 SHA256 见 course-source.json。

- `B/test_ci_reject_demo.py`：故意把 `main(["version"])` 的退出码预期写成 1。
- `fixed/test_ci_reject_demo.py`：恢复正确预期 0；不改算法。

将对应版本复制到 `services/draft/tests/test_ci_reject_demo.py` 后重建镜像。模板目录不会进入正常服务测试。

后续启用保护后的正式验收使用这里的官方模板。
