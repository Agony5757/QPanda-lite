# Measurement Examples

量子态测量与层析示例代码。

## 示例列表

| File | Description |
|------|-------------|
| [state_tomography.py](state_tomography.py) | 完整量子态层析（重构密度矩阵） |
| [shadow_tomography.py](shadow_tomography.py) | 经典影子层析（高效态表征） |

## 运行方式

从仓库根目录执行：

```bash
python examples/measurement/state_tomography.py --n-qubits 2
python examples/measurement/shadow_tomography.py --n-qubits 2 --n-shadows 1000
```

## 参考文献

- State tomography: James et al. (2001)
- Shadow tomography: Huang, Kueng, Preskill (2020)
