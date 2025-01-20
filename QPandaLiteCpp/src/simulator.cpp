#include "simulator.h"
namespace qpandalite{

    void Simulator::init_n_qubit(size_t nqubit)
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

    /* Hadamard gate 
      matrix form
      1/sqrt(2) * [ 1 1 ]
                  [ 1 -1 ]
    */
    void Simulator::hadamard(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void Simulator::u22(size_t qn, const u22_t& unitary, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void Simulator::x(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void Simulator::y(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void Simulator::z(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void Simulator::s(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)
            size_t controller_mask = make_controller_mask(global_controller);
        z_unsafe_impl(state, qn, total_qubit, controller_mask);
    }

    /* T gate

      matrix form
       [ 1  0 ]
       [ 0 -1 ]
    */
    void Simulator::t(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)
            size_t controller_mask = make_controller_mask(global_controller);
        z_unsafe_impl(state, qn, total_qubit, controller_mask);
    }


    /* CZ gate

      matrix form
       [ 1  0  0  0 ]
       [ 0  1  0  0 ]
       [ 0  0  1  0 ]
       [ 0  0  0 -1 ]
    */
    void Simulator::cz(size_t qn1, size_t qn2, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void Simulator::swap(size_t qn1, size_t qn2, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void Simulator::iswap(size_t qn1, size_t qn2, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void Simulator::xy(size_t qn1, size_t qn2, double theta, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void Simulator::cnot(size_t controller, size_t target, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void Simulator::rx(size_t qn, double angle, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void Simulator::sx(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void Simulator::ry(size_t qn, double angle, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void Simulator::rz(size_t qn, double angle, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void Simulator::u1(size_t qn, double angle, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)

        size_t controller_mask = make_controller_mask(global_controller);
        u1_unsafe_impl(state, qn, angle, total_qubit, controller_mask, is_dagger);
    }

    /* Rphi90 gate

      matrix form
       1/sqrt(2) * [     1           -iexp(-i*phi) ]
                   [ -iexp(i*phi)        1         ]
    */
    void Simulator::rphi90(size_t qn, double phi, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void Simulator::rphi180(size_t qn, double phi, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void Simulator::rphi(size_t qn, double phi, double theta, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void Simulator::toffoli(size_t qn1, size_t qn2, size_t target, const std::vector<size_t>& global_controller, bool is_dagger)
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

    void Simulator::cswap(size_t controller, size_t target1, size_t target2, const std::vector<size_t>& global_controller, bool is_dagger)
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
    *    |00> -> |00>
    *    |01> -> -exp(it/2) * |01>
    *    |10> -> -exp(it/2) * |10>
    *    |11> -> |11> 
    */
    void Simulator::zz(size_t qn1, size_t qn2, double theta, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void Simulator::xx(size_t qn1, size_t qn2, double theta, const std::vector<size_t>& global_controller, bool is_dagger)
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
   *    |00> -> [ cos(t)    0       0      -isin(t) ]
   *    |01> -> [   0     cos(t)  isin(t)    0     ]
   *    |10> -> [   0     isin(t)  cos(t)    0     ]
   *    |11> -> [ -isin(t)   0       0       cos(t) ]
   */
    void Simulator::yy(size_t qn1, size_t qn2, double theta, const std::vector<size_t>& global_controller, bool is_dagger)
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
    void Simulator::u3(size_t qn, double theta, double phi, double lambda, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)

        /* build the matrix */
        complex_t ctheta = cos(theta / 2);
        complex_t stheta = sin(theta / 2);
        complex_t eilambda = complex_t(cos(lambda), sin(lambda));
        complex_t eiphi = complex_t(cos(phi), sin(phi));
        complex_t eiphi_plus_lambda = complex_t(cos(phi + lambda), sin(phi + lambda));
        complex_t u00 = ctheta;
        complex_t u01 = -eilambda * stheta;
        complex_t u10 = eiphi * stheta;
        complex_t u11 = eiphi_plus_lambda * ctheta;

        if (is_dagger)
        {
            u00 = std::conj(u00);
            u01 = std::conj(u01);
            u11 = std::conj(u11);
            u10 = std::conj(u10);
            std::swap(u01, u10);
        }

        size_t controller_mask = make_controller_mask(global_controller);
        u22_unsafe_impl(state, qn, u00, u01, u10, u11, total_qubit, controller_mask);
    }

    dtype Simulator::get_prob_map(const std::map<size_t, int> &measure_qubits)
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

    dtype Simulator::get_prob(size_t qn, int qstate)
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

        double prob = 0;
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i >> qn) == qstate) 
                prob += abs_sqr(state[i]);
        }
        return prob;
    }

    std::vector<dtype> Simulator::pmeasure_list(const std::vector<size_t> &measure_list)
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

    std::vector<dtype> Simulator::pmeasure(size_t measure_qubit)
    {
        return pmeasure_list(std::vector{measure_qubit});
    }

}