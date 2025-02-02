import numpy as np
from qutip import (
    Qobj, basis, tensor, ket2dm, 
    qeye, sigmax, sigmay, sigmaz, 
)
from qutip_qip.operations import *
from itertools import product

def _validate_kraus_ops(kraus_ops, nqubit):
    # check if kraus_ops satisfy the Kraus representation condition
    ndim = 2**nqubit
    for K in kraus_ops:
        if not isinstance(K, Qobj):
            raise TypeError("Kraus operators must be Qobj instances.")
        if K.type != 'oper':
            raise TypeError("Kraus operators must be operators.")
        if K.shape!= (ndim, ndim):
            raise ValueError("Kraus operators must be square matrices with dimensions (ndim, ndim).")
    
    sum_kraus = sum([kraus_op.dag() * kraus_op for kraus_op in kraus_ops])
    eye = qeye(ndim)
    if not np.allclose(sum_kraus.full(), eye.full()):
        raise ValueError("Kraus operators must satisfy the Kraus representation condition.")



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

    def sx(self, qubit, control_qubits_set = [], is_dagger = False):
        U = sqrtnot()
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def cnot(self, control_qubit, target_qubit, control_qubits_set = [], is_dagger = False):
        U = cnot(2, 0, 1)  # 标准 CNOT 矩阵，需扩展
        self._apply_unitary(U, [control_qubit, target_qubit], control_qubits_set, is_dagger)

    def cz(self, qubit1, qubit2, control_qubits_set = [], is_dagger = False):
        U = Qobj([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,-1]], dims=[[2,2],[2,2]])
        self._apply_unitary(U, [qubit1, qubit2], control_qubits_set, is_dagger)

    def swap(self, qubit1, qubit2, control_qubits_set = [], is_dagger = False):
        U = swap()
        self._apply_unitary(U, [qubit1, qubit2], control_qubits_set, is_dagger)

    def toffoli(self, c1, c2, target, control_qubits_set = [], is_dagger = False):
        U = toffoli()  # 标准 Toffoli 矩阵，需扩展
        self._apply_unitary(U, [c1, c2, target], control_qubits_set, is_dagger)

    def phaseflip(self, qubit, prob):
        K0 = np.sqrt(1 - prob) * Qobj([[1,0],[0,1]])
        K1 = np.sqrt(prob) * Qobj([[1,0],[0,-1]])
        self._apply_kraus([K0, K1], [qubit])

    def _apply_kraus(self, kraus_ops, targets):
        expanded_ops = [self._expand_operator(K, targets) for K in kraus_ops]
        new_rho = sum(K * self.density_matrix * K.dag() for K in expanded_ops)
        self.density_matrix = new_rho

    def u1(self, qubit, theta, control_qubits_set = [], is_dagger = False):
        U = phasegate(theta)
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def u2(self, qubit, phi, lam, control_qubits_set = [], is_dagger = False):
        # Qiskit U2门标准定义：
        # U2(φ, λ) = 1/sqrt(2) * [[1, -e^{iλ}],
        #                         [e^{iφ}, e^{i(φ+λ)}]]
        sqrt2 = np.sqrt(2)
        matrix = np.array([
            [1/sqrt2, -np.exp(1j*lam)/sqrt2],
            [np.exp(1j*phi)/sqrt2, np.exp(1j*(phi+lam))/sqrt2]
        ])
        
        U = Qobj(matrix)
        
        # 应用酉操作
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def u3(self, qubit, theta, phi, lam, control_qubits_set = [], is_dagger = False):
        matrix = np.array([[np.cos(theta/2), -np.exp(1j*lam)*np.sin(theta/2)],
                          [np.exp(1j*phi)*np.sin(theta/2), np.exp(1j*(phi+lam))*np.cos(theta/2)]])
        # 处理dagger的情况
        U = Qobj(matrix)
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def s(self, qubit, control_qubits_set = [], is_dagger = False):
        U = phasegate(np.pi/2)
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def t(self, qubit, control_qubits_set = [], is_dagger = False):
        U = phasegate(np.pi/4)
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def iswap(self, q1, q2, control_qubits_set = [], is_dagger = False):
        matrix = Qobj([[1, 0, 0, 0],
                    [0, 0, 1j, 0],
                    [0, 1j, 0, 0],
                    [0, 0, 0, 1]], 
                    dims=[[2,2], [2,2]])
        self._apply_unitary(matrix, [q1, q2], control_qubits_set, is_dagger)

    def cswap(self, control_qubit, q1, q2, control_qubits_set = [], is_dagger = False):
        total_control = list(control_qubits_set) + [control_qubit]
        swap_op = swap()
        self._apply_unitary(swap_op, [q1, q2], total_control, is_dagger)

    def xy(self, q1, q2, theta, control_qubits_set = [], is_dagger = False):
        H = (tensor(sigmax(), sigmax()) + tensor(sigmay(), sigmay())) * (-1j*theta/4)
        U = H.expm()
        self._apply_unitary(U, [q1, q2], control_qubits_set, is_dagger)

    def rphi(self, qubit, phi, theta, control_qubits_set = [], is_dagger = False):
        U = rz(phi) * rx(theta) * rz(-phi)
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def rphi90(self, qubit, phi, control_qubits_set = [], is_dagger = False):
        return self.rphi(qubit, phi, np.pi/2, control_qubits_set, is_dagger)

    def rphi180(self, qubit, phi, control_qubits_set = [], is_dagger = False):
        return self.rphi(qubit, phi, np.pi, control_qubits_set, is_dagger)

    def xx(self, q1, q2, theta, control_qubits_set = [], is_dagger = False):
        H = tensor(sigmax(), sigmax()) * (-1j*theta/2)
        U = H.expm()
        self._apply_unitary(U, [q1, q2], control_qubits_set, is_dagger)

    def yy(self, q1, q2, theta, control_qubits_set = [], is_dagger = False):
        H = tensor(sigmay(), sigmay()) * (-1j*theta/2)
        U = H.expm()
        self._apply_unitary(U, [q1, q2], control_qubits_set, is_dagger)

    def zz(self, q1, q2, theta, control_qubits_set = [], is_dagger = False):
        H = tensor(sigmaz(), sigmaz()) * (-1j*theta/2)
        U = H.expm()
        self._apply_unitary(U, [q1, q2], control_qubits_set, is_dagger)

    def uu15(self, q1, q2, params, control_qubits_set = [], is_dagger = False):
        '''uu15 gate using KAK decomposition

            U is implemented by

            U3(q1, parameters[0:3])
            U3(q2, parameters[3:6])
            XX(q1, q2, parameters[6])
            YY(q1, q2, parameters[7])
            ZZ(q1, q2, parameters[8])
            U3(q1, parameters[9:12])
            U3(q2, parameters[12:15])

            where parameters is a list of 15 parameters.

        Args:
            q1 (int): qubit 1 index
            q2 (int): qubit 2 index
            params (list): list of parameters
            control_qubits_set (list): list of control qubits
            is_dagger (bool): whether to apply daggered gate
        '''
        if not is_dagger:
            self.u3(q1, *params[0:3], control_qubits_set, False)
            self.u3(q2, *params[3:6], control_qubits_set, False)
            self.xx(q1, q2, params[6], control_qubits_set, False)
            self.yy(q1, q2, params[7], control_qubits_set, False)
            self.zz(q1, q2, params[8], control_qubits_set, False)
            self.u3(q1, *params[9:12], control_qubits_set, False)
            self.u3(q2, *params[12:15], control_qubits_set, False)
        else:
            self.u3(q1, *params[9:12], control_qubits_set, True)
            self.u3(q2, *params[12:15], control_qubits_set, True)
            self.zz(q1, q2, params[8], control_qubits_set, True)
            self.yy(q1, q2, params[7], control_qubits_set, True)
            self.xx(q1, q2, params[6], control_qubits_set, True)
            self.u3(q2, *params[3:6], control_qubits_set, True)
            self.u3(q1, *params[0:3], control_qubits_set, True)      
              
    def phase2q(self, q1, q2, theta1, theta2, theta3, control_qubits_set = [], is_dagger = False):
        '''  phase2q gate =
            u1(qn1, theta1),
            u1(qn2, theta2),
            zz(qn1, qn2, thetazz)

        Args:
            q1 (int): qubit 1 index
            q2 (int): qubit 2 index
            theta1 (float): angle of u1 gate on qn1
            theta2 (float): angle of u1 gate on qn2
            theta3 (float): angle of zz gate
            control_qubits_set (list): list of control qubits
            is_dagger (bool): whether to apply daggered gate
        '''
        if not is_dagger:
            self.u1(q1, theta1, control_qubits_set, False)
            self.u1(q2, theta2, control_qubits_set, False)
            self.zz(q1, q2, theta3, control_qubits_set, False)
        else:
            self.zz(q1, q2, theta3, control_qubits_set, True)
            self.u1(q2, theta2, control_qubits_set, True)
            self.u1(q1, theta1, control_qubits_set, True)
        
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
        K0 = Qobj([[1, 0], [0, np.sqrt(1 - gamma)]])
        K1 = Qobj([[0, np.sqrt(gamma)], [0, 0]])
        self._apply_kraus([K0, K1], [qubit])

    def kraus2q(self, q1, q2, parameters):
        kraus_ops = [Qobj(np.array(k).reshape(4,4)) for k in parameters]
        self._apply_kraus(kraus_ops, [q1, q2])

    def pauli_error_2q(self, q1, q2, parameters):
        '''
        // 解包所有概率参数
        double xi = p[0], yi = p[1], zi = p[2];
        double ix = p[3], xx = p[4], yx = p[5], zx = p[6];
        double iy = p[7], xy = p[8], yy = p[9], zy = p[10];
        double iz = p[11], xz = p[12], yz = p[13], zz = p[14];

        double sum = xi + yi + zi +
            ix + xx + yx + zx +
            iy + xy + yy + zy +
            iz + xz + yz + zz;

        if (sum > 1)
            ThrowInvalidArgument("Probabilities must be less than or equal to 1.");

        auto Exi = multiply_scalar(pauli_xi, xi);
        auto Eyi = multiply_scalar(pauli_yi, yi);
        auto Ezi = multiply_scalar(pauli_zi, zi);

        auto Eix = multiply_scalar(pauli_ix, ix);
        auto Exx = multiply_scalar(pauli_xx, xx);
        auto Eyx = multiply_scalar(pauli_yx, yx);
        auto Ezx = multiply_scalar(pauli_zx, zx);

        auto Eiy = multiply_scalar(pauli_iy, iy);
        auto Exy = multiply_scalar(pauli_xy, xy);
        auto Eyy = multiply_scalar(pauli_yy, yy);
        auto Ezy = multiply_scalar(pauli_zy, zy);

        auto Eiz = multiply_scalar(pauli_iz, iz);
        auto Exz = multiply_scalar(pauli_xz, xz);
        auto Eyz = multiply_scalar(pauli_yz, yz);
        auto Ezz = multiply_scalar(pauli_zz, zz);

        kraus2q(qn1, qn2, { Exi, Eyi, Ezi, Exx, Eyy, Ezz, Exy, Exz, Eyz, Eix, Eiy, Eiz, Exx, Eyx, Ezx, Exy, Eyy, Ezy, Exz, Eyz, Ezz });
            

        Args:
            q1 (int): qubit 1 index
            q2 (int): qubit 2 index
            parameters (list): list of parameters
        '''
        
        # unpack all probabilities
        parameters = list(parameters)

        # validate probabilities
        if sum(parameters) > 1:
            raise ValueError("Probabilities must be less than or equal to 1.")

        ii = [1 - sum(parameters)]
        parameters = ii + parameters
        parameters = [np.sqrt(p) for p in parameters]
        (ii, xi, yi, zi, 
         ix, xx, yx, zx, 
         iy, xy, yy, zy, 
         iz, xz, yz, zz) = tuple(parameters)
        
        # create kraus operators
        Eii = ii * tensor(qeye(2), qeye(2))
        Eix = ix * tensor(sigmax(), qeye(2))
        Eiy = iy * tensor(sigmay(), qeye(2))
        Eiz = iz * tensor(sigmaz(), qeye(2))

        Exi = xi * tensor(qeye(2), sigmax())
        Exx = xx * tensor(sigmax(), sigmax())
        Exy = xy * tensor(sigmay(), sigmax())
        Exz = xz * tensor(sigmaz(), sigmax())

        Eyi = yi * tensor(qeye(2), sigmay())
        Eyx = yx * tensor(sigmax(), sigmay())
        Eyy = yy * tensor(sigmay(), sigmay())
        Eyz = yz * tensor(sigmaz(), sigmay())
        
        Ezi = zi * tensor(qeye(2), sigmaz())
        Ezx = zx * tensor(sigmax(), sigmaz())
        Ezy = zy * tensor(sigmay(), sigmaz())
        Ezz = zz * tensor(sigmaz(), sigmaz())

        kraus = [
            Eii, Exi, Eyi, Ezi, 
            Eix, Exx, Eyx, Ezx, 
            Eiy, Exy, Eyy, Ezy, 
            Eiz, Exz, Eyz, Ezz
        ]

        _validate_kraus_ops(kraus, 2)

        # apply kraus operators
        self._apply_kraus(kraus, [q1, q2])

    def twoqubit_depolarizing(self, q1, q2, p):
        self.pauli_error_2q(q1, q2, [p/15]*15)

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
    
    @property
    def state(self):
        return self.density_matrix.full()
    
if __name__ == '__main__':
    sim = DensityOperatorSimulatorQutip()
    sim.init_n_qubit(3)
    sim.x(0)
    sim.cnot(0, 1)
    sim.toffoli(0, 1, 2)

    print(sim.density_matrix)
    print(sim.pmeasure([0, 1]))
    print(sim.stateprob())