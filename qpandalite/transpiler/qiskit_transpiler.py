import qiskit
from qiskit import QuantumCircuit
from qiskit.compiler import transpile
from qiskit.transpiler import CouplingMap
from qiskit.qasm2 import loads as qasm2_loads
from qiskit.qasm2 import dumps as qasm2_dumps
from qiskit.qasm2 import LEGACY_CUSTOM_INSTRUCTIONS

if __name__ == "__main__":
    from _utils import CompilationFailedException
else:
    from ._utils import CompilationFailedException

from typing import List, Tuple, Union, Optional
from converter import convert_qasm_to_oir, convert_oir_to_qasm

def transpile_qasm(
    qasm_strings: List[str],
    topology: List[Union[List[int], Tuple[int, int]]] = None,
    optimization_level: int = 1,
    basis_gates: Optional[List[str]] = None,
) -> List[str]:
    """
    使用指定的拓扑、基本门和优化级别编译一组OPENQASM 2.0线路字符串。

    Args:
        qasm_strings: 包含 OPENQASM 2.0 线路描述的字符串列表。
        topology: 定义硬件拓扑的耦合图列表。
                  例如: [[0, 1], [1, 2], [1, 3]] 表示 0<->1, 1<->2, 1<->3 的连接。
        optimization_level: Qiskit transpile 的优化级别 (0 到 3)。
                            0: No optimization
                            1: Light optimization
                            2: Heavy optimization
                            3: Heaviest optimization
        basis_gates: 用于编译的目标基本门集。如果为 None，则使用默认 ['cz', 'sx', 'rz']。
                     请确保您选择的门在 Qiskit 的标准库中或已被正确定义。

    Returns:
        一个字符串列表，包含编译后的 OPENQASM 2.0 线路。

    Raises:
        ImportError: 如果 Qiskit 未安装。
        QiskitError: 如果输入的 QASM 字符串无效或编译过程中发生错误。
        ValueError: 如果优化级别无效。
    """        
    if not qasm_strings:
        return []
    
    if isinstance(qasm_strings, str):
        qasm_strings = [qasm_strings]
        single_circuit = True
    else:
        single_circuit = False

    try:
        if basis_gates is None:
            basis_gates = ['cz', 'sx', 'rz']

        if optimization_level not in [0, 1, 2, 3]:
            raise ValueError("Invalid optimization_level. Must be 0, 1, 2, or 3.")

        coupling_map = CouplingMap(topology)

        circuits = []
        for i, qasm_str in enumerate(qasm_strings):
            try:
                circuit = qasm2_loads(qasm_str, custom_instructions=LEGACY_CUSTOM_INSTRUCTIONS)
                circuits.append(circuit)
            except Exception as e:
                raise CompilationFailedException(f"Error loading QASM string at index {i}: {e}")

        if not circuits:
            print("Warning: No valid circuits were loaded.")
            return []

        transpiled_circuits = transpile(
            circuits,
            coupling_map=coupling_map,
            basis_gates=basis_gates,
            optimization_level=optimization_level
        )

        output_qasm_strings = []
        for i, transpiled_circuit in enumerate(transpiled_circuits):
            try:
                output_qasm = qasm2_dumps(transpiled_circuit)
                output_qasm_strings.append(output_qasm)
            except Exception as e:
                raise CompilationFailedException(f"Error dumping transpiled circuit at index {i} to QASM: {e}")

        if single_circuit:
            return output_qasm_strings[0]
        else:
            return output_qasm_strings

    except CompilationFailedException as e:
        raise e
    except ImportError:
        raise CompilationFailedException("Error: Qiskit is not installed. Please install it using 'pip install qiskit'")
    except qiskit.exceptions.QiskitError as e:
        raise CompilationFailedException(f"An error occurred during Qiskit operation: {e}")
    except Exception as e:
        raise CompilationFailedException(f"An unexpected error occurred: {e}")

