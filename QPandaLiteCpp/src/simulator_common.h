#pragma once

#include <array>
#include <complex>
#include <iostream>
#include <vector>
#include <set>
#include <map>
#include <cstdint>

#include "errors.h"
#include "basic_math.h"
#include "rng.h"

#define CHECK_QUBIT_RANGE(qn) \
        if (qn >= total_qubit)\
        {\
            auto errstr = fmt::format("Exceed total (total_qubit = {}, input = {})", total_qubit, qn);\
            ThrowInvalidArgument(errstr);\
        }

#define CHECK_QUBIT_RANGE2(qn, name) \
        if (qn >= total_qubit)\
        {\
            auto errstr = fmt::format("Exceed total (total_qubit = {}, {} = {})", total_qubit, #name, qn);\
            ThrowInvalidArgument(errstr);\
        }

#define CHECK_DUPLICATE_QUBIT(qn1, qn2) \
    if (qn1 == qn2)\
    {\
        auto errstr = fmt::format("qn1 = qn2");\
        ThrowInvalidArgument(errstr);\
    }

#define CHECK_PROBABILITY_BOUND(prob) \
    if (prob < 0 || prob > 1)\
    {\
        auto errstr = fmt::format("Probability out of range (prob = {})", prob);\
        ThrowInvalidArgument(errstr);\
    }

namespace qpandalite {
    std::map<size_t, size_t> preprocess_measure_list(const std::vector<size_t>& measure_list, size_t total_qubit);
    size_t get_state_with_qubit(size_t i, const std::map<size_t, size_t>& measure_map);
    size_t make_controller_mask(const std::vector<size_t>& global_controller);

    // ============================================================
    // Inline 2x2 statevector (matrix × vector) operation
    // |ψ'⟩ = U |ψ⟩, where ψ = (a0, a1), U = [[u00,u01],[u10,u11]]
    // ============================================================
    inline void sv_apply_u22(
        const complex_t& u00, const complex_t& u01,
        const complex_t& u10, const complex_t& u11,
        complex_t& a0, complex_t& a1)
    {
        const complex_t o0 = a0, o1 = a1;
        a0 = u00 * o0 + u01 * o1;
        a1 = u10 * o0 + u11 * o1;
    }

    // ============================================================
    // Inline 2x2 density-matrix operations
    // ρ is stored as 4 references: r00, r01, r10, r11 (row-major)
    // ============================================================

    // ρ' = U * ρ * U†  (full evolution)
    inline void dm_evolve_2x2(
        const complex_t& u00, const complex_t& u01,
        const complex_t& u10, const complex_t& u11,
        complex_t& r00, complex_t& r01,
        complex_t& r10, complex_t& r11)
    {
        const complex_t o00 = r00, o01 = r01, o10 = r10, o11 = r11;
        // T = U * ρ
        const complex_t t00 = u00*o00 + u01*o10;
        const complex_t t01 = u00*o01 + u01*o11;
        const complex_t t10 = u10*o00 + u11*o10;
        const complex_t t11 = u10*o01 + u11*o11;
        // ρ' = T * U†
        r00 = t00*std::conj(u00) + t01*std::conj(u01);
        r01 = t00*std::conj(u10) + t01*std::conj(u11);
        r10 = t10*std::conj(u00) + t11*std::conj(u01);
        r11 = t10*std::conj(u10) + t11*std::conj(u11);
    }

    // ρ' = ρ * U†  (right-multiply by U†)
    inline void dm_right_mul_udag_2x2(
        const complex_t& u00, const complex_t& u01,
        const complex_t& u10, const complex_t& u11,
        complex_t& r00, complex_t& r01,
        complex_t& r10, complex_t& r11)
    {
        const complex_t o00 = r00, o01 = r01, o10 = r10, o11 = r11;
        r00 = o00*std::conj(u00) + o01*std::conj(u01);
        r01 = o00*std::conj(u10) + o01*std::conj(u11);
        r10 = o10*std::conj(u00) + o11*std::conj(u01);
        r11 = o10*std::conj(u10) + o11*std::conj(u11);
    }

    // ρ' = U * ρ  (left-multiply by U)
    inline void dm_left_mul_u_2x2(
        const complex_t& u00, const complex_t& u01,
        const complex_t& u10, const complex_t& u11,
        complex_t& r00, complex_t& r01,
        complex_t& r10, complex_t& r11)
    {
        const complex_t o00 = r00, o01 = r01, o10 = r10, o11 = r11;
        r00 = u00*o00 + u01*o10;
        r01 = u00*o01 + u01*o11;
        r10 = u10*o00 + u11*o10;
        r11 = u10*o01 + u11*o11;
    }

    // ============================================================
    // Inline 4x4 density-matrix operations
    // ρ is stored as 16 references: i{0,1}j{0,1}{0,1} (4x4 row-major)
    // ============================================================

    // ρ' = U * ρ * U†  (full 4x4 evolution)
    inline void dm_evolve_4x4(
        const complex_t& U00, const complex_t& U01, const complex_t& U02, const complex_t& U03,
        const complex_t& U10, const complex_t& U11, const complex_t& U12, const complex_t& U13,
        const complex_t& U20, const complex_t& U21, const complex_t& U22, const complex_t& U23,
        const complex_t& U30, const complex_t& U31, const complex_t& U32, const complex_t& U33,
        complex_t& i00j00, complex_t& i00j01, complex_t& i00j10, complex_t& i00j11,
        complex_t& i01j00, complex_t& i01j01, complex_t& i01j10, complex_t& i01j11,
        complex_t& i10j00, complex_t& i10j01, complex_t& i10j10, complex_t& i10j11,
        complex_t& i11j00, complex_t& i11j01, complex_t& i11j10, complex_t& i11j11)
    {
        const complex_t o00 = i00j00, o01 = i00j01, o02 = i00j10, o03 = i00j11;
        const complex_t o10 = i01j00, o11 = i01j01, o12 = i01j10, o13 = i01j11;
        const complex_t o20 = i10j00, o21 = i10j01, o22 = i10j10, o23 = i10j11;
        const complex_t o30 = i11j00, o31 = i11j01, o32 = i11j10, o33 = i11j11;

        // T = U * ρ
        const complex_t t00 = U00*o00 + U01*o10 + U02*o20 + U03*o30;
        const complex_t t01 = U00*o01 + U01*o11 + U02*o21 + U03*o31;
        const complex_t t02 = U00*o02 + U01*o12 + U02*o22 + U03*o32;
        const complex_t t03 = U00*o03 + U01*o13 + U02*o23 + U03*o33;
        const complex_t t10 = U10*o00 + U11*o10 + U12*o20 + U13*o30;
        const complex_t t11 = U10*o01 + U11*o11 + U12*o21 + U13*o31;
        const complex_t t12 = U10*o02 + U11*o12 + U12*o22 + U13*o32;
        const complex_t t13 = U10*o03 + U11*o13 + U12*o23 + U13*o33;
        const complex_t t20 = U20*o00 + U21*o10 + U22*o20 + U23*o30;
        const complex_t t21 = U20*o01 + U21*o11 + U22*o21 + U23*o31;
        const complex_t t22 = U20*o02 + U21*o12 + U22*o22 + U23*o32;
        const complex_t t23 = U20*o03 + U21*o13 + U22*o23 + U23*o33;
        const complex_t t30 = U30*o00 + U31*o10 + U32*o20 + U33*o30;
        const complex_t t31 = U30*o01 + U31*o11 + U32*o21 + U33*o31;
        const complex_t t32 = U30*o02 + U31*o12 + U32*o22 + U33*o32;
        const complex_t t33 = U30*o03 + U31*o13 + U32*o23 + U33*o33;

        // ρ' = T * U†
        i00j00 = t00*std::conj(U00) + t01*std::conj(U01) + t02*std::conj(U02) + t03*std::conj(U03);
        i00j01 = t00*std::conj(U10) + t01*std::conj(U11) + t02*std::conj(U12) + t03*std::conj(U13);
        i00j10 = t00*std::conj(U20) + t01*std::conj(U21) + t02*std::conj(U22) + t03*std::conj(U23);
        i00j11 = t00*std::conj(U30) + t01*std::conj(U31) + t02*std::conj(U32) + t03*std::conj(U33);
        i01j00 = t10*std::conj(U00) + t11*std::conj(U01) + t12*std::conj(U02) + t13*std::conj(U03);
        i01j01 = t10*std::conj(U10) + t11*std::conj(U11) + t12*std::conj(U12) + t13*std::conj(U13);
        i01j10 = t10*std::conj(U20) + t11*std::conj(U21) + t12*std::conj(U22) + t13*std::conj(U23);
        i01j11 = t10*std::conj(U30) + t11*std::conj(U31) + t12*std::conj(U32) + t13*std::conj(U33);
        i10j00 = t20*std::conj(U00) + t21*std::conj(U01) + t22*std::conj(U02) + t23*std::conj(U03);
        i10j01 = t20*std::conj(U10) + t21*std::conj(U11) + t22*std::conj(U12) + t23*std::conj(U13);
        i10j10 = t20*std::conj(U20) + t21*std::conj(U21) + t22*std::conj(U22) + t23*std::conj(U23);
        i10j11 = t20*std::conj(U30) + t21*std::conj(U31) + t22*std::conj(U32) + t23*std::conj(U33);
        i11j00 = t30*std::conj(U00) + t31*std::conj(U01) + t32*std::conj(U02) + t33*std::conj(U03);
        i11j01 = t30*std::conj(U10) + t31*std::conj(U11) + t32*std::conj(U12) + t33*std::conj(U13);
        i11j10 = t30*std::conj(U20) + t31*std::conj(U21) + t32*std::conj(U22) + t33*std::conj(U23);
        i11j11 = t30*std::conj(U30) + t31*std::conj(U31) + t32*std::conj(U32) + t33*std::conj(U33);
    }

    // ρ' = ρ * U†  (right-multiply by U†, 4x4)
    inline void dm_right_mul_udag_4x4(
        const complex_t& U00, const complex_t& U01, const complex_t& U02, const complex_t& U03,
        const complex_t& U10, const complex_t& U11, const complex_t& U12, const complex_t& U13,
        const complex_t& U20, const complex_t& U21, const complex_t& U22, const complex_t& U23,
        const complex_t& U30, const complex_t& U31, const complex_t& U32, const complex_t& U33,
        complex_t& i00j00, complex_t& i00j01, complex_t& i00j10, complex_t& i00j11,
        complex_t& i01j00, complex_t& i01j01, complex_t& i01j10, complex_t& i01j11,
        complex_t& i10j00, complex_t& i10j01, complex_t& i10j10, complex_t& i10j11,
        complex_t& i11j00, complex_t& i11j01, complex_t& i11j10, complex_t& i11j11)
    {
        const complex_t o00=i00j00, o01=i00j01, o02=i00j10, o03=i00j11;
        const complex_t o10=i01j00, o11=i01j01, o12=i01j10, o13=i01j11;
        const complex_t o20=i10j00, o21=i10j01, o22=i10j10, o23=i10j11;
        const complex_t o30=i11j00, o31=i11j01, o32=i11j10, o33=i11j11;

        i00j00 = o00*std::conj(U00) + o01*std::conj(U01) + o02*std::conj(U02) + o03*std::conj(U03);
        i00j01 = o00*std::conj(U10) + o01*std::conj(U11) + o02*std::conj(U12) + o03*std::conj(U13);
        i00j10 = o00*std::conj(U20) + o01*std::conj(U21) + o02*std::conj(U22) + o03*std::conj(U23);
        i00j11 = o00*std::conj(U30) + o01*std::conj(U31) + o02*std::conj(U32) + o03*std::conj(U33);
        i01j00 = o10*std::conj(U00) + o11*std::conj(U01) + o12*std::conj(U02) + o13*std::conj(U03);
        i01j01 = o10*std::conj(U10) + o11*std::conj(U11) + o12*std::conj(U12) + o13*std::conj(U13);
        i01j10 = o10*std::conj(U20) + o11*std::conj(U21) + o12*std::conj(U22) + o13*std::conj(U23);
        i01j11 = o10*std::conj(U30) + o11*std::conj(U31) + o12*std::conj(U32) + o13*std::conj(U33);
        i10j00 = o20*std::conj(U00) + o21*std::conj(U01) + o22*std::conj(U02) + o23*std::conj(U03);
        i10j01 = o20*std::conj(U10) + o21*std::conj(U11) + o22*std::conj(U12) + o23*std::conj(U13);
        i10j10 = o20*std::conj(U20) + o21*std::conj(U21) + o22*std::conj(U22) + o23*std::conj(U23);
        i10j11 = o20*std::conj(U30) + o21*std::conj(U31) + o22*std::conj(U32) + o23*std::conj(U33);
        i11j00 = o30*std::conj(U00) + o31*std::conj(U01) + o32*std::conj(U02) + o33*std::conj(U03);
        i11j01 = o30*std::conj(U10) + o31*std::conj(U11) + o32*std::conj(U12) + o33*std::conj(U13);
        i11j10 = o30*std::conj(U20) + o31*std::conj(U21) + o32*std::conj(U22) + o33*std::conj(U23);
        i11j11 = o30*std::conj(U30) + o31*std::conj(U31) + o32*std::conj(U32) + o33*std::conj(U33);
    }

    // ρ' = U * ρ  (left-multiply by U, 4x4)
    inline void dm_left_mul_u_4x4(
        const complex_t& U00, const complex_t& U01, const complex_t& U02, const complex_t& U03,
        const complex_t& U10, const complex_t& U11, const complex_t& U12, const complex_t& U13,
        const complex_t& U20, const complex_t& U21, const complex_t& U22, const complex_t& U23,
        const complex_t& U30, const complex_t& U31, const complex_t& U32, const complex_t& U33,
        complex_t& i00j00, complex_t& i00j01, complex_t& i00j10, complex_t& i00j11,
        complex_t& i01j00, complex_t& i01j01, complex_t& i01j10, complex_t& i01j11,
        complex_t& i10j00, complex_t& i10j01, complex_t& i10j10, complex_t& i10j11,
        complex_t& i11j00, complex_t& i11j01, complex_t& i11j10, complex_t& i11j11)
    {
        const complex_t o00=i00j00, o01=i00j01, o02=i00j10, o03=i00j11;
        const complex_t o10=i01j00, o11=i01j01, o12=i01j10, o13=i01j11;
        const complex_t o20=i10j00, o21=i10j01, o22=i10j10, o23=i10j11;
        const complex_t o30=i11j00, o31=i11j01, o32=i11j10, o33=i11j11;

        i00j00 = U00*o00 + U01*o10 + U02*o20 + U03*o30;
        i00j01 = U00*o01 + U01*o11 + U02*o21 + U03*o31;
        i00j10 = U00*o02 + U01*o12 + U02*o22 + U03*o32;
        i00j11 = U00*o03 + U01*o13 + U02*o23 + U03*o33;
        i01j00 = U10*o00 + U11*o10 + U12*o20 + U13*o30;
        i01j01 = U10*o01 + U11*o11 + U12*o21 + U13*o31;
        i01j10 = U10*o02 + U11*o12 + U12*o22 + U13*o32;
        i01j11 = U10*o03 + U11*o13 + U12*o23 + U13*o33;
        i10j00 = U20*o00 + U21*o10 + U22*o20 + U23*o30;
        i10j01 = U20*o01 + U21*o11 + U22*o21 + U23*o31;
        i10j10 = U20*o02 + U21*o12 + U22*o22 + U23*o32;
        i10j11 = U20*o03 + U21*o13 + U22*o23 + U23*o33;
        i11j00 = U30*o00 + U31*o10 + U32*o20 + U33*o30;
        i11j01 = U30*o01 + U31*o11 + U32*o21 + U33*o31;
        i11j10 = U30*o02 + U31*o12 + U32*o22 + U33*o32;
        i11j11 = U30*o03 + U31*o13 + U32*o23 + U33*o33;
    }
}
