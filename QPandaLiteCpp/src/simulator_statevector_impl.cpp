#include "simulator_statevector_impl.h"

namespace qpandalite {
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

                sv_apply_u22(INVSQRT2, INVSQRT2, INVSQRT2, -INVSQRT2, state[i0], state[i1]);
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

                sv_apply_u22(u00, u01, u10, u11, state[i0], state[i1]);
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

                // |01>
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
            complex_t cos_t = std::cos(theta / 2);
            complex_t sin_t = (is_dagger ? complex_t(0, 1) : -complex_t(0, 1)) * std::sin(theta / 2);

            for (size_t i = 0; i < pow2(total_qubit); ++i)
            {
                if ((i & controller_mask) != controller_mask)
                    continue;

                // |01>
                if (((i >> qn1) & 1) == 0 && ((i >> qn2) & 1) == 1)
                {
                    size_t i2 = i + pow2(qn1) - pow2(qn2);
                    complex_t s1 = state[i];
                    complex_t s2 = state[i2];

                    state[i] = s1 * cos_t + s2 * sin_t;
                    state[i2] = s1 * sin_t + s2 * cos_t;
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
            else /* dagger case */
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

        dtype prob_0(const std::vector<complex_t>& state, size_t qn, size_t total_qubit)
        {
            const size_t mask = pow2(qn); // 确定目标量子比特的掩码
            const size_t N = pow2(total_qubit);
            double p0 = 0.0;
            for (size_t i = 0; i < N; ++i) {
                if (!(i & mask)) {
                    p0 += abs_sqr(state[i]);
                }
            }
            return p0;
        }

        dtype prob_1(const std::vector<complex_t>& state, size_t qn, size_t total_qubit)
        {
            const size_t mask = pow2(qn); // 确定目标量子比特的掩码
            const size_t N = pow2(total_qubit);
            double p1 = 0.0;
            for (size_t i = 0; i < N; ++i) {
                if (i & mask) {
                    p1 += abs_sqr(state[i]);
                }
            }
            return p1;
        }

        void rescale_state(std::vector<complex_t>& state, double norm) {
            if (norm < eps)
                ThrowInvalidArgument(fmt::format("The normalization factor ({}) is invalid.", norm));

            const double inv_norm = 1.0 / norm;
            for (auto& amp : state) {
                amp *= inv_norm;
            }
        }

        void amplitude_damping_unsafe_impl(std::vector<complex_t>& state, size_t qn, double gamma, size_t total_qubit)
        {
            // 计算|1⟩态的总概率
            double p1 = prob_1(state, qn, total_qubit);
            size_t mask = pow2(qn);
            size_t N = pow2(total_qubit);

            const double prob_E1 = gamma * p1; // 应用E1的概率
            const double r = qpandalite::rand();

            if (r < prob_E1) {
                for (size_t i = 0; i < N; ++i) {
                    // 仅处理目标量子比特为0的基态
                    if ((i & mask) != 0)
                        continue;

                    size_t i0 = i;
                    size_t i1 = i + mask;

                    state[i0] = state[i1];
                    state[i1] = 0;
                }

                rescale_state(state, p1);
            }
            else {
                // 应用E0操作：衰减|1⟩态幅度
                for (size_t i = 0; i < N; ++i) {
                    if (i & mask) {
                        state[i] *= std::sqrt(1 - gamma);
                    }
                }

                // 归一化处理
                const double norm = 1 - prob_E1;                
                rescale_state(state, norm);
            }
        }

        void kraus1q_unsafe_impl(std::vector<complex_t>& state, size_t qn, const std::vector<u22_t>& kraus, size_t total_qubit)
        {
            const size_t mask = pow2(qn); // 使用安全的幂计算函数
            const double r = qpandalite::rand();
            double cumulative_prob = 0.0;

            // 处理前n-1个Kraus算符
            for (size_t k = 0; k < kraus.size() - 1; ++k) {
                auto temp_state = state; // 按需复制当前态

                // 应用Kraus算符
                u22_unsafe_impl(temp_state, qn, kraus[k], total_qubit, 0);

                // 计算概率
                double prob = 0.0;
                for (const auto& amp : temp_state) {
                    prob += std::norm(amp);
                }

                // 概率决策
                if (r < cumulative_prob + prob) {
                    rescale_state(temp_state, std::sqrt(prob));
                    state = std::move(temp_state);
                    return;
                }
                cumulative_prob += prob;
            }

            // 处理最后一个Kraus算符（无需复制原始态）
            u22_unsafe_impl(state, qn, kraus.back(), total_qubit, 0);

            // 计算最终归一化因子（利用完备性条件）
            const double final_norm = std::sqrt(1.0 - cumulative_prob);
            rescale_state(state, final_norm);
        }

        dtype get_prob_unsafe_impl(const std::vector<complex_t>& state, size_t qn, int qstate, size_t total_qubit)
        {
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

        dtype get_prob_unsafe_impl(const std::vector<complex_t>& state, const std::map<size_t, int> measure_map, size_t total_qubit)
        {
            size_t mask_qubit = 0;
            size_t mask_state = 0;
            for (auto&& [qid, qstate] : measure_map)
            {
                mask_qubit |= pow2(qid);
                mask_state |= (qstate == 1 ? pow2(qid) : 0);
            }

            double prob = 0;
            for (size_t i = 0; i < pow2(total_qubit); ++i)
            {
                for (auto&& [qid, qstate] : measure_map)
                {
                    if ((i & mask_qubit) == mask_state)
                        prob += abs_sqr(state[i]);
                }
            }
            return prob;
        }

} // namespace statevector_simulator_impl
} // namespace qpandalite
