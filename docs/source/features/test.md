# 已测试的功能

QPanda-lite通过自动化的测试，保证了其功能的正确性。

## 模拟器测试

### QASMBench测试

在`qpandalite.test.test_qasmbench`中，我们选择了QASMBench作为测试用例。在QASMBench.pkl文件中，我们保存了一组以OPENQASM 2.0格式编写的量子电路以及其对应的结果。

```python
def _load_QASMBench(path):
    path = Path(path)
    filename = path / 'QASMBench.pkl'

    with open(filename, 'rb') as fp:
        dataset = pickle.load(fp)

    return dataset
```