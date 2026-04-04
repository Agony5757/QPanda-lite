#include "simulator_common.h"

namespace qpandalite {
    std::map<size_t, size_t> preprocess_measure_list(const std::vector<size_t>& measure_list, size_t total_qubit)
    {
        if (measure_list.size() > total_qubit)
        {
            auto errstr = fmt::format("Exceed total (total_qubit = {}, measure_list size = {})", total_qubit, measure_list.size());
            ThrowInvalidArgument(errstr);
        }

        std::map<size_t, size_t> qbit_cbit_map;
        for (size_t i = 0; i < measure_list.size(); ++i)
        {
            size_t qn = measure_list[i];
            if (qn >= total_qubit)
            {
                auto errstr = fmt::format("Exceed total (total_qubit = {}, measure_qubit = {})", total_qubit, qn);
                ThrowInvalidArgument(errstr);
            }
            if (qbit_cbit_map.find(qn) != qbit_cbit_map.end())
            {
                auto errstr = fmt::format("Duplicate measure qubit ({})", qn);
                ThrowInvalidArgument(errstr);
            }
            qbit_cbit_map.insert({ qn,i });
        }
        return qbit_cbit_map;
    }

    size_t get_state_with_qubit(size_t i, const std::map<size_t, size_t>& measure_map)
    {
        size_t ret = 0;
        for (auto&& [qidx, cidx] : measure_map)
        {
            ret += (((i >> qidx) & 1) << cidx);
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
} // namespace qpandalite
