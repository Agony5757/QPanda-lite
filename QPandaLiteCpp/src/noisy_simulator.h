#include "simulator.h"
#include "qopcode.h"

namespace qpandalite {

    //// A simulator that specifically models quantum noise. It is derived from a base class named StatevectorSimulator. 
    //struct NoiseSimulatorImpl : public StatevectorSimulator
    //{
    //    // NoiseSimulatorImpl can make use of all the public and protected members (methods, variables, etc.) of the StatevectorSimulator class.
    //    void depolarizing(size_t qn, double p);
    //    void damping(size_t qn, double gamma);
    //    void bitflip(size_t qn, double p);
    //    void phaseflip(size_t qn, double p);
    //    void twoqubit_depolarizing(size_t qn1, size_t qn2, double p);
    //    
    //    // Additional methods
    //    void reset(size_t qn);
    //    bool is_qubit_one(size_t qn);
    //    void scale_amplitude(size_t qn, double scale_factor);
    //    void normalize_state_vector();
    //};


    //struct NoisySimulator
    //{
    //    std::map<NoiseType, double> noise;

    //    // The measurement error is described by 1-P00 and 1-P11
    //    // When measured to 1, then it flips qi by measurement_error_matrices[qi][1] probability 
    //    std::vector<std::array<double, 2>> measurement_error_matrices;
    //    StatevectorSimulator simulator;
    //    size_t nqubit;
    //    //std::vector<complex_t> state;
    //    std::vector<size_t> measure_qubits;
    //    std::map<size_t, size_t> measure_map;
    //    std::vector<OpcodeType> opcodes; // opcode + noisy
    //    
    //    NoisySimulator(size_t n_qubit,
    //        const std::map<std::string, double>& noise_description,
    //        const std::vector<std::array<double, 2>>& measurement_error);

    //    void _load_noise(std::map<std::string, double> noise_description);

    //    void load_opcode(const std::string& opstr,
    //            const std::vector<size_t>& qubits, 
    //            const std::vector<double>& parameters,
    //            bool dagger, 
    //            const std::vector<size_t>& global_controller);
    //    
    //    /* Noisy simulation */
    //    void _insert_global_error(const std::vector<size_t>& qn);
    //    void _insert_generic_error(const std::vector<size_t>& qubits, const std::map<NoiseType, double>& generic_noise_map);

    //    void insert_error(const std::vector<size_t>& qn, UnitaryType gateType);

    //    // Model the gate error
    //    // Perform bit flip based on measurement 

    //    //void hadamard(size_t qn, bool is_dagger = false);
    //    //void id(size_t qn, bool is_dagger = false);
    //    //void u22(size_t qn, const u22_t& unitary, bool is_dagger = false);
    //    //void x(size_t qn, bool is_dagger = false);
    //    //void z(size_t qn, bool is_dagger = false);
    //    //void y(size_t qn, bool is_dagger = false);
    //    //void sx(size_t qn, bool is_dagger = false);
    //    //void cz(size_t qn1, size_t qn2, bool is_dagger = false);
    //    //void swap(size_t qn1, size_t qn2, bool is_dagger = false);
    //    //void iswap(size_t qn1, size_t qn2, bool is_dagger = false);
    //    //void xy(size_t qn1, size_t qn2, double theta, bool is_dagger = false);
    //    //void cnot(size_t controller, size_t target, bool is_dagger = false);
    //    //void rx(size_t qn, double angle, bool is_dagger = false);
    //    //void ry(size_t qn, double angle, bool is_dagger = false);
    //    //void rz(size_t qn, double angle, bool is_dagger = false);
    //    //void rphi90(size_t qn, double phi, bool is_dagger = false);
    //    //void rphi180(size_t qn, double phi, bool is_dagger = false);
    //    //void rphi(size_t qn, double phi, double theta, bool is_dagger = false);
    //    //void toffoli(size_t qn1, size_t qn2, size_t target, bool is_dagger = false);
    //    //void cswap(size_t controller, size_t target1, size_t target2, bool is_dagger = false);
    //    //void zz(size_t qn1, size_t qn2, double theta, bool is_dagger = false);
    //    //void xx(size_t qn1, size_t qn2, double theta, bool is_dagger = false);
    //    //void yy(size_t qn1, size_t qn2, double theta, bool is_dagger = false);
    //    //void u3(size_t qn1, double theta, double phi, double lambda, bool is_dagger = false);

