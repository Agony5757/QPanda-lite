.. QPanda-lite documentation master file

欢迎来到 QPanda-lite!
=======================================

QPanda-lite 是一个轻量级的量子计算框架，提供量子线路构建、本地模拟、多平台真机任务提交等功能。

.. image:: https://badge.fury.io/gh/Agony5757%2FQPanda-lite.svg?icon=si%3Agithub
    :target: https://badge.fury.io/gh/Agony5757%2FQPanda-lite

.. image:: https://readthedocs.org/projects/qpanda-lite/badge/?version=latest
   :target: https://qpanda-lite.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://badge.fury.io/py/qpandalite.svg?icon=si%3Apython
   :target: https://badge.fury.io/py/qpandalite
   :alt: PyPI version

.. image:: https://github.com/Agony5757/QPanda-lite/actions/workflows/build_and_test.yml/badge.svg?branch=main
   :target: https://github.com/Agony5757/QPanda-lite/actions/workflows/build_and_test.yml
   :alt: Build and Test

.. note::

   **开发中**
      - 不稳定
      - 未发布

.. toctree::
   :maxdepth: 2
   :caption: 教程

   source/guide/installation
   source/guide/quickstart
   source/guide/circuit
   source/guide/simulation
   source/guide/submit_task

.. toctree::
   :maxdepth: 2
   :caption: 语言规范

   source/guide/originir
   source/guide/qasm

.. toctree::
   :maxdepth: 2
   :caption: 进阶

   source/advanced/opcode
   source/advanced/noise_simulation
   source/advanced/circuit_analysis

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
   source/qpandalite.qcloud_config
   source/qpandalite.task
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
