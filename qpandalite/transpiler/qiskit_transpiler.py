# Transpiler imported from qiskit

from pyqpanda3.transpilation import Transpiler

def _impl_transpile(circuit, transpiler, gate_set):
    return circuit

def transpile(circuits, gate_set):    
    transpiler = Transpiler()
    if isinstance(circuits, list):
        return [transpiler.transpile(circuit, gate_set) for circuit in circuits]
    
    if not isinstance(circuits, str):
        raise TypeError("circuits should be a list or a string")
    
    return _impl_transpile(circuits, transpiler, gate_set)
    
    