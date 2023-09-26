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

    void Simulator::sx(size_t qn)
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

    void Simulator::y(size_t qn)
    {
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, input = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

        using namespace std::literals::complex_literals;
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i >> qn) & 1)
            {
                std::swap(state[i], state[i - pow2(qn)]);
                state[i - pow2(qn)] *= -1i;
                state[i] *= 1i;
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
    
    void Simulator::u22(size_t qn, const u22_t &unitary)
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
        if (qn1 == qn2)
        {
            auto errstr = fmt::format("qn1 = qn2");
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

    void Simulator::iswap(size_t qn1, size_t qn2)
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
        if (qn1 == qn2)
        {
            auto errstr = fmt::format("qn1 = qn2");
            ThrowInvalidArgument(errstr);
        }

        using namespace std::literals::complex_literals;
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if (((i >> qn1) & 1) == 0 && ((i >> qn2) & 1) == 1)
            {
                std::swap(state[i], state[i + pow2(qn1) - pow2(qn2)]);
                state[i] *= 1i;
                state[i + pow2(qn1) - pow2(qn2)] *= 1i;
            }

        }
    }

    void Simulator::xy(size_t qn1, size_t qn2)
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
        if (qn1 == qn2)
        {
            auto errstr = fmt::format("qn1 = qn2");
            ThrowInvalidArgument(errstr);
        }

        using namespace std::literals::complex_literals;
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if (((i >> qn1) & 1) == 0 && ((i >> qn2) & 1) == 1)
            {
                std::swap(state[i], state[i + pow2(qn1) - pow2(qn2)]);
                state[i] *= 1i;
                state[i + pow2(qn1) - pow2(qn2)] *= 1i;
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
        if (controller == target)
        {
            auto errstr = fmt::format("controller = target");
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

    void Simulator::rx(size_t qn, double angle)
    {
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

        // Rx 
        using namespace std::literals::complex_literals;
        u22_t unitary = {cos(angle / 2), -sin(angle / 2) * 1i,
                         -sin(angle / 2) * 1i, cos(angle / 2)};

        u22(qn, unitary);
    }

    void Simulator::ry(size_t qn, double angle)
    {
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

        using namespace std::literals::complex_literals;
        u22_t unitary = {cos(angle / 2), -sin(angle / 2),
                         sin(angle / 2), cos(angle / 2)};

        u22(qn, unitary);
    }

    void Simulator::rz(size_t qn, double angle)
    {
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            if ((i >> qn) & 1)
            {
                state[i] *= std::complex(cos(angle), -sin(angle));
            }
        }
    }

    void Simulator::rphi90(size_t qn, double phi)
    {
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

        using namespace std::literals::complex_literals;
        u22_t unitary;
        unitary[0] = INVSQRT2;
        unitary[1] = INVSQRT2 * -1i * std::complex(cos(phi), -sin(phi));
        unitary[2] = INVSQRT2 * -1i * std::complex(cos(phi), sin(phi));
        unitary[3] = INVSQRT2;

        u22(qn, unitary);
    }

    void Simulator::rphi180(size_t qn, double phi)
    {
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

        using namespace std::literals::complex_literals;
        u22_t unitary;
        unitary[0] = 0;
        unitary[1] = -1i * std::complex(cos(phi), -sin(phi));
        unitary[2] = -1i * std::complex(cos(phi), sin(phi));
        unitary[3] = 0;

        u22(qn, unitary);        
    }

    void Simulator::rphi(size_t qn, double phi, double theta)
    {
        if (qn >= total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, qn = {})", total_qubit, qn);
            ThrowInvalidArgument(errstr);
        }

        using namespace std::literals::complex_literals;
        u22_t unitary;
        unitary[0] = cos(theta / 2);
        unitary[1] = -1i * sin(theta / 2) * std::complex(cos(phi), -sin(phi));
        unitary[2] = -1i * sin(theta / 2) * std::complex(cos(phi), sin(phi));
        unitary[3] = cos(theta / 2);

        u22(qn, unitary);    
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
            qlist.insert({qn,i});
        }

        std::vector<dtype> ret;
        ret.resize(pow2(measure_list.size()));
        
        for (size_t i = 0; i < pow2(total_qubit); ++i)
        {
            size_t meas_idx = 0;
            for (auto &&[qn, j] : qlist)
            {
                // put "digit qn" of i to "digit j"
                meas_idx += (((i >> qn) & 1) << j);
            }
            ret[meas_idx] += abs_sqr(state[i]);
        }
        return ret;
    }

    std::vector<dtype> Simulator::pmeasure(size_t measure_qubit)
    {
        return pmeasure_list(std::vector{measure_qubit});
    }

}