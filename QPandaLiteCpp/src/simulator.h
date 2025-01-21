#pragma once

#include <array>
#include <complex>
#include <iostream>
#include <vector>
#include <set>
#include <map>
#include <cstdint>

#include "errors.h"
#include "simulator_impl.h"
namespace qpandalite {

    struct Simulator
    {
        static inline size_t max_qubit_num = 30;
        size_t total_qubit = 0;
        std::vector<complex_t> state;

        void init_n_qubit(size_t nqubit);
        //void hadamard(size_t qn,                        bool is_dagger = false);
        //void u22(size_t qn, const u22_t& unitary,       bool is_dagger = false);
        //void x(size_t qn,                               bool is_dagger = false);
        //void z(size_t qn,                               bool is_dagger = false);
        //void y(size_t qn,                               bool is_dagger = false);
        //void sx(size_t qn,                              bool is_dagger = false);
        //void cz(size_t qn1, size_t qn2,                 bool is_dagger = false);
        //void swap(size_t qn1, size_t qn2,               bool is_dagger = false);
        //void iswap(size_t qn1, size_t qn2,              bool is_dagger = false);
        //void xy(size_t qn1, size_t qn2, double theta,   bool is_dagger = false);
        //void cnot(size_t controller, size_t target,     bool is_dagger = false);
        //void rx(size_t qn, double angle,                bool is_dagger = false);
        //void ry(size_t qn, double angle,                bool is_dagger = false);
        //void rz(size_t qn, double angle,                bool is_dagger = false);
        //void rphi90(size_t qn, double phi,              bool is_dagger = false);
        //void rphi180(size_t qn, double phi,             bool is_dagger = false);
        //void rphi(size_t qn, double phi, double theta,  bool is_dagger = false);
        //void toffoli(size_t qn1, size_t qn2, size_t target, bool is_dagger = false);
        //void cswap(size_t controller, size_t target1, size_t target2, bool is_dagger = false); 
        //void zz(size_t qn1, size_t qn2, double theta,   bool is_dagger = false);
        //void xx(size_t qn1, size_t qn2, double theta,   bool is_dagger = false);
        //void yy(size_t qn1, size_t qn2, double theta,   bool is_dagger = false);
        //void u3(size_t qn, double theta, double phi, double lambda, bool is_dagger = false);

        void hadamard(size_t qn, const std::vector<size_t>& global_controller = {}, bool is_dagger = false);
        void u22(size_t qn, const u22_t& unitary, const std::vector<size_t>& global_controller = {}, bool is_dagger = false);
        void x(size_t qn, const std::vector<size_t>& global_controller = {}, bool is_dagger = false);
        void y(size_t qn, const std::vector<size_t>& global_controller = {}, bool is_dagger = false);
        void z(size_t qn, const std::vector<size_t>& global_controller = {}, bool is_dagger = false);
        void s(size_t qn, const std::vector<size_t>& global_controller = {}, bool is_dagger = false);
        void t(size_t qn, const std::vector<size_t>& global_controller = {}, bool is_dagger = false);
        void sx(size_t qn, const std::vector<size_t>& global_controller = {}, bool is_dagger = false);
        void cz(size_t qn1, size_t qn2, const std::vector<size_t>& global_controller = {}, bool is_dagger = false);
        void swap(size_t qn1, size_t qn2, const std::vector<size_t>& global_controller = {}, bool is_dagger = false);
        void iswap(size_t qn1, size_t qn2, const std::vector<size_t>& global_controller = {}, bool is_dagger = false);
        void xy(size_t qn1, size_t qn2, double theta, const std::vector<size_t>& global_controller = {}, bool is_dagger = false);
        void cnot(size_t controller, size_t target, const std::vector<size_t>& global_controller = {}, bool is_dagger = false);
        void rx(size_t qn, double angle, const std::vector<size_t>& global_controller = {}, bool is_dagger = false);
        void ry(size_t qn, double angle, const std::vector<size_t>& global_controller = {}, bool is_dagger = false);
        void rz(size_t qn, double angle, const std::vector<size_t>& global_controller = {}, bool is_dagger = false);
        void u1(size_t qn, double angle, const std::vector<size_t>& global_controller = {}, bool is_dagger = false);
        void rphi90(size_t qn, double phi, const std::vector<size_t>& global_controller = {}, bool is_dagger = false);
        void rphi180(size_t qn, double phi, const std::vector<size_t>& global_controller = {}, bool is_dagger = false);
        void rphi(size_t qn, double theta, double phi, const std::vector<size_t>& global_controller = {}, bool is_dagger = false);
        void toffoli(size_t qn1, size_t qn2, size_t target, const std::vector<size_t>& global_controller = {}, bool is_dagger = false);
        void cswap(size_t controller, size_t target1, size_t target2, const std::vector<size_t>& global_controller = {}, bool is_dagger = false);
        void zz(size_t qn1, size_t qn2, double theta, const std::vector<size_t>& global_controller = {}, bool is_dagger = false);
        void xx(size_t qn1, size_t qn2, double theta, const std::vector<size_t>& global_controller = {}, bool is_dagger = false);
        void yy(size_t qn1, size_t qn2, double theta, const std::vector<size_t>& global_controller = {}, bool is_dagger = false);
        void u3(size_t qn, double theta, double phi, double lambda, const std::vector<size_t>& global_controller = {}, bool is_dagger = false);
        void uu15(size_t qn1, size_t qn2, const std::vector<double>& parameters, const std::vector<size_t>& global_controller = {}, bool is_dagger = false);

        // static bool control_enable(size_t idx, const std::vector<size_t>& global_controller);

        dtype get_prob_map(const std::map<size_t, int>& measure_qubits);
        dtype get_prob(size_t qn, int state);
        std::vector<dtype> pmeasure_list(const std::vector<size_t>& measure_list);
        std::vector<dtype> pmeasure(size_t measure_qubit);
    };

}
