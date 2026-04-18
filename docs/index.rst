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

核心工作流
----------

QPanda-lite 的设计围绕一个简洁的工作流：**任意方式构建线路 → CLI 统一执行**。

.. code-block:: bash
   :caption: 1. 安装

   pip install qpandalite

.. code-block:: python
   :caption: 2. 构建线路（支持 QPanda-lite 原生或任意第三方工具）

   from qpandalite.circuit_builder import Circuit

   c = Circuit()
   c.h(0)
   c.cnot(0, 1)
   c.measure(0, 1)

   # 输出 OriginIR 格式，可供 CLI 使用
   open('circuit.ir', 'w').write(c.originir)

.. code-block:: bash
   :caption: 3. CLI 统一执行

   # 本地模拟
   qpandalite simulate circuit.ir --shots 1000

   # 提交到云端
   qpandalite submit circuit.ir --platform originq --shots 1000

   # 查询任务结果
   qpandalite result <task_id>

设计理念
--------

**线路构建，工具自由**

QPanda-lite 提供原生的 Circuit API，但你也可以使用 Qiskit、Cirq 等任何工具构建线路。最终只需输出 OriginIR 或 OpenQASM 2.0 格式即可。

**CLI 执行，接口统一**

无论是本地模拟还是云端真机，CLI 提供一致的命令接口：``simulate``、``submit``、``result``、``config``。

**结果数据，原生结构**

测量结果以 Python 原生 ``dict`` / ``list`` / ``ndarray`` 返回，无需额外解析，便于集成到数据分析流程。

快速入口
--------

**首次接触？**

:doc:`安装 <source/guide/installation>` → :doc:`快速上手 <source/guide/quickstart>` → :doc:`构建线路 <source/guide/circuit>` → :doc:`本地模拟 <source/guide/simulation>` → :doc:`提交任务 <source/guide/submit_task>`

**进阶功能**

:doc:`OriginIR <source/guide/originir>` | :doc:`OpenQASM 2.0 <source/guide/qasm>` | :doc:`PyTorch 集成 <source/guide/pytorch>` | :doc:`任务管理器 <source/guide/task_manager>` | :doc:`转译器 <source/qpandalite.transpiler>` | :doc:`电路分析 <source/advanced/circuit_analysis>`

**命令行工具**

:doc:`CLI 安装 <source/cli/installation>` | :doc:`本地模拟 <source/cli/simulate>` | :doc:`云端提交 <source/cli/submit>` | :doc:`结果查询 <source/cli/result>` | :doc:`配置管理 <source/cli/config>`

**算法示例**

**变分算法** :doc:`VQE <source/algorithm/variational/vqe>` | :doc:`QAOA <source/algorithm/variational/qaoa>` | :doc:`VQD <source/algorithm/variational/vqd>`

**搜索算法** :doc:`Grover 搜索 <source/algorithm/search/grover>` | :doc:`Grover Oracle <source/algorithm/search/grover_oracle>`

**相位估计** :doc:`QPE <source/algorithm/phase/qpe>` | :doc:`QFT <source/algorithm/phase/qft>`

**Oracle 算法** :doc:`振幅估计 <source/algorithm/oracle/amplitude_estimation>` | :doc:`Deutsch-Jozsa <source/algorithm/oracle/deutsch-jozsa>`

**态制备** :doc:`纠缠态 <source/algorithm/state/entangled_states>` | :doc:`Dicke 态 <source/algorithm/state/dicke_state>` | :doc:`热态 <source/algorithm/state/thermal_state>`

**测量** :doc:`影子层析 <source/algorithm/measurement/shadow_tomography>` | :doc:`态层析 <source/algorithm/measurement/state_tomography>`

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
   :caption: API 参考

   source/qpandalite_api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
