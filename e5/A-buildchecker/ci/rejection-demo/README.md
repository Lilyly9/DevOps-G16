# A3 CI 演示测试来源

当前入库实验包没有课程材料所述的 rejection-demo 测试。这里由 A3 编写等价教学样例，不能称为助教原件。

将 `A/test_ci_reject_demo.py` 复制到 `services/buildchecker/tests/`，它故意把已声明的 `config.h` 预期写为 `unused.h`，服务测试应失败。
恢复时用 `fixed/test_ci_reject_demo.py` 覆盖同名文件。两个版本只差期望头文件名；本次恢复修正的是测试预期，不是实现。

这两个模板不在服务 tests 目录，正常镜像不会运行它们。只有独立演示分支将其中一个复制到 tests。
