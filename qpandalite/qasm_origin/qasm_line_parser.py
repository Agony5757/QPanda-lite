import re
import math
from qpandalite.circuit_builder.qcircuit import Circuit

class OpenQASM2_Parser:
    """
        The module transforms circuits written in OpenQASM 2.0 into an intermediate representation known as OriginIR.

        This representation can then be further transformed to be compatible with our quantum machines.
        
        Essentially, with OpenQASM2_Parser, any quantum circuit penned in OpenQASM 2.0 can be seamlessly executed on the OriginQC platform.
        
        Example:
            # [Assume you have a circuit written in OpenQASM 2.0]
            # [And the type of it is string, e.g. circ.qasm() in qiskit]
            
            qasm_string = circ.qasm()
            
            # The quantum circuit(OriginIR) object
            circuit_origin = OpenQASM2_Parser.build_from_qasm_str(qasm_string)
            
            # Converting back to original quantum circuit(OpenQASM 2.0) using qasm in the Circuit(OriginIR) class
            qc_init = QuantumCircuit.from_qasm_str(circuit_origin.qasm)

        Notice:
            This module now only sucessfully converting QASM file with h, x, y, z, rx, ry, rz, cx, cz.
            More will be supported soon. :^)
    """
    def __init__(self):
        pass
    
    @staticmethod
    def string_to_float(s):
        # Define a safe dictionary that only contains the math module's attributes
        safe_dict = {k: getattr(math, k) for k in dir(math)}
        
        try:
            return eval(s, {"__builtins__": None}, safe_dict)
        except:
            raise ValueError(f"Failed to convert '{s}' to float")

    @staticmethod
    def parse_line(line, QASM_Origin_circuit):
        try:
            if not line:
                pass 
            elif line.startswith('qreg'):
                pass
            elif line.startswith('creg'):
                pass
            elif line.startswith('h'):
                match_h = re.match(r'h q\[(\d+)\];', line) 
                qubit = int(match_h.group(1))
                QASM_Origin_circuit.h(qubit)

            elif line.startswith('x'):
                match_x = re.match(r'x q\[(\d+)\];', line) 
                qubit = int(match_x.group(1))
                QASM_Origin_circuit.x(qubit)

            elif line.startswith('SX'):
                pass
            elif line.startswith('y'):
                match_y = re.match(r'y q\[(\d+)\];', line) 
                qubit = int(match_y.group(1))
                QASM_Origin_circuit.y(qubit)

            elif line.startswith('z'):
                match_z = re.match(r'z q\[(\d+)\];', line) 
                qubit = int(match_z.group(1))
                QASM_Origin_circuit.z(qubit)

            elif line.startswith('cz'):
                match_cz = re.match(r'cz q\[(\d+)\],q\[(\d+)\];', line)
                qubit1, qubit2 = map(int, match_cz.groups())
                QASM_Origin_circuit.cz(qubit1, qubit2)

            elif line.startswith('ISWAP'):
                pass
            elif line.startswith('XY'):
                pass
            elif line.startswith('cx'):
                # Match the cx operation
                match_cx = re.match(r'cx q\[(\d+)\],q\[(\d+)\];', line)
                qubit1, qubit2 = map(int, match_cx.groups())
                QASM_Origin_circuit.cnot(qubit1, qubit2)

            elif line.startswith('rx'):
                pattern = r'rx\(([^)]+)\) q\[(\d+)\];'

                match = re.match(pattern, line)
                
                param_str = match.group(1)
                qubit = int(match.group(2))

                param = OpenQASM2_Parser.string_to_float(param_str)

                QASM_Origin_circuit.rx(qubit, param)

            elif line.startswith('ry'):
                pattern = r'ry\(([^)]+)\) q\[(\d+)\];'

                match = re.match(pattern, line)
                
                param_str = match.group(1)
                qubit = int(match.group(2))

                param = OpenQASM2_Parser.string_to_float(param_str)

                QASM_Origin_circuit.ry(qubit, param)
            
            elif line.startswith('rz'):
                pattern = r'rz\(([^)]+)\) q\[(\d+)\];'

                match = re.match(pattern, line)
                
                param_str = match.group(1)
                qubit = int(match.group(2))

                param = OpenQASM2_Parser.string_to_float(param_str)

                QASM_Origin_circuit.rz(qubit, param)

            elif line.startswith('u3'):
                pass

            elif line.startswith('barrier'):
                pattern = r'q\[(\d+)\]'
                matches = re.findall(pattern, line)
                # Convert matched strings to integers
                qubit_indices = [int(index) for index in matches]
                # print(qubit_indices)
                QASM_Origin_circuit.barrier(*qubit_indices)
            
            elif line.startswith('measure'):
                match_measure = re.match(r'measure (\w+)\[(\d+)\] -> (\w+)\[\d+\];', line)
                qubit = int(match_measure.group(2))
                QASM_Origin_circuit.measure_list.append(qubit)
            elif line.startswith('CONTROL'):
                pass
            elif line.startswith('ENDCONTROL'):
                pass
            elif line.startswith('DAGGER'):
                pass
            elif line.startswith('ENDDAGGER'):
                pass
            else:
                raise NotImplementedError(f'This line of OpenQASM 2 has not been supported yet: {line}.')      
            
            return None
        except AttributeError as e:
            raise RuntimeError(f'Error when parsing the line: {line}')

    @staticmethod
    def build_from_qasm_str(qasm_str):
        """
        The function coverts OpenQASM string into OriginIR circuit. It will create the
        quantum circuit object given the qasm_str.

        In the initilization phase, we need to notice that OriginIR-based quantum circuit
        doe not need to specify how many qregs and cregs used. 
        
        Parameters:
        - qasm_str: The quantum circuit of intersts in the OpenQASM format.

        Returns:
        - origin_qcirc: The quantum circuit of intersts in the OriginIR format. 
        """
        # Create an empty Circuit object
        origincircuit = Circuit()
        # parser = OpenQASM2_Parser()

        lines_to_remove = ["OPENQASM 2.0;", "include \"qelib1.inc\";"]

        # Split the QASM string into lines and parse each line
        for line in qasm_str.split("\n"):
            if line not in lines_to_remove:
                OpenQASM2_Parser.parse_line(line, origincircuit)

        return origincircuit