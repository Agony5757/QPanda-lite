#include "simulator_impl.h"

namespace qpandalite {
    bool _assert_u22(const u22_t& u)
    {
        // u00 u01
        // u10 u11
        // U * U^dag = I
        auto a00 = u[0], a01 = u[1], a10 = u[2], a11 = u[3];
        auto b00 = std::conj(u[0]), b01 = std::conj(u[2]), b10 = std::conj(u[1]), b11 = std::conj(u[3]);
        if (!complex_equal(a00 * b00 + a01 * b10, 1))
        {
            return false;
        }
        if (!complex_equal(a00 * b01 + a01 * b11, 0))
        {
            return false;
        }
        if (!complex_equal(a10 * b00 + a11 * b10, 0))
        {
            return false;
        }
        if (!complex_equal(a10 * b01 + a11 * b11, 1))
        {
            return false;
        }
        return true;
    }
    std::map<size_t, size_t> preprocess_measure_list(const std::vector<size_t>& measure_list, size_t total_qubit)
    {
        if (measure_list.size() > total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, measure_list size = {})", total_qubit, measure_list.size());
            ThrowInvalidArgument(errstr);
        }

        std::map<size_t, size_t> qlist;
        for (size_t i = 0; i < measure_list.size(); ++i)
        {
            size_t qn = measure_list[i];
            if (qn >= total_qubit)
            {
                auto errstr = fmt::format("Exceed total (total_qubit = {}, measure_qubit = {})", total_qubit, qn);
                ThrowInvalidArgument(errstr);
            }
            if (qlist.find(qn) != qlist.end())
            {
                auto errstr = fmt::format("Duplicate measure qubit ({})", qn);
                ThrowInvalidArgument(errstr);
            }
            qlist.insert({ qn,i });
        }
        return qlist;
    }
    size_t get_state_with_qubit(size_t i, const std::map<size_t, size_t>& measure_map)
    {
        size_t ret = 0;
        for (auto&& [qn, j] : measure_map)
        {
            // put "digit qn" of i to "digit j"
            ret += (((i >> qn) & 1) << j);
        }
        return ret;
    }
    size_t make_controller_mask(const std::vector<size_t>& global_controller)
    {
        size_t mask = 0;
        for (size_t qn : global_controller)
        {
            mask |= (1ull << qn);
        }
        return mask;
    }
    void hadamard_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask)
    {
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;
            if ((i >> qn) & 1)
                continue;

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
    void u22_unsafe_impl(std::vector<std::complex<double>>& state, size_t qn, complex_t u00, complex_t u01, complex_t u10, complex_t u11, size_t total_qubit, size_t controller_mask)
    {
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;
            if ((i >> qn) & 1)
                continue;

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
    void u22_unsafe_impl(std::vector<std::complex<double>>& state, size_t qn, u22_t unitary, size_t total_qubit, size_t controller_mask)
    {
        return u22_unsafe_impl(state, qn, unitary[0], unitary[1], unitary[2], unitary[3], total_qubit, controller_mask);
    }
    void u3_unsafe_impl(std::vector<complex_t>& state, size_t qn, double theta, double phi, double lambda, size_t total_qubit, size_t controller_mask, bool is_dagger)
    {

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

        u22_unsafe_impl(state, qn, u00, u01, u10, u11, total_qubit, controller_mask);

    }
    void x_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask)
    {
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

            if ((i >> qn) & 1)
            {
                std::swap(state[i], state[i - pow2(qn)]);
            }
        }
    }
    void y_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask)
    {
        using namespace std::literals::complex_literals;
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

            if ((i >> qn) & 1)
            {
                std::swap(state[i], state[i - pow2(qn)]);
                state[i - pow2(qn)] *= -1i;
                state[i] *= 1i;
            }
        }
    }
    void z_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask)
    {
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

            if ((i >> qn) & 1)
            {
                state[i] *= -1;
            }
        }
    }
    void s_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask)
    {
        using namespace std::literals::complex_literals;
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

            if ((i >> qn) & 1)
            {
                state[i] *= 1i;
            }
        }
    }
    void sdg_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask)
    {
        using namespace std::literals::complex_literals;
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

            if ((i >> qn) & 1)
            {
                state[i] *= -1i;
            }
        }
    }
    void t_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask)
    {
        using namespace std::literals::complex_literals;

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

            if ((i >> qn) & 1)
            {
                state[i] *= complex_t(INVSQRT2, INVSQRT2);
            }
        }
    }
    void tdg_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask)
    {
        using namespace std::literals::complex_literals;

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

            if ((i >> qn) & 1)
            {
                state[i] *= complex_t(INVSQRT2, -INVSQRT2);
            }
        }
    }
    void cz_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, size_t total_qubit, size_t controller_mask)
    {
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

            if (((i >> qn1) & 1) && ((i >> qn2) & 1))
            {
                state[i] *= -1;
            }
        }
    }
    void swap_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, size_t total_qubit, size_t controller_mask)
    {
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
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
    void iswap_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, size_t total_qubit, size_t controller_mask, bool is_dagger)
    {
        using namespace std::literals::complex_literals;
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
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

    /* H = 1/2 * (XX+YY)

    XY(theta) = exp(-i*theta/2 * H)
    = [ 1 0 0 0 ]
    [ 0 cos(theta/2) -i sin(theta/2) 0 ]
    [ 0 -i sin(theta/2) cos(theta/2) 0 ]
    [ 0 0 0 1 ]
    */
    void xy_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta, size_t total_qubit, size_t controller_mask, bool is_dagger)
    {
        using namespace std::literals::complex_literals;
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;
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
    void cnot_unsafe_impl(std::vector<complex_t>& state, size_t controller, size_t target, size_t total_qubit, size_t controller_mask)
    {
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

            if (((i >> controller) & 1) && ((i >> target) & 1))
            {
                std::swap(state[i], state[i - pow2(target)]);
            }
        }
    }
    void rz_unsafe_impl(std::vector<complex_t>& state, size_t qn, double theta, size_t total_qubit, size_t controller_mask, bool is_dagger)
    {
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

            if (((i >> qn) & 1) ^ is_dagger)
            {
                // 0 and not dagger -> exp(-it/2)
                // 1 and dagger -> exp(-it/2)
                state[i] *= std::complex(cos(theta / 2), sin(theta / 2));
            }
            else
            {
                // 0 and dagger -> exp(it/2)
                // 1 and not dagger -> exp(it/2)
                state[i] *= std::complex(cos(theta / 2), -sin(theta / 2));
            }
        }
    }
    void u1_unsafe_impl(std::vector<complex_t>& state, size_t qn, double theta, size_t total_qubit, size_t controller_mask, bool is_dagger)
    {
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

            if ((i >> qn) & 1)
            {
                if (is_dagger)
                    state[i] *= std::complex(cos(theta), -sin(theta));
                else
                    state[i] *= std::complex(cos(theta), sin(theta));
            }
        }
    }
    void toffoli_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, size_t target, size_t total_qubit, size_t controller_mask)
    {
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

            if (((i >> qn1) & 1) && ((i >> qn2) & 1) && ((i >> target) & 1))
            {
                std::swap(state[i], state[i - pow2(target)]);
            }
        }
    }
    void cswap_unsafe_impl(std::vector<complex_t>& state, size_t controller, size_t target1, size_t target2, size_t total_qubit, size_t controller_mask)
    {
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;

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
    * exp(-i*theta/2 * ZZ)
    *    |00> -> exp(-i*theta/2) * |00>
    *    |01> -> exp(i*theta/2) * |01>
    *    |10> -> exp(i*theta/2) * |10>
    *    |11> -> exp(-i*theta/2) * |11>
    */
    void zz_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta, size_t total_qubit, size_t controller_mask)
    {
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;
            bool v1 = (i >> qn1) & 1;
            bool v2 = (i >> qn2) & 1;
            if (v1 == v2) /* 00 or 11 */
            {
                state[i] *= complex_t(cos(theta / 2), sin(-theta / 2));
            }
            else /* 01 or 10 */
            {
                state[i] *= complex_t(cos(theta / 2), sin(theta / 2));
            }
        }
    }

    /* XX interaction
    * exp(-i*theta/2 * XX)
    *    |00> -> [ cos(t)    0       0      isin(t) ]
    *    |01> -> [   0     cos(t)  isin(t)    0     ]
    *    |10> -> [   0     isin(t)  cos(t)    0     ]
    *    |11> -> [ isin(t)   0       0       cos(t) ] where t=-theta/2
    */
    void xx_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta, size_t total_qubit, size_t controller_mask)
    {
        using namespace std::literals::complex_literals;

        /* the RXX will be implemented as exp(-i*theta/2 * XX) */
        theta = -theta / 2;

        complex_t ctheta = cos(theta);
        complex_t stheta = sin(theta);
        complex_t istheta = 1i * stheta;

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;
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
    *
    * exp(-i*theta/2 * YY)
    *    |00> -> [ cos(t)    0       0      -isin(t) ]
    *    |01> -> [   0     cos(t)  isin(t)    0     ]
    *    |10> -> [   0     isin(t)  cos(t)    0     ]
    *    |11> -> [ -isin(t)   0       0       cos(t) ] where t=-theta/2
    */
    void yy_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta, size_t total_qubit, size_t controller_mask)
    {
        using namespace std::literals::complex_literals;

        /* the RYY will be implemented as exp(-i*theta/2 * YY) */
        theta = -theta / 2;

        complex_t ctheta = cos(theta);
        complex_t stheta = sin(theta);
        complex_t istheta = 1i * stheta;

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i & controller_mask) != controller_mask)
                continue;
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

    /* uu15 gate using KAK decomposition

    U is implemented by

    U3(q1, parameters[0:3])
    U3(q2, parameters[3:6])
    XX(q1, q2, parameters[6])
    YY(q1, q2, parameters[7])
    ZZ(q1, q2, parameters[8])
    U3(q1, parameters[9:12])
    U3(q2, parameters[12:15])

    where parameters[0:15] are the 15 parameters of the gate.
    */
    void uu15_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, const std::vector<double>& parameters, size_t total_qubit, size_t controller_mask, bool is_dagger)
    {
        using namespace std::literals::complex_literals;

        if (!is_dagger)
        {
            /* U3(q1, parameters[0:3]) */
            double theta1 = parameters[0];
            double phi1 = parameters[1];
            double lambda1 = parameters[2];
            u3_unsafe_impl(state, qn1, theta1, phi1, lambda1, total_qubit, controller_mask, false);

            /* U3(q2, parameters[3:6]) */
            double theta2 = parameters[3];
            double phi2 = parameters[4];
            double lambda2 = parameters[5];
            u3_unsafe_impl(state, qn2, theta2, phi2, lambda2, total_qubit, controller_mask, false);

            /* XX(q1, q2, parameters[6]) */
            double theta_xx = parameters[6];
            xx_unsafe_impl(state, qn1, qn2, theta_xx, total_qubit, controller_mask);

            /* YY(q1, q2, parameters[7]) */
            double theta_yy = parameters[7];
            yy_unsafe_impl(state, qn1, qn2, theta_yy, total_qubit, controller_mask);

            /* ZZ(q1, q2, parameters[8]) */
            double theta_zz = parameters[8];
            zz_unsafe_impl(state, qn1, qn2, theta_zz, total_qubit, controller_mask);

            /* U3(q1, parameters[9:12]) */
            double theta3 = parameters[9];
            double phi3 = parameters[10];
            double lambda3 = parameters[11];
            u3_unsafe_impl(state, qn1, theta3, phi3, lambda3, total_qubit, controller_mask, false);

            /* U3(q2, parameters[12:15]) */
            double theta4 = parameters[12];
            double phi4 = parameters[13];
            double lambda4 = parameters[14];
            u3_unsafe_impl(state, qn2, theta4, phi4, lambda4, total_qubit, controller_mask, false);
        }
        else /* dagger case*/
        {
            /* U3(q1, parameters[9:12]) */
            double theta3 = parameters[9];
            double phi3 = parameters[10];
            double lambda3 = parameters[11];
            u3_unsafe_impl(state, qn1, theta3, phi3, lambda3, total_qubit, controller_mask, true);

            /* U3(q2, parameters[12:15]) */
            double theta4 = parameters[12];
            double phi4 = parameters[13];
            double lambda4 = parameters[14];
            u3_unsafe_impl(state, qn2, theta4, phi4, lambda4, total_qubit, controller_mask, true);

            /* ZZ(q1, q2, parameters[8]) */
            double theta_zz = parameters[8];
            theta_zz = -theta_zz;
            zz_unsafe_impl(state, qn1, qn2, theta_zz, total_qubit, controller_mask);

            /* YY(q1, q2, parameters[7]) */
            double theta_yy = parameters[7];
            theta_yy = -theta_yy;
            yy_unsafe_impl(state, qn1, qn2, theta_yy, total_qubit, controller_mask);

            /* XX(q1, q2, parameters[6]) */
            double theta_xx = parameters[6];
            theta_xx = -theta_xx;
            xx_unsafe_impl(state, qn1, qn2, theta_xx, total_qubit, controller_mask);

            /* U3(q2, parameters[3:6]) */
            double theta2 = parameters[3];
            double phi2 = parameters[4];
            double lambda2 = parameters[5];
            u3_unsafe_impl(state, qn2, theta2, phi2, lambda2, total_qubit, controller_mask, true);

            /* U3(q1, parameters[0:3]) */
            double theta1 = parameters[0];
            double phi1 = parameters[1];
            double lambda1 = parameters[2];
            u3_unsafe_impl(state, qn1, theta1, phi1, lambda1, total_qubit, controller_mask, true);
        }

    }
}