    //    void id(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger = false);
    //    void hadamard(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger = false);
    //    void u22(size_t qn, const u22_t& unitary, const std::vector<size_t>& global_controller, bool is_dagger = false);
    //    void x(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger = false);
    //    void z(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger = false);
    //    void y(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger = false);
    //    void sx(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger = false);
    //    void cz(size_t qn1, size_t qn2, const std::vector<size_t>& global_controller, bool is_dagger = false);
    //    void swap(size_t qn1, size_t qn2, const std::vector<size_t>& global_controller, bool is_dagger = false);
    //    void iswap(size_t qn1, size_t qn2, const std::vector<size_t>& global_controller, bool is_dagger = false);
    //    void xy(size_t qn1, size_t qn2, double theta, const std::vector<size_t>& global_controller, bool is_dagger = false);
    //    void cnot(size_t controller, size_t target, const std::vector<size_t>& global_controller, bool is_dagger = false);
    //    void rx(size_t qn, double angle, const std::vector<size_t>& global_controller, bool is_dagger = false);
    //    void ry(size_t qn, double angle, const std::vector<size_t>& global_controller, bool is_dagger = false);
    //    void rz(size_t qn, double angle, const std::vector<size_t>& global_controller, bool is_dagger = false);
    //    void rphi90(size_t qn, double phi, const std::vector<size_t>& global_controller, bool is_dagger = false);
    //    void rphi180(size_t qn, double phi, const std::vector<size_t>& global_controller, bool is_dagger = false);
    //    void rphi(size_t qn, double phi, double theta, const std::vector<size_t>& global_controller, bool is_dagger = false);
    //    void toffoli(size_t qn1, size_t qn2, size_t target, const std::vector<size_t>& global_controller, bool is_dagger = false);
    //    void cswap(size_t controller, size_t target1, size_t target2, const std::vector<size_t>& global_controller, bool is_dagger = false);
    //    void zz(size_t qn1, size_t qn2, double theta, const std::vector<size_t>& global_controller, bool is_dagger = false);
    //    void xx(size_t qn1, size_t qn2, double theta, const std::vector<size_t>& global_controller, bool is_dagger = false);
    //    void yy(size_t qn1, size_t qn2, double theta, const std::vector<size_t>& global_controller, bool is_dagger = false);
    //    void u3(size_t qn1, double theta, double phi, double lambda, const std::vector<size_t>& global_controller, bool is_dagger = false);

    //    void measure(const std::vector<size_t> measure_qubits_);

    //    void execute_once();
    //    std::pair<size_t, double> _get_state_prob(size_t i);
    //    size_t get_measure_no_readout_error();
    //    size_t get_measure();
    //    std::map<size_t, size_t> measure_shots(size_t shots);
    //    std::map<size_t, size_t> measure_shots(const std::vector<size_t>& measure_list, size_t shots);

    //};

    //struct NoisySimulator_GateDependent : public NoisySimulator
    //{
    //    using GateDependentNoise_t = std::map<UnitaryType, std::map<NoiseType, double>>;
    //    using GateDependentNoise_Description_t = std::map<std::string, std::map<std::string, double>>;
    //    GateDependentNoise_t gate_dependent_noise;

    //    NoisySimulator_GateDependent(size_t n_qubit,
    //        const std::map<std::string, double>& noise_description,
    //        const GateDependentNoise_Description_t& gate_noise_description,
    //        const std::vector<std::array<double, 2>>& measurement_error);

    //    void _load_gate_dependent_noise(const GateDependentNoise_Description_t& gate_noise_description);

    //    /* Noisy simulation */
    //    void insert_error(const std::vector<size_t>& qn, UnitaryType gateType);
    //    void _insert_gate_dependent_error(const std::vector<size_t>& qubits, UnitaryType gateType);
    //    
    //};

    //struct NoisySimulator_GateSpecificError : public NoisySimulator
    //{
    //    using GateError1q_t = std::map<std::pair<UnitaryType, size_t>, std::map<NoiseType, double>>;
    //    using GateError2q_t = std::map<std::pair<UnitaryType, std::pair<size_t, size_t>>, std::map<NoiseType, double>>;
    //    using GateError1q_Description_t = std::map<std::pair<std::string, size_t>, std::map<std::string, double>>;
    //    using GateError2q_Description_t = std::map<std::pair<std::string, std::pair<size_t, size_t>>, std::map<std::string, double>>;
    //    GateError1q_t gate_error1q;
    //    GateError2q_t gate_error2q;

    //    NoisySimulator_GateSpecificError(size_t n_qubit,
    //        const std::map<std::string, double>& noise_description,
    //        const GateError1q_Description_t& gate_error1q_description,
    //        const GateError2q_Description_t& gate_error2q_description,
    //        const std::vector<std::array<double, 2>>& measurement_error);

    //    void _load_gate_error1q(const GateError1q_Description_t& gate_noise_description);
    //    void _load_gate_error2q(const GateError2q_Description_t& gate_noise_description);

    //    /* Noisy simulation */
    //    void insert_error(const std::vector<size_t>& qn, UnitaryType gateType);
    //    void _insert_gate_error1q(UnitaryType gateType, size_t qn);
    //    void _insert_gate_error2q(UnitaryType gateType, size_t qn1, size_t qn2);
    //};

}