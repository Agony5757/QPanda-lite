"""OriginIR line parser module.

This module provides regex-based parsing for individual OriginIR lines,
supporting 1-3 qubit gates, parameterized gates, dagger flags, and control qubits.

Key exports:
    OriginIR_LineParser: Parser class for individual OriginIR lines.
"""

__all__ = ["OriginIR_LineParser"]
import re


class OriginIR_LineParser:
    """Parser for individual OriginIR lines.

    Provides regex-based parsing for OriginIR gate statements with support for
    1-3 qubit gates, parameterized gates, dagger flags, and control qubits.
    """

    opname = r"([A-Za-z][A-Za-z\d]*)"
    blank = r" *"
    qid = r"q *\[ *(\d+) *\]"
    cid = r"c *\[ *(\d+) *\]"
    comma = r","
    lbracket = r"\("
    rbracket = r"\)"
    parameter = r"([-+]?\d+(\.\d*)?([eE][-+]?\d+)?)"

    # extended originir syntax
    dagger_flag = blank + "(dagger *)?"
    control_qubits = blank + (
        r"(controlled_by"
        + blank
        + lbracket
        + f"({blank}{qid}{blank}{comma})*{blank}{qid}{blank}"
        + rbracket
        + blank
        + ")?"
    )

    regexp_1q_str = "^" + opname + blank + qid + dagger_flag + control_qubits + "$"
    regexp_2q_str = "^" + opname + blank + qid + blank + comma + blank + qid + dagger_flag + control_qubits + "$"
    regexp_3q_str = (
        "^"
        + opname
        + blank
        + qid
        + blank
        + comma
        + blank
        + qid
        + blank
        + comma
        + blank
        + qid
        + dagger_flag
        + control_qubits
        + "$"
    )
    regexp_1q1p_str = (
        "^"
        + opname
        + blank
        + qid
        + blank
        + comma
        + blank
        + lbracket
        + blank
        + parameter
        + blank
        + rbracket
        + dagger_flag
        + control_qubits
        + "$"
    )
    regexp_1q2p_str = (
        "^"
        + opname
        + blank
        + qid
        + blank
        + comma
        + blank
        + lbracket
        + blank
        + parameter
        + blank
        + comma
        + blank
        + parameter
        + blank
        + rbracket
        + dagger_flag
        + control_qubits
        + "$"
    )
    regexp_1q3p_str = (
        "^"
        + opname
        + blank
        + qid
        + blank
        + comma
        + blank
        + lbracket
        + blank
        + parameter
        + blank
        + comma
        + blank
        + parameter
        + blank
        + comma
        + blank
        + parameter
        + blank
        + rbracket
        + dagger_flag
        + control_qubits
        + "$"
    )
    regexp_1q4p_str = (
        "^"
        + opname
        + blank
        + qid
        + blank
        + comma
        + blank
        + lbracket
        + blank
        + parameter
        + blank
        + comma
        + blank
        + parameter
        + blank
        + comma
        + blank
        + parameter
        + blank
        + comma
        + blank
        + parameter
        + blank
        + rbracket
        + dagger_flag
        + control_qubits
        + "$"
    )
    regexp_2q1p_str = (
        "^"
        + opname
        + blank
        + qid
        + blank
        + comma
        + blank
        + qid
        + blank
        + comma
        + blank
        + lbracket
        + blank
        + parameter
        + blank
        + rbracket
        + dagger_flag
        + control_qubits
        + "$"
    )

    regexp_2q3p_str = (
        "^"
        + opname
        + blank
        + qid
        + blank
        + comma
        + blank
        + qid
        + blank
        + comma
        + blank
        + lbracket
        + blank
        + parameter
        + blank  # 1
        + comma
        + blank
        + parameter
        + blank  # 2
        + comma
        + blank
        + parameter
        + blank  # 3
        + rbracket
        + dagger_flag
        + control_qubits
        + "$"
    )

    regexp_2q15p_str = (
        "^"
        + opname
        + blank
        + qid
        + blank
        + comma
        + blank
        + qid
        + blank
        + comma
        + blank
        + lbracket
        + blank
        + parameter
        + blank  # 1
        + comma
        + blank
        + parameter
        + blank  # 1
        + comma
        + blank
        + parameter
        + blank  # 3
        + comma
        + blank
        + parameter
        + blank  # 4
        + comma
        + blank
        + parameter
        + blank  # 5
        + comma
        + blank
        + parameter
        + blank  # 6
        + comma
        + blank
        + parameter
        + blank  # 7
        + comma
        + blank
        + parameter
        + blank  # 8
        + comma
        + blank
        + parameter
        + blank  # 9
        + comma
        + blank
        + parameter
        + blank  # 10
        + comma
        + blank
        + parameter
        + blank  # 11
        + comma
        + blank
        + parameter
        + blank  # 12
        + comma
        + blank
        + parameter
        + blank  # 13
        + comma
        + blank
        + parameter
        + blank  # 14
        + comma
        + blank
        + parameter
        + blank  # 15
        + rbracket
        + dagger_flag
        + control_qubits
        + "$"
    )

    regexp_measure_str = "^" + r"MEASURE" + blank + qid + blank + comma + blank + cid + "$"
    regexp_barrier_str = r"^BARRIER" + f"(({blank}{qid}{blank}{comma})*{blank}{qid}{blank})" + "$"
    regexp_control_str = r"^(CONTROL|ENDCONTROL)" + f"(({blank}{qid}{blank}{comma})*{blank}{qid}{blank})" + "$"

    # DEF block patterns: DEF name(q[0], q[1], ...) (param1, param2, ...)
    # Parameter names can be alphanumeric
    param_name = r"[A-Za-z_][A-Za-z0-9_]*"
    qid_list = f"({blank}{qid}{blank}{comma})*{blank}{qid}{blank}"
    param_list = f"({blank}{param_name}{blank}{comma})*{blank}{param_name}{blank}"
    regexp_def_str = (
        "^DEF"
        + blank
        + r"([A-Za-z_][A-Za-z0-9_]*)"
        + blank  # circuit name
        + r"\("
        + blank
        + qid_list
        + blank
        + r"\)"
        + "(?:"
        + blank
        + r"\("
        + blank
        + param_list
        + blank
        + r"\)"
        + ")?"
        + "$"
    )
    regexp_enddef_str = "^ENDDEF$"

    regexp_1q = re.compile(regexp_1q_str)
    regexp_2q = re.compile(regexp_2q_str)
    regexp_3q = re.compile(regexp_3q_str)
    regexp_1q1p = re.compile(regexp_1q1p_str)
    regexp_1q2p = re.compile(regexp_1q2p_str)
    regexp_1q3p = re.compile(regexp_1q3p_str)
    regexp_1q4p = re.compile(regexp_1q4p_str)
    regexp_2q1p = re.compile(regexp_2q1p_str)
    regexp_2q3p = re.compile(regexp_2q3p_str)
    regexp_2q15p = re.compile(regexp_2q15p_str)
    regexp_meas = re.compile(regexp_measure_str)
    regexp_barrier = re.compile(regexp_barrier_str)
    regexp_control = re.compile(regexp_control_str)
    regexp_def = re.compile(regexp_def_str)
    regexp_enddef = re.compile(regexp_enddef_str)
    regexp_qid = re.compile(qid)

    def __init__(self):
        pass

    @staticmethod
    def handle_1q(line):
        """Parse a 1-qubit gate line.

        Returns:
            tuple: (operation, qubit, dagger_flag, control_qubits)
        """
        matches = OriginIR_LineParser.regexp_1q.match(line)
        operation = matches.group(1)
        q = int(matches.group(2))
        dagger_flag = True if matches.group(3) is not None else False
        control_qubits = []
        if matches.group(4) is not None:
            control_qubits = [int(q) for q in OriginIR_LineParser.regexp_qid.findall(matches.group(4))]

        return operation, q, dagger_flag, control_qubits

    @staticmethod
    def handle_2q(line):
        """Parse a 2-qubit gate line.

        Returns:
            tuple: (operation, [q1, q2], dagger_flag, control_qubits)
        """
        matches = OriginIR_LineParser.regexp_2q.match(line)
        operation = matches.group(1)
        q1 = int(matches.group(2))
        q2 = int(matches.group(3))
        dagger_flag = True if matches.group(4) is not None else False
        control_qubits = []
        if matches.group(5) is not None:
            control_qubits = [int(q) for q in OriginIR_LineParser.regexp_qid.findall(matches.group(5))]

        return operation, [q1, q2], dagger_flag, control_qubits

    @staticmethod
    def handle_3q(line):
        """Parse a 3-qubit gate line.

        Returns:
            tuple: (operation, [q1, q2, q3], dagger_flag, control_qubits)
        """
        matches = OriginIR_LineParser.regexp_3q.match(line)
        operation = matches.group(1)
        q1 = int(matches.group(2))
        q2 = int(matches.group(3))
        q3 = int(matches.group(4))
        dagger_flag = True if matches.group(5) is not None else False
        control_qubits = []
        if matches.group(6) is not None:
            control_qubits = [int(q) for q in OriginIR_LineParser.regexp_qid.findall(matches.group(6))]

        return operation, [q1, q2, q3], dagger_flag, control_qubits

    @staticmethod
    def handle_1q1p(line):
        """Parse a 1-qubit 1-parameter gate line.

        Returns:
            tuple: (operation, qubit, parameter, dagger_flag, control_qubits)
        """
        matches = OriginIR_LineParser.regexp_1q1p.match(line)
        operation = matches.group(1)
        q = int(matches.group(2))
        parameter = float(matches.group(3))
        dagger_flag = True if matches.group(6) is not None else False
        control_qubits = []
        if matches.group(7) is not None:
            control_qubits = [int(q) for q in OriginIR_LineParser.regexp_qid.findall(matches.group(7))]

        return operation, q, parameter, dagger_flag, control_qubits

    @staticmethod
    def handle_1q2p(line):
        """Parse a 1-qubit 2-parameter gate line.

        Returns:
            tuple: (operation, qubit, [p1, p2], dagger_flag, control_qubits)
        """
        matches = OriginIR_LineParser.regexp_1q2p.match(line)
        operation = matches.group(1)
        q = int(matches.group(2))
        parameter1 = float(matches.group(3))
        parameter2 = float(matches.group(6))
        dagger_flag = True if matches.group(9) is not None else False
        control_qubits = []
        if matches.group(10) is not None:
            control_qubits = [int(q) for q in OriginIR_LineParser.regexp_qid.findall(matches.group(10))]

        return operation, q, [parameter1, parameter2], dagger_flag, control_qubits

    @staticmethod
    def handle_1q3p(line):
        """Parse a 1-qubit 3-parameter gate line.

        Returns:
            tuple: (operation, qubit, [p1, p2, p3], dagger_flag, control_qubits)
        """
        matches = OriginIR_LineParser.regexp_1q3p.match(line)
        operation = matches.group(1)
        q = int(matches.group(2))
        parameter1 = float(matches.group(3))
        parameter2 = float(matches.group(6))
        parameter3 = float(matches.group(9))
        dagger_flag = True if matches.group(12) is not None else False
        control_qubits = []
        if matches.group(13) is not None:
            control_qubits = [int(q) for q in OriginIR_LineParser.regexp_qid.findall(matches.group(13))]

        return operation, q, [parameter1, parameter2, parameter3], dagger_flag, control_qubits

    @staticmethod
    def handle_1q4p(line):
        """Parse a 1-qubit 4-parameter gate line.

        Returns:
            tuple: (operation, qubit, [p1, p2, p3, p4], dagger_flag, control_qubits)
        """
        matches = OriginIR_LineParser.regexp_1q4p.match(line)
        operation = matches.group(1)
        q = int(matches.group(2))
        parameter1 = float(matches.group(3))
        parameter2 = float(matches.group(6))
        parameter3 = float(matches.group(9))
        parameter4 = float(matches.group(12))
        dagger_flag = True if matches.group(15) is not None else False
        control_qubits = []
        if matches.group(16) is not None:
            control_qubits = [int(q) for q in OriginIR_LineParser.regexp_qid.findall(matches.group(16))]

        return operation, q, [parameter1, parameter2, parameter3, parameter4], dagger_flag, control_qubits

    @staticmethod
    def handle_2q1p(line):
        """Parse a 2-qubit 1-parameter gate line.

        Returns:
            tuple: (operation, [q1, q2], parameter, dagger_flag, control_qubits)
        """
        matches = OriginIR_LineParser.regexp_2q1p.match(line)
        operation = matches.group(1)
        q1 = int(matches.group(2))
        q2 = int(matches.group(3))
        parameter1 = float(matches.group(4))
        dagger_flag = True if matches.group(7) is not None else False
        control_qubits = []
        if matches.group(8) is not None:
            control_qubits = [int(q) for q in OriginIR_LineParser.regexp_qid.findall(matches.group(8))]

        return operation, [q1, q2], parameter1, dagger_flag, control_qubits

    @staticmethod
    def handle_2q3p(line):
        """Parse a 2-qubit 3-parameter gate line.

        Returns:
            tuple: (operation, [q1, q2], [p1, p2, p3], dagger_flag, control_qubits)
        """
        matches = OriginIR_LineParser.regexp_2q3p.match(line)
        operation = matches.group(1)
        q1 = int(matches.group(2))
        q2 = int(matches.group(3))
        parameter1 = float(matches.group(4))
        parameter2 = float(matches.group(7))
        parameter3 = float(matches.group(10))
        dagger_flag = True if matches.group(13) is not None else False
        control_qubits = []
        if matches.group(14) is not None:
            control_qubits = [int(q) for q in OriginIR_LineParser.regexp_qid.findall(matches.group(14))]

        return operation, [q1, q2], [parameter1, parameter2, parameter3], dagger_flag, control_qubits

    @staticmethod
    def handle_2q15p(line):
        """Parse a 2-qubit 15-parameter gate line.

        Returns:
            tuple: (operation, [q1, q2], parameters, dagger_flag, control_qubits)
        """
        matches = OriginIR_LineParser.regexp_2q15p.match(line)
        operation = matches.group(1)
        q1 = int(matches.group(2))
        q2 = int(matches.group(3))
        parameters = []
        for i in range(15):
            parameters.append(float(matches.group(4 + i * 3)))

        dagger_flag = True if matches.group(49) is not None else False
        control_qubits = []
        if matches.group(50) is not None:
            control_qubits = [int(q) for q in OriginIR_LineParser.regexp_qid.findall(matches.group(50))]

        return operation, [q1, q2], parameters, dagger_flag, control_qubits

    @staticmethod
    def handle_measure(line):
        """Parse a MEASURE statement line.

        Returns:
            tuple: (qubit, cbit)
        """
        matches = OriginIR_LineParser.regexp_meas.match(line)
        q = int(matches.group(1))
        c = int(matches.group(2))
        return q, c

    @staticmethod
    def handle_barrier(line):
        """Parse a BARRIER statement line.

        Returns:
            tuple: ("BARRIER", qubit_indices)
        """
        matches = OriginIR_LineParser.regexp_barrier.match(line)
        # Extract individual qubit patterns
        qubits = OriginIR_LineParser.regexp_qid.findall(line)
        # Extract only the numeric part of each qubit pattern
        qubit_indices = [int(q) for q in qubits]
        return "BARRIER", qubit_indices

    @staticmethod
    def handle_control(line):
        """
        Parse a line to extract control qubits information and the type of control operation.

        This function analyzes a given line of text to identify and extract information about
        control qubits and determine whether the line represents the beginning of a control operation
        (CONTROL) or the end of a control operation (ENDCONTROL) in OriginIR language.

        Parameters
        ----------
        line : str
            The line of text to be parsed for control qubit information.

        Returns
        -------
        tuple of (str, list)
            A tuple where the first element is a string indicating the control operation type
            ("CONTROL" or "ENDCONTROL") and the second element is a list of integers representing
            the parsed control qubits.

        Notes
        -----
        The function relies on the `regexp_control` regular expression to match the CONTROL or
        ENDCONTROL patterns in OriginIR language. This regular expression should be predefined
        and properly constructed to capture the necessary information from the line.
        """
        matches = OriginIR_LineParser.regexp_control.match(line)
        # Extracting the operation type and multiple control qubits
        operation_type = matches.group(1)
        qubits = OriginIR_LineParser.regexp_qid.findall(matches.group(2))
        controls = [int(ctrl) for ctrl in qubits]
        return operation_type, controls

    @staticmethod
    def handle_dagger(line):
        """
        Parse a line to identify DAGGER or ENDDAGGER commands in OriginIR.

        This function checks a line of text to determine if it contains a command
        related to the start or end of a DAGGER operation block in the OriginIR language.

        Parameters
        ----------
        line : str
            The line of text to be parsed.

        Returns
        -------
        str or None
            Returns "DAGGER" if the line is a DAGGER command, "ENDDAGGER" if it's an ENDDAGGER command,
            or None if neither command is present.

        Notes
        -----
        The DAGGER command in OriginIR denotes the start of a block where the operations are to be
        applied in reverse order with conjugate transposition (dagger operation). The ENDDAGGER command
        signifies the end of such a block.
        """
        if "ENDDAGGER" in line:
            return "ENDDAGGER"
        elif "DAGGER" in line:
            return "DAGGER"
        else:
            return None

    @staticmethod
    def handle_def(line):
        """Parse a DEF block header line.

        Format: DEF name(q[0], q[1], ...) (param1, param2, ...)

        Returns:
            tuple: (operation="DEF", qubits_list, params_list, name)
        """
        matches = OriginIR_LineParser.regexp_def.match(line)
        if not matches:
            raise ValueError(f"Invalid DEF line: {line}")

        name = matches.group(1)

        # Extract qubit indices from the first parentheses group
        qubits = []
        # Find all q[N] patterns
        qid_matches = OriginIR_LineParser.regexp_qid.findall(line)
        qubits = [int(q) for q in qid_matches]

        # Extract parameter names from second parentheses (if present)
        params = []
        # Look for the second parentheses group containing parameter names
        import re as re_module

        param_pattern = r"\(\s*([A-Za-z_][A-Za-z0-9_\s,]*)\s*\)\s*$"
        param_match = re_module.search(param_pattern, line)
        if param_match:
            param_str = param_match.group(1)
            # Split by comma and strip
            params = [p.strip() for p in param_str.split(",") if p.strip()]

        return ("DEF", qubits, params, name)

    @staticmethod
    def parse_line(line):
        """Parse a single OriginIR line and return operation details.

        Args:
            line: Single line of OriginIR code.

        Returns:
            tuple: (operation, qubits, cbit, parameter, dagger_flag, control_qubits)
        """

        try:
            q = None
            c = None
            operation = None
            parameter = None
            dagger_flag = None
            control_qubits = None

            # remove the empty line
            if not line:
                return q, c, operation, parameter, dagger_flag, control_qubits

            line = line.strip()
            # extract operation
            operation = line.split()[0]

            if operation == "QINIT":
                q = int(line.strip().split()[1])
                operation = "QINIT"
            elif operation == "CREG":
                c = int(line.strip().split()[1])
                operation = "CREG"
            # 1-qubit gates
            elif (
                operation == "H"
                or operation == "X"
                or operation == "Y"
                or operation == "Z"
                or operation == "S"
                or operation == "SX"
                or operation == "T"
                or operation == "I"
            ):
                operation, q, dagger_flag, control_qubits = OriginIR_LineParser.handle_1q(line)
            # 2-qubit gates
            elif operation == "CZ" or operation == "CNOT" or operation == "SWAP" or operation == "ISWAP":
                operation, q, dagger_flag, control_qubits = OriginIR_LineParser.handle_2q(line)
            # 3-qubit gates
            elif operation == "TOFFOLI" or operation == "CSWAP":
                operation, q, dagger_flag, control_qubits = OriginIR_LineParser.handle_3q(line)
            # 1q1p gates
            elif (
                operation == "RX"
                or operation == "RY"
                or operation == "RZ"
                or operation == "U1"
                or operation == "RPhi90"
                or operation == "RPhi180"
                or operation == "Depolarizing"
                or operation == "BitFlip"
                or operation == "AmplitudeDamping"
                or operation == "PhaseFlip"
            ):
                operation, q, parameter, dagger_flag, control_qubits = OriginIR_LineParser.handle_1q1p(line)
            # 1q2p gates
            elif operation == "RPhi" or operation == "U2":
                operation, q, parameter, dagger_flag, control_qubits = OriginIR_LineParser.handle_1q2p(line)
            # 1q3p gates
            elif operation == "U3" or operation == "PauliError1Q":
                operation, q, parameter, dagger_flag, control_qubits = OriginIR_LineParser.handle_1q3p(line)
            # 2q1p gates
            elif (
                operation == "XX"
                or operation == "YY"
                or operation == "ZZ"
                or operation == "XY"
                or operation == "TwoQubitDepolarizing"
            ):
                operation, q, parameter, dagger_flag, control_qubits = OriginIR_LineParser.handle_2q1p(line)
            # 2q3p gates
            elif operation == "PHASE2Q":
                operation, q, parameter, dagger_flag, control_qubits = OriginIR_LineParser.handle_2q3p(line)
            # 2q15p gates
            elif operation == "UU15" or operation == "PauliError2Q":
                operation, q, parameter, dagger_flag, control_qubits = OriginIR_LineParser.handle_2q15p(line)
            elif operation == "BARRIER":
                operation = "BARRIER"
                operation, q = OriginIR_LineParser.handle_barrier(line)
                dagger_flag = False
                control_qubits = []
            elif operation == "MEASURE":
                operation = "MEASURE"
                q, c = OriginIR_LineParser.handle_measure(line)
            elif operation == "CONTROL":
                operation, q = OriginIR_LineParser.handle_control(line)
            elif operation == "ENDCONTROL":
                operation = "ENDCONTROL"
            elif operation == "DAGGER":
                operation = OriginIR_LineParser.handle_dagger(line)
            elif operation == "ENDDAGGER":
                operation = OriginIR_LineParser.handle_dagger(line)
            elif operation == "DEF":
                # DEF block header - return special operation
                operation, q, parameter = OriginIR_LineParser.handle_def(line)
                dagger_flag = False
                control_qubits = []
            elif operation == "ENDDEF":
                operation = "ENDDEF"
                dagger_flag = False
                control_qubits = []
            else:
                # print("something wrong")
                raise NotImplementedError(f"A invalid line: {line}.")

            return operation, q, c, parameter, dagger_flag, control_qubits
        except AttributeError as e:
            raise RuntimeError(f"Error when parsing the line: {line}")


