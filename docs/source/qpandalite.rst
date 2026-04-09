qpandalite
==========

这是 **API 总览页**，用于在你已经知道自己要查哪个模块时，快速定位对应的 Python 接口文档；它不是教程首页，也不替代 guide/advanced 的任务导览。

- 想按任务学习如何使用框架：优先返回首页的教程、格式互转与语言接口、进阶入口。
- 想查询 `Circuit`、模拟器、任务提交或格式处理的具体接口：从首页 API 参考区或其下方模块页继续查阅。
- 想先确认“该看 guide 还是该查 API”：通常先看 guide，只有在你已经知道模块名、需要查参数签名或类/函数成员时再进入 API 参考。

常见查阅路径：

- 线路构建：`qpandalite.circuit_builder`，对应教程页 :doc:`guide/circuit`
- 本地模拟：`qpandalite.simulator`，对应教程页 :doc:`guide/simulation`
- 提交任务：`qpandalite.task`，对应教程页 :doc:`guide/submit_task`
- 格式与语言接口：`qpandalite.originir`、`qpandalite.qasm`，对应教程页 :doc:`guide/originir`、:doc:`guide/qasm`
- 分析与格式互转：`qpandalite.analyzer`、`qpandalite.transpiler`，对应进阶页 :doc:`advanced/circuit_analysis`
