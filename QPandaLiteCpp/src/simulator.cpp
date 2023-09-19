#include "simulator.h"

namespace qpandalite{
    void Simulator::init_n_qubit(size_t nqubit)
    {
        if (nqubit > max_qubit_num)
            ThrowRuntimeError(fmt::format("Exceed max_qubit_num (nqubit = {}, limit = {})", nqubit, max_qubit_num));

        state = std::vector<complex_t>(pow2(nqubit), 0);
        state[0] = 1;
        total_qubit = nqubit;
    }

    void Simulator::hadamard(size_t qn)
    {
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
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if (((i >> controller) & 1) && ((i >> target) & 1))
            {
                std::swap(state[i], state[i - pow2(target)]);
            }
        }
    }
}