.. QPanda-lite documentation master file, created by
   sphinx-quickstart on Tue Aug 29 11:07:09 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

欢迎来到QPanda-lite!
=======================================
QPanda-lite是一个轻量级的QPanda支持。

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
   source/guide/originir_simple
   source/guide/build_circuit_simple
   source/guide/opcode
   source/guide/simulation_simple
   source/guide/submit_task_simple
   source/guide/qasm

.. toctree::
   :maxdepth: 2
   :caption: 功能文档

   source/features/build_circuit
   source/features/submit_task_general

.. toctree::
   :maxdepth: 2
   :caption: qpandalite analyzer模块 API文档
   source/qpandalite.analyzer

.. toctree::
   :maxdepth: 2
   :caption: qpandalite circuit_builder模块 API文档

   source/qpandalite.circuit_builder

.. toctree::
   :maxdepth: 2
   :caption: qpandalite originir模块 API文档
   
   source/qpandalite.originir

.. toctree::
   :maxdepth: 2
   :caption: qpandalite qasm模块 API文档

   source/qpandalite.qasm

.. toctree::
   :maxdepth: 2
   :caption: qpandalite simulator模块 API文档

   source/qpandalite.simulator
   source/qpandalite.simulator.opcode_simulator
   source/qpandalite.simulator.originir_simulator
   source/qpandalite.simulator.qasm_simulator
   source/qpandalite.simulator.error_model

.. toctree::
   :maxdepth: 2
   :caption: qpandalite task模块 API文档
   
   .. source/qpandalite.task

   source/qpandalite.task.origin_qcloud
   source/qpandalite.task.quafu
   source/qpandalite.task.platform_template

.. toctree::
   :maxdepth: 2
   :caption: qpandalite test模块 API文档

   source/qpandalite.test
   

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
