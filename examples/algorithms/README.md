# Algorithm Examples

完整量子算法实现示例。

每个算法包含 Python 代码与 Markdown 文档。

## 算法列表

| Algorithm | Code | Documentation |
|-----------|------|---------------|
| Grover 搜索 | [grover.py](grover.py) | [grover.md](grover.md) |
| VQE | [vqe.py](vqe.py) | [vqe.md](vqe.md) |
| QAOA | [qaoa.py](qaoa.py) | [qaoa.md](qaoa.md) |
| QPE | [qpe.py](qpe.py) | [qpe.md](qpe.md) |

## 运行方式

从仓库根目录执行：

```bash
# Grover 搜索
python examples/algorithms/grover.py --n-qubits 3 --target 5

# VQE (H2 分子)
python examples/algorithms/vqe.py --ansatz hea --n-qubits 2

# QAOA (MaxCut)
python examples/algorithms/qaoa.py --n-qubits 4 --p 2

# QPE
python examples/algorithms/qpe.py --n-qubits 3
```

## 文档说明

每个 `.md` 文件包含：

- 算法原理与数学背景
- 代码实现详解
- 运行示例与预期输出
- 扩展思路
- 参考文献
