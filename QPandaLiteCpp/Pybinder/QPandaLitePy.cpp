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
#include "density_operator_simulator.h"
#include "rng.h"
using namespace std;
using namespace pybind11::literals;
namespace py = pybind11;

PYBIND11_MODULE(QPandaLitePy, m)
{
	m.doc() = "[Module QPandaLitePy]";
	m.def("seed", &qpandalite::seed);
	m.def("rand", &qpandalite::rand);

	auto py_arg_global_controller = (py::arg("global_controller") = std::vector<size_t>{});
	auto py_arg_dagger = (py::arg("dagger") = false);
	py::class_<qpandalite::Simulator>(m, "Simulator")
		.def(py::init<>())
		.def_readwrite_static("max_qubit_num", &qpandalite::Simulator::max_qubit_num)
		.def_readonly("total_qubit", &qpandalite::Simulator::total_qubit)
		.def_readonly("state", &qpandalite::Simulator::state)
		.def("init_n_qubit", &qpandalite::Simulator::init_n_qubit)
		.def("hadamard", &qpandalite::Simulator::hadamard, py::arg("qn"), py_arg_global_controller, py_arg_dagger)
		.def("u22", &qpandalite::Simulator::u22, py::arg("qn"), py::arg("unitary"), py_arg_global_controller, py_arg_dagger)
		.def("x", &qpandalite::Simulator::x, py::arg("qn"), py_arg_global_controller, py_arg_dagger)
		.def("sx", &qpandalite::Simulator::sx, py::arg("qn"), py_arg_global_controller, py_arg_dagger)
		.def("y", &qpandalite::Simulator::y, py::arg("qn"), py_arg_global_controller, py_arg_dagger)
		.def("z", &qpandalite::Simulator::z, py::arg("qn"), py_arg_global_controller, py_arg_dagger)
		.def("s", &qpandalite::Simulator::s, py::arg("qn"), py_arg_global_controller, py_arg_dagger)
		.def("t", &qpandalite::Simulator::t, py::arg("qn"), py_arg_global_controller, py_arg_dagger)
		.def("cz", &qpandalite::Simulator::cz, py::arg("qn1"), py::arg("qn2"), py_arg_global_controller, py_arg_dagger)
		.def("iswap", &qpandalite::Simulator::iswap, py::arg("qn1"), py::arg("qn2"), py_arg_global_controller, py_arg_dagger)
		.def("xy", &qpandalite::Simulator::xy, py::arg("qn1"), py::arg("qn2"), py::arg("theta"), py_arg_global_controller, py_arg_dagger)
		.def("cnot", &qpandalite::Simulator::cnot, py::arg("controller"), py::arg("target"), py_arg_global_controller, py_arg_dagger)
		.def("rx", &qpandalite::Simulator::rx, py::arg("qn"), py::arg("theta"), py_arg_global_controller, py_arg_dagger)
		.def("ry", &qpandalite::Simulator::ry, py::arg("qn"), py::arg("theta"), py_arg_global_controller, py_arg_dagger)
		.def("rz", &qpandalite::Simulator::rz, py::arg("qn"), py::arg("theta"), py_arg_global_controller, py_arg_dagger)
		.def("u1", &qpandalite::Simulator::u1, py::arg("qn"), py::arg("theta"), py_arg_global_controller, py_arg_dagger)
		.def("rphi90", &qpandalite::Simulator::rphi90, py::arg("qn"), py::arg("phi"), py_arg_global_controller, py_arg_dagger)
		.def("rphi180", &qpandalite::Simulator::rphi180, py::arg("qn"), py::arg("phi"), py_arg_global_controller, py_arg_dagger)
		.def("rphi", &qpandalite::Simulator::rphi, py::arg("qn"), py::arg("theta"), py::arg("phi"), py_arg_global_controller, py_arg_dagger)
		.def("toffoli", &qpandalite::Simulator::toffoli, py::arg("controller1"), py::arg("controller2"), py::arg("target"), py_arg_global_controller, py_arg_dagger)
		.def("cswap", &qpandalite::Simulator::cswap, py::arg("controller"), py::arg("target1"), py::arg("target2"), py_arg_global_controller, py_arg_dagger)
		.def("xx", &qpandalite::Simulator::xx, py::arg("qn1"), py::arg("qn2"), py::arg("theta"), py_arg_global_controller, py_arg_dagger)
		.def("yy", &qpandalite::Simulator::yy, py::arg("qn1"), py::arg("qn2"), py::arg("theta"), py_arg_global_controller, py_arg_dagger)
		.def("zz", &qpandalite::Simulator::zz, py::arg("qn1"), py::arg("qn2"), py::arg("theta"), py_arg_global_controller, py_arg_dagger)
		.def("u3", &qpandalite::Simulator::u3, py::arg("qn"), py::arg("theta"), py::arg("phi"), py::arg("lambda"), py_arg_global_controller, py_arg_dagger)
		.def("phase2q", &qpandalite::Simulator::phase2q, py::arg("qn1"), py::arg("qn2"), py::arg("theta1"), py::arg("theta2"), py::arg("thetazz"), py_arg_global_controller, py_arg_dagger)
		.def("uu15", &qpandalite::Simulator::uu15, py::arg("qn1"), py::arg("qn2"), py::arg("parameters"), py_arg_global_controller, py_arg_dagger)
		.def("get_prob", &qpandalite::Simulator::get_prob)
		.def("get_prob", &qpandalite::Simulator::get_prob_map)
		.def("pmeasure", &qpandalite::Simulator::pmeasure)
		.def("pmeasure", &qpandalite::Simulator::pmeasure_list)
		;

	py::class_<qpandalite::DensityOperatorSimulator>(m, "DensityOperatorSimulator")
		.def(py::init<>())
		.def_readwrite_static("max_qubit_num", &qpandalite::DensityOperatorSimulator::max_qubit_num)
		.def_readonly("total_qubit", &qpandalite::DensityOperatorSimulator::total_qubit)
		.def_readonly("state", &qpandalite::DensityOperatorSimulator::state)
		.def("init_n_qubit", &qpandalite::DensityOperatorSimulator::init_n_qubit)
		.def("hadamard", &qpandalite::DensityOperatorSimulator::hadamard, py::arg("qn"), py_arg_global_controller, py_arg_dagger)
		.def("u22", &qpandalite::DensityOperatorSimulator::u22, py::arg("qn"), py::arg("unitary"), py_arg_global_controller, py_arg_dagger)
		.def("x", &qpandalite::DensityOperatorSimulator::x, py::arg("qn"), py_arg_global_controller, py_arg_dagger)
		.def("sx", &qpandalite::DensityOperatorSimulator::sx, py::arg("qn"), py_arg_global_controller, py_arg_dagger)
		.def("y", &qpandalite::DensityOperatorSimulator::y, py::arg("qn"), py_arg_global_controller, py_arg_dagger)
		.def("z", &qpandalite::DensityOperatorSimulator::z, py::arg("qn"), py_arg_global_controller, py_arg_dagger)
		.def("s", &qpandalite::DensityOperatorSimulator::s, py::arg("qn"), py_arg_global_controller, py_arg_dagger)
		.def("t", &qpandalite::DensityOperatorSimulator::t, py::arg("qn"), py_arg_global_controller, py_arg_dagger)
		.def("cz", &qpandalite::DensityOperatorSimulator::cz, py::arg("qn1"), py::arg("qn2"), py_arg_global_controller, py_arg_dagger)
		.def("iswap", &qpandalite::DensityOperatorSimulator::iswap, py::arg("qn1"), py::arg("qn2"), py_arg_global_controller, py_arg_dagger)
		.def("xy", &qpandalite::DensityOperatorSimulator::xy, py::arg("qn1"), py::arg("qn2"), py::arg("theta"), py_arg_global_controller, py_arg_dagger)
		.def("cnot", &qpandalite::DensityOperatorSimulator::cnot, py::arg("controller"), py::arg("target"), py_arg_global_controller, py_arg_dagger)
		.def("rx", &qpandalite::DensityOperatorSimulator::rx, py::arg("qn"), py::arg("theta"), py_arg_global_controller, py_arg_dagger)
		.def("ry", &qpandalite::DensityOperatorSimulator::ry, py::arg("qn"), py::arg("theta"), py_arg_global_controller, py_arg_dagger)
		.def("rz", &qpandalite::DensityOperatorSimulator::rz, py::arg("qn"), py::arg("theta"), py_arg_global_controller, py_arg_dagger)
		.def("u1", &qpandalite::DensityOperatorSimulator::u1, py::arg("qn"), py::arg("theta"), py_arg_global_controller, py_arg_dagger)
		.def("rphi90", &qpandalite::DensityOperatorSimulator::rphi90, py::arg("qn"), py::arg("phi"), py_arg_global_controller, py_arg_dagger)
		.def("rphi180", &qpandalite::DensityOperatorSimulator::rphi180, py::arg("qn"), py::arg("phi"), py_arg_global_controller, py_arg_dagger)
		.def("rphi", &qpandalite::DensityOperatorSimulator::rphi, py::arg("qn"), py::arg("theta"), py::arg("phi"), py_arg_global_controller, py_arg_dagger)
		.def("toffoli", &qpandalite::DensityOperatorSimulator::toffoli, py::arg("controller1"), py::arg("controller2"), py::arg("target"), py_arg_global_controller, py_arg_dagger)
		.def("cswap", &qpandalite::DensityOperatorSimulator::cswap, py::arg("controller"), py::arg("target1"), py::arg("target2"), py_arg_global_controller, py_arg_dagger)
		.def("xx", &qpandalite::DensityOperatorSimulator::xx, py::arg("qn1"), py::arg("qn2"), py::arg("theta"), py_arg_global_controller, py_arg_dagger)
		.def("yy", &qpandalite::DensityOperatorSimulator::yy, py::arg("qn1"), py::arg("qn2"), py::arg("theta"), py_arg_global_controller, py_arg_dagger)
		.def("zz", &qpandalite::DensityOperatorSimulator::zz, py::arg("qn1"), py::arg("qn2"), py::arg("theta"), py_arg_global_controller, py_arg_dagger)
		.def("u3", &qpandalite::DensityOperatorSimulator::u3, py::arg("qn"), py::arg("theta"), py::arg("phi"), py::arg("lambda"), py_arg_global_controller, py_arg_dagger)
		.def("phase2q", &qpandalite::DensityOperatorSimulator::phase2q, py::arg("qn1"), py::arg("qn2"), py::arg("theta1"), py::arg("theta2"), py::arg("thetazz"), py_arg_global_controller, py_arg_dagger)
		.def("uu15", &qpandalite::DensityOperatorSimulator::uu15, py::arg("qn1"), py::arg("qn2"), py::arg("parameters"), py_arg_global_controller, py_arg_dagger)
		.def("get_prob", &qpandalite::DensityOperatorSimulator::get_prob)
		.def("get_prob", &qpandalite::DensityOperatorSimulator::get_prob_map)
		.def("pmeasure", &qpandalite::DensityOperatorSimulator::pmeasure)
		.def("pmeasure", &qpandalite::DensityOperatorSimulator::pmeasure_list)
		.def("stateprob", &qpandalite::DensityOperatorSimulator::stateprob)
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
		.value("S", qpandalite::SupportOperationType::S)
		.value("T", qpandalite::SupportOperationType::T)
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

		.def("hadamard", &qpandalite::NoisySimulator::hadamard, py::arg("qn"), py_arg_global_controller, py_arg_dagger)
		.def("u22", &qpandalite::NoisySimulator::u22, py::arg("qn"), py::arg("unitary"), py_arg_global_controller, py_arg_dagger)
		.def("x", &qpandalite::NoisySimulator::x, py::arg("qn"), py_arg_global_controller, py_arg_dagger)
		.def("sx", &qpandalite::NoisySimulator::sx, py::arg("qn"), py_arg_global_controller, py_arg_dagger)
		.def("y", &qpandalite::NoisySimulator::y, py::arg("qn"), py_arg_global_controller, py_arg_dagger)
		.def("z", &qpandalite::NoisySimulator::z, py::arg("qn"), py_arg_global_controller, py_arg_dagger)
		.def("cz", &qpandalite::NoisySimulator::cz, py::arg("qn1"), py::arg("qn2"), py_arg_global_controller, py_arg_dagger)
		.def("iswap", &qpandalite::NoisySimulator::iswap, py::arg("qn1"), py::arg("qn2"), py_arg_global_controller, py_arg_dagger)
		.def("xy", &qpandalite::NoisySimulator::xy, py::arg("qn1"), py::arg("qn2"), py::arg("theta"), py_arg_global_controller, py_arg_dagger)
		.def("cnot", &qpandalite::NoisySimulator::cnot, py::arg("controller"), py::arg("target"), py_arg_global_controller, py_arg_dagger)
		.def("rx", &qpandalite::NoisySimulator::rx, py::arg("qn"), py::arg("theta"), py_arg_global_controller, py_arg_dagger)
		.def("ry", &qpandalite::NoisySimulator::ry, py::arg("qn"), py::arg("theta"), py_arg_global_controller, py_arg_dagger)
		.def("rz", &qpandalite::NoisySimulator::rz, py::arg("qn"), py::arg("theta"), py_arg_global_controller, py_arg_dagger)
		.def("rphi90", &qpandalite::NoisySimulator::rphi90, py::arg("qn"), py::arg("phi"), py_arg_global_controller, py_arg_dagger)
		.def("rphi180", &qpandalite::NoisySimulator::rphi180, py::arg("qn"), py::arg("phi"), py_arg_global_controller, py_arg_dagger)
		.def("rphi", &qpandalite::NoisySimulator::rphi, py::arg("qn"), py::arg("phi"), py::arg("theta"), py_arg_global_controller, py_arg_dagger)
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