if __name__ == "__main__":
    print(OriginIR_LineParser.regexp_1q_str)
    matches = OriginIR_LineParser.regexp_1q.match("H  q [ 45 ]")
    print(matches.group(0))
    print(matches.group(1))  # H
    print(matches.group(2))  # 45

    print(OriginIR_LineParser.regexp_1q_str)
    matches = OriginIR_LineParser.regexp_1q.match("H  q [ 45 ] dagger   controlled_by (q[0], q[1], q[2])")
    print(matches.group(0))
    print(matches.group(1))  # H
    print(matches.group(2))  # 45
    print(matches.group(3))  # dagger
    print(matches.group(4))  # controlled_by (q[0], q[1], q[2])
    print(OriginIR_LineParser.regexp_1q1p_str)

    matches = OriginIR_LineParser.regexp_1q1p.match("RX  q [ 45 ] , ( 1.1e+3) dagger")
    print(matches.group(0))
    print(matches.group(1))  # RX
    print(matches.group(2))  # 45
    print(matches.group(3))  # 1.1e+3
    print(matches.group(4))  #
    print(matches.group(5))  #
    print(matches.group(6))  # dagger
    print(matches.group(7))  # None

    print(OriginIR_LineParser.regexp_1q2p_str)
    matches = OriginIR_LineParser.regexp_1q2p.match("Rphi q[ 45 ], ( -1.1 , 1.2e-5) dagger")
    print(matches.group(0))
    print(matches.group(1))  # Rphi
    print(matches.group(2))  # 45
    print(matches.group(3))  # -1.1
    print(matches.group(4))  #
    print(matches.group(5))  #
    print(matches.group(6))  # 1.2e-5
    print(matches.group(7))  #
    print(matches.group(8))  #
    print(matches.group(9))  # dagger

    print(OriginIR_LineParser.regexp_1q3p_str)
    matches = OriginIR_LineParser.regexp_1q3p.match("U3 q[ 45 ], ( -1.1 , 1.2e-5 , 0.11) dagger")
    print(matches.group(0))
    print(matches.group(1))  # U3
    print(matches.group(2))  # 45
    print(matches.group(3))  # -1.1
    print(matches.group(4))  #
    print(matches.group(5))  #
    print(matches.group(6))  # 1.2e-5
    print(matches.group(7))  #
    print(matches.group(8))  #
    print(matches.group(9))  # 0.11
    print(matches.group(10))  #
    print(matches.group(11))  #
    print(matches.group(12))  # dagger

    print(OriginIR_LineParser.regexp_1q4p_str)
    matches = OriginIR_LineParser.regexp_1q4p.match("U4 q[ 45 ], ( -1.1 , 1.2e-5, 0 , 0.11)   dagger")
    print(matches.group(0))
    print(matches.group(1))  # U4
    print(matches.group(2))  # 45
    print(matches.group(3))  # -1.1
    print(matches.group(4))  #
    print(matches.group(5))  #
    print(matches.group(6))  # 1.2e-5
    print(matches.group(7))  #
    print(matches.group(8))  #
    print(matches.group(9))  # 0
    print(matches.group(10))  #
    print(matches.group(11))  #
    print(matches.group(12))  # 0.11
    print(matches.group(13))  #
    print(matches.group(14))  #
    print(matches.group(15))  # dagger

    print(OriginIR_LineParser.regexp_2q_str)
    matches = OriginIR_LineParser.regexp_2q.match("CNOT q[ 45], q[46 ]")
    print(matches.group(0))
    print(matches.group(1))  # CNOT
    print(matches.group(2))  # 45
    print(matches.group(3))  # 46

    print(OriginIR_LineParser.regexp_3q_str)
    matches = OriginIR_LineParser.regexp_3q.match("TOFFOLI q[ 45], q[46 ], q [ 42 ]")
    print(matches.group(0))
    print(matches.group(1))  # TOFFOLI
    print(matches.group(2))  # 45
    print(matches.group(3))  # 46
    print(matches.group(4))  # 42

    print(OriginIR_LineParser.regexp_2q1p_str)
    matches = OriginIR_LineParser.regexp_2q1p.match("XY q[ 45], q[46 ], ( -1.1 )  dagger")
    print(matches.group(0))
    print(matches.group(1))  # XY
    print(matches.group(2))  # 45
    print(matches.group(3))  # 46
    print(matches.group(4))  # -1.1
    print(matches.group(5))  #
    print(matches.group(6))  #
    print(matches.group(7))  # dagger

    print(OriginIR_LineParser.regexp_2q3p_str)
    matches = OriginIR_LineParser.regexp_2q3p.match(
        "PHASE2Q q[ 45], q[46 ], ( -1.1, 1.5, 8 ) controlled_by (q[0], q[1], q[2])"
    )
    print(matches.group(0))
    print(matches.group(1))  # XY
    print(matches.group(2))  # 45
    print(matches.group(3))  # 46
    print(matches.group(4))  # -1.1
    print(matches.group(5))
    print(matches.group(6))
    print(matches.group(7))  # 1.5
    print(matches.group(8))
    print(matches.group(9))
    print(matches.group(10))  # 8
    print(matches.group(11))  #
    print(matches.group(12))  #
    print(matches.group(13))  # dagger (None)
    print(matches.group(14))  # controlled_by (q[0], q[1], q[2])

    print(OriginIR_LineParser.regexp_2q15p_str)
    matches = OriginIR_LineParser.regexp_2q15p.match(
        "UU15 q[ 45], q[46 ], ( 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15 ) dagger"
    )
    print(matches.group(0))
    print(matches.group(1))  # UU15
    print(matches.group(2))  # 45
    print(matches.group(3))  # 46
    print(matches.group(4))  # 1
    print(matches.group(7))  # 2
    print(matches.group(10))  # 3
    print(matches.group(13))  # 4
    print(matches.group(16))  # 5
    print(matches.group(19))  # 6
    print(matches.group(22))  # 7
    print(matches.group(25))  # 8
    print(matches.group(28))  # 9
    print(matches.group(31))  # 10
    print(matches.group(34))  # 11
    print(matches.group(37))  # 12
    print(matches.group(40))  # 13
    print(matches.group(43))  # 14
    print(matches.group(46))  # 15
    print(matches.group(49))  # dagger
    print(matches.group(50))  # None

    print(OriginIR_LineParser.regexp_measure_str)
    matches = OriginIR_LineParser.regexp_meas.match("MEASURE  q [ 45 ] ,  c[ 11 ]")
    print(matches.group(0))
    print(matches.group(1))  # 45
    print(matches.group(2))  # 11

    print(OriginIR_LineParser.regexp_control_str)
    matches = OriginIR_LineParser.regexp_control.match("CONTROL   q [ 45] , q[ 46]  ,  q [  999 ]")
    print(matches.group(0))
    print(matches.group(1))  # CONTROL
    print(matches.group(2))  #    q [ 45] , q[ 46]  ,  q [  999 ]
    all_matches = OriginIR_LineParser.regexp_qid.findall(matches.group(2))
    print(all_matches)  # ['45', '46', '999']
