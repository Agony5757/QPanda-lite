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
using namespace std;
using namespace pybind11::literals;
namespace py = pybind11;

PYBIND11_MODULE(QPandaLitePy, m)
{
	m.doc() = "[Module QPandaLitePy]";
	py::class_<qpandalite::Simulator>(m, "Simulator")
		.def(py::init<>())
		.def_readwrite_static("max_qubit_num", &qpandalite::Simulator::max_qubit_num)
		.def_readonly("total_qubit", &qpandalite::Simulator::total_qubit)
		.def_readonly("state", &qpandalite::Simulator::state)
		.def("init_n_qubit", &qpandalite::Simulator::init_n_qubit)
		.def("hadamard", &qpandalite::Simulator::hadamard, py::arg("dagger") = false)
		.def("u22", &qpandalite::Simulator::u22, py::arg("dagger") = false)
		.def("x", &qpandalite::Simulator::x, py::arg("dagger") = false)
		.def("sx", &qpandalite::Simulator::sx, py::arg("dagger") = false)
		.def("y", &qpandalite::Simulator::y, py::arg("dagger") = false)
		.def("z", &qpandalite::Simulator::z, py::arg("dagger") = false)
		.def("cz", &qpandalite::Simulator::cz, py::arg("dagger") = false)
		.def("iswap", &qpandalite::Simulator::iswap, py::arg("dagger") = false)
		.def("xy", &qpandalite::Simulator::xy, py::arg("dagger") = false)
		.def("cnot", &qpandalite::Simulator::cnot, py::arg("dagger") = false)
		.def("rx", &qpandalite::Simulator::rx, py::arg("dagger") = false)
		.def("ry", &qpandalite::Simulator::ry, py::arg("dagger") = false)
		.def("rz", &qpandalite::Simulator::rz, py::arg("dagger") = false)
		.def("rphi90", &qpandalite::Simulator::rphi90, py::arg("dagger") = false)
		.def("rphi180", &qpandalite::Simulator::rphi180, py::arg("dagger") = false)
		.def("rphi", &qpandalite::Simulator::rphi, py::arg("dagger") = false)
		.def("hadamard_cont", &qpandalite::Simulator::hadamard_cont, py::arg("dagger") = false)
		.def("u22_cont", &qpandalite::Simulator::u22_cont, py::arg("dagger") = false)
		.def("x_cont", &qpandalite::Simulator::x_cont, py::arg("dagger") = false)
		.def("sx_cont", &qpandalite::Simulator::sx_cont, py::arg("dagger") = false)
		.def("y_cont", &qpandalite::Simulator::y_cont, py::arg("dagger") = false)
		.def("z_cont", &qpandalite::Simulator::z_cont, py::arg("dagger") = false)
		.def("cz_cont", &qpandalite::Simulator::cz_cont, py::arg("dagger") = false)
		.def("iswap_cont", &qpandalite::Simulator::iswap_cont, py::arg("dagger") = false)
		.def("xy_cont", &qpandalite::Simulator::xy_cont, py::arg("dagger") = false)
		.def("cnot_cont", &qpandalite::Simulator::cnot_cont, py::arg("dagger") = false)
		.def("rx_cont", &qpandalite::Simulator::rx_cont, py::arg("dagger") = false)
		.def("ry_cont", &qpandalite::Simulator::ry_cont, py::arg("dagger") = false)
		.def("rz_cont", &qpandalite::Simulator::rz_cont, py::arg("dagger") = false)
		.def("rphi90_cont", &qpandalite::Simulator::rphi90_cont, py::arg("dagger") = false)
		.def("rphi180_cont", &qpandalite::Simulator::rphi180_cont, py::arg("dagger") = false)
		.def("rphi_cont", &qpandalite::Simulator::rphi_cont, py::arg("dagger") = false)
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
		.export_values()
		;

	py::enum_<qpandalite::SupportOperationType>(m, "SupportOperationType")
        .value("HADAMARD", qpandalite::SupportOperationType::HADAMARD)
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

	py::class_<qpandalite::NoisySimulator>(m, "NoisySimulator")
		.def(py::init<size_t, 
                      const std::map<std::string, double>&, 
                      const std::map<std::string, std::map<std::string, double>>&,
                      const std::vector<std::array<double, 2>>&>(),
             py::arg("n_qubit"),
             py::arg("noise_description") = std::map<std::string, double>{},  // Default empty map
             py::arg("gate_noise_description") = std::map<std::string, std::map<std::string, double>>{},  // Default empty map
             py::arg("measurement_error") = std::vector<std::array<double, 2>>{}  // Default empty vector
        )
		.def_readonly("total_qubit", &qpandalite::NoisySimulator::nqubit)
		.def_readonly("noise", &qpandalite::NoisySimulator::noise)
		.def_readonly("gate_dependent_noise", &qpandalite::NoisySimulator::gate_dependent_noise)
		.def_readonly("measurement_error_matrices", &qpandalite::NoisySimulator::measurement_error_matrices)
		.def("load_opcode", &qpandalite::NoisySimulator::load_opcode)
		.def("insert_error", &qpandalite::NoisySimulator::insert_error)

		.def("hadamard", &qpandalite::NoisySimulator::hadamard, py::arg("qn"), py::arg("is_dagger") = false)
		// .def("u22", &qpandalite::NoisySimulator::u22)
		.def("x", &qpandalite::NoisySimulator::x, py::arg("qn"), py::arg("is_dagger") = false)
		.def("sx", &qpandalite::NoisySimulator::sx, py::arg("qn"), py::arg("is_dagger") = false)
		.def("y", &qpandalite::NoisySimulator::y, py::arg("qn"), py::arg("is_dagger") = false)
		.def("z", &qpandalite::NoisySimulator::z, py::arg("qn"), py::arg("is_dagger") = false)
		.def("cz", &qpandalite::NoisySimulator::cz, py::arg("qn1"), py::arg("qn2"), py::arg("is_dagger") = false)
		.def("iswap", &qpandalite::NoisySimulator::iswap, py::arg("qn1"), py::arg("qn2"), py::arg("is_dagger") = false)
        .def("xy", &qpandalite::NoisySimulator::xy, py::arg("qn1"), py::arg("qn2"), py::arg("theta"), py::arg("is_dagger") = false)
        .def("cnot", &qpandalite::NoisySimulator::cnot, py::arg("controller"), py::arg("target"), py::arg("is_dagger") = false)        
		.def("rx", &qpandalite::NoisySimulator::rx, py::arg("qn"), py::arg("theta"), py::arg("is_dagger") = false)
		.def("ry", &qpandalite::NoisySimulator::ry, py::arg("qn"), py::arg("theta"), py::arg("is_dagger") = false)
		.def("rz", &qpandalite::NoisySimulator::rz, py::arg("qn"), py::arg("theta"), py::arg("is_dagger") = false)
		.def("rphi90", &qpandalite::NoisySimulator::rphi90, py::arg("qn"), py::arg("phi"), py::arg("is_dagger") = false)
		.def("rphi180", &qpandalite::NoisySimulator::rphi180, py::arg("qn"), py::arg("phi"), py::arg("is_dagger") = false)
		.def("rphi", &qpandalite::NoisySimulator::rphi, py::arg("qn"), py::arg("phi"), py::arg("theta"), py::arg("is_dagger") = false)
		.def("measure_shots", &qpandalite::NoisySimulator::measure_shots)
		;

}

#ifdef __GNUC__
#pragma GCC diagnostic pop
#endif