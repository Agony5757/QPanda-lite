#include "simulator.h"
namespace qpandalite {

    using namespace statevector_simulator_impl;

    void StatevectorSimulator::init_n_qubit(size_t nqubit)
    {
        if (nqubit > max_qubit_num)
        {
            auto errstr = fmt::format("Exceed max_qubit_num (nqubit = {}, limit = {})", nqubit, max_qubit_num);
            ThrowInvalidArgument(errstr);
        }

        state = std::vector<complex_t>(pow2(nqubit), 0);
        state[0] = 1;
        total_qubit = nqubit;
    }

    void StatevectorSimulator::id(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)

        // do nothing
    }

    /* Hadamard gate 
      matrix form
      1/sqrt(2) * [ 1 1 ]
                  [ 1 -1 ]
    */
    void StatevectorSimulator::hadamard(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void StatevectorSimulator::u22(size_t qn, const u22_t& unitary, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void StatevectorSimulator::x(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void StatevectorSimulator::y(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void StatevectorSimulator::z(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void StatevectorSimulator::s(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void StatevectorSimulator::t(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void StatevectorSimulator::cz(size_t qn1, size_t qn2, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void StatevectorSimulator::swap(size_t qn1, size_t qn2, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void StatevectorSimulator::iswap(size_t qn1, size_t qn2, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void StatevectorSimulator::xy(size_t qn1, size_t qn2, double theta, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void StatevectorSimulator::cnot(size_t controller, size_t target, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void StatevectorSimulator::rx(size_t qn, double angle, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)

        using namespace std::literals::complex_literals;
        u22_t unitary;
        if(is_dagger)
        {
            unitary = {cos(angle / 2), sin(angle / 2) * 1i,
                sin(angle / 2) * 1i, cos(angle / 2)};
        }else
        {
            unitary = {cos(angle / 2), -sin(angle / 2) * 1i,
                -sin(angle / 2) * 1i, cos(angle / 2)};
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
    void StatevectorSimulator::sx(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)

        u22_t unitary;
        if(is_dagger)
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
    void StatevectorSimulator::ry(size_t qn, double angle, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)

        using namespace std::literals::complex_literals;
        u22_t unitary; 
        if (is_dagger)
        {
            unitary = {cos(angle / 2), sin(angle / 2),
                       -sin(angle / 2), cos(angle / 2)};
        }else
        {
            unitary = {cos(angle / 2), -sin(angle / 2),
                       sin(angle / 2), cos(angle / 2)};
        }

        size_t controller_mask = make_controller_mask(global_controller);
        u22_unsafe_impl(state, qn, unitary, total_qubit, controller_mask);
    }

    /* Rz gate

      matrix form
       [ exp(-it/2)     0     ]
       [     0      exp(it/2) ]
    */
    void StatevectorSimulator::rz(size_t qn, double angle, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void StatevectorSimulator::u1(size_t qn, double angle, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)

        size_t controller_mask = make_controller_mask(global_controller);
        u1_unsafe_impl(state, qn, angle, total_qubit, controller_mask, is_dagger);
    }

    /* U2 gate
        
       matrix form

       1/sqrt(2) * [     1         -exp(i*lambda) ]
                   [ exp(i*phi)  exp(i*(phi+lambda)]
    */
    void StatevectorSimulator::u2(size_t qn, double phi, double lambda, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void StatevectorSimulator::rphi90(size_t qn, double phi, const std::vector<size_t>& global_controller, bool is_dagger)
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
        }else
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
    void StatevectorSimulator::rphi180(size_t qn, double phi, const std::vector<size_t>& global_controller, bool is_dagger)
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
        }else
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
    void StatevectorSimulator::rphi(size_t qn, double theta, double phi, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void StatevectorSimulator::toffoli(size_t qn1, size_t qn2, size_t target, const std::vector<size_t>& global_controller, bool is_dagger)
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

    void StatevectorSimulator::cswap(size_t controller, size_t target1, size_t target2, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE2(controller, controller)
        CHECK_QUBIT_RANGE2(target1, target1)
        CHECK_QUBIT_RANGE2(target2, target2)

        CHECK_DUPLICATE_QUBIT(controller, target1)
        CHECK_DUPLICATE_QUBIT(target1, target2)
        CHECK_DUPLICATE_QUBIT(controller, target2)

        size_t controller_mask = make_controller_mask({controller});
        cswap_unsafe_impl(state, controller, target1, target2, total_qubit, controller_mask);
    }

    /* ZZ interaction
    *    |00> -> exp(-it/2) * |00>
    *    |01> -> exp(it/2) * |01>
    *    |10> -> exp(it/2) * |10>
    *    |11> -> exp(-it/2) * |11> 
    */
    void StatevectorSimulator::zz(size_t qn1, size_t qn2, double theta, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void StatevectorSimulator::xx(size_t qn1, size_t qn2, double theta, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void StatevectorSimulator::yy(size_t qn1, size_t qn2, double theta, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void StatevectorSimulator::u3(size_t qn, double theta, double phi, double lambda, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)

        size_t controller_mask = make_controller_mask(global_controller);
        u3_unsafe_impl(state, qn, theta, phi, lambda, total_qubit, controller_mask, is_dagger);
    }

    void StatevectorSimulator::phase2q(size_t qn1, size_t qn2, double theta1, double theta2, double thetazz, const std::vector<size_t>& global_controller, bool is_dagger)
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


    void StatevectorSimulator::uu15(size_t qn1, size_t qn2, const std::vector<double>& parameters, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE2(qn1, qn1)
        CHECK_QUBIT_RANGE2(qn2, qn2)

        CHECK_DUPLICATE_QUBIT(qn1, qn2)

        size_t controller_mask = make_controller_mask(global_controller);
        uu15_unsafe_impl(state, qn1, qn2, parameters, total_qubit, controller_mask, is_dagger);
    }

    void StatevectorSimulator::pauli_error_1q(size_t qn, double px, double py, double pz)
    {
        double sum = px + py + pz;
        if (sum > 1.0)
            ThrowInvalidArgument("The 1Q Pauli error model has total error exceeding 1.0.");

        double r = qpandalite::rand();
        if (r < px)
        {
            // [0, px] perform x gate
            x(qn);
            return;
        }
        r -= px;
        if (r < py)
        {
            // [px, px+py] perform y gate
            y(qn);
            return;
        }
        r -= py;
        if (r < pz)
        {
            // [px+py, px+py+pz] perform z gate
            z(qn);
            return;
        }
        // otherwise perform id gate
        id(qn);
    }

    void StatevectorSimulator::depolarizing(size_t qn, double p)
    {
        if (p > 1.0)
            ThrowInvalidArgument("The depolarizing model has p>1.0.");
        return pauli_error_1q(qn, p / 3, p / 3, p / 3);
    }

    void StatevectorSimulator::bitflip(size_t qn, double p)
    {
        if (p > 1.0)
            ThrowInvalidArgument("The bitflip model has p>1.0.");

        return pauli_error_1q(qn, p, 0, 0);
    }

    void StatevectorSimulator::phaseflip(size_t qn, double p)
    {
        if (p > 1.0)
            ThrowInvalidArgument("The phaseflip model has p>1.0.");
        return pauli_error_1q(qn, 0, 0, p);
    }

    void StatevectorSimulator::pauli_error_2q(size_t qn1, size_t qn2, const std::vector<double>& p)
    {
        // the input must be a 15-sized vector
        // Depolarizing matrix
        // II  XI  YI  ZI
        // IX  XX  YX  ZX
        // IY  XY  YY  ZY
        // IZ  XZ  YZ  ZZ
        if (p.size() != 15)
            ThrowInvalidArgument("The generalized 2q model must be a 15-sized vector, "
                "representing p{xi, yi, zi, ix, xx, yx, zx, iy, xy, yy, zy, "
                "iz, xz, yz, zz}, respectively");

        // 解包所有概率参数
        double xi = p[0], yi = p[1], zi = p[2];
        double ix = p[3], xx = p[4], yx = p[5], zx = p[6];
        double iy = p[7], xy = p[8], yy = p[9], zy = p[10];
        double iz = p[11], xz = p[12], yz = p[13], zz = p[14];

        double sum = xi + yi + zi +
            ix + xx + yx + zx +
            iy + xy + yy + zy +
            iz + xz + yz + zz;

        if (sum > 1.0)
            ThrowInvalidArgument("The 2Q Pauli error model has total error exceeding 1.0.");

        double r = qpandalite::rand();

        // 处理XI, YI, ZI
        if (r < xi) { x(qn1); id(qn2); return; } r -= xi;
        if (r < yi) { y(qn1); id(qn2); return; } r -= yi;
        if (r < zi) { z(qn1); id(qn2); return; } r -= zi;

        // 处理IX, XX, YX, ZX
        if (r < ix) { id(qn1); x(qn2); return; } r -= ix;
        if (r < xx) { x(qn1); x(qn2); return; } r -= xx;
        if (r < yx) { y(qn1); x(qn2); return; } r -= yx;
        if (r < zx) { z(qn1); x(qn2); return; } r -= zx;

        // 处理IY, XY, YY, ZY
        if (r < iy) { id(qn1); y(qn2); return; } r -= iy;
        if (r < xy) { x(qn1); y(qn2); return; } r -= xy;
        if (r < yy) { y(qn1); y(qn2); return; } r -= yy;
        if (r < zy) { z(qn1); y(qn2); return; } r -= zy;

        // 处理IZ, XZ, YZ, ZZ
        if (r < iz) { id(qn1); z(qn2); return; } r -= iz;
        if (r < xz) { x(qn1); z(qn2); return; } r -= xz;
        if (r < yz) { y(qn1); z(qn2); return; } r -= yz;
        if (r < zz) { z(qn1); z(qn2); return; }

        // Otherwise, II
        id(qn1); id(qn2);
    }

    void StatevectorSimulator::twoqubit_depolarizing(size_t qn1, size_t qn2, double p)
    {
        CHECK_QUBIT_RANGE2(qn1, qn1)
        CHECK_QUBIT_RANGE2(qn2, qn2)

        const static std::vector<double> p_(15, p / 15);
        pauli_error_2q(qn1, qn2, p_);
    }


    void StatevectorSimulator::kraus1q(size_t qn, const std::vector<u22_t>& kraus_ops) {

        CHECK_QUBIT_RANGE(qn)

        // 验证Kraus算符完备性（必须确保∑E_i†E_i = I）
        if (!validate_kraus(kraus_ops)) {
            ThrowInvalidArgument("Invalid Kraus operators: sum(E†E) != I");
        }
        
        kraus1q_unsafe_impl(state, qn, kraus_ops, total_qubit);
    }

    void StatevectorSimulator::amplitude_damping(size_t qn, double gamma)
    {
        if (gamma > 1.0)
            ThrowInvalidArgument("The phaseflip model has gamma>1.0.");

        CHECK_QUBIT_RANGE(qn)

        amplitude_damping_unsafe_impl(state, qn, gamma, total_qubit);
    }


    dtype StatevectorSimulator::get_prob_map(const std::map<size_t, int> &measure_qubits)
    {
        for (auto &&[qn, qstate] : measure_qubits)
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
            for (auto &&[qid, qstate] : measure_qubits)
            {
                if ((i >> qid) != qstate)
                    break;
            }
            prob += abs_sqr(state[i]);
        }
        return prob;
    }

    dtype StatevectorSimulator::get_prob(size_t qn, int qstate)
    {
        CHECK_QUBIT_RANGE(qn)

        if (qstate == 0)
        {
            return prob_0(state, qn, total_qubit);
        }
        else if (qstate == 1)
        {
            return prob_1(state, qn, total_qubit);
        }
        else
        {
            auto errstr = fmt::format("State must be 0 or 1. (input = {} at qn = {})", qstate, qn);
            ThrowInvalidArgument(errstr);
        }
    }

    std::vector<dtype> StatevectorSimulator::pmeasure_list(const std::vector<size_t> &measure_list)
    {
        auto measure_map = preprocess_measure_list(measure_list, total_qubit);

        std::vector<dtype> ret;
        ret.resize(pow2(measure_list.size()));
        
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            size_t meas_idx = get_state_with_qubit(i, measure_map);
            ret[meas_idx] += abs_sqr(state[i]);
        }
        return ret;
    }

    std::vector<dtype> StatevectorSimulator::pmeasure(size_t measure_qubit)
    {
        return pmeasure_list(std::vector{measure_qubit});
    }

}