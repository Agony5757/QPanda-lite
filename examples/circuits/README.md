# QPanda-Lite Circuit Examples

基于 `qpandalite.algorithmics.circuits` 组件库的示例代码。

## 示例列表

- `qft.py` — 量子傅里叶变换
- `deutsch-jozsa.py` — Deutsch-Jozsa 算法
- `thermal_state.py` — 热态制备
- `dicke_state.py` — Dicke 态制备
- `grover_oracle.py` — Grover Oracle 构造
- `vqd.py` — 变分量子 deflate（激发态搜索）
- `amplitude_estimation.py` — 量子振幅估计
- `entangled_states.py` — GHZ / W / Cluster 纠缠态

## 运行方式

从仓库根目录执行：

```bash
python examples/circuits/qft.py --n-qubits 3 --input-state 5
```
