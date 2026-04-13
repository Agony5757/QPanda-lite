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

**首次接触？** :doc:`安装 <source/guide/installation>` → :doc:`快速上手 <source/guide/quickstart>` → :doc:`构建线路 <source/guide/circuit>` → :doc:`本地模拟 <source/guide/simulation>` → :doc:`提交任务 <source/guide/submit_task>`

**格式与底层：** :doc:`OriginIR <source/guide/originir>` / :doc:`OpenQASM 2.0 <source/guide/qasm>` / :doc:`进阶分析 <source/advanced/circuit_analysis>` / :doc:`Opcode <source/advanced/opcode>`

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
   :caption: 算法讲解

   source/algorithm

.. toctree::
   :maxdepth: 2
   :caption: API 参考

   source/qpandalite_api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
