# QPanda-lite 安装

## 从pip安装

仅需一行代码就可以安装qpandalite的本体

```bash
pip install qpandalite
```

## 从源码构建

### 平台要求

- 操作系统：QPanda-lite应该是跨平台的，但是由于人手有限，仅在windows上进行了测试

- Python (>=3.8, <=3.13)
   
- C++量子线路模拟器支持（可选）
   - C++ compiler (支持C++17)
   - CMake 3.x

### 安装方式

```bash
git clone https://github.com/Agony5757/QPanda-lite.git
cd QPanda-lite
python setup.py install

# 无C++模拟器（不需要安装C++编译环境）
python setup.py install --no-cpp
```

### 额外要求

#### OriginQ平台支持

```bash
pip install quafu
```

#### quafu平台支持

```bash
pip install quafu
```

#### IBM平台支持
```bash
pip install qiskit
pip install qiskit-ibm-provider
pip install qiskit-ibmq-provider
```


## 构建文档
当已经安装了QPanda-lite之后
```bash
cd docs
pip install -r requirements.txt
make html
```