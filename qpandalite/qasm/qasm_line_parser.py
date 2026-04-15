"""OpenQASM 2.0 line parser module.

This module provides regex-based parsing for individual OpenQASM 2.0 lines,
supporting qreg/creg definitions, 1-4 qubit gates, parameterized gates, and measurements.

Key exports:
    OpenQASM2_LineParser: Parser class for individual OpenQASM 2.0 lines.
"""

from __future__ import annotations

__all__ = ["OpenQASM2_LineParser"]

import math
import re
from typing import Any


class OpenQASM2_LineParser:  # noqa: N801
    """Parser for individual OpenQASM 2.0 lines.

    Provides regex-based parsing for OpenQASM 2.0 statements including
    qreg/creg definitions, 1-4 qubit gates, parameterized gates, and measurements.
    """

    
    # Fragment patterns
    identifier: str = r"([A-Za-z_][A-Za-z_\d]*)"
    blank: str = r" *"
    comma: str = r","
    index: str = r"\[ *(\d+) *\]"
    any_parameters: str = r"\(([^()]+)\)"

    # Regex pattern strings
    regexp_qreg_str: str = "^" + "qreg" + blank + identifier + blank + index + blank + "$"
    regexp_creg_str: str = "^" + "creg" + blank + identifier + blank + index + blank + "$"
    qreg_str: str = identifier + blank + index + blank
    regexp_1q_str: str = "^" + identifier + blank + qreg_str + "$"
    regexp_2q_str: str = "^" + identifier + blank + qreg_str + comma + blank + qreg_str + "$"
    regexp_3q_str: str = "^" + identifier + blank + qreg_str + comma + blank + qreg_str + comma + blank + qreg_str + "$"
    regexp_4q_str: str = (
        "^"
        + identifier
        + blank
        + qreg_str
        + comma
        + blank
        + qreg_str
        + comma
        + blank
        + qreg_str
        + comma
        + blank
        + qreg_str
        + "$"
    )
    regexp_1qnp_str: str = "^" + identifier + blank + any_parameters + blank + qreg_str + "$"
    regexp_2qnp_str: str = "^" + identifier + blank + any_parameters + blank + qreg_str + comma + blank + qreg_str + "$"
    regexp_3qnp_str: str = (
        "^"
        + identifier
        + blank
        + any_parameters
        + blank
        + qreg_str
        + comma
        + blank
        + qreg_str
        + comma
        + blank
        + qreg_str
        + "$"
    )
    regexp_measure_str: str = "^" + "measure" + blank + qreg_str + "->" + blank + qreg_str + "$"

    # Compiled regex objects
    regexp_qreg: re.Pattern[str] = re.compile(regexp_qreg_str)
    regexp_creg: re.Pattern[str] = re.compile(regexp_creg_str)
    regexp_1q: re.Pattern[str] = re.compile(regexp_1q_str)
    regexp_2q: re.Pattern[str] = re.compile(regexp_2q_str)
    regexp_3q: re.Pattern[str] = re.compile(regexp_3q_str)
    regexp_4q: re.Pattern[str] = re.compile(regexp_4q_str)
    regexp_1qnp: re.Pattern[str] = re.compile(regexp_1qnp_str)
    regexp_2qnp: re.Pattern[str] = re.compile(regexp_2qnp_str)
    regexp_3qnp: re.Pattern[str] = re.compile(regexp_3qnp_str)
    regexp_measure: re.Pattern[str] = re.compile(regexp_measure_str)

    def __init__(self) -> None: ...

    @staticmethod
    def handle_qreg(line: str) -> tuple[str, int]:
        """Parse a qreg definition line.

        Args:
            line: QASM line defining a quantum register.

        Returns:
            tuple: (register_name, size)
        """
        matches = OpenQASM2_LineParser.regexp_qreg.match(line)
        qreg_name: str = matches.group(1)  # type: ignore[union-attr]
        qreg_size: int = int(matches.group(2))  # type: ignore[union-attr]
        return qreg_name, qreg_size

    @staticmethod
    def handle_creg(line: str) -> tuple[str, int]:
        """Parse a creg definition line.

        Args:
            line: QASM line defining a classical register.

        Returns:
            tuple: (register_name, size)
        """
        matches = OpenQASM2_LineParser.regexp_creg.match(line)
        creg_name: str = matches.group(1)  # type: ignore[union-attr]
        creg_size: int = int(matches.group(2))  # type: ignore[union-attr]
        return creg_name, creg_size

    @staticmethod
    def handle_parameters(parameters_str: str) -> list[float]:
        """Parse a parameter string into a list of floats.

        Args:
            parameters_str: Comma-separated parameter expression string.

        Returns:
            list[float]: List of parsed parameter values.
        """
        parameters_str = parameters_str.strip()
        parameter_str_list = parameters_str.split(",")
        parameters: list[float] = []
        for parameter_str in parameter_str_list:
            parameters.append(float(eval(parameter_str.strip(), {"pi": math.pi})))  # noqa: PGH001, S307
        return parameters

    @staticmethod
    def handle_1q(line: str) -> tuple[str, str, int]:
        """Parse a 1-qubit gate line.

        Returns:
            tuple: (op_name, qreg_name, qubit_index)
        """
        matches = OpenQASM2_LineParser.regexp_1q.match(line)
        op_name: str = matches.group(1)  # type: ignore[union-attr]
        qreg_name: str = matches.group(2)  # type: ignore[union-attr]
        qubit_index: int = int(matches.group(3))  # type: ignore[union-attr]
        return op_name, qreg_name, qubit_index

    @staticmethod
    def handle_2q(line: str) -> tuple[str, str, int, str, int]:
        """Parse a 2-qubit gate line.

        Returns:
            tuple: (op_name, qreg_name1, qubit_index1, qreg_name2, qubit_index2)
        """
        matches = OpenQASM2_LineParser.regexp_2q.match(line)
        op_name: str = matches.group(1)  # type: ignore[union-attr]
        qreg_name1: str = matches.group(2)  # type: ignore[union-attr]
        qubit_index1: int = int(matches.group(3))  # type: ignore[union-attr]
        qreg_name2: str = matches.group(4)  # type: ignore[union-attr]
        qubit_index2: int = int(matches.group(5))  # type: ignore[union-attr]
        return op_name, qreg_name1, qubit_index1, qreg_name2, qubit_index2

    @staticmethod
    def handle_3q(
        line: str,
    ) -> tuple[str, str, int, str, int, str, int]:
        """Parse a 3-qubit gate line.

        Returns:
            tuple: (op_name, qreg_name1, qubit_index1, qreg_name2, qubit_index2, qreg_name3, qubit_index3)
        """
        matches = OpenQASM2_LineParser.regexp_3q.match(line)
        op_name: str = matches.group(1)  # type: ignore[union-attr]
        qreg_name1: str = matches.group(2)  # type: ignore[union-attr]
        qubit_index1: int = int(matches.group(3))  # type: ignore[union-attr]
        qreg_name2: str = matches.group(4)  # type: ignore[union-attr]
        qubit_index2: int = int(matches.group(5))  # type: ignore[union-attr]
        qreg_name3: str = matches.group(6)  # type: ignore[union-attr]
        qubit_index3: int = int(matches.group(7))  # type: ignore[union-attr]
        return (op_name, qreg_name1, qubit_index1, qreg_name2, qubit_index2, qreg_name3, qubit_index3)

    @staticmethod
    def handle_4q(
        line: str,
    ) -> tuple[str, str, int, str, int, str, int, str, int]:
        """Parse a 4-qubit gate line.

        Returns:
            tuple: (op_name, qreg_name1, qubit_index1, qreg_name2, qubit_index2, qreg_name3, qubit_index3, qreg_name4, qubit_index4)
        """
        matches = OpenQASM2_LineParser.regexp_4q.match(line)
        op_name: str = matches.group(1)  # type: ignore[union-attr]
        qreg_name1: str = matches.group(2)  # type: ignore[union-attr]
        qubit_index1: int = int(matches.group(3))  # type: ignore[union-attr]
        qreg_name2: str = matches.group(4)  # type: ignore[union-attr]
        qubit_index2: int = int(matches.group(5))  # type: ignore[union-attr]
        qreg_name3: str = matches.group(6)  # type: ignore[union-attr]
        qubit_index3: int = int(matches.group(7))  # type: ignore[union-attr]
        qreg_name4: str = matches.group(8)  # type: ignore[union-attr]
        qubit_index4: int = int(matches.group(9))  # type: ignore[union-attr]
        return (
            op_name,
            qreg_name1,
            qubit_index1,
            qreg_name2,
            qubit_index2,
            qreg_name3,
            qubit_index3,
            qreg_name4,
            qubit_index4,
        )

    @staticmethod
    def handle_1qnp(line: str, n_parameters: int) -> tuple[str, list[float], str, int]:
        """Parse a 1-qubit n-parameter gate line.

        Args:
            line: QASM line.
            n_parameters: Expected number of parameters.

        Returns:
            tuple: (op_name, parameters, qreg_name, qubit_index)
        """
        matches = OpenQASM2_LineParser.regexp_1qnp.match(line)
        op_name: str = matches.group(1)  # type: ignore[union-attr]
        parameters: list[float] = OpenQASM2_LineParser.handle_parameters(matches.group(2))  # type: ignore[union-attr]
        qreg_name: str = matches.group(3)  # type: ignore[union-attr]
        qubit_index: int = int(matches.group(4))  # type: ignore[union-attr]
        if len(parameters) != n_parameters:
            raise ValueError(
                f"The number of parameters for {op_name} should be {n_parameters}, but got {len(parameters)}."
            )
        return op_name, parameters, qreg_name, qubit_index

    @staticmethod
    def handle_2qnp(line: str, n_parameters: int) -> tuple[str, list[float], str, int, str, int]:
        """Parse a 2-qubit n-parameter gate line.

        Args:
            line: QASM line.
            n_parameters: Expected number of parameters.

        Returns:
            tuple: (op_name, parameters, qreg_name1, qubit_index1, qreg_name2, qubit_index2)
        """
        matches = OpenQASM2_LineParser.regexp_2qnp.match(line)
        op_name: str = matches.group(1)  # type: ignore[union-attr]
        parameters: list[float] = OpenQASM2_LineParser.handle_parameters(matches.group(2))  # type: ignore[union-attr]
        qreg_name1: str = matches.group(3)  # type: ignore[union-attr]
        qubit_index1: int = int(matches.group(4))  # type: ignore[union-attr]
        qreg_name2: str = matches.group(5)  # type: ignore[union-attr]
        qubit_index2: int = int(matches.group(6))  # type: ignore[union-attr]
        if len(parameters) != n_parameters:
            raise ValueError(
                f"The number of parameters for {op_name} should be {n_parameters}, but got {len(parameters)}."
            )
        return op_name, parameters, qreg_name1, qubit_index1, qreg_name2, qubit_index2

    @staticmethod
    def handle_3qnp(line: str, n_parameters: int) -> tuple[str, list[float], str, int, str, int, str, int]:
        """Parse a 3-qubit n-parameter gate line.

        Args:
            line: QASM line.
            n_parameters: Expected number of parameters.

        Returns:
            tuple: (op_name, parameters, qreg_name1, qubit_index1, qreg_name2, qubit_index2, qreg_name3, qubit_index3)
        """
        matches = OpenQASM2_LineParser.regexp_3qnp.match(line)
        op_name: str = matches.group(1)  # type: ignore[union-attr]
        parameters: list[float] = OpenQASM2_LineParser.handle_parameters(matches.group(2))  # type: ignore[union-attr]
        qreg_name1: str = matches.group(3)  # type: ignore[union-attr]
        qubit_index1: int = int(matches.group(4))  # type: ignore[union-attr]
        qreg_name2: str = matches.group(5)  # type: ignore[union-attr]
        qubit_index2: int = int(matches.group(6))  # type: ignore[union-attr]
        qreg_name3: str = matches.group(7)  # type: ignore[union-attr]
        qubit_index3: int = int(matches.group(8))  # type: ignore[union-attr]
        if len(parameters) != n_parameters:
            raise ValueError(
                f"The number of parameters for {op_name} should be {n_parameters}, but got {len(parameters)}."
            )
        return (
            op_name,
            parameters,
            qreg_name1,
            qubit_index1,
            qreg_name2,
            qubit_index2,
            qreg_name3,
            qubit_index3,
        )

    @staticmethod
    def handle_1q1p(line: str) -> tuple[str, list[float], str, int]:
        """Parse a 1-qubit 1-parameter gate line.

        Returns:
            tuple: (op_name, parameters, qreg_name, qubit_index)
        """
        return OpenQASM2_LineParser.handle_1qnp(line, 1)

    @staticmethod
    def handle_1q2p(line: str) -> tuple[str, list[float], str, int]:
        """Parse a 1-qubit 2-parameter gate line.

        Returns:
            tuple: (op_name, parameters, qreg_name, qubit_index)
        """
        return OpenQASM2_LineParser.handle_1qnp(line, 2)

    @staticmethod
    def handle_1q3p(line: str) -> tuple[str, list[float], str, int]:
        """Parse a 1-qubit 3-parameter gate line.

        Returns:
            tuple: (op_name, parameters, qreg_name, qubit_index)
        """
        return OpenQASM2_LineParser.handle_1qnp(line, 3)

    @staticmethod
    def handle_1q4p(line: str) -> tuple[str, list[float], str, int]:
        """Parse a 1-qubit 4-parameter gate line.

        Returns:
            tuple: (op_name, parameters, qreg_name, qubit_index)
        """
        return OpenQASM2_LineParser.handle_1qnp(line, 4)

    @staticmethod
    def handle_2q1p(line: str) -> tuple[str, list[float], str, int, str, int]:
        """Parse a 2-qubit 1-parameter gate line.

        Returns:
            tuple: (op_name, parameters, qreg_name1, qubit_index1, qreg_name2, qubit_index2)
        """
        return OpenQASM2_LineParser.handle_2qnp(line, 1)

    @staticmethod
    def handle_2q2p(line: str) -> tuple[str, list[float], str, int, str, int]:
        """Parse a 2-qubit 2-parameter gate line.

        Returns:
            tuple: (op_name, parameters, qreg_name1, qubit_index1, qreg_name2, qubit_index2)
        """
        return OpenQASM2_LineParser.handle_2qnp(line, 2)

    @staticmethod
    def handle_2q3p(line: str) -> tuple[str, list[float], str, int, str, int]:
        """Parse a 2-qubit 3-parameter gate line.

        Returns:
            tuple: (op_name, parameters, qreg_name1, qubit_index1, qreg_name2, qubit_index2)
        """
        return OpenQASM2_LineParser.handle_2qnp(line, 3)

    @staticmethod
    def handle_2q4p(line: str) -> tuple[str, list[float], str, int, str, int]:
        """Parse a 2-qubit 4-parameter gate line.

        Returns:
            tuple: (op_name, parameters, qreg_name1, qubit_index1, qreg_name2, qubit_index2)
        """
        return OpenQASM2_LineParser.handle_2qnp(line, 4)

    @staticmethod
    def handle_3q1p(line: str) -> tuple[str, list[float], str, int, str, int, str, int]:
        """Parse a 3-qubit 1-parameter gate line.

        Returns:
            tuple: (op_name, parameters, qreg_name1, qubit_index1, qreg_name2, qubit_index2, qreg_name3, qubit_index3)
        """
        return OpenQASM2_LineParser.handle_3qnp(line, 1)

    @staticmethod
    def handle_3q2p(line: str) -> tuple[str, list[float], str, int, str, int, str, int]:
        """Parse a 3-qubit 2-parameter gate line.

        Returns:
            tuple: (op_name, parameters, qreg_name1, qubit_index1, qreg_name2, qubit_index2, qreg_name3, qubit_index3)
        """
        return OpenQASM2_LineParser.handle_3qnp(line, 2)

    @staticmethod
    def handle_3q3p(line: str) -> tuple[str, list[float], str, int, str, int, str, int]:
        """Parse a 3-qubit 3-parameter gate line.

        Returns:
            tuple: (op_name, parameters, qreg_name1, qubit_index1, qreg_name2, qubit_index2, qreg_name3, qubit_index3)
        """
        return OpenQASM2_LineParser.handle_3qnp(line, 3)

    @staticmethod
    def handle_3q4p(line: str) -> tuple[str, list[float], str, int, str, int, str, int]:
        """Parse a 3-qubit 4-parameter gate line.

        Returns:
            tuple: (op_name, parameters, qreg_name1, qubit_index1, qreg_name2, qubit_index2, qreg_name3, qubit_index3)
        """
        return OpenQASM2_LineParser.handle_3qnp(line, 4)

    @staticmethod
    def handle_measure(line: str) -> tuple[str, int, str, int]:
        """Parse a MEASURE statement line.

        Args:
            line: QASM measure statement.

        Returns:
            tuple: (qreg_name, qubit_index, creg_name, creg_index)
        """
        matches = OpenQASM2_LineParser.regexp_measure.match(line)
        qreg_name: str = matches.group(1)  # type: ignore[union-attr]
        qubit_index: int = int(matches.group(2))  # type: ignore[union-attr]
        creg_name: str = matches.group(3)  # type: ignore[union-attr]
        creg_index: int = int(matches.group(4))  # type: ignore[union-attr]
        return qreg_name, qubit_index, creg_name, creg_index

    @staticmethod
    def parse_line(
        line: str,
    ) -> tuple[str | None, tuple[str, int] | list[tuple[str, int]] | None, tuple[str, int] | None, Any]:
        """Parse a single line of OpenQASM 2 code.

        Returns:
            operation: Gate name string or None
            q: Qubit spec — (qreg_name, qubit_index) for 1q, list for multi-q, or None
            c: Classical bit spec — (creg_name, creg_index) or None
            parameter: Parameter list (from handle_parameters) or None
        """
        try:
            q: tuple[str, int] | list[tuple[str, int]] | None = None
            c: tuple[str, int] | None = None
            operation: str | None = None
            parameter: Any = None

            # remove comments and whitespace
            if not line:
                return q, c, operation, parameter
            if line.startswith("//"):
                return q, c, operation, parameter

            # extract operation
            if "(" in line:  # noqa: SIM108
                operation = line.split("(")[0].strip()
            else:
                operation = line.split()[0].strip()

            if operation == "qreg":
                qreg_name, qreg_size = OpenQASM2_LineParser.handle_qreg(line)
                q = (qreg_name, qreg_size)
            elif operation == "creg":
                creg_name, creg_size = OpenQASM2_LineParser.handle_creg(line)
                c = (creg_name, creg_size)
            elif operation == "//":
                pass
            elif (
                operation == "id"
                or operation == "h"
                or operation == "x"
                or operation == "y"
                or operation == "z"
                or operation == "s"
                or operation == "sdg"
                or operation == "sx"
                or operation == "sxdg"
                or operation == "t"
                or operation == "tdg"
            ):
                operation, qreg_name, qubit_index = OpenQASM2_LineParser.handle_1q(line)
                q = (qreg_name, qubit_index)
            elif operation in ("cx", "cy", "cz", "swap", "ch"):
                (
                    operation,
                    qreg_name1,
                    qubit_index1,
                    qreg_name2,
                    qubit_index2,
                ) = OpenQASM2_LineParser.handle_2q(line)
                q = [(qreg_name1, qubit_index1), (qreg_name2, qubit_index2)]
            elif operation in ("ccx", "cswap"):
                (
                    operation,
                    qreg_name1,
                    qubit_index1,
                    qreg_name2,
                    qubit_index2,
                    qreg_name3,
                    qubit_index3,
                ) = OpenQASM2_LineParser.handle_3q(line)
                q = [
                    (qreg_name1, qubit_index1),
                    (qreg_name2, qubit_index2),
                    (qreg_name3, qubit_index3),
                ]
            elif operation == "c3x":
                (
                    operation,
                    qreg_name1,
                    qubit_index1,
                    qreg_name2,
                    qubit_index2,
                    qreg_name3,
                    qubit_index3,
                    qreg_name4,
                    qubit_index4,
                ) = OpenQASM2_LineParser.handle_4q(line)
                q = [
                    (qreg_name1, qubit_index1),
                    (qreg_name2, qubit_index2),
                    (qreg_name3, qubit_index3),
                    (qreg_name4, qubit_index4),
                ]
            elif operation in ("rx", "ry", "rz", "u1"):
                operation, parameter, qreg_name, qubit_index = OpenQASM2_LineParser.handle_1q1p(line)  # type: ignore[assignment]
                q = (qreg_name, qubit_index)
            elif operation == "u2":
                operation, parameter, qreg_name, qubit_index = OpenQASM2_LineParser.handle_1q2p(line)  # type: ignore[assignment]
                q = (qreg_name, qubit_index)
            elif operation == "u0":
                raise NotImplementedError(f"This line of OpenQASM 2 has not been supported yet: {line}.")
            elif operation in ("u3", "u"):
                operation, parameter, qreg_name, qubit_index = OpenQASM2_LineParser.handle_1q3p(line)  # type: ignore[assignment]
                q = (qreg_name, qubit_index)
            elif operation in ("rxx", "ryy", "rzz", "cu1", "crx", "cry", "crz"):
                (
                    operation,
                    parameter,
                    qreg_name1,
                    qubit_index1,
                    qreg_name2,
                    qubit_index2,
                ) = OpenQASM2_LineParser.handle_2q1p(line)  # type: ignore[assignment]
                q = [(qreg_name1, qubit_index1), (qreg_name2, qubit_index2)]
            elif operation == "cu3":
                (
                    operation,
                    parameter,
                    qreg_name1,
                    qubit_index1,
                    qreg_name2,
                    qubit_index2,
                ) = OpenQASM2_LineParser.handle_2q3p(line)  # type: ignore[assignment]
                q = [(qreg_name1, qubit_index1), (qreg_name2, qubit_index2)]
            elif operation == "barrier":
                pass
            elif operation == "measure":
                qreg_name, qubit_index, creg_name, creg_index = OpenQASM2_LineParser.handle_measure(line)
                operation = "measure"  # type: ignore[assignment]
                q = (qreg_name, qubit_index)
                c = (creg_name, creg_index)
            else:
                raise NotImplementedError(f"This line of OpenQASM 2 has not been supported yet: {line}.")

            return operation, q, c, parameter
        except AttributeError as e:
            raise RuntimeError(f"Error when parsing the line: {line}") from e


