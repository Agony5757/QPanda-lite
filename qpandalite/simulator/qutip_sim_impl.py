import numpy as np
from qutip import (
    Qobj, basis, tensor, ket2dm, 
    qeye, sigmax, sigmay, sigmaz, 
)
from qutip_qip.operations import *
from itertools import product

class DensityOperatorSimulatorQutip:
    def __init__(self):
        self.n_qubits = 0
        self.density_matrix = None

    def init_n_qubit(self, n):
        self.n_qubits = n
        zero_state = tensor([basis(2, 0) for _ in range(n)])
        self.density_matrix = ket2dm(zero_state)

    def _expand_operator(self, operator, targets):
        return expand_operator(operator, self.n_qubits, [self.n_qubits - 1 - i for i in targets])

    def _construct_control_op(self, control_qubits, U_expanded):
        if not control_qubits:
            return U_expanded
        
        # reverse the control qubits (since qutip uses little-endian)
        control_qubits = [self.n_qubits - 1 - i for i in control_qubits]

        identity = tensor([qeye(2)] * self.n_qubits)
        proj = tensor([qeye(2)] * self.n_qubits)
        for q in control_qubits:
            op_list = [qeye(2) if i != q else basis(2, 1).proj() for i in range(self.n_qubits)]
            proj_q = tensor(op_list)
            proj = proj * proj_q
        return proj * U_expanded + (identity - proj)

    def _apply_unitary(self, U, qubits, control_qubits_set = [], is_dagger = False):
        U_base = U.dag() if is_dagger else U
        U_expanded = self._expand_operator(U_base, qubits)
        control_op = self._construct_control_op(control_qubits_set, U_expanded)
        self.density_matrix = control_op * self.density_matrix * control_op.dag()

    def rx(self, qubit, theta, control_qubits_set = [], is_dagger = False):
        U = rx(theta)
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def ry(self, qubit, theta, control_qubits_set = [], is_dagger = False):
        U = ry(theta)
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def rz(self, qubit, theta, control_qubits_set = [], is_dagger = False):
        U = rz(theta)
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def x(self, qubit, control_qubits_set = [], is_dagger = False):
        U = sigmax()
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def y(self, qubit, control_qubits_set = [], is_dagger = False):
        U = sigmay()
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def z(self, qubit, control_qubits_set = [], is_dagger = False):
        U = sigmaz()
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def hadamard(self, qubit, control_qubits_set = [], is_dagger = False):
        U = snot()
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def cnot(self, control_qubit, target_qubit, control_qubits_set = [], is_dagger = False):
        U = cnot(2, 0, 1)  # 标准 CNOT 矩阵，需扩展
        U_expanded = self._expand_operator(U, [control_qubit, target_qubit])
        control_op = self._construct_control_op(control_qubits_set, U_expanded)
        self.density_matrix = control_op * self.density_matrix * control_op.dag()

    def cz(self, qubit1, qubit2, control_qubits_set = [], is_dagger = False):
        U = Qobj([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,-1]], dims=[[2,2],[2,2]])
        self._apply_unitary(U, [qubit1, qubit2], control_qubits_set, is_dagger)

    def swap(self, qubit1, qubit2, control_qubits_set = [], is_dagger = False):
        U = swap()
        self._apply_unitary(U, [qubit1, qubit2], control_qubits_set, is_dagger)

    def toffoli(self, c1, c2, target, control_qubits_set = [], is_dagger = False):
        U = toffoli()  # 标准 Toffoli 矩阵，需扩展
        U_expanded = self._expand_operator(U, [c1, c2, target])
        control_op = self._construct_control_op(control_qubits_set, U_expanded)
        self.density_matrix = control_op * self.density_matrix * control_op.dag()

    def phaseflip(self, qubit, prob):
        K0 = np.sqrt(1 - prob) * Qobj([[1,0],[0,1]])
        K1 = np.sqrt(prob) * Qobj([[1,0],[0,-1]])
        self._apply_kraus([K0, K1], [qubit])

    def _apply_kraus(self, kraus_ops, targets):
        expanded_ops = [self._expand_operator(K, targets) for K in kraus_ops]
        new_rho = sum(K * self.density_matrix * K.dag() for K in expanded_ops)
        self.density_matrix = new_rho

        # 在DensityOperatorSimulator类中添加以下方法
    def u1(self, qubit, theta, control_qubits_set, is_dagger):
        U = phasegate(theta)
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def u2(self, qubit, phi, lam, control_qubits_set, is_dagger):
        # Qiskit U2门标准定义：
        # U2(φ, λ) = 1/sqrt(2) * [[1, -e^{iλ}],
        #                         [e^{iφ}, e^{i(φ+λ)}]]
        sqrt2 = np.sqrt(2)
        matrix = np.array([
            [1/sqrt2, -np.exp(1j*lam)/sqrt2],
            [np.exp(1j*phi)/sqrt2, np.exp(1j*(phi+lam))/sqrt2]
        ])
        
        # 处理dagger的情况
        U = Qobj(matrix if not is_dagger else matrix.conj().T)
        
        # 应用酉操作
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger=False)

    def u3(self, qubit, theta, phi, lam, control_qubits_set, is_dagger):
        matrix = np.array([[np.cos(theta/2), -np.exp(1j*lam)*np.sin(theta/2)],
                          [np.exp(1j*phi)*np.sin(theta/2), np.exp(1j*(phi+lam))*np.cos(theta/2)]])
        # 处理dagger的情况
        U = Qobj(matrix if not is_dagger else matrix.conj().T)
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger=False)

    def s(self, qubit, control_qubits_set, is_dagger):
        U = phasegate(np.pi/2)
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def t(self, qubit, control_qubits_set, is_dagger):
        U = phasegate(np.pi/4)
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def iswap(self, q1, q2, control_qubits_set, is_dagger):
        matrix = Qobj([[1, 0, 0, 0],
                    [0, 0, 1j, 0],
                    [0, 1j, 0, 0],
                    [0, 0, 0, 1]], 
                    dims=[[2,2], [2,2]])
        self._apply_unitary(matrix, [q1, q2], control_qubits_set, is_dagger)

    def cswap(self, control_qubit, q1, q2, control_qubits_set, is_dagger):
        total_control = list(control_qubits_set) + [control_qubit]
        swap_op = swap()
        self._apply_unitary(swap_op, [q1, q2], total_control, is_dagger)

    def xy(self, q1, q2, theta, control_qubits_set, is_dagger):
        H = (tensor(sigmax(), sigmax()) + tensor(sigmay(), sigmay())) * (-theta/2)
        U = H.expm()
        self._apply_unitary(U, [q1, q2], control_qubits_set, is_dagger)

    def rphi(self, qubit, phi, theta, control_qubits_set, is_dagger):
        U = rz(phi) * rx(theta)
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def rphi90(self, qubit, phi, control_qubits_set, is_dagger):
        return self.rphi(qubit, phi, np.pi/2, control_qubits_set, is_dagger)

    def rphi180(self, qubit, phi, control_qubits_set, is_dagger):
        return self.rphi(qubit, phi, np.pi, control_qubits_set, is_dagger)

    def xx(self, q1, q2, theta, control_qubits_set, is_dagger):
        H = tensor(sigmax(), sigmax()) * (-theta/2)
        U = H.expm()
        self._apply_unitary(U, [q1, q2], control_qubits_set, is_dagger)

    def yy(self, q1, q2, theta, control_qubits_set, is_dagger):
        H = tensor(sigmay(), sigmay()) * (-theta/2)
        U = H.expm()
        self._apply_unitary(U, [q1, q2], control_qubits_set, is_dagger)

    def zz(self, q1, q2, theta, control_qubits_set, is_dagger):
        H = tensor(sigmaz(), sigmaz()) * (-theta/2)
        U = H.expm()
        self._apply_unitary(U, [q1, q2], control_qubits_set, is_dagger)

    def uu15(self, q1, q2, params, control_qubits_set, is_dagger):
        raise NotImplementedError()
        
    def phase2q(self, q1, q2, theta1, theta2, theta3, control_qubits_set, is_dagger):
        raise NotImplementedError()
        
    # 噪声模型
    def pauli_error_1q(self, qubit, px, py, pz):
        p0 = max(1 - px - py - pz, 0)
        K0 = np.sqrt(p0) * qeye(2)
        K1 = np.sqrt(px) * sigmax()
        K2 = np.sqrt(py) * sigmay()
        K3 = np.sqrt(pz) * sigmaz()
        self._apply_kraus([K0, K1, K2, K3], [qubit])

    def depolarizing(self, qubit, p):
        K0 = np.sqrt(1 - p) * qeye(2)
        K1 = np.sqrt(p/3) * sigmax()
        K2 = np.sqrt(p/3) * sigmay()
        K3 = np.sqrt(p/3) * sigmaz()
        self._apply_kraus([K0, K1, K2, K3], [qubit])

    def bitflip(self, qubit, p):
        K0 = np.sqrt(1 - p) * qeye(2)
        K1 = np.sqrt(p) * sigmax()
        self._apply_kraus([K0, K1], [qubit])

    def kraus1q(self, qubit, parameters):
        kraus_ops = [Qobj(np.array(k).reshape(2,2)) for k in parameters]
        self._apply_kraus(kraus_ops, [qubit])

    def amplitude_damping(self, qubit, gamma):
        from qutip import destroy
        a = destroy(2)
        K0 = Qobj([[1, 0], [0, np.sqrt(1 - gamma)]])
        K1 = Qobj([[0, np.sqrt(gamma)], [0, 0]])
        self._apply_kraus([K0, K1], [qubit])

    def pmeasure(self, measure_qubits):
        # get a partial traced density matrix with respect to the measure_qubits
        prob_list = [0]*(2**len(measure_qubits))
        for bits in product([0,1], repeat=len(measure_qubits)):
            proj_list = []
            for q in range(self.n_qubits):
                if q in measure_qubits:
                    idx = measure_qubits.index(q)
                    proj = basis(2, bits[idx]).proj()
                else:
                    proj = qeye(2)
                proj_list.append(proj)
            projector = tensor(proj_list)
            prob = (self.density_matrix * projector).tr().real

            # convert bit string to integer index
            bit_idx = int(''.join(map(str, bits)), 2)
            prob_list[bit_idx] = prob
        return prob_list
    
    def stateprob(self):
        return self.density_matrix.diag().real
    
if __name__ == '__main__':
    sim = DensityOperatorSimulatorQutip()
    sim.init_n_qubit(3)
    sim.x(0)
    sim.cnot(0, 1)
    sim.toffoli(0, 1, 2)

    print(sim.density_matrix)
    print(sim.pmeasure([0, 1]))
    print(sim.stateprob())