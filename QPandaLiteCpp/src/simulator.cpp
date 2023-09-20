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

    void Simulator::hadamard(size_t qn)
    {
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, input = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
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

    void Simulator::x(size_t qn)
    {
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, input = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i >> qn) & 1)
            {
                std::swap(state[i], state[i - pow2(qn)]);
            }
        }
    }

    void Simulator::z(size_t qn)
    {
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, input = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i >> qn) & 1)
            {
                state[i] *= -1;
            }
        }
    }
    
    void Simulator::u22(size_t qn, const std::array<complex_t, 4> &unitary)
    {
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
        
        complex_t u00 = unitary[0];
        complex_t u01 = unitary[1];
        complex_t u10 = unitary[2];
        complex_t u11 = unitary[3];
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
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

    void Simulator::cz(size_t qn1, size_t qn2)
    {
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

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if (((i >> qn1) & 1) && ((i >> qn2) & 1))
            {
                state[i] *= -1;
            }
        }
    }

    void Simulator::cnot(size_t controller, size_t target)
    {
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

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if (((i >> controller) & 1) && ((i >> target) & 1))
            {
                std::swap(state[i], state[i - pow2(target)]);
            }
        }
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
                auto errstr = fmt::format("State must be 0 or 1. (input = {} at qn = {})", state, qn);
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
            auto errstr = fmt::format("State must be 0 or 1. (input = {} at qn = {})", state, qn);
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
}