if __name__ == "__main__":
    print("----------qreg test------------")
    matches = OpenQASM2_LineParser.regexp_qreg.match("qreg q [ 12 ]")
    print(matches.group(0))
    print(matches.group(1))
    print(matches.group(2))

    print("----------creg test------------")
    matches = OpenQASM2_LineParser.regexp_creg.match("creg c [ 12 ]")
    print(matches.group(0))
    print(matches.group(1))
    print(matches.group(2))

    print("----------op 1q test-----------")
    matches = OpenQASM2_LineParser.regexp_1q.match("h q[0]")
    print(matches.group(0))
    print(matches.group(1))
    print(matches.group(2))
    print(matches.group(3))

    print("----------op 2q test-----------")
    matches = OpenQASM2_LineParser.regexp_2q.match("cx q[0],q[12]")
    print(matches.group(0))
    print(matches.group(1))
    print(matches.group(2))
    print(matches.group(3))
    print(matches.group(4))
    print(matches.group(5))

    print("----------op 3q test-----------")
    matches = OpenQASM2_LineParser.regexp_3q.match("ccx q[0],q[12],q[11]")
    print(matches.group(0))
    for i in range(1, 8):
        print(matches.group(i))

    print("----------op 1q1p test---------")
    matches = OpenQASM2_LineParser.regexp_1qnp.match("ry (-0.5*pi) q[0]")
    print(matches.group(0))
    print(matches.group(1))
    print(matches.group(2))
    print(matches.group(3))
    print(matches.group(4))

    results = OpenQASM2_LineParser.handle_1q1p("ry (-0.5*pi) q[0]")
    print(results)

    print("----------op 1q2p test---------")
    matches = OpenQASM2_LineParser.regexp_1qnp.match("u2 (-0.5*pi, 11) q[0]")
    print(matches.group(0))
    print(matches.group(1))
    print(matches.group(2))
    print(matches.group(3))
    print(matches.group(4))

    results = OpenQASM2_LineParser.handle_1q2p("u2 (-0.5*pi, 11) q[0]")
    print(results)

    print("----------op 1q3p test---------")
    matches = OpenQASM2_LineParser.regexp_1qnp.match("u3 (-0.5*pi, 11, 888.1111) q[0]")
    print(matches.group(0))
    print(matches.group(1))
    print(matches.group(2))
    print(matches.group(3))
    print(matches.group(4))

    results = OpenQASM2_LineParser.handle_1q3p("u3 (-0.5*pi, 11, 888.1111) q[0]")
    print(results)

    print("----------op 2q1p test---------")
    matches = OpenQASM2_LineParser.regexp_2qnp.match("rxx (-0.5*pi) q[0], q[108]")
    print(matches.group(0))
    print(matches.group(1))
    print(matches.group(2))
    print(matches.group(3))
    print(matches.group(4))

    results = OpenQASM2_LineParser.handle_2q1p("rxx (-0.5*pi) q[0], q[108]")
    print(results)

    results = OpenQASM2_LineParser.handle_2q1p("rzz(0.8342297582553907) q[2],q[0] ")
    print(results)

    print("----------measure test---------")
    matches = OpenQASM2_LineParser.regexp_measure.match("measure q[0] -> c[18]")
    print(matches.group(0))
    print(matches.group(1))
    print(matches.group(2))
    print(matches.group(3))
    print(matches.group(4))
