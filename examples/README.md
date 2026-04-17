# QPanda-Lite Examples

> 示例代码已迁移至 [文档中心 → 算法讲解](https://qpanda-lite.readthedocs.io/zh-cn/latest/source/algorithm.html)

## 示例代码目录

| 目录 | 说明 |
|------|------|
| [getting-started/](getting-started/) | 快速上手教程（电路构建、模拟、配置） |
| [state_preparation/](state_preparation/) | 态制备示例（叠加态、任意态） |
| [measurement/](measurement/) | 测量技术（态层析、影子层析） |
| [circuits/](circuits/) | 电路组件（QFT、Grover Oracle、VQD 等） |
| [algorithms/](algorithms/) | 完整算法（Grover、VQE、QAOA、QPE） |
| [advanced/](advanced/) | 进阶功能（参数化电路、PyTorch 集成） |

## 快速导航

**新手入门**

```bash
python examples/getting-started/1_circuit_remap.py
python examples/getting-started/config_example.py
```

**算法示例**

```bash
python examples/algorithms/grover.py --n-qubits 3
python examples/algorithms/vqe.py --ansatz hea
```

**进阶功能**

```bash
python examples/advanced/pytorch_integration.py
```
