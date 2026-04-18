.. QPanda-lite documentation master file

QPanda-lite — 轻量级量子计算框架
================================

QPanda-lite 是一个 Python 原生、轻量且强调透明性的量子计算框架，提供量子线路构建、本地模拟、多平台任务提交，以及 OriginIR / OpenQASM 2.0 格式支持。

|GitHub| |PyPI| |Docs| |Build|

.. |GitHub| image:: https://badge.fury.io/gh/Agony5757%2FQPanda-lite.svg?icon=si%3Agithub
    :target: https://badge.fury.io/gh/Agony5757%2FQPanda-lite

.. |PyPI| image:: https://badge.fury.io/py/qpandalite.svg?icon=si%3Apython
    :target: https://badge.fury.io/py/qpandalite

.. |Docs| image:: https://readthedocs.org/projects/qpanda-lite/badge/?version=latest
    :target: https://qpanda-lite.readthedocs.io/zh-cn/latest/?badge=latest

.. |Build| image:: https://github.com/Agony5757/QPanda-lite/actions/workflows/build_and_test.yml/badge.svg?branch=main
    :target: https://github.com/Agony5757/QPanda-lite/actions/workflows/build_and_test.yml

快速入口
--------

**首次接触？**

:doc:`安装 <source/guide/installation>` → :doc:`快速上手 <source/guide/quickstart>` → :doc:`构建线路 <source/guide/circuit>` → :doc:`本地模拟 <source/guide/simulation>` → :doc:`提交任务 <source/guide/submit_task>`

**进阶功能**

:doc:`OriginIR <source/guide/originir>` | :doc:`OpenQASM 2.0 <source/guide/qasm>` | :doc:`PyTorch 集成 <source/guide/pytorch>` | :doc:`任务管理器 <source/guide/task_manager>` | :doc:`转译器 <source/qpandalite.transpiler>` | :doc:`电路分析 <source/advanced/circuit_analysis>`

**命令行工具**

:doc:`CLI 概览 <source/cli/index>` | :doc:`电路转换 <source/cli/index#电路格式转换-qpandalite-circuit>` | :doc:`本地模拟 <source/cli/index#本地模拟-qpandalite-simulate>` | :doc:`云端任务 <source/cli/index#云端任务提交-qpandalite-submit>` | :doc:`配置管理 <source/cli/index#配置管理-qpandalite-config>`

**算法示例**

:doc:`Grover 搜索 <source/algorithm/search/grover>` | :doc:`VQE <source/algorithm/variational/vqe>` | :doc:`QAOA <source/algorithm/variational/qaoa>` | :doc:`QPE <source/algorithm/phase/qpe>` | :doc:`影子层析 <source/algorithm/measurement/shadow_tomography>`

.. toctree::
   :maxdepth: 2
   :caption: 入门指南

   source/guide

.. toctree::
   :maxdepth: 2
   :caption: 进阶指南

   source/advanced

.. toctree::
   :maxdepth: 2
   :caption: 命令行工具

   source/cli

.. toctree::
   :maxdepth: 2
   :caption: 算法讲解

   source/algorithm

.. toctree::
   :maxdepth: 2
   :caption: 命令行工具 (CLI)

   source/cli

.. toctree::
   :maxdepth: 2
   :caption: API 参考

   source/qpandalite_api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
