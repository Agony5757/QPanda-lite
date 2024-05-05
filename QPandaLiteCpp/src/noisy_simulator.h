#include "simulator.h"

namespace qpandalite {
    enum class NoiseType : uint32_t
    {
        __NoiseTypeBegin,
        Depolarizing,
        Damping,
        BitFlip,
        PhaseFlip,
        TwoQubitDepolarizing,
        __NoiseTypeEnd,
    };

    enum class SupportOperationType : uint32_t
    {
        __SupportOperationTypeBegin = 1000,
        HADAMARD,
        U22,
        X,
        Y,
        Z,
        SX,
        CZ,
        SWAP,
        ISWAP,
        XY,
        CNOT,
        RX,
        RY,
        RZ,
        RPHI90,
        RPHI180,
        RPHI,
        TOFFOLI,
        CSWAP,
        __SupportOperationTypeEnd,
    };

    inline int gate_qubit_count(SupportOperationType type)
    {
        switch (type)
        {
        case SupportOperationType::HADAMARD:
        case SupportOperationType::U22:
        case SupportOperationType::X:
        case SupportOperationType::Y:
        case SupportOperationType::Z:
        case SupportOperationType::SX:
        case SupportOperationType::RX:
        case SupportOperationType::RY:
        case SupportOperationType::RZ:
        case SupportOperationType::RPHI90:
        case SupportOperationType::RPHI180:
        case SupportOperationType::RPHI:
            return 1;
        case SupportOperationType::CZ:
        case SupportOperationType::SWAP:
        case SupportOperationType::ISWAP:
        case SupportOperationType::XY:
        case SupportOperationType::CNOT:
            return 2;
        case SupportOperationType::TOFFOLI:
        case SupportOperationType::CSWAP:
            return 3;
        default:
            ThrowOutOfRange("Input does not belong to SupportOperationType.");
        }
    }

    inline NoiseType string_to_NoiseType(const std::string& noise_str)
    {
        static const std::map<std::string, NoiseType> noise_type_map =
        {
           {"depolarizing", NoiseType::Depolarizing},
           {"damping", NoiseType::Damping},
           {"bitflip", NoiseType::BitFlip},
           {"phaseflip", NoiseType::PhaseFlip},
           {"twoqubit_depolarizing", NoiseType::TwoQubitDepolarizing},
        };

        auto iter = noise_type_map.find(noise_str);
        if (iter != noise_type_map.end())
            return iter->second;

        // Handle the default case where the string doesn't match any known NoiseType        
        ThrowRuntimeError(fmt::format("Failed to handle noise_str: {}\nPlease check.", noise_str));
    }

    inline SupportOperationType string_to_SupportOperationType(const std::string& gate_str)
    {
        static const std::map<std::string, SupportOperationType> op_type_map =
        {
           {"HADAMARD", SupportOperationType::HADAMARD},
           {"U22", SupportOperationType::U22},
           {"X", SupportOperationType::X},
           {"Y", SupportOperationType::Y},
           {"Z", SupportOperationType::Z},
           {"SX", SupportOperationType::SX},
           {"CZ", SupportOperationType::CZ},
           {"SWAP", SupportOperationType::SWAP},
           {"ISWAP", SupportOperationType::ISWAP},
           {"XY", SupportOperationType::XY},
           {"CNOT", SupportOperationType::CNOT},
           {"RX", SupportOperationType::RX},
           {"RY", SupportOperationType::RY},
           {"RZ", SupportOperationType::RZ},
           {"RPHI90", SupportOperationType::RPHI90},
           {"RPHI180", SupportOperationType::RPHI180},
           {"RPHI", SupportOperationType::RPHI},
           {"TOFFOLI", SupportOperationType::TOFFOLI},
           {"CSWAP", SupportOperationType::CSWAP},
        };

        auto iter = op_type_map.find(gate_str);
        if (iter != op_type_map.end())
            return iter->second;

        // Handle the default case where the string doesn't match any known SupportOperationType
        ThrowRuntimeError(fmt::format("Failed to handle gate_str: {}\nPlease check.", gate_str));
        
    }