def transpile_originir(
        originir_strings: List[str],
        topology: List[Union[List[int], Tuple[int, int]]] = None,
        optimization_level: int = 1,
        basis_gates: Optional[List[str]] = None,
):
    """
    使用指定的拓扑、基本门和优化级别编译一组 OriginIR 线路字符串。

    Args:
        originir_strings: 包含 OriginIR 线路描述的字符串列表。
        topology: 定义硬件拓扑的耦合图列表。
                  例如: [[0, 1], [1, 2], [1, 3]] 表示 0<->1, 1<->2, 1<->3 的连接。
        optimization_level: Qiskit transpile 的优化级别 (0 到 3)。
                            0: No optimization
                            1: Light optimization
                            2: Heavy optimization
                            3: Heaviest optimization
        basis_gates: 用于编译的目标基本门集。如果为 None，则使用默认 ['cz', 'sx', 'rz']。
                     请确保您选择的门在 Qiskit 的标准库中或已被正确定义。

    Returns:
        一个字符串列表，包含编译后的 OriginIR 线路。

    Raises:
        ImportError: 如果 Qiskit 未安装。
        QiskitError: 如果输入的 OriginIR 字符串无效或编译过程中发生错误。
        ValueError: 如果优化级别无效。        
    """
    if not originir_strings:
        return []
    
    if isinstance(originir_strings, str):
        originir_strings = [originir_strings]
        single_circuit = True
    else:
        single_circuit = False

    qasm_strs = []
    for originir_str in originir_strings:
        qasm_str = convert_oir_to_qasm(originir_str)
        qasm_strs.append(qasm_str)

    transpiled_qasm_strs = transpile_qasm(
        qasm_strs,
        topology=topology,
        optimization_level=optimization_level,
        basis_gates=basis_gates
    )

    output_originir_strs = []
    for transpiled_qasm_str in transpiled_qasm_strs:
        output_originir_str = convert_qasm_to_oir(transpiled_qasm_str)
        output_originir_strs.append(output_originir_str)

    if single_circuit:
        return output_originir_strs[0]
    else:
        return output_originir_strs
                 


# --- 示例用法 ---
if __name__ == "__main__":
    # 1. 定义示例 OPENQASM 2.0 线路字符串列表
    qasm_input_list = [
        """
        OPENQASM 2.0;
        include "qelib1.inc";
        qreg q[3];
        creg c[3];
        h q[0];
        cx q[0], q[1];
        rz(pi/4) q[1];
        cx q[1], q[2];
        measure q[0] -> c[0];
        measure q[1] -> c[1];
        measure q[2] -> c[2];
        """,
        """
        OPENQASM 2.0;
        include "qelib1.inc";
        qreg q[2];
        creg c[2];
        h q[0];
        cz q[0], q[1]; // 使用 CZ 门
        sx q[1];      // 使用 SX 门
        measure q -> c;
        """
    ]

    # 2. 定义目标拓扑结构 (例如，一个简单的线性链)
    # 0 -- 1 -- 2
    custom_topology = [[0, 1], [1, 0], [1, 2], [2, 1]] # 需要双向连接

    # 3. 调用包装函数
    try:
        print("--- Transpiling with optimization level 1 ---")
        transpiled_qasm_list_opt1 = transpile_qasm(
            qasm_strings=qasm_input_list,
            topology=custom_topology,
            optimization_level=1,
        )

        print("\n--- Transpiled QASM (Opt Level 1) ---")
        for i, qasm_out in enumerate(transpiled_qasm_list_opt1):
            print(f"--- Circuit {i+1} ---")
            print(qasm_out)
            print("-" * 20)

        print("\n--- Transpiling with optimization level 3 ---")
        transpiled_qasm_list_opt3 = transpile_qasm(
            qasm_strings=qasm_input_list,
            topology=custom_topology,
            optimization_level=3 # 更高的优化级别
            # 使用默认 basis_gates ['cz', 'sx', 'rz']
        )

        print("\n--- Transpiled QASM (Opt Level 3) ---")
        for i, qasm_out in enumerate(transpiled_qasm_list_opt3):
            print(f"--- Circuit {i+1} ---")
            print(qasm_out)
            print("-" * 20)

    except Exception as e:
        print(f"An error occurred during the example execution: {e}")

