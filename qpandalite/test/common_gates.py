import numpy as np

# Some commonly-used quantum gates

# Identity
I_Gate = np.array([[1, 0],
              [0, 1]], dtype=complex)

# Pauli-X (NOT)
X_Gate = np.array([[0, 1],
              [1, 0]], dtype=complex)

# Pauli-Y
Y_Gate = np.array([[0, -1j],
              [1j, 0]], dtype=complex)

# Pauli-Z (Phase)
Z_Gate = np.array([[1, 0],
              [0, -1]], dtype=complex)

# Hadamard
H_Gate = (1/np.sqrt(2)) * np.array([[1, 1],
                               [1, -1]], dtype=complex)

# Phase (S)
S_Gate = np.array([[1, 0],
              [0, 1j]], dtype=complex)

# Pi/8 (T)
T_Gate = np.array([[1, 0],
              [0, np.exp(1j * np.pi / 4)]], dtype=complex)

# Controlled NOT (CNOT)
# Note: This is a 2-qubit gate represented in a 4x4 matrix
CNOT_Gate = np.array([[1, 0, 0, 0],
                 [0, 1, 0, 0],
                 [0, 0, 0, 1],
                 [0, 0, 1, 0]], dtype=complex)

# Controlled Z-Gate (CZ)
# Note: This is a 2-qubit gate represented in a 4x4 matrix
CZ_Gate = np.array([[1, 0, 0, 0],
                 [0, 1, 0, 0],
                 [0, 0, 1, 0],
                 [0, 0, 0, -1]], dtype=complex)
# Controlled NOT (CNOT)
# Note: This is a 2-qubit gate represented in a 4x4 matrix
SWAP_Gate = np.array([[1, 0, 0, 0],
                 [0, 0, 1, 0],
                 [0, 1, 0, 0],
                 [0, 0, 0, 1]], dtype=complex)

# The Controlled-SWAP (Fredkin) gate matrix
CSWAP_Gate = np.array([[1, 0, 0, 0, 0, 0, 0, 0],
                        [0, 1, 0, 0, 0, 0, 0, 0],
                        [0, 0, 1, 0, 0, 0, 0, 0],
                        [0, 0, 0, 1, 0, 0, 0, 0],
                        [0, 0, 0, 0, 1, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 1, 0],
                        [0, 0, 0, 0, 0, 1, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 1]], dtype=complex)

def RX_Gate(theta):
    return np.array([[np.cos(theta/2), -1j*np.sin(theta/2)],
                     [-1j*np.sin(theta/2), np.cos(theta/2)]], dtype=complex)

def RY_Gate(theta):
    return np.array([[np.cos(theta/2), -np.sin(theta/2)],
                     [np.sin(theta/2), np.cos(theta/2)]], dtype=complex)

def RZ_Gate(theta):
    return np.array([[np.exp(-1j*theta/2), 0],
                     [0, np.exp(1j*theta/2)]], dtype=complex)