    // A simulator that specifically models quantum noise. It is derived from a base class named Simulator. 
    struct NoiseSimulatorImpl : public Simulator
    {
        // NoiseSimulatorImpl can make use of all the public and protected members (methods, variables, etc.) of the Simulator class.
        void depolarizing(size_t qn, double p);
        void damping(size_t qn, double gamma);
        void bitflip(size_t qn, double p);
        void phaseflip(size_t qn, double p);
        void twoqubit_depolarizing(size_t qn1, size_t qn2, double p);
        
        // Additional methods
        void reset(size_t qn);
        bool is_qubit_one(size_t qn);
        void scale_amplitude(size_t qn, double scale_factor);
        void normalize_state_vector();
    };

    struct OpcodeType
    {
        uint32_t op;
        std::vector<size_t> qubits;
        std::vector<double> parameters;
        bool dagger;
        std::vector<size_t> global_controller;
        OpcodeType(uint32_t op_,
            const std::vector<size_t>& qubits_,
            const std::vector<double>& parameters_,
            bool dagger_,
            const std::vector<size_t>& global_controller_
        ) :op(op_), qubits(qubits_),
            parameters(parameters_), dagger(dagger_),
            global_controller(global_controller_)
        {
        }
    };

    struct NoisySimulator
    {
        std::map<NoiseType, double> noise;

        // The measurement error is described by 1-P00 and 1-P11
        // When measured to 1, then it flips qi by measurement_error_matrices[qi][1] probability 
        std::vector<std::array<double, 2>> measurement_error_matrices;
        NoiseSimulatorImpl simulator;
        size_t nqubit;
        //std::vector<complex_t> state;
        std::vector<size_t> measure_qubits;
        std::map<size_t, size_t> measure_map;
        std::vector<OpcodeType> opcodes; // opcode + noisy
        std::vector<OpcodeType> original_opcodes; // perfect, without noise

        NoisySimulator(size_t n_qubit,
            const std::map<std::string, double>& noise_description,
            const std::vector<std::array<double, 2>>& measurement_error);

        void _load_noise(std::map<std::string, double> noise_description);

        void load_opcode(const std::string& opstr,
                const std::vector<size_t>& qubits, 
                const std::vector<double>& parameters,
                bool dagger, 
                const std::vector<size_t>& global_controller);
        
        /* Noisy simulation */
        void _insert_global_error(const std::vector<size_t>& qn);
        void _insert_generic_error(const std::vector<size_t>& qubits, const std::map<NoiseType, double>& generic_noise_map);

        void insert_error(const std::vector<size_t>& qn, SupportOperationType gateType);

        // Model the gate error
        // Perform bit flip based on measurement 

        void hadamard(size_t qn, bool is_dagger = false);
        void u22(size_t qn, const u22_t& unitary, bool is_dagger = false);
        void x(size_t qn, bool is_dagger = false);
        void z(size_t qn, bool is_dagger = false);
        void y(size_t qn, bool is_dagger = false);
        void sx(size_t qn, bool is_dagger = false);
        void cz(size_t qn1, size_t qn2, bool is_dagger = false);
        void swap(size_t qn1, size_t qn2, bool is_dagger = false);
        void iswap(size_t qn1, size_t qn2, bool is_dagger = false);
        void xy(size_t qn1, size_t qn2, double theta, bool is_dagger = false);
        void cnot(size_t controller, size_t target, bool is_dagger = false);
        void rx(size_t qn, double angle, bool is_dagger = false);
        void ry(size_t qn, double angle, bool is_dagger = false);
        void rz(size_t qn, double angle, bool is_dagger = false);
        void rphi90(size_t qn, double phi, bool is_dagger = false);
        void rphi180(size_t qn, double phi, bool is_dagger = false);
        void rphi(size_t qn, double phi, double theta, bool is_dagger = false);
        void toffoli(size_t qn1, size_t qn2, size_t target, bool is_dagger = false);
        void cswap(size_t controller, size_t target1, size_t target2, bool is_dagger = false);

