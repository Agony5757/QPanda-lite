#include "density_operator_simulator.h"

namespace qpandalite
{
	using namespace density_operator_simulator_impl;


	void DensityOperatorSimulator::init_n_qubit(size_t nqubit)
	{
        if (nqubit > max_qubit_num)
        {
            auto errstr = fmt::format("Exceed max_qubit_num (nqubit = {}, limit = {})", nqubit, max_qubit_num);
            ThrowInvalidArgument(errstr);
        }

        state = std::vector<complex_t>(pow2(nqubit * 2), 0);
        state[0] = 1;
        total_qubit = nqubit;
	}

    /* Hadamard gate
      matrix form
      1/sqrt(2) * [ 1 1 ]
                  [ 1 -1 ]
    */
    void DensityOperatorSimulator::hadamard(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)

            size_t controller_mask = make_controller_mask(global_controller);
        hadamard_unsafe_impl(state, qn, total_qubit, controller_mask);
    }

    /* U22 gate
      matrix form
       [ u00 u01 ]
       [ u10 u11 ]
    */
    void DensityOperatorSimulator::u22(size_t qn, const u22_t& unitary, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)

            if (!_assert_u22(unitary))
            {
                auto errstr = fmt::format("Input is not a unitary.");
                ThrowInvalidArgument(errstr);
            }

        complex_t u00, u01, u10, u11;
        if (is_dagger)
        {
            u00 = std::conj(unitary[0]);
            u01 = std::conj(unitary[2]);
            u10 = std::conj(unitary[1]);
            u11 = std::conj(unitary[3]);
        }
        else
        {
            u00 = unitary[0];
            u01 = unitary[1];
            u10 = unitary[2];
            u11 = unitary[3];
        }

        size_t controller_mask = make_controller_mask(global_controller);

        u22_unsafe_impl(state, qn, u00, u01, u10, u11, total_qubit, controller_mask);
    }

    /* Pauli-X gate
      matrix form
       [ 0 1 ]
       [ 1 0 ]
    */
    void DensityOperatorSimulator::x(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)

            size_t controller_mask = make_controller_mask(global_controller);
        x_unsafe_impl(state, qn, total_qubit, controller_mask);
    }


    /* Pauli-Y gate
      matrix form
       [ 0  -1i ]
       [ 1i  0  ]

       Note: global phase is effective when controlled qubits are applied.
    */
    void DensityOperatorSimulator::y(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)
            size_t controller_mask = make_controller_mask(global_controller);
        y_unsafe_impl(state, qn, total_qubit, controller_mask);
    }

    /* Pauli-Z gate

      matrix form
       [ 1  0 ]
       [ 0 -1 ]
    */
    void DensityOperatorSimulator::z(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)
            size_t controller_mask = make_controller_mask(global_controller);
        z_unsafe_impl(state, qn, total_qubit, controller_mask);
    }

    /* S gate

      matrix form
       [ 1  0 ]
       [ 0 -1 ]
    */
    void DensityOperatorSimulator::s(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)
            size_t controller_mask = make_controller_mask(global_controller);
        if (is_dagger)
            sdg_unsafe_impl(state, qn, total_qubit, controller_mask);
        else
            s_unsafe_impl(state, qn, total_qubit, controller_mask);
    }

    /* T gate

      matrix form
       [ 1  0 ]
       [ 0 -1 ]
    */
    void DensityOperatorSimulator::t(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)
            size_t controller_mask = make_controller_mask(global_controller);
        if (is_dagger)
            tdg_unsafe_impl(state, qn, total_qubit, controller_mask);
        else
            t_unsafe_impl(state, qn, total_qubit, controller_mask);
    }


    /* CZ gate

      matrix form
       [ 1  0  0  0 ]
       [ 0  1  0  0 ]
       [ 0  0  1  0 ]
       [ 0  0  0 -1 ]
    */
    void DensityOperatorSimulator::cz(size_t qn1, size_t qn2, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE2(qn1, input1)
        CHECK_QUBIT_RANGE2(qn2, input2)
        CHECK_DUPLICATE_QUBIT(qn1, qn2)

        size_t controller_mask = make_controller_mask(global_controller);
        cz_unsafe_impl(state, qn1, qn2, total_qubit, controller_mask);
    }

    /* SWAP gate

      matrix form
       [ 1  0  0  0 ]
       [ 0  0  1  0 ]
       [ 0  1  0  0 ]
       [ 0  0  0  1 ]
    */
    void DensityOperatorSimulator::swap(size_t qn1, size_t qn2, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE2(qn1, input1)
        CHECK_QUBIT_RANGE2(qn2, input2)
        CHECK_DUPLICATE_QUBIT(qn1, qn2)

        size_t controller_mask = make_controller_mask(global_controller);
        swap_unsafe_impl(state, qn1, qn2, total_qubit, controller_mask);
    }

    /* iSWAP gate

      matrix form
       [ 1  0  0  0 ]
       [ 0  0  1j 0 ]
       [ 0  1j 0  0 ]
       [ 0  0  0  1 ]
    */
    void DensityOperatorSimulator::iswap(size_t qn1, size_t qn2, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE2(qn1, input1)
        CHECK_QUBIT_RANGE2(qn2, input2)
        CHECK_DUPLICATE_QUBIT(qn1, qn2)

        size_t controller_mask = make_controller_mask(global_controller);
        iswap_unsafe_impl(state, qn1, qn2, total_qubit, controller_mask, is_dagger);
    }

    /* XX-YY interaction

      matrix form
       [ 1  0  0  0 ]
       [ 0  c  s  0 ]
       [ 0  s  c  0 ]
       [ 0  0  0  1 ]

      where c = cos(theta/2), s = -1j * sin(theta/2)
    */
    void DensityOperatorSimulator::xy(size_t qn1, size_t qn2, double theta, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE2(qn1, input1)
        CHECK_QUBIT_RANGE2(qn2, input2)
        CHECK_DUPLICATE_QUBIT(qn1, qn2)

        size_t controller_mask = make_controller_mask(global_controller);
        xy_unsafe_impl(state, qn1, qn2, theta, total_qubit, controller_mask, is_dagger);
    }

    /* CNOT gate

      matrix form
       [ 1  0  0  0 ]
       [ 0  1  0  0 ]
       [ 0  0  0  1 ]
       [ 0  0  1  0 ]
    */
    void DensityOperatorSimulator::cnot(size_t controller, size_t target, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE2(controller, controller)
        CHECK_QUBIT_RANGE2(target, target)
        CHECK_DUPLICATE_QUBIT(controller, target)

        size_t controller_mask = make_controller_mask(global_controller);
        cnot_unsafe_impl(state, controller, target, total_qubit, controller_mask);
    }

    /* Rx gate

      matrix form
       [ cos(theta/2)    -i*sin(theta/2) ]
       [ -i*sin(theta/2)    cos(theta/2) ]
    */
    void DensityOperatorSimulator::rx(size_t qn, double angle, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)

        using namespace std::literals::complex_literals;
        u22_t unitary;
        if (is_dagger)
        {
            unitary = { cos(angle / 2), sin(angle / 2) * 1i,
                sin(angle / 2) * 1i, cos(angle / 2) };
        }
        else
        {
            unitary = { cos(angle / 2), -sin(angle / 2) * 1i,
                -sin(angle / 2) * 1i, cos(angle / 2) };
        }

        size_t controller_mask = make_controller_mask(global_controller);
        u22_unsafe_impl(state, qn, unitary, total_qubit, controller_mask);
    }

    /* SX gate

      matrix form

       1/2 * [ 1+j  1-j ]
             [ 1-j  1+j ]

       Note: global phase is effective when controlled qubits are applied.
    */
    void DensityOperatorSimulator::sx(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)

        u22_t unitary;
        if (is_dagger)
        {
            unitary[0] = 0.5 * std::complex<double>(1, -1);
            unitary[1] = 0.5 * std::complex<double>(1, 1);
            unitary[2] = 0.5 * std::complex<double>(1, 1);
            unitary[3] = 0.5 * std::complex<double>(1, -1);
        }
        else
        {
            unitary[0] = 0.5 * std::complex<double>(1, 1);
            unitary[1] = 0.5 * std::complex<double>(1, -1);
            unitary[2] = 0.5 * std::complex<double>(1, -1);
            unitary[3] = 0.5 * std::complex<double>(1, 1);
        }

        size_t controller_mask = make_controller_mask(global_controller);
        u22_unsafe_impl(state, qn, unitary, total_qubit, controller_mask);
    }

    /* Ry gate

      matrix form
       [ cos(theta/2)   -sin(theta/2) ]
       [ sin(theta/2)    cos(theta/2) ]
    */
    void DensityOperatorSimulator::ry(size_t qn, double angle, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)

        using namespace std::literals::complex_literals;
        u22_t unitary;
        if (is_dagger)
        {
            unitary = { cos(angle / 2), sin(angle / 2),
                       -sin(angle / 2), cos(angle / 2) };
        }
        else
        {
            unitary = { cos(angle / 2), -sin(angle / 2),
                       sin(angle / 2), cos(angle / 2) };
        }

        size_t controller_mask = make_controller_mask(global_controller);
        u22_unsafe_impl(state, qn, unitary, total_qubit, controller_mask);
    }

    /* Rz gate

      matrix form
       [ exp(-it/2)     0     ]
       [     0      exp(it/2) ]
    */
    void DensityOperatorSimulator::rz(size_t qn, double angle, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)

            size_t controller_mask = make_controller_mask(global_controller);
        rz_unsafe_impl(state, qn, angle, total_qubit, controller_mask, is_dagger);
    }

    /* U1 gate

      matrix form
       [     1     0     ]
       [     0     exp(it) ]
    */
    void DensityOperatorSimulator::u1(size_t qn, double angle, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)

        if (global_controller.size() == 1)
        {
            cu1_unsafe_impl(state, global_controller[0], qn, angle, total_qubit, 0, is_dagger);
        }
        else
        {
            size_t controller_mask = make_controller_mask(global_controller);
            u1_unsafe_impl(state, qn, angle, total_qubit, controller_mask, is_dagger);
        }

        //size_t controller_mask = make_controller_mask(global_controller);
        //u1_unsafe_impl(state, qn, angle, total_qubit, controller_mask, is_dagger);
    }


    /* U2 gate

      matrix form
       [     1     0     ]
       [     0     exp(it) ]
    */
    void DensityOperatorSimulator::u2(size_t qn, double phi, double lambda, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)

        using namespace std::literals::complex_literals;
        u22_t unitary;

        if (is_dagger)
        {
            unitary[0] = INVSQRT2;
            unitary[2] = INVSQRT2 * -1 * std::complex<double>(cos(lambda), -sin(lambda));
            unitary[1] = INVSQRT2 * std::complex<double>(cos(phi), -sin(phi));
            unitary[3] = INVSQRT2 * std::complex<double>(cos(phi + lambda), -sin(phi + lambda));
        }
        else
        {
            unitary[0] = INVSQRT2;
            unitary[1] = INVSQRT2 * -1 * std::complex<double>(cos(lambda), sin(lambda));
            unitary[2] = INVSQRT2 * std::complex<double>(cos(phi), sin(phi));
            unitary[3] = INVSQRT2 * std::complex<double>(cos(phi + lambda), sin(phi + lambda));
        }

        size_t controller_mask = make_controller_mask(global_controller);
        u22_unsafe_impl(state, qn, unitary, total_qubit, controller_mask);
    }

    /* Rphi90 gate

      matrix form
       1/sqrt(2) * [     1           -iexp(-i*phi) ]
                   [ -iexp(i*phi)        1         ]
    */
    void DensityOperatorSimulator::rphi90(size_t qn, double phi, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)

        using namespace std::literals::complex_literals;
        u22_t unitary;
        if (is_dagger)
        {
            unitary[0] = INVSQRT2;
            unitary[2] = INVSQRT2 * -1i * std::complex(-cos(phi), -sin(phi));
            unitary[1] = INVSQRT2 * -1i * std::complex(-cos(phi), sin(phi));
            unitary[3] = INVSQRT2;
        }
        else
        {
            unitary[0] = INVSQRT2;
            unitary[1] = INVSQRT2 * -1i * std::complex(cos(phi), -sin(phi));
            unitary[2] = INVSQRT2 * -1i * std::complex(cos(phi), sin(phi));
            unitary[3] = INVSQRT2;
        }

        size_t controller_mask = make_controller_mask(global_controller);
        u22_unsafe_impl(state, qn, unitary, total_qubit, controller_mask);
    }

    /* Rphi180 gate

      matrix form
       [   0           -i*exp(-i*phi) ]
       [ -i*exp(i*phi)      0         ]
    */
    void DensityOperatorSimulator::rphi180(size_t qn, double phi, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)

        using namespace std::literals::complex_literals;
        u22_t unitary;
        if (is_dagger)
        {
            unitary[0] = 0;
            unitary[2] = -1i * std::complex(-cos(phi), -sin(phi));
            unitary[1] = -1i * std::complex(-cos(phi), sin(phi));
            unitary[3] = 0;
        }
        else
        {
            unitary[0] = 0;
            unitary[1] = -1i * std::complex(cos(phi), -sin(phi));
            unitary[2] = -1i * std::complex(cos(phi), sin(phi));
            unitary[3] = 0;
        }

        size_t controller_mask = make_controller_mask(global_controller);
        u22_unsafe_impl(state, qn, unitary, total_qubit, controller_mask);
    }

    /* Rphi gate

      matrix form
       [      cos(theta/2)          -i*exp(-i*phi)*sin(theta/2) ]
       [ -iexp(i*phi)*sin(theta/2)         cos(theta/2)         ]

    */
    void DensityOperatorSimulator::rphi(size_t qn, double theta, double phi, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)

        using namespace std::literals::complex_literals;
        u22_t unitary;
        if (is_dagger)
        {
            unitary[0] = cos(theta / 2);
            unitary[2] = std::conj(-1i * sin(theta / 2) * std::complex(cos(phi), -sin(phi)));
            unitary[1] = std::conj(-1i * sin(theta / 2) * std::complex(cos(phi), sin(phi)));
            unitary[3] = cos(theta / 2);
        }
        else
        {
            unitary[0] = cos(theta / 2);
            unitary[1] = -1i * sin(theta / 2) * std::complex(cos(phi), -sin(phi));
            unitary[2] = -1i * sin(theta / 2) * std::complex(cos(phi), sin(phi));
            unitary[3] = cos(theta / 2);
        }

        size_t controller_mask = make_controller_mask(global_controller);
        u22_unsafe_impl(state, qn, unitary, total_qubit, controller_mask);
    }

    /* Toffoli gate */
    void DensityOperatorSimulator::toffoli(size_t qn1, size_t qn2, size_t target, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE2(qn1, qn1)
        CHECK_QUBIT_RANGE2(qn2, qn2)
        CHECK_QUBIT_RANGE2(target, target)

        CHECK_DUPLICATE_QUBIT(qn1, qn2)
        CHECK_DUPLICATE_QUBIT(qn2, target)
        CHECK_DUPLICATE_QUBIT(qn1, target)

        size_t controller_mask = make_controller_mask(global_controller);
        toffoli_unsafe_impl(state, qn1, qn2, target, total_qubit, controller_mask);
    }

    void DensityOperatorSimulator::cswap(size_t controller, size_t target1, size_t target2, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE2(controller, controller)
        CHECK_QUBIT_RANGE2(target1, target1)
        CHECK_QUBIT_RANGE2(target2, target2)

        CHECK_DUPLICATE_QUBIT(controller, target1)
        CHECK_DUPLICATE_QUBIT(target1, target2)
        CHECK_DUPLICATE_QUBIT(controller, target2)

        size_t controller_mask = make_controller_mask({ controller });
        cswap_unsafe_impl(state, controller, target1, target2, total_qubit, controller_mask);
    }

    /* ZZ interaction
    *    |00> -> exp(-it/2) * |00>
    *    |01> -> exp(it/2) * |01>
    *    |10> -> exp(it/2) * |10>
    *    |11> -> exp(-it/2) * |11>
    */
    void DensityOperatorSimulator::zz(size_t qn1, size_t qn2, double theta, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE2(qn1, qn1)
        CHECK_QUBIT_RANGE2(qn2, qn2)

        CHECK_DUPLICATE_QUBIT(qn1, qn2)

        if (is_dagger)
            theta = -theta;

        size_t controller_mask = make_controller_mask(global_controller);
        zz_unsafe_impl(state, qn1, qn2, theta, total_qubit, controller_mask);
    }

    /* XX interaction
    *    |00> -> [ cos(t)    0       0      isin(t) ]
    *    |01> -> [   0     cos(t)  isin(t)    0     ]
    *    |10> -> [   0     isin(t)  cos(t)    0     ]
    *    |11> -> [ isin(t)   0       0       cos(t) ]
    */
    void DensityOperatorSimulator::xx(size_t qn1, size_t qn2, double theta, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE2(qn1, qn1)
        CHECK_QUBIT_RANGE2(qn2, qn2)

        CHECK_DUPLICATE_QUBIT(qn1, qn2)

        if (is_dagger)
            theta = -theta;

        size_t controller_mask = make_controller_mask(global_controller);
        xx_unsafe_impl(state, qn1, qn2, theta, total_qubit, controller_mask);
    }

    /* YY interaction
    *
    * exp(-i*theta/2 * YY)
   *    |00> -> [ cos(t)    0       0      -isin(t) ]
   *    |01> -> [   0     cos(t)  isin(t)    0     ]
   *    |10> -> [   0     isin(t)  cos(t)    0     ]
   *    |11> -> [ -isin(t)   0       0       cos(t) ] where t=-theta/2
   */
    void DensityOperatorSimulator::yy(size_t qn1, size_t qn2, double theta, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE2(qn1, qn1)
        CHECK_QUBIT_RANGE2(qn2, qn2)

        CHECK_DUPLICATE_QUBIT(qn1, qn2)

        if (is_dagger)
            theta = -theta;

        size_t controller_mask = make_controller_mask(global_controller);
        yy_unsafe_impl(state, qn1, qn2, theta, total_qubit, controller_mask);
    }

    /* U3 gate

      matrix form

        [  cos(theta/2)                -exp(i*lambda)*sin(theta/2)     ]
        [  exp(i*phi)*sin(theta/2)   exp(i*(phi+lambda))*cos(theta/2)  ]
    */
    void DensityOperatorSimulator::u3(size_t qn, double theta, double phi, double lambda, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)

        size_t controller_mask = make_controller_mask(global_controller);
        u3_unsafe_impl(state, qn, theta, phi, lambda, total_qubit, controller_mask, is_dagger);
    }

    void DensityOperatorSimulator::phase2q(size_t qn1, size_t qn2, double theta1, double theta2, double thetazz, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE2(qn1, qn1)
        CHECK_QUBIT_RANGE2(qn2, qn2)

        CHECK_DUPLICATE_QUBIT(qn1, qn2)

        if (is_dagger)
        {
            theta1 = -theta1;
            theta2 = -theta2;
            thetazz = -thetazz;
        }

        size_t controller_mask = make_controller_mask(global_controller);
        phase2q_unsafe_impl(state, qn1, qn2, theta1, theta2, thetazz, total_qubit, controller_mask);
    }


    void DensityOperatorSimulator::uu15(size_t qn1, size_t qn2, const std::vector<double>& parameters, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE2(qn1, qn1)
        CHECK_QUBIT_RANGE2(qn2, qn2)

        CHECK_DUPLICATE_QUBIT(qn1, qn2)

        size_t controller_mask = make_controller_mask(global_controller);
        uu15_unsafe_impl(state, qn1, qn2, parameters, total_qubit, controller_mask, is_dagger);
    }

    void DensityOperatorSimulator::pauli_error_1q(size_t qn, double px, double py, double pz)
    {
        // TODO: Check probability bounds
        double sum = px + py + pz;

        if (sum > 1)
            ThrowInvalidArgument("Probabilities must be less than or equal to 1.");

        auto Ex = multiply_scalar(pauli_x, std::sqrt(px));
        auto Ey = multiply_scalar(pauli_y, std::sqrt(py));
        auto Ez = multiply_scalar(pauli_z, std::sqrt(pz));
        auto Ei = multiply_scalar(pauli_id, std::sqrt(1 - px - py - pz));

        kraus1q(qn, { Ex, Ey, Ez, Ei });
    }

    void DensityOperatorSimulator::depolarizing(size_t qn, double p)
    {
        pauli_error_1q(qn, p / 3, p / 3, p / 3);
    }

    void DensityOperatorSimulator::bitflip(size_t qn, double p)
    {
        if (p < 0 || p > 1)
            ThrowInvalidArgument("Probability must be between 0 and 1.");

        auto Ex = multiply_scalar(pauli_x, std::sqrt(p));
        auto Ei = multiply_scalar(pauli_id, std::sqrt(1 - p));

        kraus1q(qn, { Ex, Ei });
    }

    void DensityOperatorSimulator::phaseflip(size_t qn, double p)
    {
        auto Ez = multiply_scalar(pauli_z, std::sqrt(p));
        auto Ei = multiply_scalar(pauli_id, std::sqrt(1 - p));

        kraus1q(qn, { Ez, Ei });
    }

    void DensityOperatorSimulator::pauli_error_2q(size_t qn1, size_t qn2, const std::vector<double>& p)
    {
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

        double ii = 1 - sum;

        //ii = (0.9);
        //xi = (0.05);
        //yi = 0; // (0.05);
        //zi = (0.05);

        //ix = 0;
        //xx = 0;
        //yx = 0;
        //zx = 0;

        //iy = 0;
        //xy = 0;
        //yy = 0;
        //zy = 0;
        //iz = 0;
        //xz = 0;
        //yz = 0;
        //zz = 0;

        auto Eii = multiply_scalar(pauli_ii, std::sqrt(ii));
        auto Exi = multiply_scalar(pauli_xi, std::sqrt(xi));
        auto Eyi = multiply_scalar(pauli_yi, std::sqrt(yi));
        auto Ezi = multiply_scalar(pauli_zi, std::sqrt(zi));

        auto Eix = multiply_scalar(pauli_ix, std::sqrt(ix));
        auto Exx = multiply_scalar(pauli_xx, std::sqrt(xx));
        auto Eyx = multiply_scalar(pauli_yx, std::sqrt(yx));
        auto Ezx = multiply_scalar(pauli_zx, std::sqrt(zx));

        auto Eiy = multiply_scalar(pauli_iy, std::sqrt(iy));
        auto Exy = multiply_scalar(pauli_xy, std::sqrt(xy));
        auto Eyy = multiply_scalar(pauli_yy, std::sqrt(yy));
        auto Ezy = multiply_scalar(pauli_zy, std::sqrt(zy));

        auto Eiz = multiply_scalar(pauli_iz, std::sqrt(iz));
        auto Exz = multiply_scalar(pauli_xz, std::sqrt(xz));
        auto Eyz = multiply_scalar(pauli_yz, std::sqrt(yz));
        auto Ezz = multiply_scalar(pauli_zz, std::sqrt(zz));

        kraus2q(qn1, qn2, { 
            Eii, Exi, Eyi, Ezi, 
            Eix, Exx, Eyx, Ezx, 
            Eiy, Exy, Eyy, Ezy, 
            Eiz, Exz, Eyz, Ezz 
            });
    }

    void DensityOperatorSimulator::twoqubit_depolarizing(size_t qn1, size_t qn2, double p)
    {
        pauli_error_2q(qn1, qn2, std::vector<dtype>(15, p / 15));
    }

    void DensityOperatorSimulator::kraus1q(size_t qn, const Kraus1Q& kraus_ops)
    {
        CHECK_QUBIT_RANGE(qn)

        // 验证Kraus算符完备性（必须确保∑E_i†E_i = I）
        if (!validate_kraus(kraus_ops)) {
            auto kraus_op_str_list = kraus2str(kraus_ops);
            auto kraus_strs = fmt::format("Kraus = \n{}", kraus_op_str_list);
            ThrowInvalidArgument(fmt::format("Invalid Kraus operators: sum(E†E) != I. {}", kraus_strs));
        }

        auto ret_state = state;
        u22_unsafe_impl(ret_state, qn, kraus_ops[0], total_qubit, 0);
        
        for (size_t i = 1; i<kraus_ops.size();++i)
        {
            auto copy_state = state;
            auto& E = kraus_ops[i];
            u22_unsafe_impl(copy_state, qn, E, total_qubit, 0);

            merge_state(ret_state, copy_state);
        }

        state = std::move(ret_state);
    }


    void DensityOperatorSimulator::kraus2q(size_t qn1, size_t qn2, const Kraus2Q& kraus_ops)
    {
        CHECK_QUBIT_RANGE2(qn1, qn1)
        CHECK_QUBIT_RANGE2(qn2, qn2)

        CHECK_DUPLICATE_QUBIT(qn1, qn2)

        // 验证Kraus算符完备性（必须确保∑E_i†E_i = I）
        if (!validate_kraus(kraus_ops)) {
            auto kraus_op_str_list = kraus2str(kraus_ops);
            auto kraus_strs = fmt::format("Kraus = \n{}", kraus_op_str_list);
            ThrowInvalidArgument(fmt::format("Invalid Kraus operators: sum(E†E) != I. {}", kraus_strs));
        }

        auto ret_state = state;
        u44_unsafe_impl(ret_state, qn1, qn2, kraus_ops[0], total_qubit, 0);

        for (size_t i = 1; i < kraus_ops.size(); ++i)
        {
            auto copy_state = state;
            auto& E = kraus_ops[i];
            u44_unsafe_impl(copy_state, qn1, qn2, E, total_qubit, 0);

            merge_state(ret_state, copy_state);
        }

        state = std::move(ret_state);
    }

    void DensityOperatorSimulator::amplitude_damping(size_t qn, double gamma)
    {
        auto E0 = u22_t{ 1, 0, 0, sqrt(1 - gamma) };
        auto E1 = u22_t{ 0, sqrt(gamma), 0, 0 };

        kraus1q(qn, { E0, E1 });
    }

    dtype DensityOperatorSimulator::get_prob_map(const std::map<size_t, int>& measure_qubits)
    {
        size_t N = pow2(total_qubit);
        for (auto&& [qn, qstate] : measure_qubits)
        {
            if (qn >= total_qubit)
            {
                auto errstr = fmt::format("Exceed total (total_qubit = {}, qn = {})", total_qubit, qn);
                ThrowInvalidArgument(errstr);
            }
            if (qstate != 0 && qstate != 1)
            {
                auto errstr = fmt::format("State must be 0 or 1. (input = {} at qn = {})", qstate, qn);
                ThrowInvalidArgument(errstr);
            }
        }

        double prob = 0;
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            for (auto&& [qid, qstate] : measure_qubits)
            {
                if ((i >> qid) != qstate)
                    break;
            }
            /* use the diagonal term to calculate the prob */
            prob += std::abs(val(state, i, i, N));
        }
        return prob;
    }

    dtype DensityOperatorSimulator::get_prob(size_t qn, int qstate)
    {
        size_t N = pow2(total_qubit);
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }
        if (qstate != 0 && qstate != 1)
        {
            auto errstr = fmt::format("State must be 0 or 1. (input = {} at qn = {})", qstate, qn);
            ThrowInvalidArgument(errstr);
        }

        double prob = 0;
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i >> qn) == qstate)
                prob += std::abs(val(state, i, i, N));
        }
        return prob;
    }

    std::vector<dtype> DensityOperatorSimulator::pmeasure_list(const std::vector<size_t>& measure_list)
    {
        size_t N = pow2(total_qubit);
        auto measure_map = preprocess_measure_list(measure_list, total_qubit);

        std::vector<dtype> ret;
        ret.resize(pow2(measure_list.size()));

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            size_t meas_idx = get_state_with_qubit(i, measure_map);
            ret[meas_idx] += std::abs(val(state, i, i, N));
        }
        return ret;
    }

    std::vector<dtype> DensityOperatorSimulator::pmeasure(size_t measure_qubit)
    {
        return pmeasure_list(std::vector{ measure_qubit });
    }

    std::vector<dtype> DensityOperatorSimulator::stateprob() const
    {
        size_t N = pow2(total_qubit);
        std::vector<dtype> ret(N);
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            ret[i] = std::abs(val(state, i, i, N));
        }
        return ret;
    } 

    std::string u22_to_str(const u22_t& E)
    {
        return fmt::format("[{}+{}j, {}+{}j; {}+{}j, {}+{}j]\n",
            std::real(E[0]), std::imag(E[0]),
            std::real(E[1]), std::imag(E[1]),
            std::real(E[2]), std::imag(E[2]),
            std::real(E[3]), std::imag(E[3]));
    }

    std::string u44_to_str(const u44_t& E)
    {
        std::string ret = "[";
        for (size_t i = 0; i < 4; ++i)
        {
            for (size_t j = 0; j < 4; ++j)
            {
                ret += fmt::format("{}+{}j", std::real(val(E, i, j)), std::imag(val(E, i, j)));
                if (j != 3)
                    ret += ", ";
            }
            if (i != 3)
                ret += "; ";
        }
        ret += "]";
        return ret;
    }

    std::string kraus2str(const Kraus1Q& kraus_ops)
    {
        std::string kraus_op_str_list;
        for (auto& E : kraus_ops)
        {
            kraus_op_str_list += (u22_to_str(E) + "\n");
        }
        return kraus_op_str_list;
    }

    std::string kraus2str(const Kraus2Q& kraus_ops)
    {
        std::string kraus_op_str_list;
        for (auto& E : kraus_ops)
        {
            kraus_op_str_list += (u44_to_str(E) + "\n");
        }
        return kraus_op_str_list;
    }

}