#include "simulator_density_op_impl.h"

namespace qpandalite {
namespace density_operator_simulator_impl {
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

        void evolve_u22(const complex_t& U00, const complex_t & U01, 
            const complex_t & U10, const complex_t & U11,
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

        void apply_irho_udag_u22(const complex_t& U00, const complex_t& U01, 
            const complex_t& U10, const complex_t& U11, 
            complex_t& i0j0, complex_t& i0j1, complex_t& i1j0, complex_t& i1j1) 
        {

            const complex_t orig_i0j0 = i0j0, orig_i0j1 = i0j1;
            const complex_t orig_i1j0 = i1j0, orig_i1j1 = i1j1;

            // ρ_block' = ρ_block * U† （仅右乘 U†）
            i0j0 = orig_i0j0 * std::conj(U00) + orig_i0j1 * std::conj(U10);
            i0j1 = orig_i0j0 * std::conj(U01) + orig_i0j1 * std::conj(U11);
            i1j0 = orig_i1j0 * std::conj(U00) + orig_i1j1 * std::conj(U10);
            i1j1 = orig_i1j0 * std::conj(U01) + orig_i1j1 * std::conj(U11);
        }

        void apply_urho_i_u22(const complex_t& U00, const complex_t& U01,
            const complex_t& U10, const complex_t& U11, 
            complex_t& i0j0, complex_t& i0j1, complex_t& i1j0, complex_t& i1j1) 
        {

            const complex_t orig_i0j0 = i0j0, orig_i0j1 = i0j1;
            const complex_t orig_i1j0 = i1j0, orig_i1j1 = i1j1;

            // ρ_block' = U * ρ_block （仅左乘 U）
            i0j0 = U00 * orig_i0j0 + U01 * orig_i1j0;
            i0j1 = U00 * orig_i0j1 + U01 * orig_i1j1;
            i1j0 = U10 * orig_i0j0 + U11 * orig_i1j0;
            i1j1 = U10 * orig_i0j1 + U11 * orig_i1j1;
        }

        void hadamard_unsafe_impl(std::vector<complex_t>& state, size_t qn, size_t total_qubit, size_t controller_mask)
        {
            return u22_unsafe_impl(state, qn,
                INVSQRT2, INVSQRT2, INVSQRT2, -INVSQRT2,
                total_qubit, controller_mask
            );
        }

        void _u22_unsafe_impl_ctrl_v2(std::vector<std::complex<double>>& state, size_t qn, complex_t u00, complex_t u01, complex_t u10, complex_t u11, size_t total_qubit, size_t controller_mask)
        {
            // v2: 受控 U 门对密度矩阵的作用
            // Λ = |0⟩⟨0|_ctrl ⊗ I_target + |1⟩⟨1|_ctrl ⊗ U_target
            // ρ' = Λ ρ Λ†
            //
            // 关键洞察：Λ 按 control qubit 做 block-diagonal 分解，不是按 target qubit。
            // 对于每个 control sub-block (ctrl_row=a, ctrl_col=b)：
            //   a=1,b=1: U * ρ_sub * U†
            //   a=0,b=1: I * ρ_sub * U† = ρ_sub * U†  （右乘 U†）
            //   a=1,b=0: U * ρ_sub * I = U * ρ_sub    （左乘 U）
            //   a=0,b=0: I * ρ_sub * I = ρ_sub        （不变）
            //
            // 其中 ρ_sub 是 target qubit 的 2x2 sub-block

            const size_t N = pow2(total_qubit);
            const size_t target_mask = pow2(qn);

            // 预计算 U†
            const complex_t ud00 = std::conj(u00), ud01 = std::conj(u10);
            const complex_t ud10 = std::conj(u01), ud11 = std::conj(u11);

            // 按 controller_mask 做 block-diagonal 分解
            // 遍历所有 control sub-block 的 (row_base, col_base)
            for (size_t i = 0; i < N; ++i) {
                if (i & target_mask) continue; // 跳过 target bit=1 的行（与原非受控版一致）

                // control qubit 在 row 端的状态
                const bool a = ((i & controller_mask) == controller_mask);

                for (size_t j = 0; j < N; ++j) {
                    if (j & target_mask) continue; // 跳过 target bit=1 的列

                    // control qubit 在 col 端的状态
                    const bool b = ((j & controller_mask) == controller_mask);

                    if (!a && !b) continue; // 不变，跳过

                    // 提取 target qubit 的 2x2 sub-block
                    // ρ_sub[alpha, beta] = rho[i + alpha*target_mask, j + beta*target_mask]
                    complex_t& r00 = val(state, i, j, N);
                    complex_t& r01 = val(state, i, j + target_mask, N);
                    complex_t& r10 = val(state, i + target_mask, j, N);
                    complex_t& r11 = val(state, i + target_mask, j + target_mask, N);

                    if (a && b) {
                        // ρ_sub' = U * ρ_sub * U†
                        const complex_t o00 = r00, o01 = r01, o10 = r10, o11 = r11;
                        r00 = (u00*o00 + u01*o10)*ud00 + (u00*o01 + u01*o11)*ud10;
                        r01 = (u00*o00 + u01*o10)*ud01 + (u00*o01 + u01*o11)*ud11;
                        r10 = (u10*o00 + u11*o10)*ud00 + (u10*o01 + u11*o11)*ud10;
                        r11 = (u10*o00 + u11*o10)*ud01 + (u10*o01 + u11*o11)*ud11;
                    }
                    else if (!a && b) {
                        // ρ_sub' = ρ_sub * U†
                        const complex_t o00 = r00, o01 = r01, o10 = r10, o11 = r11;
                        r00 = o00*ud00 + o01*ud10;
                        r01 = o00*ud01 + o01*ud11;
                        r10 = o10*ud00 + o11*ud10;
                        r11 = o10*ud01 + o11*ud11;
                    }
                    else { // a && !b
                        // ρ_sub' = U * ρ_sub
                        const complex_t o00 = r00, o01 = r01, o10 = r10, o11 = r11;
                        r00 = u00*o00 + u01*o10;
                        r01 = u00*o01 + u01*o11;
                        r10 = u10*o00 + u11*o10;
                        r11 = u10*o01 + u11*o11;
                    }
                }
            }
        }

        void u22_unsafe_impl(std::vector<std::complex<double>>& state, size_t qn, complex_t u00, complex_t u01, complex_t u10, complex_t u11, size_t total_qubit, size_t controller_mask)
        {
            /* control version must be specially handled */
            if (controller_mask != 0)
            {
                _u22_unsafe_impl_ctrl_v2(state, qn, u00, u01, u10, u11, total_qubit, controller_mask);
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

        void u22_unsafe_impl(std::vector<std::complex<double>>& state, size_t qn, u22_t unitary, size_t total_qubit, size_t controller_mask)
        {
            return u22_unsafe_impl(state, qn, unitary[0], unitary[1], unitary[2], unitary[3],
                total_qubit, controller_mask);
        }


        void evolve_u44(const complex_t& U00, const complex_t& U01, const complex_t& U02, const complex_t& U03,
            const complex_t& U10, const complex_t& U11, const complex_t& U12, const complex_t& U13,
            const complex_t& U20, const complex_t& U21, const complex_t& U22, const complex_t& U23,
            const complex_t& U30, const complex_t& U31, const complex_t& U32, const complex_t& U33,
            complex_t& i00j00, complex_t& i00j01, complex_t& i00j10, complex_t& i00j11,
            complex_t& i01j00, complex_t& i01j01, complex_t& i01j10, complex_t& i01j11,
            complex_t& i10j00, complex_t& i10j01, complex_t& i10j10, complex_t& i10j11,
            complex_t& i11j00, complex_t& i11j01, complex_t& i11j10, complex_t& i11j11) {

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

        void _u44_unsafe_impl_ctrl(std::vector<std::complex<double>>& state, size_t qn1, size_t qn2, complex_t u00, complex_t u01, complex_t u02, complex_t u03, complex_t u10, complex_t u11, complex_t u12, complex_t u13, complex_t u20, complex_t u21, complex_t u22, complex_t u23, complex_t u30, complex_t u31, complex_t u32, complex_t u33, size_t total_qubit, size_t controller_mask) {

            const size_t N = pow2(total_qubit);
            const size_t mask1 = pow2(qn1);
            const size_t mask2 = pow2(qn2);

            for (size_t i = 0; i < N; ++i) {
                // 提前过滤条件：控制位 + 目标量子比特为 0
                if ((i & (mask1 | mask2)) != 0) continue;
                const bool a = ((i & controller_mask) == controller_mask);

                for (size_t j = 0; j < N; ++j) {
                    if ((j & (mask1 | mask2)) != 0) continue;
                    const bool b = ((j & controller_mask) == controller_mask);

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


                    if (a && b) {
                        evolve_u44(u00, u01, u02, u03, u10, u11, u12, u13, u20, u21, u22, u23, u30, u31, u32, u33,
                            i00j00, i00j01, i00j10, i00j11, i01j00, i01j01, i01j10, i01j11, i10j00, i10j01, i10j10, i10j11, i11j00, i11j01, i11j10, i11j11);
                    }
                    else if (!a && b) {
                        apply_irho_udag_u44(u00, u01, u02, u03, u10, u11, u12, u13, u20, u21, u22, u23, u30, u31, u32, u33,
                            i00j00, i00j01, i00j10, i00j11, i01j00, i01j01, i01j10, i01j11, i10j00, i10j01, i10j10, i10j11, i11j00, i11j01, i11j10, i11j11);
                    }
                    else if (a && !b) {
                        apply_urho_i_u44(u00, u01, u02, u03, u10, u11, u12, u13, u20, u21, u22, u23, u30, u31, u32, u33,
                            i00j00, i00j01, i00j10, i00j11, i01j00, i01j01, i01j10, i01j11, i10j00, i10j01, i10j10, i10j11, i11j00, i11j01, i11j10, i11j11);
                    }
                }
            }
        }

        void apply_irho_udag_u44(const complex_t& U00, const complex_t& U01, const complex_t& U02, const complex_t& U03, 
            const complex_t& U10, const complex_t& U11, const complex_t& U12, const complex_t& U13, 
            const complex_t& U20, const complex_t& U21, const complex_t& U22, const complex_t& U23, 
            const complex_t& U30, const complex_t& U31, const complex_t& U32, const complex_t& U33, 
            complex_t& i00j00, complex_t& i00j01, complex_t& i00j10, complex_t& i00j11, 
            complex_t& i01j00, complex_t& i01j01, complex_t& i01j10, complex_t& i01j11, 
            complex_t& i10j00, complex_t& i10j01, complex_t& i10j10, complex_t& i10j11, 
            complex_t& i11j00, complex_t& i11j01, complex_t& i11j10, complex_t& i11j11) {

            // 保存原始值
            const complex_t orig_i00j00 = i00j00, orig_i00j01 = i00j01, orig_i00j10 = i00j10, orig_i00j11 = i00j11;
            const complex_t orig_i01j00 = i01j00, orig_i01j01 = i01j01, orig_i01j10 = i01j10, orig_i01j11 = i01j11;
            const complex_t orig_i10j00 = i10j00, orig_i10j01 = i10j01, orig_i10j10 = i10j10, orig_i10j11 = i10j11;
            const complex_t orig_i11j00 = i11j00, orig_i11j01 = i11j01, orig_i11j10 = i11j10, orig_i11j11 = i11j11;

            // 计算 U† 的转置共轭（预计算）
            const complex_t Udag00 = std::conj(U00), Udag10 = std::conj(U01), Udag20 = std::conj(U02), Udag30 = std::conj(U03);
            const complex_t Udag01 = std::conj(U10), Udag11 = std::conj(U11), Udag21 = std::conj(U12), Udag31 = std::conj(U13);
            const complex_t Udag02 = std::conj(U20), Udag12 = std::conj(U21), Udag22 = std::conj(U22), Udag32 = std::conj(U23);
            const complex_t Udag03 = std::conj(U30), Udag13 = std::conj(U31), Udag23 = std::conj(U32), Udag33 = std::conj(U33);

            // 第一行（原 ρ 的行 × U† 的列）
            i00j00 = orig_i00j00 * Udag00 + orig_i00j01 * Udag01 + orig_i00j10 * Udag02 + orig_i00j11 * Udag03;
            i00j01 = orig_i00j00 * Udag10 + orig_i00j01 * Udag11 + orig_i00j10 * Udag12 + orig_i00j11 * Udag13;
            i00j10 = orig_i00j00 * Udag20 + orig_i00j01 * Udag21 + orig_i00j10 * Udag22 + orig_i00j11 * Udag23;
            i00j11 = orig_i00j00 * Udag30 + orig_i00j01 * Udag31 + orig_i00j10 * Udag32 + orig_i00j11 * Udag33;

            // 第二行
            i01j00 = orig_i01j00 * Udag00 + orig_i01j01 * Udag01 + orig_i01j10 * Udag02 + orig_i01j11 * Udag03;
            i01j01 = orig_i01j00 * Udag10 + orig_i01j01 * Udag11 + orig_i01j10 * Udag12 + orig_i01j11 * Udag13;
            i01j10 = orig_i01j00 * Udag20 + orig_i01j01 * Udag21 + orig_i01j10 * Udag22 + orig_i01j11 * Udag23;
            i01j11 = orig_i01j00 * Udag30 + orig_i01j01 * Udag31 + orig_i01j10 * Udag32 + orig_i01j11 * Udag33;

            // 第三行
            i10j00 = orig_i10j00 * Udag00 + orig_i10j01 * Udag01 + orig_i10j10 * Udag02 + orig_i10j11 * Udag03;
            i10j01 = orig_i10j00 * Udag10 + orig_i10j01 * Udag11 + orig_i10j10 * Udag12 + orig_i10j11 * Udag13;
            i10j10 = orig_i10j00 * Udag20 + orig_i10j01 * Udag21 + orig_i10j10 * Udag22 + orig_i10j11 * Udag23;
            i10j11 = orig_i10j00 * Udag30 + orig_i10j01 * Udag31 + orig_i10j10 * Udag32 + orig_i10j11 * Udag33;

            // 第四行
            i11j00 = orig_i11j00 * Udag00 + orig_i11j01 * Udag01 + orig_i11j10 * Udag02 + orig_i11j11 * Udag03;
            i11j01 = orig_i11j00 * Udag10 + orig_i11j01 * Udag11 + orig_i11j10 * Udag12 + orig_i11j11 * Udag13;
            i11j10 = orig_i11j00 * Udag20 + orig_i11j01 * Udag21 + orig_i11j10 * Udag22 + orig_i11j11 * Udag23;
            i11j11 = orig_i11j00 * Udag30 + orig_i11j01 * Udag31 + orig_i11j10 * Udag32 + orig_i11j11 * Udag33;
        }

        void apply_urho_i_u44(
            const complex_t& U00, const complex_t& U01, const complex_t& U02, const complex_t& U03,
            const complex_t& U10, const complex_t& U11, const complex_t& U12, const complex_t& U13,
            const complex_t& U20, const complex_t& U21, const complex_t& U22, const complex_t& U23,
            const complex_t& U30, const complex_t& U31, const complex_t& U32, const complex_t& U33,
            complex_t& i00j00, complex_t& i00j01, complex_t& i00j10, complex_t& i00j11,
            complex_t& i01j00, complex_t& i01j01, complex_t& i01j10, complex_t& i01j11,
            complex_t& i10j00, complex_t& i10j01, complex_t& i10j10, complex_t& i10j11,
            complex_t& i11j00, complex_t& i11j01, complex_t& i11j10, complex_t& i11j11) {

            // 保存原始值
            const complex_t orig_i00j00 = i00j00, orig_i00j01 = i00j01, orig_i00j10 = i00j10, orig_i00j11 = i00j11;
            const complex_t orig_i01j00 = i01j00, orig_i01j01 = i01j01, orig_i01j10 = i01j10, orig_i01j11 = i01j11;
            const complex_t orig_i10j00 = i10j00, orig_i10j01 = i10j01, orig_i10j10 = i10j10, orig_i10j11 = i10j11;
            const complex_t orig_i11j00 = i11j00, orig_i11j01 = i11j01, orig_i11j10 = i11j10, orig_i11j11 = i11j11;

            // 第一行（U 的行 × ρ 的列）
            i00j00 = U00 * orig_i00j00 + U01 * orig_i01j00 + U02 * orig_i10j00 + U03 * orig_i11j00;
            i00j01 = U00 * orig_i00j01 + U01 * orig_i01j01 + U02 * orig_i10j01 + U03 * orig_i11j01;
            i00j10 = U00 * orig_i00j10 + U01 * orig_i01j10 + U02 * orig_i10j10 + U03 * orig_i11j10;
            i00j11 = U00 * orig_i00j11 + U01 * orig_i01j11 + U02 * orig_i10j11 + U03 * orig_i11j11;

            // 第二行
            i01j00 = U10 * orig_i00j00 + U11 * orig_i01j00 + U12 * orig_i10j00 + U13 * orig_i11j00;
            i01j01 = U10 * orig_i00j01 + U11 * orig_i01j01 + U12 * orig_i10j01 + U13 * orig_i11j01;
            i01j10 = U10 * orig_i00j10 + U11 * orig_i01j10 + U12 * orig_i10j10 + U13 * orig_i11j10;
            i01j11 = U10 * orig_i00j11 + U11 * orig_i01j11 + U12 * orig_i10j11 + U13 * orig_i11j11;

            // 第三行
            i10j00 = U20 * orig_i00j00 + U21 * orig_i01j00 + U22 * orig_i10j00 + U23 * orig_i11j00;
            i10j01 = U20 * orig_i00j01 + U21 * orig_i01j01 + U22 * orig_i10j01 + U23 * orig_i11j01;
            i10j10 = U20 * orig_i00j10 + U21 * orig_i01j10 + U22 * orig_i10j10 + U23 * orig_i11j10;
            i10j11 = U20 * orig_i00j11 + U21 * orig_i01j11 + U22 * orig_i10j11 + U23 * orig_i11j11;

            // 第四行
            i11j00 = U30 * orig_i00j00 + U31 * orig_i01j00 + U32 * orig_i10j00 + U33 * orig_i11j00;
            i11j01 = U30 * orig_i00j01 + U31 * orig_i01j01 + U32 * orig_i10j01 + U33 * orig_i11j01;
            i11j10 = U30 * orig_i00j10 + U31 * orig_i01j10 + U32 * orig_i10j10 + U33 * orig_i11j10;
            i11j11 = U30 * orig_i00j11 + U31 * orig_i01j11 + U32 * orig_i10j11 + U33 * orig_i11j11;
        }

        void u44_unsafe_impl(std::vector<std::complex<double>>& state, size_t qn1, size_t qn2,
            complex_t u00, complex_t u01, complex_t u02, complex_t u03,
            complex_t u10, complex_t u11, complex_t u12, complex_t u13,
            complex_t u20, complex_t u21, complex_t u22, complex_t u23,
            complex_t u30, complex_t u31, complex_t u32, complex_t u33,
            size_t total_qubit, size_t controller_mask) {

            if (controller_mask != 0)
            {
                _u44_unsafe_impl_ctrl(state, qn1, qn2,
                    u00, u01, u02, u03,
                    u10, u11, u12, u13,
                    u20, u21, u22, u23,
                    u30, u31, u32, u33,
                    total_qubit, controller_mask);
                return;
            }

            const size_t N = pow2(total_qubit);
            const size_t mask1 = pow2(qn1);
            const size_t mask2 = pow2(qn2);

            for (size_t i = 0; i < N; ++i) {
                // 提前过滤条件：控制位 + 目标量子比特为 0
                if ((i & (mask1 | mask2)) != 0) continue;

                for (size_t j = 0; j < N; ++j) {
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

        void u44_unsafe_impl(std::vector<std::complex<double>>& state, size_t qn1, size_t qn2, u44_t unitary, size_t total_qubit, size_t controller_mask)
        {
            u44_unsafe_impl(state, qn1, qn2, unitary[0], unitary[1], unitary[2], unitary[3],
                unitary[4], unitary[5], unitary[6], unitary[7],
                unitary[8], unitary[9], unitary[10], unitary[11],
                unitary[12], unitary[13], unitary[14], unitary[15],
                total_qubit, controller_mask);
        }

        void u3_unsafe_impl(std::vector<complex_t>& state, size_t qn,
            double theta, double phi, double lambda,
            size_t total_qubit, size_t controller_mask, bool is_dagger) {

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
            complex_t cos_t = std::cos(theta / 2);
            complex_t sin_t = (is_dagger ? complex_t(0, 1) : -complex_t(0, 1)) * std::sin(theta / 2);

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

            // 合并控制位掩码：原有控制位 + qn1 和 qn2
            const size_t new_controller_mask = controller_mask | pow2(controller);

            // 调用 X 门，目标为 target，控制位为 new_controller_mask
            x_unsafe_impl(state, target, total_qubit, new_controller_mask);
            
            // 定义 4x4 酉矩阵（例如 CNOT 门）
            /*
            * 
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
            */

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

            double theta1 = parameters[0];
            double phi1 = parameters[1];
            double lambda1 = parameters[2];

            double theta2 = parameters[3];
            double phi2 = parameters[4];
            double lambda2 = parameters[5];

            double theta_xx = parameters[6];
            double theta_yy = parameters[7];
            double theta_zz = parameters[8];

            double theta3 = parameters[9];
            double phi3 = parameters[10];
            double lambda3 = parameters[11];

            double theta4 = parameters[12];
            double phi4 = parameters[13];
            double lambda4 = parameters[14];

            if (!is_dagger)
            {
                /* U3(q1, parameters[0:3]) */
                u3_unsafe_impl(state, qn1, theta1, phi1, lambda1, total_qubit, controller_mask, false);

                /* U3(q2, parameters[3:6]) */
                u3_unsafe_impl(state, qn2, theta2, phi2, lambda2, total_qubit, controller_mask, false);

                /* XX(q1, q2, parameters[6]) */
                xx_unsafe_impl(state, qn1, qn2, theta_xx, total_qubit, controller_mask);

                /* YY(q1, q2, parameters[7]) */
                yy_unsafe_impl(state, qn1, qn2, theta_yy, total_qubit, controller_mask);

                /* ZZ(q1, q2, parameters[8]) */
                zz_unsafe_impl(state, qn1, qn2, theta_zz, total_qubit, controller_mask);

                /* U3(q1, parameters[9:12]) */
                u3_unsafe_impl(state, qn1, theta3, phi3, lambda3, total_qubit, controller_mask, false);

                /* U3(q2, parameters[12:15]) */
                u3_unsafe_impl(state, qn2, theta4, phi4, lambda4, total_qubit, controller_mask, false);
            }
            else /* dagger case*/
            {
                /* U3(q1, parameters[9:12]) */
                u3_unsafe_impl(state, qn1, theta3, phi3, lambda3, total_qubit, controller_mask, true);

                /* U3(q2, parameters[12:15]) */
                u3_unsafe_impl(state, qn2, theta4, phi4, lambda4, total_qubit, controller_mask, true);

                /* ZZ(q1, q2, parameters[8]) */
                zz_unsafe_impl(state, qn1, qn2, -theta_zz, total_qubit, controller_mask);

                /* YY(q1, q2, parameters[7]) */
                yy_unsafe_impl(state, qn1, qn2, -theta_yy, total_qubit, controller_mask);

                /* XX(q1, q2, parameters[6]) */
                xx_unsafe_impl(state, qn1, qn2, -theta_xx, total_qubit, controller_mask);

                /* U3(q1, parameters[0:3]) */
                u3_unsafe_impl(state, qn1, theta1, phi1, lambda1, total_qubit, controller_mask, true);

                /* U3(q2, parameters[3:6]) */
                u3_unsafe_impl(state, qn2, theta2, phi2, lambda2, total_qubit, controller_mask, true);

            }
        }

        void merge_state(std::vector<complex_t>& target_state, const std::vector<complex_t>& add_state, double coef)
        {
            for (size_t i = 0; i < target_state.size(); ++i)
            {
                target_state[i] += add_state[i] * coef;
            }
        }

        void kraus1q_unsafe_impl(std::vector<complex_t>& state, size_t qn, const Kraus1Q& kraus1q, size_t total_qubit)
        {
            std::vector<complex_t> init_state(state.size());
            for (size_t i = 0; i < kraus1q.size(); ++i)
            {
                std::vector<complex_t> copy_state = state;

                u22_unsafe_impl(copy_state, qn, kraus1q[i], total_qubit, 0);
                merge_state(init_state, copy_state);
            }
            state = std::move(init_state);
        }

        void pauli_error_2q_unsafe_impl(std::vector<complex_t>& state, size_t qn1, size_t qn2, const std::vector<double>& p, size_t total_qubit)
        {
            // 解包所有概率参数
            // XI means qn1 has X error and qn2 has no error with probability xi
            double xi = p[0], yi = p[1], zi = p[2];
            double ix = p[3], xx = p[4], yx = p[5], zx = p[6];
            double iy = p[7], xy = p[8], yy = p[9], zy = p[10];
            double iz = p[11], xz = p[12], yz = p[13], zz = p[14];

            double sum = xi + yi + zi +
                ix + xx + yx + zx +
                iy + xy + yy + zy +
                iz + xz + yz + zz;

            double ii = 1 - sum;

            std::vector<double> p_new = {
                ii, xi, yi, zi,
                ix, xx, yx, zx,
                iy, xy, yy, zy,
                iz, xz, yz, zz
            };

            std::vector<complex_t> init_state(state.size());
            for (size_t i = 0; i < 16; ++i)
            {
                std::vector<complex_t> copy_state = state;

                switch (i / 4)
                {
                case 0:
                    break;
                case 1:
                    x_unsafe_impl(copy_state, qn1, total_qubit, 0);
                    break;
                case 2:
                    y_unsafe_impl(copy_state, qn1, total_qubit, 0);
                    break;
                case 3:
                    z_unsafe_impl(copy_state, qn1, total_qubit, 0);
                    break;
                }

                switch (i % 4)
                {
                case 0:
                    break;
                case 1:
                    x_unsafe_impl(copy_state, qn2, total_qubit, 0);
                    break;
                case 2:
                    y_unsafe_impl(copy_state, qn2, total_qubit, 0);
                    break;
                case 3:
                    z_unsafe_impl(copy_state, qn2, total_qubit, 0);
                    break;
                }
                merge_state(init_state, copy_state, p_new[i]);
            }

            state = std::move(init_state);
        }

} // namespace density_operator_simulator_impl
} // namespace qpandalite
