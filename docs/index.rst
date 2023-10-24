.. QPanda-lite documentation master file, created by
   sphinx-quickstart on Tue Aug 29 11:07:09 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=======================================
欢迎来到QPanda-lite!
=======================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   qpandalite.task
   qpandalite.task.originq
   qpandalite.task.quafu
   qpandalite.simulator
   :ref:`modindex`


What is QPanda-lite?
==========================
QPanda-lite是一个轻量级的QPanda支持。

当前状态
==========================
**开发中**
   - 不稳定
   - 未发布

安装
==========================

从源码安装
--------------

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

从pip安装
--------------
将在未来支持。

.. code-block:: bash

   pip install qpandalite


模块
==========================

Task
--------------

Task模块是一个第三方的量子云平台任务提交的支持。现在支持OriginQ平台和Quafu平台。

* OriginQ

API文档详见
:doc:`source/qpandalite.task.originq`

简易用法

.. code-block:: python

   import qpandalite.task.originq as task
   
   # code an originir
   # originir = ...
   taskid = task.submit_task(originir)
   result = task.query_by_taskid(taskid)
   print(result)
   
   # code many originirs
   # originir_list = list()
   # ... append to originir_list
   task.submit_task(originir_list)
   result_list = task.query_by_taskid(taskid)
   for result in result_list:
      print(result)


* Quafu 

API文档详见
:doc:`source/qpandalite.task.quafu`

简易用法

.. code-block:: python

   import qpandalite.task.quafu as task
   
   # code some originir
   # originir = ...
   taskid = task.submit_task(originir)
   result = task.query_by_taskid(taskid)
   print(result)


Circuit builder
---------------
简单的线路编辑器（开发中）

Simulator
--------------
一个C++量子线路模拟器（开发中）



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
