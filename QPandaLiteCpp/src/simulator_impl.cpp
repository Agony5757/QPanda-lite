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

    namespace statevector_simulator_impl {
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

        /* u1(qn1, theta1),
           u1(qn2, theta2),
           zz(qn1, qn2, thetazz)
        */
        void phase2q_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta1, double theta2, double thetazz,
            size_t total_qubit, size_t controller_mask)
        {
            using namespace std::literals::complex_literals;

            /* u1(qn1, theta1) */
            u1_unsafe_impl(state, qn1, theta1, total_qubit, controller_mask, false);

            /* u1(qn2, theta2) */
            u1_unsafe_impl(state, qn2, theta2, total_qubit, controller_mask, false);

            /* zz(qn1, qn2, thetazz) */
            zz_unsafe_impl(state, qn1, qn2, thetazz, total_qubit, controller_mask);
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
    } // namespace statevector_simulator_impl

    namespace density_operator_simulator_impl
    {
        complex_t& val(std::vector<complex_t>& state, size_t i, size_t j, size_t N)
        {
            return state[i * N + j];
        }

        complex_t val(const std::vector<complex_t>& state, size_t i, size_t j, size_t N)
        {
            return state[i * N + j];
        }

        void evolve_u22(const u22_t& mat, complex_t& i0j0, complex_t& i0j1, complex_t& i1j0, complex_t& i1j1)
        {
            const complex_t& U00 = mat[0];
            const complex_t& U01 = mat[1];
            const complex_t& U10 = mat[2];
            const complex_t& U11 = mat[3];

            evolve_u22(U00, U01, U10, U11, i0j0, i0j1, i1j0, i1j1);
        }

        void evolve_u22(const complex_t& U00, const complex_t & U01, const complex_t & U10, const complex_t & U11,
            complex_t &i0j0, complex_t& i0j1, complex_t &i1j0, complex_t &i1j1)
        {
            const complex_t orig_i0j0 = i0j0;
            const complex_t orig_i0j1 = i0j1;
            const complex_t orig_i1j0 = i1j0;
            const complex_t orig_i1j1 = i1j1;

            // T = U * ρ_block
            const complex_t T00 = U00 * orig_i0j0 + U01 * orig_i1j0;
            const complex_t T01 = U00 * orig_i0j1 + U01 * orig_i1j1;
            const complex_t T10 = U10 * orig_i0j0 + U11 * orig_i1j0;
            const complex_t T11 = U10 * orig_i0j1 + U11 * orig_i1j1;

            // ρ_block' = T * U†
            i0j0 = T00 * std::conj(U00) + T01 * std::conj(U01); // (0,0)
            i0j1 = T00 * std::conj(U10) + T01 * std::conj(U11); // (0,1)
            i1j0 = T10 * std::conj(U00) + T11 * std::conj(U01); // (1,0)
            i1j1 = T10 * std::conj(U10) + T11 * std::conj(U11); // (1,1)
        }

        void evolve_u44(
            const complex_t& U00, const complex_t& U01, const complex_t& U02, const complex_t& U03,
            const complex_t& U10, const complex_t& U11, const complex_t& U12, const complex_t& U13,
            const complex_t& U20, const complex_t& U21, const complex_t& U22, const complex_t& U23,
            const complex_t& U30, const complex_t& U31, const complex_t& U32, const complex_t& U33,
            complex_t& i00j00, complex_t& i00j01, complex_t& i00j10, complex_t& i00j11,
            complex_t& i01j00, complex_t& i01j01, complex_t& i01j10, complex_t& i01j11,
            complex_t& i10j00, complex_t& i10j01, complex_t& i10j10, complex_t& i10j11,
            complex_t& i11j00, complex_t& i11j01, complex_t& i11j10, complex_t& i11j11
        ) {
            // 保存原始值
            const complex_t orig_i00j00 = i00j00, orig_i00j01 = i00j01, orig_i00j10 = i00j10, orig_i00j11 = i00j11;
            const complex_t orig_i01j00 = i01j00, orig_i01j01 = i01j01, orig_i01j10 = i01j10, orig_i01j11 = i01j11;
            const complex_t orig_i10j00 = i10j00, orig_i10j01 = i10j01, orig_i10j10 = i10j10, orig_i10j11 = i10j11;
            const complex_t orig_i11j00 = i11j00, orig_i11j01 = i11j01, orig_i11j10 = i11j10, orig_i11j11 = i11j11;

            // 计算中间矩阵 T = U * ρ_block
            const complex_t T00 = U00 * orig_i00j00 + U01 * orig_i01j00 + U02 * orig_i10j00 + U03 * orig_i11j00;
            const complex_t T01 = U00 * orig_i00j01 + U01 * orig_i01j01 + U02 * orig_i10j01 + U03 * orig_i11j01;
            const complex_t T02 = U00 * orig_i00j10 + U01 * orig_i01j10 + U02 * orig_i10j10 + U03 * orig_i11j10;
            const complex_t T03 = U00 * orig_i00j11 + U01 * orig_i01j11 + U02 * orig_i10j11 + U03 * orig_i11j11;

            const complex_t T10 = U10 * orig_i00j00 + U11 * orig_i01j00 + U12 * orig_i10j00 + U13 * orig_i11j00;
            const complex_t T11 = U10 * orig_i00j01 + U11 * orig_i01j01 + U12 * orig_i10j01 + U13 * orig_i11j01;
            const complex_t T12 = U10 * orig_i00j10 + U11 * orig_i01j10 + U12 * orig_i10j10 + U13 * orig_i11j10;
            const complex_t T13 = U10 * orig_i00j11 + U11 * orig_i01j11 + U12 * orig_i10j11 + U13 * orig_i11j11;

            const complex_t T20 = U20 * orig_i00j00 + U21 * orig_i01j00 + U22 * orig_i10j00 + U23 * orig_i11j00;
            const complex_t T21 = U20 * orig_i00j01 + U21 * orig_i01j01 + U22 * orig_i10j01 + U23 * orig_i11j01;
            const complex_t T22 = U20 * orig_i00j10 + U21 * orig_i01j10 + U22 * orig_i10j10 + U23 * orig_i11j10;
            const complex_t T23 = U20 * orig_i00j11 + U21 * orig_i01j11 + U22 * orig_i10j11 + U23 * orig_i11j11;

            const complex_t T30 = U30 * orig_i00j00 + U31 * orig_i01j00 + U32 * orig_i10j00 + U33 * orig_i11j00;
            const complex_t T31 = U30 * orig_i00j01 + U31 * orig_i01j01 + U32 * orig_i10j01 + U33 * orig_i11j01;
            const complex_t T32 = U30 * orig_i00j10 + U31 * orig_i01j10 + U32 * orig_i10j10 + U33 * orig_i11j10;
            const complex_t T33 = U30 * orig_i00j11 + U31 * orig_i01j11 + U32 * orig_i10j11 + U33 * orig_i11j11;

            // 计算最终结果 ρ_block' = T * U†
            // 第一行
            i00j00 = T00 * std::conj(U00) + T01 * std::conj(U10) + T02 * std::conj(U20) + T03 * std::conj(U30);
            i00j01 = T00 * std::conj(U01) + T01 * std::conj(U11) + T02 * std::conj(U21) + T03 * std::conj(U31);
            i00j10 = T00 * std::conj(U02) + T01 * std::conj(U12) + T02 * std::conj(U22) + T03 * std::conj(U32);
            i00j11 = T00 * std::conj(U03) + T01 * std::conj(U13) + T02 * std::conj(U23) + T03 * std::conj(U33);

            // 第二行
            i01j00 = T10 * std::conj(U00) + T11 * std::conj(U10) + T12 * std::conj(U20) + T13 * std::conj(U30);
            i01j01 = T10 * std::conj(U01) + T11 * std::conj(U11) + T12 * std::conj(U21) + T13 * std::conj(U31);
            i01j10 = T10 * std::conj(U02) + T11 * std::conj(U12) + T12 * std::conj(U22) + T13 * std::conj(U32);
            i01j11 = T10 * std::conj(U03) + T11 * std::conj(U13) + T12 * std::conj(U23) + T13 * std::conj(U33);

            // 第三行
            i10j00 = T20 * std::conj(U00) + T21 * std::conj(U10) + T22 * std::conj(U20) + T23 * std::conj(U30);
            i10j01 = T20 * std::conj(U01) + T21 * std::conj(U11) + T22 * std::conj(U21) + T23 * std::conj(U31);
            i10j10 = T20 * std::conj(U02) + T21 * std::conj(U12) + T22 * std::conj(U22) + T23 * std::conj(U32);
            i10j11 = T20 * std::conj(U03) + T21 * std::conj(U13) + T22 * std::conj(U23) + T23 * std::conj(U33);

            // 第四行
            i11j00 = T30 * std::conj(U00) + T31 * std::conj(U10) + T32 * std::conj(U20) + T33 * std::conj(U30);
            i11j01 = T30 * std::conj(U01) + T31 * std::conj(U11) + T32 * std::conj(U21) + T33 * std::conj(U31);
            i11j10 = T30 * std::conj(U02) + T31 * std::conj(U12) + T32 * std::conj(U22) + T33 * std::conj(U32);
            i11j11 = T30 * std::conj(U03) + T31 * std::conj(U13) + T32 * std::conj(U23) + T33 * std::conj(U33);
        }

        void hadamard_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask)
        {
            return u22_unsafe_impl(state, qn,
                INVSQRT2, INVSQRT2, INVSQRT2, -INVSQRT2,
                total_qubit, controller_mask
            );
        }

        void _u22_unsafe_impl_ctrl(std::vector<std::complex<double>>& state, size_t qn, complex_t u00, complex_t u01, complex_t u10, complex_t u11, size_t total_qubit, size_t controller_mask)
        {
            const size_t N = pow2(total_qubit);
            const size_t mask = pow2(qn);

            for (size_t i = 0; i < N; ++i) {
                if ((i & mask) != 0) continue;
                // 行控制位状态 (a): 0 或 1
                const bool a = ((i & controller_mask) == controller_mask);

                for (size_t j = 0; j < N; ++j) {
                    if ((j & mask) != 0) continue;
                    // 列控制位状态 (b): 0 或 1
                    const bool b = ((j & controller_mask) == controller_mask);

                    // 提取目标量子比特的子矩阵元素
                    complex_t& elem_00 = val(state, i, j, N);
                    complex_t& elem_01 = val(state, i, j + mask, N);
                    complex_t& elem_10 = val(state, i + mask, j, N);
                    complex_t& elem_11 = val(state, i + mask, j + mask, N);

                    // 根据 (a, b) 组合处理子矩阵
                    if (!a && !b) {
                        // Case 00: IρI → 无需修改
                        continue;
                    }
                    else if (!a && b) {
                        // Case 01: IρU† → 右乘 U†
                        const complex_t orig_00 = elem_00, orig_01 = elem_01;
                        const complex_t orig_10 = elem_10, orig_11 = elem_11;

                        elem_00 = orig_00 * std::conj(u00) + orig_01 * std::conj(u10);
                        elem_01 = orig_00 * std::conj(u01) + orig_01 * std::conj(u11);
                        elem_10 = orig_10 * std::conj(u00) + orig_11 * std::conj(u10);
                        elem_11 = orig_10 * std::conj(u01) + orig_11 * std::conj(u11);
                    }
                    else if (a && !b) {
                        // Case 10: UρI → 左乘 U
                        const complex_t orig_00 = elem_00, orig_01 = elem_01;
                        const complex_t orig_10 = elem_10, orig_11 = elem_11;

                        elem_00 = u00 * orig_00 + u01 * orig_10;
                        elem_01 = u00 * orig_01 + u01 * orig_11;
                        elem_10 = u10 * orig_00 + u11 * orig_10;
                        elem_11 = u10 * orig_01 + u11 * orig_11;
                    }
                    else {
                        // Case 11: UρU† → 完全演化
                        evolve_u22(u00, u01, u10, u11, elem_00, elem_01, elem_10, elem_11);
                    }
                }
            }
        }

        void u22_unsafe_impl(std::vector<std::complex<double>>& state, size_t qn, complex_t u00, complex_t u01, complex_t u10, complex_t u11, size_t total_qubit, size_t controller_mask)
        {
            /* control version must be specially handled */
            if (controller_mask != 0)
            {
                _u22_unsafe_impl_ctrl(state, qn, u00, u01, u10, u11, total_qubit, controller_mask);
                return;
            }

            const size_t N = pow2(total_qubit);
            const size_t mask = pow2(qn);            // 目标量子比特的掩码

            for (size_t i = 0; i < N; ++i) {
                // 检查控制位是否满足且目标比特为 0
                if ((i & mask) != 0) continue;

                // 遍历所有满足控制位且目标比特为 0 的 j
                for (size_t j = 0; j < N; ++j) {
                    if ((j & mask) != 0) continue;

                    // 提取子矩阵元素（无需重复计算索引）
                    complex_t& i0j0 = val(state, i, j, N);
                    complex_t& i1j0 = val(state, i + mask, j, N);
                    complex_t& i0j1 = val(state, i, j + mask, N);
                    complex_t& i1j1 = val(state, i + mask, j + mask, N);

                    // 应用演化
                    evolve_u22(u00, u01, u10, u11, i0j0, i1j0, i0j1, i1j1);
                }
            }
        }


        void u44_unsafe_impl(std::vector<std::complex<double>>& state, size_t qn1, size_t qn2,
            complex_t u00, complex_t u01, complex_t u02, complex_t u03,
            complex_t u10, complex_t u11, complex_t u12, complex_t u13,
            complex_t u20, complex_t u21, complex_t u22, complex_t u23,
            complex_t u30, complex_t u31, complex_t u32, complex_t u33,
            size_t total_qubit, size_t controller_mask) {

            const size_t N = pow2(total_qubit);
            const size_t mask1 = pow2(qn1);
            const size_t mask2 = pow2(qn2);

            for (size_t i = 0; i < N; ++i) {
                // 提前过滤条件：控制位 + 目标量子比特为 0
                if ((i & controller_mask) != controller_mask) continue;
                if ((i & (mask1 | mask2)) != 0) continue;

                for (size_t j = 0; j < N; ++j) {
                    if ((j & controller_mask) != controller_mask) continue;
                    if ((j & (mask1 | mask2)) != 0) continue;

                    // 提取子矩阵引用
                    complex_t& i00j00 = val(state, i, j, N);
                    complex_t& i01j00 = val(state, i + mask1, j, N);
                    complex_t& i10j00 = val(state, i + mask2, j, N);
                    complex_t& i11j00 = val(state, i + mask1 + mask2, j, N);

                    complex_t& i00j01 = val(state, i, j + mask1, N);
                    complex_t& i01j01 = val(state, i + mask1, j + mask1, N);
                    complex_t& i10j01 = val(state, i + mask2, j + mask1, N);
                    complex_t& i11j01 = val(state, i + mask1 + mask2, j + mask1, N);

                    complex_t& i00j10 = val(state, i, j + mask2, N);
                    complex_t& i01j10 = val(state, i + mask1, j + mask2, N);
                    complex_t& i10j10 = val(state, i + mask2, j + mask2, N);
                    complex_t& i11j10 = val(state, i + mask1 + mask2, j + mask2, N);

                    complex_t& i00j11 = val(state, i, j + mask1 + mask2, N);
                    complex_t& i01j11 = val(state, i + mask1, j + mask1 + mask2, N);
                    complex_t& i10j11 = val(state, i + mask2, j + mask1 + mask2, N);
                    complex_t& i11j11 = val(state, i + mask1 + mask2, j + mask1 + mask2, N);

                    // evolve_u44 
                    evolve_u44(u00, u01, u02, u03,
                        u10, u11, u12, u13,
                        u20, u21, u22, u23,
                        u30, u31, u32, u33,
                        i00j00, i01j00, i10j00, i11j00,
                        i00j01, i01j01, i10j01, i11j01,
                        i00j10, i01j10, i10j10, i11j10,
                        i00j11, i01j11, i10j11, i11j11
                    );
                   
                }
            }
        }

        void u22_unsafe_impl(std::vector<std::complex<double>>& state, size_t qn, u22_t unitary, size_t total_qubit, size_t controller_mask)
        {
            return u22_unsafe_impl(state, qn, unitary[0], unitary[1], unitary[2], unitary[3],
                total_qubit, controller_mask);
        }

        void u3_unsafe_impl(std::vector<complex_t>& state, size_t qn,
            double theta, double phi, double lambda,
            size_t total_qubit, size_t controller_mask, bool is_dagger) {
            // U3 门的矩阵元素
            complex_t U00 = std::cos(theta / 2);
            complex_t U01 = -std::exp(complex_t(0, lambda)) * std::sin(theta / 2);
            complex_t U10 = std::exp(complex_t(0, phi)) * std::sin(theta / 2);
            complex_t U11 = std::exp(complex_t(0, phi + lambda)) * std::cos(theta / 2);

            // 如果是共轭转置，取共轭
            if (is_dagger) {
                U01 = std::conj(U01);
                U10 = std::conj(U10);
                std::swap(U00, U11);
            }

            // 调用 u22_unsafe_impl
            u22_unsafe_impl(state, qn, U00, U01, U10, U11, total_qubit, controller_mask);
        }

        void x_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask) {
            // Pauli-X 门的矩阵元素
            complex_t U00 = 0, U01 = 1, U10 = 1, U11 = 0;

            // 调用 u22_unsafe_impl
            u22_unsafe_impl(state, qn, U00, U01, U10, U11, total_qubit, controller_mask);
        }

        void y_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask) {
            // Pauli-Y 门的矩阵元素
            complex_t U00 = 0, U01 = complex_t(0, -1), U10 = complex_t(0, 1), U11 = 0;

            // 调用 u22_unsafe_impl
            u22_unsafe_impl(state, qn, U00, U01, U10, U11, total_qubit, controller_mask);
        }

        void z_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask) {
            // Pauli-Z 门的矩阵元素
            complex_t U00 = 1, U01 = 0, U10 = 0, U11 = -1;

            // 调用 u22_unsafe_impl
            u22_unsafe_impl(state, qn, U00, U01, U10, U11, total_qubit, controller_mask);
        }

        void s_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask) {
            // S 门的矩阵元素
            complex_t U00 = 1, U01 = 0, U10 = 0, U11 = complex_t(0, 1);

            // 调用 u22_unsafe_impl
            u22_unsafe_impl(state, qn, U00, U01, U10, U11, total_qubit, controller_mask);
        }

        void sdg_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask) {
            // S† 门的矩阵元素
            complex_t U00 = 1, U01 = 0, U10 = 0, U11 = complex_t(0, -1);

            // 调用 u22_unsafe_impl
            u22_unsafe_impl(state, qn, U00, U01, U10, U11, total_qubit, controller_mask);
        }

        void t_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask) {
            // T 门的矩阵元素
            complex_t U00 = 1, U01 = 0, U10 = 0, U11 = complex_t(INVSQRT2, INVSQRT2);

            // 调用 u22_unsafe_impl
            u22_unsafe_impl(state, qn, U00, U01, U10, U11, total_qubit, controller_mask);
        }
        
        void tdg_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask) {
            // T† 门的矩阵元素
            complex_t U00 = 1, U01 = 0, U10 = 0, U11 = complex_t(INVSQRT2, -INVSQRT2);

            // 调用 u22_unsafe_impl
            u22_unsafe_impl(state, qn, U00, U01, U10, U11, total_qubit, controller_mask);
        }

        void cz_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2,
            size_t total_qubit, size_t controller_mask) {
            complex_t U00 = 1, U01 = 0, U02 = 0, U03 = 0;
            complex_t U10 = 0, U11 = 1, U12 = 0, U13 = 0;
            complex_t U20 = 0, U21 = 0, U22 = 1, U23 = 0;
            complex_t U30 = 0, U31 = 0, U32 = 0, U33 = -1;

            u44_unsafe_impl(state, qn1, qn2,
                U00, U01, U02, U03,
                U10, U11, U12, U13,
                U20, U21, U22, U23,
                U30, U31, U32, U33,
                total_qubit, controller_mask);
        }

        void swap_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2,
            size_t total_qubit, size_t controller_mask) {
            // SWAP 门的 4x4 矩阵
            complex_t U00 = 1, U01 = 0, U02 = 0, U03 = 0;
            complex_t U10 = 0, U11 = 0, U12 = 1, U13 = 0;
            complex_t U20 = 0, U21 = 1, U22 = 0, U23 = 0;
            complex_t U30 = 0, U31 = 0, U32 = 0, U33 = 1;

            u44_unsafe_impl(state, qn1, qn2,
                U00, U01, U02, U03,
                U10, U11, U12, U13,
                U20, U21, U22, U23,
                U30, U31, U32, U33,
                total_qubit, controller_mask);
        }

        void iswap_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2,
            size_t total_qubit, size_t controller_mask, bool is_dagger) {
            // iSWAP 门的 4x4 矩阵
            complex_t i = complex_t(0, 1);
            complex_t U00 = 1, U01 = 0, U02 = 0, U03 = 0;
            complex_t U10 = 0, U11 = 0, U12 = (is_dagger ? -i : i), U13 = 0;
            complex_t U20 = 0, U21 = (is_dagger ? -i : i), U22 = 0, U23 = 0;
            complex_t U30 = 0, U31 = 0, U32 = 0, U33 = 1;

            u44_unsafe_impl(state, qn1, qn2,
                U00, U01, U02, U03,
                U10, U11, U12, U13,
                U20, U21, U22, U23,
                U30, U31, U32, U33,
                total_qubit, controller_mask);
        }

        void xy_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2,
            double theta, size_t total_qubit, size_t controller_mask, bool is_dagger) {
            double t = theta / 2;
            complex_t cos_t = std::cos(t);
            complex_t sin_t = (is_dagger ? -complex_t(0, 1) : complex_t(0, 1)) * std::sin(t);

            // XY 门的 4x4 矩阵
            complex_t U00 = 1, U01 = 0, U02 = 0, U03 = 0;
            complex_t U10 = 0, U11 = cos_t, U12 = sin_t, U13 = 0;
            complex_t U20 = 0, U21 = sin_t, U22 = cos_t, U23 = 0;
            complex_t U30 = 0, U31 = 0, U32 = 0, U33 = 1;

            u44_unsafe_impl(state, qn1, qn2,
                U00, U01, U02, U03,
                U10, U11, U12, U13,
                U20, U21, U22, U23,
                U30, U31, U32, U33,
                total_qubit, controller_mask);
        }

        void cnot_unsafe_impl(std::vector<complex_t>& state, size_t controller, size_t target,
            size_t total_qubit, size_t controller_mask) {

            //// 合并控制位掩码：原有控制位 + qn1 和 qn2
            //const size_t new_controller_mask = controller_mask | pow2(controller);

            //// 调用 X 门，目标为 target，控制位为 new_controller_mask
            //x_unsafe_impl(state, target, total_qubit, new_controller_mask);
            // 定义 4x4 酉矩阵（例如 CNOT 门）
            complex_t u00 = 1, u01 = 0, u02 = 0, u03 = 0;
            complex_t u10 = 0, u11 = 1, u12 = 0, u13 = 0;
            complex_t u20 = 0, u21 = 0, u22 = 0, u23 = 1;
            complex_t u30 = 0, u31 = 0, u32 = 1, u33 = 0;

            u44_unsafe_impl(state, target, controller,
                u00, u01, u02, u03,
                u10, u11, u12, u13,
                u20, u21, u22, u23,
                u30, u31, u32, u33,
                total_qubit, controller_mask);

        }

        void rx_unsafe_impl(std::vector<complex_t>& state, size_t qn, double theta,
            size_t total_qubit, size_t controller_mask, bool is_dagger) {
            double half_theta = theta / 2.0;
            if (is_dagger) {
                half_theta = -half_theta; // 共轭转置等价于反向旋转
            }

            complex_t cos_t = std::cos(half_theta);
            complex_t sin_t = complex_t(0, -1) * std::sin(half_theta); // -i*sin(theta/2)

            // RX 的矩阵元素
            complex_t U00 = cos_t;
            complex_t U01 = sin_t;
            complex_t U10 = sin_t;
            complex_t U11 = cos_t;

            // 调用 u22_unsafe_impl
            u22_unsafe_impl(state, qn, U00, U01, U10, U11, total_qubit, controller_mask);
        }

        void ry_unsafe_impl(std::vector<complex_t>& state, size_t qn, double theta,
            size_t total_qubit, size_t controller_mask, bool is_dagger) {
            double half_theta = theta / 2.0;
            if (is_dagger) {
                half_theta = -half_theta; // 共轭转置等价于反向旋转
            }

            complex_t cos_t = std::cos(half_theta);
            complex_t sin_t = std::sin(half_theta);

            // RY 的矩阵元素
            complex_t U00 = cos_t;
            complex_t U01 = -sin_t; // 注意负号
            complex_t U10 = sin_t;
            complex_t U11 = cos_t;

            // 调用 u22_unsafe_impl
            u22_unsafe_impl(state, qn, U00, U01, U10, U11, total_qubit, controller_mask);
        }

        void rz_unsafe_impl(std::vector<complex_t>& state, size_t qn, double theta,
            size_t total_qubit, size_t controller_mask, bool is_dagger) {
            double angle = theta / 2;
            complex_t phase = std::exp(complex_t(0, (is_dagger ? -1 : 1) * angle));
            complex_t U00 = std::conj(phase); // 对角元素取共轭
            complex_t U11 = phase;

            u22_unsafe_impl(state, qn, U00, 0, 0, U11, total_qubit, controller_mask);
        }

        void u1_unsafe_impl(std::vector<complex_t>& state, size_t qn, double theta,
            size_t total_qubit, size_t controller_mask, bool is_dagger) {
            complex_t phase = std::exp(complex_t(0, (is_dagger ? -1 : 1) * theta));
            
            complex_t U00 = 1, U01 = 0, U10 = 0, U11 = phase;

            u22_unsafe_impl(state, qn, U00, U01, U10, U11, total_qubit, controller_mask);
        }

        void toffoli_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, size_t target,
            size_t total_qubit, size_t controller_mask) {
            // 合并控制位掩码：原有控制位 + qn1 和 qn2
            const size_t new_controller_mask = controller_mask | pow2(qn1) | pow2(qn2);

            // 调用 X 门，目标为 target，控制位为 new_controller_mask
            x_unsafe_impl(state, target, total_qubit, new_controller_mask);
        }

        void cswap_unsafe_impl(std::vector<complex_t>& state, size_t controller,
            size_t target1, size_t target2,
            size_t total_qubit, size_t controller_mask) {
            // 合并控制位掩码：原有控制位 + controller
            const size_t new_controller_mask = controller_mask | pow2(controller);

            // 调用 SWAP 门，目标为 target1 和 target2，控制位为 new_controller_mask
            swap_unsafe_impl(state, target1, target2, total_qubit, new_controller_mask);
        }

        void cu1_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta,
            size_t total_qubit, size_t controller_mask, bool is_dagger) {
            const complex_t phase_11 = std::exp(complex_t(0, is_dagger ? -theta : theta)); // |11> 的相位

            // 定义 ZZ 门的对角矩阵
            u44_unsafe_impl(state, qn1, qn2,
                1, 0, 0, 0,
                0, 1, 0, 0,
                0, 0, 1, 0,
                0, 0, 0, phase_11,
                total_qubit, controller_mask);
        }

        void zz_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta,
            size_t total_qubit, size_t controller_mask) {
            const complex_t phase_00_11 = std::exp(complex_t(0, -theta / 2)); // |00> 和 |11> 的相位
            const complex_t phase_01_10 = std::exp(complex_t(0, theta / 2));  // |01> 和 |10> 的相位

            // 定义 ZZ 门的对角矩阵
            u44_unsafe_impl(state, qn1, qn2,
                phase_00_11, 0, 0, 0,
                0, phase_01_10, 0, 0,
                0, 0, phase_01_10, 0,
                0, 0, 0, phase_00_11,
                total_qubit, controller_mask);
        }

        void xx_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta,
            size_t total_qubit, size_t controller_mask) {
            const double t = -theta / 2;
            const complex_t cos_t = std::cos(t);
            const complex_t i_sin_t = complex_t(0, 1) * std::sin(t); // i*sin(t)

            // 定义 XX 门的矩阵
            u44_unsafe_impl(state, qn1, qn2,
                cos_t, 0, 0, i_sin_t,
                0, cos_t, i_sin_t, 0,
                0, i_sin_t, cos_t, 0,
                i_sin_t, 0, 0, cos_t,
                total_qubit, controller_mask);
        }

        void yy_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta,
            size_t total_qubit, size_t controller_mask) {
            const double t = -theta / 2;
            const complex_t cos_t = std::cos(t);
            const complex_t i_sin_t_pos = complex_t(0, 1) * std::sin(t);  // +i*sin(t)
            const complex_t i_sin_t_neg = complex_t(0, -1) * std::sin(t); // -i*sin(t)

            // 定义 YY 门的矩阵
            u44_unsafe_impl(state, qn1, qn2,
                cos_t, 0, 0, i_sin_t_neg,
                0, cos_t, i_sin_t_pos, 0,
                0, i_sin_t_pos, cos_t, 0,
                i_sin_t_neg, 0, 0, cos_t,
                total_qubit, controller_mask);
        }

        /* u1(qn1, theta1),
           u1(qn2, theta2),
           zz(qn1, qn2, thetazz)
        */
        void phase2q_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, double theta1, double theta2, double thetazz,
            size_t total_qubit, size_t controller_mask)
        {
            using namespace std::literals::complex_literals;

            /* u1(qn1, theta1) */
            u1_unsafe_impl(state, qn1, theta1, total_qubit, controller_mask, false);

            /* u1(qn2, theta2) */
            u1_unsafe_impl(state, qn2, theta2, total_qubit, controller_mask, false);

            /* zz(qn1, qn2, thetazz) */
            zz_unsafe_impl(state, qn1, qn2, thetazz, total_qubit, controller_mask);
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

    } // namespace density_operator_simulator_impl


}