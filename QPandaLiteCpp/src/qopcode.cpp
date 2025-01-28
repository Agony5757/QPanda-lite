#include "qopcode.h"

namespace qpandalite {

    // DEPRECATED !!!!
    // 
    //UnitaryType string_to_UnitaryType(const std::string& gate_str)
    //{
    //    static const std::map<std::string, UnitaryType> op_type_map =
    //    {
    //        { "HADAMARD", UnitaryType::HADAMARD },
    //        { "IDENTITY", UnitaryType::IDENTITY },
    //        { "U22", UnitaryType::U22 },
    //        { "X", UnitaryType::X },
    //        { "Y", UnitaryType::Y },
    //        { "Z", UnitaryType::Z },
    //        { "SX", UnitaryType::SX },
    //        { "CZ", UnitaryType::CZ },
    //        { "SWAP", UnitaryType::SWAP },
    //        { "ISWAP", UnitaryType::ISWAP },
    //        { "XY", UnitaryType::XY },
    //        { "CNOT", UnitaryType::CNOT },
    //        { "RX", UnitaryType::RX },
    //        { "RY", UnitaryType::RY },
    //        { "RZ", UnitaryType::RZ },
    //        { "U1", UnitaryType::U1 },
    //        { "U2", UnitaryType::U2 },
    //        { "RPHI90", UnitaryType::RPHI90 },
    //        { "RPHI180", UnitaryType::RPHI180 },
    //        { "RPHI", UnitaryType::RPHI },
    //        { "TOFFOLI", UnitaryType::TOFFOLI },
    //        { "CSWAP", UnitaryType::CSWAP },
    //        { "ZZ", UnitaryType::ZZ },
    //        { "XX", UnitaryType::XX },
    //        { "YY", UnitaryType::YY },
    //        { "U3", UnitaryType::U3 },
    //        { "PHASE2Q", UnitaryType::PHASE2Q },
    //        { "UU15", UnitaryType::UU15 },
    //    };

    //    auto iter = op_type_map.find(gate_str);
    //    if (iter != op_type_map.end())
    //        return iter->second;

    //    // Handle the default case where the string doesn't match any known UnitaryType
    //    ThrowRuntimeError(fmt::format("Failed to handle gate_str: {}\nPlease check.", gate_str));
    //}

    //NoiseType string_to_NoiseType(const std::string& noise_str)
    //{
    //    static const std::map<std::string, NoiseType> noise_type_map =
    //    {
    //        { "depolarizing", NoiseType::Depolarizing },
    //        { "damping", NoiseType::Damping },
    //        { "bitflip", NoiseType::BitFlip },
    //        { "phaseflip", NoiseType::PhaseFlip },
    //        { "twoqubit_depolarizing", NoiseType::TwoQubitDepolarizing },
    //    };

    //    auto iter = noise_type_map.find(noise_str);
    //    if (iter != noise_type_map.end())
    //        return iter->second;

    //    // Handle the default case where the string doesn't match any known NoiseType        
    //    ThrowRuntimeError(fmt::format("Failed to handle noise_str: {}\nPlease check.", noise_str));
    //}

    //int gate_qubit_count(UnitaryType type)
    //{
    //    switch (type)
    //    {
    //    case UnitaryType::HADAMARD:
    //    case UnitaryType::U22:
    //    case UnitaryType::X:
    //    case UnitaryType::Y:
    //    case UnitaryType::Z:
    //    case UnitaryType::SX:
    //    case UnitaryType::S:
    //    case UnitaryType::T:
    //    case UnitaryType::RX:
    //    case UnitaryType::RY:
    //    case UnitaryType::RZ:
    //    case UnitaryType::RPHI90:
    //    case UnitaryType::RPHI180:
    //    case UnitaryType::RPHI:
    //    case UnitaryType::U1:
    //    case UnitaryType::U2:
    //    case UnitaryType::U3:
    //        return 1;
    //    case UnitaryType::CZ:
    //    case UnitaryType::SWAP:
    //    case UnitaryType::ISWAP:
    //    case UnitaryType::XY:
    //    case UnitaryType::CNOT:
    //    case UnitaryType::XX:
    //    case UnitaryType::YY:
    //    case UnitaryType::ZZ:
    //    case UnitaryType::PHASE2Q:
    //    case UnitaryType::UU15:
    //        return 2;
    //    case UnitaryType::TOFFOLI:
    //    case UnitaryType::CSWAP:
    //        return 3;
    //    default:
    //        ThrowOutOfRange("Input does not belong to UnitaryType.");
    //    }
    //}
} // namespace qpandalite