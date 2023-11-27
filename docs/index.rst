.. QPanda-lite documentation master file, created by
   sphinx-quickstart on Tue Aug 29 11:07:09 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

欢迎来到QPanda-lite!
=======================================
QPanda-lite是一个轻量级的QPanda支持。


.. note::
   
   **开发中**
      - 不稳定
      - 未发布

.. _install:

*************************
QPanda-lite 安装
*************************

.. _pip-install:

从pip安装
------------------------

* 安装方式

.. code-block:: bash

   pip install qpandalite


.. _build-from-source:

从源码安装
------------------------

* 平台要求

Python本体
   - Python 3

C++量子线路模拟器支持（可选）
   - C++ compiler (support C++17 or more)
   - CMake 3.x

* 安装方式

.. code-block:: bash

   # installation
   python setup.py install

   # development
   # (deprecated when building with C++)
   python setup.py develop


.. toctree::
   :maxdepth: 2
   :caption: API docs

   source/qpandalite.circuit_builder
   source/qpandalite.originir
   source/qpandalite.task
   source/qpandalite.task.originq
   source/qpandalite.task.quafu
   source/qpandalite.simulator



.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
