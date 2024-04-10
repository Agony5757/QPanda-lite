#pragma once

#include <array>
#include <complex>
#include <iostream>
#include <vector>
#include <set>
#include <map>

#include "errors.h"
namespace qpandalite {
    using dtype = double;
    using complex_t = std::complex<dtype>;
    using u22_t = std::array<complex_t, 4>;
    
    constexpr dtype SQRT2 = 1.4142135623730951;
    constexpr dtype INVSQRT2 = 1.0 / SQRT2;
    constexpr dtype eps = 1e-7;

    constexpr unsigned long long pow2(size_t n) { return 1ull << n; }
    constexpr auto abs_sqr(complex_t c)
    {
        return c.real() * c.real() + c.imag() * c.imag();
    }

    constexpr auto float_equal(dtype a, dtype b)
    {
        dtype compare = a - b;
        if (compare > eps) return false;
        if (compare < -eps) return false;
        return true;
    }

    constexpr auto complex_equal(complex_t a, complex_t b)
    {
        dtype compare_real = a.real() - b.real();
        if (compare_real > eps) return false;
        if (compare_real < -eps) return false;

        dtype compare_imag = a.imag() - b.imag();
        if (compare_imag > eps) return false;
        if (compare_imag < -eps) return false;
        return true;
    }
    
    inline bool _assert_u22(const u22_t &u)
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

    inline std::map<size_t, size_t> preprocess_measure_list(const std::vector<size_t> &measure_list, size_t total_qubit)
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

    inline size_t get_state_with_qubit(size_t i, const std::map<size_t, size_t> &measure_map)
    {
        size_t ret = 0;
        for (auto&& [qn, j] : measure_map)
        {
            // put "digit qn" of i to "digit j"
            ret += (((i >> qn) & 1) << j);
        }
        return ret;
    }

    struct Simulator
    { 
        static inline size_t max_qubit_num = 30;
        size_t total_qubit = 0;
        std::vector<complex_t> state;

        void init_n_qubit(size_t nqubit);
        void hadamard(size_t qn,                        bool is_dagger = false);
        void u22(size_t qn, const u22_t& unitary,       bool is_dagger = false);
        void x(size_t qn,                               bool is_dagger = false);
        void z(size_t qn,                               bool is_dagger = false);
        void y(size_t qn,                               bool is_dagger = false);
        void sx(size_t qn,                              bool is_dagger = false);
        void cz(size_t qn1, size_t qn2,                 bool is_dagger = false);
        void iswap(size_t qn1, size_t qn2,              bool is_dagger = false);
        void xy(size_t qn1, size_t qn2, double theta,   bool is_dagger = false);
        void cnot(size_t controller, size_t target,     bool is_dagger = false);
        void swap(size_t qn1, size_t qn2,               bool is_dagger = false);
        void rx(size_t qn, double angle,                bool is_dagger = false);
        void ry(size_t qn, double angle,                bool is_dagger = false);
        void rz(size_t qn, double angle,                bool is_dagger = false);
        void rphi90(size_t qn, double phi,              bool is_dagger = false);
        void rphi180(size_t qn, double phi,             bool is_dagger = false);
        void rphi(size_t qn, double phi, double theta,  bool is_dagger = false);
        

        // void ccnot(size_t controller, size_t target1, size_t target2, bool is_dagger = false);
        // void cswap(size_t controller, size_t target1, size_t target2, bool is_dagger = false);

        void hadamard_cont(size_t qn,                        const std::vector<size_t>& global_controller, bool is_dagger = false);
        void u22_cont(size_t qn, const u22_t &unitary,       const std::vector<size_t>& global_controller, bool is_dagger = false);
        void x_cont(size_t qn,                               const std::vector<size_t>& global_controller, bool is_dagger = false);
        void z_cont(size_t qn,                               const std::vector<size_t>& global_controller, bool is_dagger = false);
        void y_cont(size_t qn,                               const std::vector<size_t>& global_controller, bool is_dagger = false);
        void sx_cont(size_t qn,                              const std::vector<size_t>& global_controller, bool is_dagger = false);
        void cz_cont(size_t qn1, size_t qn2,                 const std::vector<size_t>& global_controller, bool is_dagger = false);
        void iswap_cont(size_t qn1, size_t qn2,              const std::vector<size_t>& global_controller, bool is_dagger = false);
        void xy_cont(size_t qn1, size_t qn2, double theta,   const std::vector<size_t>& global_controller, bool is_dagger = false);
        void cnot_cont(size_t controller, size_t target,     const std::vector<size_t>& global_controller, bool is_dagger = false);
        void rx_cont(size_t qn, double angle,                const std::vector<size_t>& global_controller, bool is_dagger = false);
        void ry_cont(size_t qn, double angle,                const std::vector<size_t>& global_controller, bool is_dagger = false);
        void rz_cont(size_t qn, double angle,                const std::vector<size_t>& global_controller, bool is_dagger = false);
        void rphi90_cont(size_t qn, double phi,              const std::vector<size_t>& global_controller, bool is_dagger = false);
        void rphi180_cont(size_t qn, double phi,             const std::vector<size_t>& global_controller, bool is_dagger = false);
        void rphi_cont(size_t qn, double phi, double theta,  const std::vector<size_t>& global_controller, bool is_dagger = false);

        static bool control_enable(size_t idx, const std::vector<size_t>& global_controller);

        dtype get_prob_map(const std::map<size_t, int> &measure_qubits);
        dtype get_prob(size_t qn, int state);
        std::vector<dtype> pmeasure_list(const std::vector<size_t> &measure_list);
        std::vector<dtype> pmeasure(size_t measure_qubit);
    };

}
