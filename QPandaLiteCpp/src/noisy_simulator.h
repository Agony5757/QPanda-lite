#include "simulator.h"

namespace qpandalite {
    enum class NoiseType : uint8_t
    {
        Depolarizing,
        Damping,
        BitFlip,
        PhaseFlip,
    };

    enum class SupportOperationType : uint8_t
    {
        HADAMARD = 1000,
        U22,
        X,
        Y,
        Z,
        SX,
        CZ,
        ISWAP,
        XY,
        CNOT,
        RX,
        RY,
        RZ,
        RPHI90,
        RPHI180,
        RPHI
    };

    struct NoiseSimulatorImpl : public Simulator
    {
        void depolarizing(size_t qn, double p);
        void damping(size_t qn, double gamma);
        void bitflip(size_t qn, double p);
        void phaseflip(size_t qn, double p);
    };

    struct OpcodeType
    {
        uint8_t op;
        std::vector<size_t> qubits;
        std::vector<double> parameters;
        bool dagger;
        std::vector<size_t> global_controller;
    };

    struct NoisySimulator
    {
        std::map<NoiseType, double> noise;
        std::vector<std::array<double, 2>> measurement_error_matrices;
        NoiseSimulatorImpl simulator;
        size_t nqubit;
        std::vector<size_t> measure_qubits;
        std::vector<OpcodeType> opcodes; // opcode + noisy
        std::vector<OpcodeType> original_opcodes; // perfect, without noise

        NoisySimulator(size_t n_qubit,
            const std::map<std::string, double>& noise_description,
            std::vector<std::array<double, 2>> measurement_error)
            : nqubit(n_qubit), noise(noise_description),
            measurement_error_matrices(measurement_error)
        { 
        }

        void insert_error(std::vector<size_t> qn);

        void hadamard(size_t qn, bool is_dagger = false);
        void u22(size_t qn, const u22_t& unitary, bool is_dagger = false);
        void x(size_t qn, bool is_dagger = false);
        void z(size_t qn, bool is_dagger = false);
        void y(size_t qn, bool is_dagger = false);
        void sx(size_t qn, bool is_dagger = false);
        void cz(size_t qn1, size_t qn2, bool is_dagger = false);
        void iswap(size_t qn1, size_t qn2, bool is_dagger = false);
        void xy(size_t qn1, size_t qn2, double theta, bool is_dagger = false);
        void cnot(size_t controller, size_t target, bool is_dagger = false);
        void rx(size_t qn, double angle, bool is_dagger = false);
        void ry(size_t qn, double angle, bool is_dagger = false);
        void rz(size_t qn, double angle, bool is_dagger = false);
        void rphi90(size_t qn, double phi, bool is_dagger = false);
        void rphi180(size_t qn, double phi, bool is_dagger = false);
        void rphi(size_t qn, double phi, double theta, bool is_dagger = false);

        void hadamard_cont(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void u22_cont(size_t qn, const u22_t& unitary, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void x_cont(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void z_cont(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void y_cont(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void sx_cont(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void cz_cont(size_t qn1, size_t qn2, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void iswap_cont(size_t qn1, size_t qn2, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void xy_cont(size_t qn1, size_t qn2, double theta, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void cnot_cont(size_t controller, size_t target, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void rx_cont(size_t qn, double angle, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void ry_cont(size_t qn, double angle, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void rz_cont(size_t qn, double angle, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void rphi90_cont(size_t qn, double phi, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void rphi180_cont(size_t qn, double phi, const std::vector<size_t>& global_controller, bool is_dagger = false);
        void rphi_cont(size_t qn, double phi, double theta, const std::vector<size_t>& global_controller, bool is_dagger = false);
        
        void measure(const std::vector<size_t> measure_qubits_);

        void execute_once();
        size_t get_measure();
        std::map<size_t, size_t> measure_shots(size_t shots);



    };
}