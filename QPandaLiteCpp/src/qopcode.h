#pragma once

// opcode loader
// Instead of immediately execute the quantum program,
// we can load the program first, and then compute.
// This allows a flexible loader for **Noisy simulation**

#include "errors.h"

namespace qpandalite {
    
    // DEPRECATED !!!!

    ///* Operation type */
    //enum class UnitaryType : uint32_t
    //{
    //    __SupportOperationTypeBegin = 1000,
    //    IDENTITY,
    //    HADAMARD,
    //    U22,
    //    X,
    //    Y,
    //    Z,
    //    S,
    //    T,
    //    SX,
    //    CZ,
    //    SWAP,
    //    ISWAP,
    //    XY,
    //    CNOT,
    //    RX,
    //    RY,
    //    RZ,
    //    U1,
    //    U2,
    //    RPHI90,
    //    RPHI180,
    //    RPHI,
    //    TOFFOLI,
    //    CSWAP,
    //    ZZ,
    //    XX,
    //    YY,
    //    U3,
    //    PHASE2Q,
    //    UU15,
    //    __SupportOperationTypeEnd,
    //};

    //UnitaryType string_to_UnitaryType(const std::string& gate_str);

    //enum class NoiseType : uint32_t
    //{
    //    __NoiseTypeBegin=20000,
    //    Depolarizing,
    //    Damping,
    //    BitFlip,
    //    PhaseFlip,
    //    TwoQubitDepolarizing,
    //    __NoiseTypeEnd,
    //};

    //NoiseType string_to_NoiseType(const std::string& noise_str);

    //int gate_qubit_count(UnitaryType type);

    //struct OpcodeType
    //{
    //    uint32_t op;
    //    std::vector<size_t> qubits;
    //    std::vector<double> parameters;
    //    bool dagger;
    //    std::vector<size_t> global_controller;
    //    OpcodeType(uint32_t op_,
    //        const std::vector<size_t>& qubits_,
    //        const std::vector<double>& parameters_,
    //        bool dagger_,
    //        const std::vector<size_t>& global_controller_
    //    ) :op(op_), qubits(qubits_),
    //        parameters(parameters_), dagger(dagger_),
    //        global_controller(global_controller_)
    //    {
    //    }
    //};

} // namespace qpandalite