        void hadamard_cont(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void u22_cont(size_t qn, const u22_t& unitary, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void x_cont(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void z_cont(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void y_cont(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void sx_cont(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void cz_cont(size_t qn1, size_t qn2, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void swap_cont(size_t qn1, size_t qn2, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void iswap_cont(size_t qn1, size_t qn2, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void xy_cont(size_t qn1, size_t qn2, double theta, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void cnot_cont(size_t controller, size_t target, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void rx_cont(size_t qn, double angle, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void ry_cont(size_t qn, double angle, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void rz_cont(size_t qn, double angle, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void rphi90_cont(size_t qn, double phi, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void rphi180_cont(size_t qn, double phi, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void rphi_cont(size_t qn, double phi, double theta, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void toffoli_cont(size_t qn1, size_t qn2, size_t target, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void cswap_cont(size_t controller, size_t target1, size_t target2, const std::vector<size_t>& global_controller, bool is_dagger = false);

        void measure(const std::vector<size_t> measure_qubits_);

        void execute_once();
        std::pair<size_t, double> _get_state_prob(size_t i);
        size_t get_measure_no_readout_error();
        size_t get_measure();
        std::map<size_t, size_t> measure_shots(const std::vector<size_t>& measure_list, size_t shots);

    };

    struct NoisySimulator_GateDependent : public NoisySimulator
    {
        using GateDependentNoise_t = std::map<SupportOperationType, std::map<NoiseType, double>>;
        using GateDependentNoise_Description_t = std::map<std::string, std::map<std::string, double>>;
        GateDependentNoise_t gate_dependent_noise;

        NoisySimulator_GateDependent(size_t n_qubit,
            const std::map<std::string, double>& noise_description,
            const GateDependentNoise_Description_t& gate_noise_description,
            const std::vector<std::array<double, 2>>& measurement_error);

        void _load_gate_dependent_noise(const GateDependentNoise_Description_t&gate_noise_description);

        /* Noisy simulation */
        void insert_error(const std::vector<size_t>& qn, SupportOperationType gateType);
        void _insert_gate_dependent_error(const std::vector<size_t>& qubits, SupportOperationType gateType);
        
    };

    struct NoisySimulator_GateErrorSpecific : public NoisySimulator
    {
        using GateError1q_t = std::map<std::pair<SupportOperationType, size_t>, std::map<NoiseType, double>>;
        using GateError2q_t = std::map<std::pair<SupportOperationType, std::pair<size_t, size_t>>, std::map<NoiseType, double>>;
        using GateError1q_Description_t = std::map<std::pair<std::string, size_t>, std::map<std::string, double>>;
        using GateError2q_Description_t = std::map<std::pair<std::string, std::pair<size_t, size_t>>, std::map<std::string, double>>;
        GateError1q_t gate_error1q;
        GateError2q_t gate_error2q;

        NoisySimulator_GateErrorSpecific(size_t n_qubit,
            const std::map<std::string, double>& noise_description,
            const GateError1q_Description_t& gate_error1q_description,
            const GateError2q_Description_t& gate_error2q_description,
            const std::vector<std::array<double, 2>>& measurement_error);

        void _load_gate_error1q(const GateError1q_Description_t& gate_noise_description);
        void _load_gate_error2q(const GateError2q_Description_t& gate_noise_description);

        /* Noisy simulation */
        void insert_error(const std::vector<size_t>& qn, SupportOperationType gateType);
        void _insert_gate_error1q(SupportOperationType gateType, size_t qn);
        void _insert_gate_error2q(SupportOperationType gateType, size_t qn1, size_t qn2);
    };

}