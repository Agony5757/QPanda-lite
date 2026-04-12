.. QPanda-lite documentation master file

QPanda-lite — 轻量级量子计算框架

QPanda-lite 是一个 Python 原生、轻量且强调透明性的量子计算框架，提供量子线路构建、本地模拟、多平台任务提交，以及 OriginIR / OpenQASM 2.0 格式支持。

|GitHub| |PyPI| |Docs| |Build|

.. |GitHub| image:: https://badge.fury.io/gh/Agony5757%2FQPanda-lite.svg?icon=si%3Agithub
    :target: https://badge.fury.io/gh/Agony5757%2FQPanda-lite

.. |PyPI| image:: https://badge.fury.io/py/qpandalite.svg?icon=si%3Apython
    :target: https://badge.fury.io/py/qpandalite

.. |Docs| image:: https://readthedocs.org/projects/qpanda-lite/badge/?version=latest
    :target: https://qpanda-lite.readthedocs.io/en/latest/?badge=latest

.. |Build| image:: https://github.com/Agony5757/QPanda-lite/actions/workflows/build_and_test.yml/badge.svg?branch=main
    :target: https://github.com/Agony5757/QPanda-lite/actions/workflows/build_and_test.yml

快速入口
--------

**首次接触 QPanda-lite？** 按以下路径快速上手：

1. :doc:`安装 <source/guide/installation>`
2. :doc:`快速上手 <source/guide/quickstart>`
3. :doc:`构建量子线路 <source/guide/circuit>`
4. :doc:`本地模拟 <source/guide/simulation>`
5. :doc:`提交任务 <source/guide/submit_task>`

**需要格式转换或底层细节？**

- :doc:`OriginIR <source/guide/originir>` / :doc:`OpenQASM 2.0 <source/guide/qasm>`
- :doc:`进阶分析 <source/advanced/circuit_analysis>` / :doc:`Opcode <source/advanced/opcode>`

.. toctree::
   :maxdepth: 2
   :caption: 快速上手

   source/guide/installation
   source/guide/quickstart
   source/guide/circuit
   source/guide/simulation
   source/guide/submit_task

.. toctree::
   :maxdepth: 2
   :caption: 格式与接口

   source/guide/originir
   source/guide/qasm
   source/guide/testing

.. toctree::
   :maxdepth: 2
   :caption: 进阶

   source/advanced/circuit_analysis
   source/advanced/opcode
   source/advanced/noise_simulation

.. toctree::
   :maxdepth: 2
   :caption: API 参考

   source/qpandalite.rst
   source/qpandalite.circuit_builder
   source/qpandalite.simulator
   source/qpandalite.originir
   source/qpandalite.qasm
   source/qpandalite.transpiler
   source/qpandalite.analyzer
   source/qpandalite.algorithmics
   source/qpandalite.qcloud_config
   source/qpandalite.task
   source/qpandalite.task.adapters
   source/qpandalite.task.config
   source/qpandalite.task.ibm
   source/qpandalite.task.quafu
   source/qpandalite.task.originq
   source/qpandalite.task.originq_dummy
   source/qpandalite.task.origin_qcloud
   source/qpandalite.task.platform_template

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
