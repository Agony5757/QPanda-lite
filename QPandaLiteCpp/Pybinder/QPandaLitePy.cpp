#ifdef __GNUC__
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wunused-value"
#endif

#include "pybind11/pybind11.h"
#include "pybind11/stl.h"
#include "pybind11/complex.h"
#include "pybind11/functional.h"
#include "pybind11/operators.h"

#include "simulator.h"
#include "noisy_simulator.h"
#include "rng.h"
using namespace std;
using namespace pybind11::literals;
namespace py = pybind11;

PYBIND11_MODULE(QPandaLitePy, m)
{
	m.doc() = "[Module QPandaLitePy]";
	m.def("seed", &qpandalite::seed);
	m.def("rand", &qpandalite::rand);

	py::class_<qpandalite::Simulator>(m, "Simulator")
		.def(py::init<>())
		.def_readwrite_static("max_qubit_num", &qpandalite::Simulator::max_qubit_num)
		.def_readonly("total_qubit", &qpandalite::Simulator::total_qubit)
		.def_readonly("state", &qpandalite::Simulator::state)
		.def("init_n_qubit", &qpandalite::Simulator::init_n_qubit)
		//.def("hadamard", &qpandalite::Simulator::hadamard, py::arg("qn"), py::arg("dagger") = false)
		//.def("u22", &qpandalite::Simulator::u22, py::arg("qn"), py::arg("unitary"), py::arg("dagger") = false)
		//.def("x", &qpandalite::Simulator::x, py::arg("qn"), py::arg("dagger") = false)
		//.def("sx", &qpandalite::Simulator::sx, py::arg("qn"), py::arg("dagger") = false)
		//.def("y", &qpandalite::Simulator::y, py::arg("qn"), py::arg("dagger") = false)
		//.def("z", &qpandalite::Simulator::z, py::arg("qn"), py::arg("dagger") = false)
		//.def("cz", &qpandalite::Simulator::cz, py::arg("qn1"), py::arg("qn2"), py::arg("is_dagger") = false)
		//.def("iswap", &qpandalite::Simulator::iswap, py::arg("qn1"), py::arg("qn2"), py::arg("dagger") = false)
		//.def("xy", &qpandalite::Simulator::xy, py::arg("qn1"), py::arg("qn2"), py::arg("theta"), py::arg("dagger") = false)
		//.def("cnot", &qpandalite::Simulator::cnot, py::arg("controller"), py::arg("target"), py::arg("is_dagger") = false)
		//.def("rx", &qpandalite::Simulator::rx, py::arg("qn"), py::arg("theta"), py::arg("dagger") = false)
		//.def("ry", &qpandalite::Simulator::ry, py::arg("qn"), py::arg("theta"), py::arg("dagger") = false)
		//.def("rz", &qpandalite::Simulator::rz, py::arg("qn"), py::arg("theta"), py::arg("dagger") = false)
		//.def("rphi90", &qpandalite::Simulator::rphi90, py::arg("qn"), py::arg("phi"), py::arg("dagger") = false)
		//.def("rphi180", &qpandalite::Simulator::rphi180, py::arg("qn"), py::arg("phi"), py::arg("dagger") = false)
		//.def("rphi", &qpandalite::Simulator::rphi, py::arg("qn"), py::arg("phi"), py::arg("theta"), py::arg("dagger") = false)
		//.def("toffoli", &qpandalite::Simulator::toffoli, py::arg("qn1"), py::arg("qn2"), py::arg("target"), py::arg("dagger") = false)
		//.def("cswap", &qpandalite::Simulator::cswap, py::arg("controller"), py::arg("target1"), py::arg("target2"), py::arg("dagger") = false)
		//.def("zz", &qpandalite::Simulator::zz, py::arg("qn1"), py::arg("qn1"), py::arg("theta"), py::arg("dagger") = false)
		//.def("xx", &qpandalite::Simulator::xx, py::arg("qn1"), py::arg("qn2"), py::arg("theta"), py::arg("dagger") = false)
		//.def("yy", &qpandalite::Simulator::yy, py::arg("qn1"), py::arg("qn2"), py::arg("theta"), py::arg("dagger") = false)
		//.def("u3", &qpandalite::Simulator::u3, py::arg("qn"), py::arg("theta"), py::arg("phi"), py::arg("lambda"), py::arg("dagger") = false)
		
		.def("hadamard", &qpandalite::Simulator::hadamard, py::arg("qn"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("u22", &qpandalite::Simulator::u22, py::arg("qn"), py::arg("unitary"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("x", &qpandalite::Simulator::x, py::arg("qn"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("sx", &qpandalite::Simulator::sx, py::arg("qn"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("y", &qpandalite::Simulator::y, py::arg("qn"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("z", &qpandalite::Simulator::z, py::arg("qn"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("cz", &qpandalite::Simulator::cz, py::arg("qn1"), py::arg("qn2"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("iswap", &qpandalite::Simulator::iswap, py::arg("qn1"), py::arg("qn2"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("xy", &qpandalite::Simulator::xy, py::arg("qn1"), py::arg("qn2"), py::arg("theta"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("cnot", &qpandalite::Simulator::cnot, py::arg("controller"), py::arg("target"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("rx", &qpandalite::Simulator::rx, py::arg("qn"), py::arg("theta"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("ry", &qpandalite::Simulator::ry, py::arg("qn"), py::arg("theta"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("rz", &qpandalite::Simulator::rz, py::arg("qn"), py::arg("theta"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("rphi90", &qpandalite::Simulator::rphi90, py::arg("qn"), py::arg("phi"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("rphi180", &qpandalite::Simulator::rphi180, py::arg("qn"), py::arg("phi"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("rphi", &qpandalite::Simulator::rphi, py::arg("qn"), py::arg("phi"), py::arg("theta"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("get_prob", &qpandalite::Simulator::get_prob)
		.def("get_prob", &qpandalite::Simulator::get_prob_map)
		.def("pmeasure", &qpandalite::Simulator::pmeasure)
		.def("pmeasure", &qpandalite::Simulator::pmeasure_list)
		;
	
	py::enum_<qpandalite::NoiseType>(m, "NoiseType")
		.value("Depolarizing", qpandalite::NoiseType::Depolarizing)
		.value("Damping", qpandalite::NoiseType::Damping)
		.value("BitFlip", qpandalite::NoiseType::BitFlip)
		.value("PhaseFlip", qpandalite::NoiseType::PhaseFlip)
		.value("TwoQubitDepolarizing", qpandalite::NoiseType::TwoQubitDepolarizing)
		.export_values()
		;

	py::enum_<qpandalite::SupportOperationType>(m, "SupportOperationType")
        .value("HADAMARD", qpandalite::SupportOperationType::HADAMARD)
        .value("IDENTITY", qpandalite::SupportOperationType::IDENTITY)
        .value("U22", qpandalite::SupportOperationType::U22)
        .value("X", qpandalite::SupportOperationType::X)
        .value("Y", qpandalite::SupportOperationType::Y)
        .value("Z", qpandalite::SupportOperationType::Z)
        .value("SX", qpandalite::SupportOperationType::SX)
        .value("CZ", qpandalite::SupportOperationType::CZ)
        .value("ISWAP", qpandalite::SupportOperationType::ISWAP)
        .value("XY", qpandalite::SupportOperationType::XY)
        .value("CNOT", qpandalite::SupportOperationType::CNOT)
        .value("RX", qpandalite::SupportOperationType::RX)
        .value("RY", qpandalite::SupportOperationType::RY)
        .value("RZ", qpandalite::SupportOperationType::RZ)
        .value("RPHI90", qpandalite::SupportOperationType::RPHI90)
        .value("RPHI180", qpandalite::SupportOperationType::RPHI180)
		.value("RPHI", qpandalite::SupportOperationType::RPHI)
		.value("TOFFOLI", qpandalite::SupportOperationType::TOFFOLI)
		.value("CSWAP", qpandalite::SupportOperationType::CSWAP)
        .export_values();

	py::class_<qpandalite::OpcodeType>(m, "OpcodeType")
		.def(py::init<uint32_t, 
                  const std::vector<size_t>&, 
                  const std::vector<double>&, 
                  bool, 
                  const std::vector<size_t>&>())
		.def_readwrite("op", &qpandalite::OpcodeType::op)
		// There might be others
		;

	using measure_shots_type1 = std::map<size_t, size_t> (qpandalite::NoisySimulator::*)(const std::vector<size_t>&, size_t);
	using measure_shots_type2 = std::map<size_t, size_t> (qpandalite::NoisySimulator::*)(size_t);

	py::class_<qpandalite::NoisySimulator>(m, "NoisySimulator")
		.def(py::init<size_t, 
                      const std::map<std::string, double>&, 
                      const std::vector<std::array<double, 2>>&>(),
			 py::arg("n_qubit"),
             py::arg("noise_description") = std::map<std::string, double>{},  // Default empty map
             py::arg("measurement_error") = std::vector<std::array<double, 2>>{}  // Default empty vector
        )
		.def_readonly("total_qubit", &qpandalite::NoisySimulator::nqubit)
		.def_readonly("noise", &qpandalite::NoisySimulator::noise)
		.def_readonly("measurement_error_matrices", &qpandalite::NoisySimulator::measurement_error_matrices)
		.def("load_opcode", &qpandalite::NoisySimulator::load_opcode)
		.def("insert_error", &qpandalite::NoisySimulator::insert_error)	
		.def("get_measure_no_readout_error", &qpandalite::NoisySimulator::get_measure_no_readout_error)
		.def("get_measure", &qpandalite::NoisySimulator::get_measure)
		.def("measure_shots", (measure_shots_type1)&qpandalite::NoisySimulator::measure_shots, py::arg("measure_qubits"), py::arg("shots"))
		.def("measure_shots", (measure_shots_type2)&qpandalite::NoisySimulator::measure_shots, py::arg("shots"))
		
		//.def("id", &qpandalite::NoisySimulator::id, py::arg("qn"), py::arg("is_dagger") = false)
		//.def("hadamard", &qpandalite::NoisySimulator::hadamard, py::arg("qn"), py::arg("dagger") = false)
		//.def("u22", &qpandalite::NoisySimulator::u22, py::arg("qn"), py::arg("unitary"), py::arg("dagger") = false)
		//.def("x", &qpandalite::NoisySimulator::x, py::arg("qn"), py::arg("dagger") = false)
		//.def("sx", &qpandalite::NoisySimulator::sx, py::arg("qn"), py::arg("dagger") = false)
		//.def("y", &qpandalite::NoisySimulator::y, py::arg("qn"), py::arg("dagger") = false)
		//.def("z", &qpandalite::NoisySimulator::z, py::arg("qn"), py::arg("dagger") = false)
		//.def("cz", &qpandalite::NoisySimulator::cz, py::arg("qn1"), py::arg("qn2"), py::arg("is_dagger") = false)
		//.def("iswap", &qpandalite::NoisySimulator::iswap, py::arg("qn1"), py::arg("qn2"), py::arg("dagger") = false)
		//.def("xy", &qpandalite::NoisySimulator::xy, py::arg("qn1"), py::arg("qn2"), py::arg("theta"), py::arg("dagger") = false)
		//.def("cnot", &qpandalite::NoisySimulator::cnot, py::arg("controller"), py::arg("target"), py::arg("is_dagger") = false)
		//.def("rx", &qpandalite::NoisySimulator::rx, py::arg("qn"), py::arg("theta"), py::arg("dagger") = false)
		//.def("ry", &qpandalite::NoisySimulator::ry, py::arg("qn"), py::arg("theta"), py::arg("dagger") = false)
		//.def("rz", &qpandalite::NoisySimulator::rz, py::arg("qn"), py::arg("theta"), py::arg("dagger") = false)
		//.def("rphi90", &qpandalite::NoisySimulator::rphi90, py::arg("qn"), py::arg("phi"), py::arg("dagger") = false)
		//.def("rphi180", &qpandalite::NoisySimulator::rphi180, py::arg("qn"), py::arg("phi"), py::arg("dagger") = false)
		//.def("rphi", &qpandalite::NoisySimulator::rphi, py::arg("qn"), py::arg("phi"), py::arg("theta"), py::arg("dagger") = false)

		.def("hadamard", &qpandalite::NoisySimulator::hadamard, py::arg("qn"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("u22", &qpandalite::NoisySimulator::u22, py::arg("qn"), py::arg("unitary"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("x", &qpandalite::NoisySimulator::x, py::arg("qn"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("sx", &qpandalite::NoisySimulator::sx, py::arg("qn"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("y", &qpandalite::NoisySimulator::y, py::arg("qn"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("z", &qpandalite::NoisySimulator::z, py::arg("qn"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("cz", &qpandalite::NoisySimulator::cz, py::arg("qn1"), py::arg("qn2"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("iswap", &qpandalite::NoisySimulator::iswap, py::arg("qn1"), py::arg("qn2"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("xy", &qpandalite::NoisySimulator::xy, py::arg("qn1"), py::arg("qn2"), py::arg("theta"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("cnot", &qpandalite::NoisySimulator::cnot, py::arg("controller"), py::arg("target"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("rx", &qpandalite::NoisySimulator::rx, py::arg("qn"), py::arg("theta"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("ry", &qpandalite::NoisySimulator::ry, py::arg("qn"), py::arg("theta"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("rz", &qpandalite::NoisySimulator::rz, py::arg("qn"), py::arg("theta"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("rphi90", &qpandalite::NoisySimulator::rphi90, py::arg("qn"), py::arg("phi"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("rphi180", &qpandalite::NoisySimulator::rphi180, py::arg("qn"), py::arg("phi"), py::arg("global_controller"), py::arg("dagger") = false)
		.def("rphi", &qpandalite::NoisySimulator::rphi, py::arg("qn"), py::arg("phi"), py::arg("theta"), py::arg("global_controller"), py::arg("dagger") = false)
		;

	py::class_<qpandalite::NoisySimulator_GateDependent, qpandalite::NoisySimulator>(m, "NoisySimulator_GateDependent")
		.def(py::init<size_t,
				const std::map<std::string, double>&,
				const std::map<std::string, std::map<std::string, double>>&,
				const std::vector<std::array<double, 2>>&>(),
			py::arg("n_qubit"),
			py::arg("noise_description") = std::map<std::string, double>{},  // Default empty map
			py::arg("gate_noise_description") = std::map<std::string, std::map<std::string, double>>{},  // Default empty map
			py::arg("measurement_error") = std::vector<std::array<double, 2>>{}  // Default empty vector
		)
		;

	py::class_<qpandalite::NoisySimulator_GateSpecificError, qpandalite::NoisySimulator>(m, "NoisySimulator_GateSpecificError")
		.def(py::init<size_t,
			const std::map<std::string, double>&,
			const qpandalite::NoisySimulator_GateSpecificError::GateError1q_Description_t&,
			const qpandalite::NoisySimulator_GateSpecificError::GateError2q_Description_t&,
			const std::vector<std::array<double, 2>>&>(),
			py::arg("n_qubit"),
			py::arg("noise_description") = std::map<std::string, double>{},  // Default empty map
			py::arg("gate_error1q_description") = qpandalite::NoisySimulator_GateSpecificError::GateError1q_Description_t{},  // Default empty map
			py::arg("gate_error2q_description") = qpandalite::NoisySimulator_GateSpecificError::GateError2q_Description_t{},  // Default empty map
			py::arg("measurement_error") = std::vector<std::array<double, 2>>{}  // Default empty vector
		)
		;
}

#ifdef __GNUC__
#pragma GCC diagnostic pop
#endif