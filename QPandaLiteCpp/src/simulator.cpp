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

    void Simulator::hadamard(size_t qn, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)
        
        hadamard_unsafe_impl(state, qn, total_qubit);
    }

    void Simulator::u22(size_t qn, const u22_t& unitary, bool is_dagger)
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
        u22_unsafe_impl(state, qn, u00, u01, u10, u11, total_qubit);
    }

    void Simulator::x(size_t qn, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)
        x_unsafe_impl(state, qn, total_qubit);
    }

    void Simulator::y(size_t qn, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)
        y_unsafe_impl(state, qn, total_qubit);
    }

    void Simulator::z(size_t qn, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)
        z_unsafe_impl(state, qn, total_qubit);
    }
    
    void Simulator::cz(size_t qn1, size_t qn2, bool is_dagger)
    {
        CHECK_QUBIT_RANGE2(qn1, input1)
        CHECK_QUBIT_RANGE2(qn2, input2)
        CHECK_DUPLICATE_QUBIT(qn1, qn2)

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if (((i >> qn1) & 1) && ((i >> qn2) & 1))
            {
                state[i] *= -1;
            }
        }
    }

    void Simulator::swap(size_t qn1, size_t qn2, bool is_dagger)
    {
        CHECK_QUBIT_RANGE2(qn1, input1)
        CHECK_QUBIT_RANGE2(qn2, input2)
        CHECK_DUPLICATE_QUBIT(qn1, qn2)

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            bool v1 = (i >> qn1) & 1;
            bool v2 = (i >> qn2) & 1;
            if (v1 && (!v2))
            {
                // |10>
                // let it swap with |01>
                std::swap(state[i - pow2(qn1) + pow2(qn2)], state[i]);
            }
        }
    }

    void Simulator::iswap(size_t qn1, size_t qn2, bool is_dagger)
    {
        CHECK_QUBIT_RANGE2(qn1, input1)
        CHECK_QUBIT_RANGE2(qn2, input2)
        CHECK_DUPLICATE_QUBIT(qn1, qn2)

        using namespace std::literals::complex_literals;
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if (((i >> qn1) & 1) == 0 && ((i >> qn2) & 1) == 1)
            {
                std::swap(state[i], state[i + pow2(qn1) - pow2(qn2)]);
                if(is_dagger)
                {
                    state[i] *= -1i;
                    state[i + pow2(qn1) - pow2(qn2)] *= -1i;
                }else
                {
                    state[i] *= 1i;
                    state[i + pow2(qn1) - pow2(qn2)] *= 1i;
                }
            }
        }
    }

    void Simulator::xy(size_t qn1, size_t qn2, double theta, bool is_dagger)
    {
        CHECK_QUBIT_RANGE2(qn1, input1)
        CHECK_QUBIT_RANGE2(qn2, input2)
        CHECK_DUPLICATE_QUBIT(qn1, qn2)

        using namespace std::literals::complex_literals;

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            // |01>
            if (((i >> qn1) & 0) && ((i >> qn2) & 1))
            {
                size_t i2 = i + pow2(qn1) - pow2(qn2);
                complex_t s1 = state[i];
                complex_t s2 = state[i2];
                if (is_dagger)
                {
                    state[i] = s1 * cos(theta / 2) + s2 * 1i * sin(theta / 2);
                    state[i2] = s1 * 1i * sin(theta / 2) + cos(theta / 2) * s2;
                }
                else
                {
                    state[i] = s1 * cos(theta / 2) - s2 * 1i * sin(theta / 2);
                    state[i2] = -s1 * 1i * sin(theta / 2) + cos(theta / 2) * s2;
                }
            }
        }
    }
    
    void Simulator::cnot(size_t controller, size_t target, bool is_dagger)
    {
        CHECK_QUBIT_RANGE2(controller, controller)
        CHECK_QUBIT_RANGE2(target, target)
        CHECK_DUPLICATE_QUBIT(controller, target)

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if (((i >> controller) & 1) && ((i >> target) & 1))
            {
                std::swap(state[i], state[i - pow2(target)]);
            }
        }
    }

    void Simulator::rx(size_t qn, double angle, bool is_dagger)
    {
        CHECK_QUBIT_RANGE(qn)

        // Rx 
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


        u22_unsafe_impl(state, qn, unitary, total_qubit);
    }


    void Simulator::sx(size_t qn, bool is_dagger)
    {
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

        u22_t unitary;
        if(is_dagger)
        {
            unitary[0] = 0.5 * std::complex<double>(1, -1);
            unitary[2] = 0.5 * std::complex<double>(1, 1);
            unitary[1] = 0.5 * std::complex<double>(1, 1);
            unitary[3] = 0.5 * std::complex<double>(1, -1);
        }else
        {
            unitary[0] = 0.5 * std::complex<double>(1, 1);
            unitary[1] = 0.5 * std::complex<double>(1, -1);
            unitary[2] = 0.5 * std::complex<double>(1, -1);
            unitary[3] = 0.5 * std::complex<double>(1, 1);
        }


        u22(qn, unitary);
    }

    void Simulator::ry(size_t qn, double angle, bool is_dagger)
    {
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

        using namespace std::literals::complex_literals;
        u22_t unitary; 
        if(is_dagger)
        {
            unitary = {cos(angle / 2), sin(angle / 2),
                       -sin(angle / 2), cos(angle / 2)};
        }else
        {
            unitary = {cos(angle / 2), -sin(angle / 2),
                       sin(angle / 2), cos(angle / 2)};
        }


        u22(qn, unitary);
    }

    void Simulator::rz(size_t qn, double angle, bool is_dagger)
    {
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if (((i >> qn) & 1) ^ is_dagger)
            {
                // 0 and not dagger -> exp(-it/2)
                // 1 and dagger -> exp(-it/2)
                state[i] *= std::complex(cos(angle / 2), -sin(angle / 2));
            }
            else
            {
                // 0 and dagger -> exp(it/2)
                // 1 and not dagger -> exp(it/2)
                state[i] *= std::complex(cos(angle / 2), sin(angle / 2));
            }

        }
    }

    void Simulator::rphi90(size_t qn, double phi, bool is_dagger)
    {
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

        using namespace std::literals::complex_literals;
        u22_t unitary;
        if(is_dagger)
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
        u22(qn, unitary);
    }

    void Simulator::rphi180(size_t qn, double phi, bool is_dagger)
    {
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

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

        u22(qn, unitary);        
    }

    void Simulator::rphi(size_t qn, double phi, double theta, bool is_dagger)
    {
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

        using namespace std::literals::complex_literals;
        u22_t unitary;
        if (is_dagger)
        {
            unitary[0] = cos(theta / 2);
            unitary[2] = -1i * sin(theta / 2) * std::complex(-cos(phi), -sin(phi));
            unitary[1] = -1i * sin(theta / 2) * std::complex(-cos(phi), sin(phi));
            unitary[3] = cos(theta / 2);           
        }
        else
        {
            unitary[0] = cos(theta / 2);
            unitary[1] = -1i * sin(theta / 2) * std::complex(cos(phi), -sin(phi));
            unitary[2] = -1i * sin(theta / 2) * std::complex(cos(phi), sin(phi));
            unitary[3] = cos(theta / 2);
        }
        u22(qn, unitary);    
    }

    void Simulator::toffoli(size_t qn1, size_t qn2, size_t target, bool is_dagger)
    {
        if (qn1 >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn1 = {})", total_qubit, qn1);
            ThrowInvalidArgument(errstr);
        }
        if (qn2 >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn2 = {})", total_qubit, qn2);
            ThrowInvalidArgument(errstr);
        }
        if (target >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, target = {})", total_qubit, target);
            ThrowInvalidArgument(errstr);
        }

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if (((i >> qn1) & 1) && ((i >> qn2) & 1) && ((i >> target) & 1))
            {
                std::swap(state[i], state[i - pow2(target)]);
            }
        }
    }

    void Simulator::cswap(size_t controller, size_t target1, size_t target2, bool is_dagger)
    {
        if (controller >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, controller = {})", total_qubit, controller);
            ThrowInvalidArgument(errstr);
        }
        if (target1 >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, target1 = {})", total_qubit, target1);
            ThrowInvalidArgument(errstr);
        }
        if (target2 >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, target2 = {})", total_qubit, target2);
            ThrowInvalidArgument(errstr);
        }

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if (!((i >> controller) & 1))
                continue;

            bool v1 = (i >> target1) & 1;
            bool v2 = (i >> target2) & 1;
            if (v1 && (!v2))
            {
                // |10>
                // let it swap with |01>
                std::swap(state[i - pow2(target1) + pow2(target2)], state[i]);
            }
        }
    }

    /* ZZ interaction
    *    |00> -> |00>
    *    |01> -> -exp(it/2) * |01>
    *    |10> -> -exp(it/2) * |10>
    *    |11> -> |11> 
    */
    void Simulator::zz(size_t qn1, size_t qn2, double theta, bool is_dagger)
    {
        if (qn1 >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn1 = {})", total_qubit, qn1);
            ThrowInvalidArgument(errstr);
        }
        if (qn2 >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn2 = {})", total_qubit, qn2);
            ThrowInvalidArgument(errstr);
        }

        if (is_dagger)
            theta = -theta;

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            bool v1 = (i >> qn1) & 1;
            bool v2 = (i >> qn2) & 1;
            if (v1 != v2)
            {
                state[i] *= complex_t(cos(-theta / 2), sin(-theta / 2));
            }
        }
    }

    /* XX interaction
    *    |00> -> [ cos(t)    0       0      isin(t) ]
    *    |01> -> [   0     cos(t)  isin(t)    0     ]
    *    |10> -> [   0     isin(t)  cos(t)    0     ]
    *    |11> -> [ isin(t)   0       0       cos(t) ]
    */
    void Simulator::xx(size_t qn1, size_t qn2, double theta, bool is_dagger)
    {
        if (qn1 >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn1 = {})", total_qubit, qn1);
            ThrowInvalidArgument(errstr);
        }
        if (qn2 >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn2 = {})", total_qubit, qn2);
            ThrowInvalidArgument(errstr);
        }

        if (is_dagger)
            theta = -theta;
        using namespace std::literals::complex_literals;
        complex_t ctheta = cos(theta);
        complex_t stheta = sin(theta);
        complex_t istheta = 1i * stheta;

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            bool v1 = (i >> qn1) & 1;
            bool v2 = (i >> qn2) & 1;
            if (v1 == false && v2 == false) /* 00 */
            {
                /* only 00 will be operated */
                size_t i00 = i;
                size_t i01 = i + pow2(qn1);
                size_t i10 = i + pow2(qn2);
                size_t i11 = i + pow2(qn1) + pow2(qn2);

                complex_t a00 = state[i00];
                complex_t a01 = state[i01];
                complex_t a10 = state[i10];
                complex_t a11 = state[i11];

                state[i00] = a00 * ctheta + a11 * istheta;
                state[i01] = a01 * ctheta + a10 * istheta;
                state[i10] = a01 * istheta + a10 * ctheta;
                state[i11] = a00 * istheta + a11 * ctheta;
            }
        }
    }

    /* YY interaction
   *    |00> -> [ cos(t)    0       0      -isin(t) ]
   *    |01> -> [   0     cos(t)  isin(t)    0     ]
   *    |10> -> [   0     isin(t)  cos(t)    0     ]
   *    |11> -> [ -isin(t)   0       0       cos(t) ]
   */
    void Simulator::yy(size_t qn1, size_t qn2, double theta, bool is_dagger)
    {
        if (qn1 >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn1 = {})", total_qubit, qn1);
            ThrowInvalidArgument(errstr);
        }
        if (qn2 >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn2 = {})", total_qubit, qn2);
            ThrowInvalidArgument(errstr);
        }

        if (is_dagger)
            theta = -theta;
        using namespace std::literals::complex_literals;
        complex_t ctheta = cos(theta);
        complex_t stheta = sin(theta);
        complex_t istheta = 1i * stheta;

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            bool v1 = (i >> qn1) & 1;
            bool v2 = (i >> qn2) & 1;
            if (v1 == false && v2 == false) /* 00 */
            {
                /* only 00 will be operated */
                size_t i00 = i;
                size_t i01 = i + pow2(qn1);
                size_t i10 = i + pow2(qn2);
                size_t i11 = i + pow2(qn1) + pow2(qn2);

                complex_t a00 = state[i00];
                complex_t a01 = state[i01];
                complex_t a10 = state[i10];
                complex_t a11 = state[i11];

                state[i00] = a00 * ctheta - a11 * istheta;
                state[i01] = a01 * ctheta + a10 * istheta;
                state[i10] = a01 * istheta + a10 * ctheta;
                state[i11] = -a00 * istheta + a11 * ctheta;
            }
        }
    }

    void Simulator::u3(size_t qn, double theta, double phi, double lambda, bool is_dagger)
    {
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn1 = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

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

        u22(qn, { u00, u01, u10, u11 }, is_dagger);
    }

    void Simulator::hadamard_cont(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        if (global_controller.size() == 0)
        {
            hadamard(qn, is_dagger);
            return;
        }

        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, input = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if (!control_enable(i, global_controller))
                continue;
            if ((i >> qn) & 1) continue;
            size_t i0 = i;
            size_t i1 = i + pow2(qn);

            complex_t a0 = state[i0];
            complex_t a1 = state[i1];

            complex_t new_a0 = (a0 + a1) * INVSQRT2;
            complex_t new_a1 = (a0 - a1) * INVSQRT2;

            state[i0] = new_a0;
            state[i1] = new_a1;
        }
    }

    void Simulator::u22_cont(size_t qn, const u22_t& unitary, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        if (global_controller.size() == 0)
        {
            u22(qn, unitary, is_dagger);
            return;
        }
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, input = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }
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
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if (!control_enable(i, global_controller))
                continue;
            if ((i >> qn) & 1) continue;
            size_t i0 = i;
            size_t i1 = i + pow2(qn);

            complex_t a0 = state[i0];
            complex_t a1 = state[i1];

            complex_t new_a0 = u00 * a0 + u01 * a1;
            complex_t new_a1 = u10 * a0 + u11 * a1;

            state[i0] = new_a0;
            state[i1] = new_a1;
        }
    }

    void Simulator::x_cont(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        if (global_controller.size() == 0)
        {
            x(qn, is_dagger);
            return;
        }
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, input = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if (!control_enable(i, global_controller))
                continue;
            if ((i >> qn) & 1)
            {
                std::swap(state[i], state[i - pow2(qn)]);
            }
        }
    }

    void Simulator::y_cont(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        if (global_controller.size() == 0)
        {
            y(qn, is_dagger);
            return;
        }
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, input = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

        using namespace std::literals::complex_literals;
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if (!control_enable(i, global_controller))
                continue;
            if ((i >> qn) & 1)
            {
                std::swap(state[i], state[i - pow2(qn)]);
                state[i - pow2(qn)] *= -1i;
                state[i] *= 1i;
            }
        }
    }

    void Simulator::z_cont(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        if (global_controller.size() == 0)
        {
            z(qn, is_dagger);
            return;
        }
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, input = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if (!control_enable(i, global_controller))
                continue;
            if ((i >> qn) & 1)
            {
                state[i] *= -1;
            }
        }
    }

    void Simulator::cz_cont(size_t qn1, size_t qn2, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        if (global_controller.size() == 0)
        {
            cz(qn1, qn2, is_dagger);
            return;
        }
        if (qn1 >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, input1 = {})", total_qubit, qn1);
            ThrowInvalidArgument(errstr);
        }
        if (qn2 >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, input2 = {})", total_qubit, qn2);
            ThrowInvalidArgument(errstr);
        }
        if (qn1 == qn2)
        {
            auto errstr = fmt::format("qn1 = qn2");
            ThrowInvalidArgument(errstr);
        }


        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if (!control_enable(i, global_controller))
                continue;
            if (((i >> qn1) & 1) && ((i >> qn2) & 1))
            {
                state[i] *= -1;
            }
        }
    }

    void Simulator::swap_cont(size_t qn1, size_t qn2, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        if (global_controller.size() == 0)
        {
            swap(qn1, qn2, is_dagger);
            return;
        }

        if (qn1 >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn1 = {})", total_qubit, qn1);
            ThrowInvalidArgument(errstr);
        }
        if (qn2 >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn2 = {})", total_qubit, qn2);
            ThrowInvalidArgument(errstr);
        }

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if (!control_enable(i, global_controller))
                continue;

            bool v1 = (i >> qn1) & 1;
            bool v2 = (i >> qn2) & 1;
            if (v1 && (!v2))
            {
                // |10>
                // let it swap with |01>
                std::swap(state[i - pow2(qn1) + pow2(qn2)], state[i]);
            }
        }
    }

    void Simulator::iswap_cont(size_t qn1, size_t qn2, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        if (global_controller.size() == 0)
        {
            iswap(qn1, qn2, is_dagger);
            return;
        }
        if (qn1 >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, input1 = {})", total_qubit, qn1);
            ThrowInvalidArgument(errstr);
        }
        if (qn2 >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, input2 = {})", total_qubit, qn2);
            ThrowInvalidArgument(errstr);
        }
        if (qn1 == qn2)
        {
            auto errstr = fmt::format("qn1 = qn2");
            ThrowInvalidArgument(errstr);
        }

        using namespace std::literals::complex_literals;
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if (!control_enable(i, global_controller))
                continue;
            if (((i >> qn1) & 1) == 0 && ((i >> qn2) & 1) == 1)
            {
                std::swap(state[i], state[i + pow2(qn1) - pow2(qn2)]);
                if (is_dagger)
                {
                    state[i] *= -1i;
                    state[i + pow2(qn1) - pow2(qn2)] *= -1i;
                }
                else
                {
                    state[i] *= 1i;
                    state[i + pow2(qn1) - pow2(qn2)] *= 1i;
                }
            }
        }
    }

    void Simulator::xy_cont(size_t qn1, size_t qn2, double theta, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        if (global_controller.size() == 0)
        {
            xy(qn1, qn2, theta, is_dagger);
            return;
        }
        if (qn1 >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, input1 = {})", total_qubit, qn1);
            ThrowInvalidArgument(errstr);
        }
        if (qn2 >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, input2 = {})", total_qubit, qn2);
            ThrowInvalidArgument(errstr);
        }
        if (qn1 == qn2)
        {
            auto errstr = fmt::format("qn1 = qn2");
            ThrowInvalidArgument(errstr);
        }

        using namespace std::literals::complex_literals;
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if (!control_enable(i, global_controller))
                continue;
            size_t i2 = i + pow2(qn1) - pow2(qn2);
            complex_t s1 = state[i];
            complex_t s2 = state[i2];
            if (is_dagger)
            {
                state[i] = s1 * cos(theta / 2) + s2 * 1i * sin(theta / 2);
                state[i2] = s1 * 1i * sin(theta / 2) + cos(theta / 2) * s2;
            }
            else
            {
                state[i] = s1 * cos(theta / 2) - s2 * 1i * sin(theta / 2);
                state[i2] = -s1 * 1i * sin(theta / 2) + cos(theta / 2) * s2;
            }
        }
    }

    void Simulator::cnot_cont(size_t controller, size_t target, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        if (global_controller.size() == 0)
        {
            cnot(controller, target, is_dagger);
            return;
        }
        if (controller >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, controller = {})", total_qubit, controller);
            ThrowInvalidArgument(errstr);
        }
        if (target >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, target = {})", total_qubit, target);
            ThrowInvalidArgument(errstr);
        }
        if (controller == target)
        {
            auto errstr = fmt::format("controller = target");
            ThrowInvalidArgument(errstr);
        }

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if (!control_enable(i, global_controller))
                continue;
            bool control_active = true;
            
            // Check if all global controllers are active (in state 1)
            for (size_t q : global_controller) {

                if (!((i >> q) & 1)) {
                    control_active = false;
                    break;
                }
            }
            if (control_active && ((i >> controller) & 1) && ((i >> target) & 1))
            {
                // Printing i when all conditions are satisfied
                std::swap(state[i], state[i - pow2(target)]);
            }
        }
    }

    void Simulator::rx_cont(size_t qn, double angle, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        if (global_controller.size() == 0)
        {
            rx(qn, angle, is_dagger);
            return;
        }
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

        // Rx 
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

        u22_cont(qn, unitary, global_controller);
    }


    void Simulator::sx_cont(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        if (global_controller.size() == 0)
        {
            sx(qn, is_dagger);
            return;
        }
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

        u22_t unitary;
        if (is_dagger)
        {
            unitary[0] = 0.5 * std::complex<double>(1, -1);
            unitary[2] = 0.5 * std::complex<double>(1, 1);
            unitary[1] = 0.5 * std::complex<double>(1, 1);
            unitary[3] = 0.5 * std::complex<double>(1, -1);
        }
        else
        {
            unitary[0] = 0.5 * std::complex<double>(1, 1);
            unitary[1] = 0.5 * std::complex<double>(1, -1);
            unitary[2] = 0.5 * std::complex<double>(1, -1);
            unitary[3] = 0.5 * std::complex<double>(1, 1);
        }

        u22_cont(qn, unitary, global_controller);
    }

    void Simulator::ry_cont(size_t qn, double angle, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        if (global_controller.size() == 0)
        {
            ry(qn, angle, is_dagger);
            return;
        }
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

        using namespace std::literals::complex_literals;
        u22_t unitary;
        if (is_dagger)
        {
            unitary = { cos(angle / 2), -sin(angle / 2),
                        sin(angle / 2), cos(angle / 2) };
        }
        else
        {
            unitary = { cos(angle / 2), sin(angle / 2),
                        -sin(angle / 2), cos(angle / 2) };
        }

        u22_cont(qn, unitary, global_controller);
    }

    void Simulator::rz_cont(size_t qn, double angle, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        if (global_controller.size() == 0)
        {
            rz(qn, angle, is_dagger);
            return;
        }
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if (!control_enable(i, global_controller))
                continue;
            if ((i >> qn) & 1)
            {
                if (is_dagger)
                {
                    state[i] *= std::complex(cos(angle), -sin(angle));
                }
                else
                {
                    state[i] *= std::complex(cos(angle), sin(angle));
                }
            }
        }
    }

    void Simulator::rphi90_cont(size_t qn, double phi, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        if (global_controller.size() == 0)
        {
            rphi90(qn, phi, is_dagger);
            return;
        }
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

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
        u22_cont(qn, unitary, global_controller);
    }

    void Simulator::rphi180_cont(size_t qn, double phi, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        if (global_controller.size() == 0)
        {
            rphi180(qn, phi, is_dagger);
            return;
        }
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

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
        u22_cont(qn, unitary, global_controller);
    }

    void Simulator::rphi_cont(size_t qn, double phi, double theta, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        if (global_controller.size() == 0)
        {
            rphi(qn, phi, theta, is_dagger);
            return;
        }
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

        using namespace std::literals::complex_literals;
        u22_t unitary;
        if (is_dagger)
        {
            unitary[0] = cos(theta / 2);
            unitary[2] = -1i * sin(theta / 2) * std::complex(-cos(phi), -sin(phi));
            unitary[1] = -1i * sin(theta / 2) * std::complex(-cos(phi), sin(phi));
            unitary[3] = cos(theta / 2);
        }
        else
        {
            unitary[0] = cos(theta / 2);
            unitary[1] = -1i * sin(theta / 2) * std::complex(cos(phi), -sin(phi));
            unitary[2] = -1i * sin(theta / 2) * std::complex(cos(phi), sin(phi));
            unitary[3] = cos(theta / 2);
        }
        u22_cont(qn, unitary, global_controller);
    }

    void Simulator::toffoli_cont(size_t qn1, size_t qn2, size_t target, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        if (global_controller.size() == 0)
        {
            toffoli(qn1, qn2, target, is_dagger);
            return;
        }
        if (qn1 >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn1 = {})", total_qubit, qn1);
            ThrowInvalidArgument(errstr);
        }
        if (qn2 >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn2 = {})", total_qubit, qn2);
            ThrowInvalidArgument(errstr);
        }
        if (target >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, target = {})", total_qubit, target);
            ThrowInvalidArgument(errstr);
        }

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if (!control_enable(i, global_controller))
                continue;
            if (((i >> qn1) & 1) && ((i >> qn2) & 1) && ((i >> target) & 1))
            {
                // |111> swap with |110>
                std::swap(state[i], state[i - pow2(target)]);
            }
        }
    }

    void Simulator::cswap_cont(size_t controller, size_t target1, size_t target2, const std::vector<size_t>& global_controller, bool is_dagger)
    {
        if (global_controller.size() == 0)
        {
            cswap(controller, target1, target2, is_dagger);
            return;
        }
        if (controller >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, controller = {})", total_qubit, controller);
            ThrowInvalidArgument(errstr);
        }
        if (target1 >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, target1 = {})", total_qubit, target1);
            ThrowInvalidArgument(errstr);
        }
        if (target2 >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, target2 = {})", total_qubit, target2);
            ThrowInvalidArgument(errstr);
        }

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if (!control_enable(i, global_controller))
                continue;
            if (!((i >> controller) & 1))
                continue;

            if (((i >> target1) & 1) && (!((i >> target2) & 1)))
            {
                // |10>
                // let it swap with |01>
                std::swap(state[i - pow2(target1) + pow2(target2)], state[i]);
            }
        }
    }
    
    bool Simulator::control_enable(size_t idx, const std::vector<size_t>& global_controller)
    {
        for (auto qid : global_controller)
        {
            // qid digit is 0, then disable
            if (!((idx >> qid) & 1)) return false;
        }
        // all 1, then enable
        return true;
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