﻿#ifdef __GNUC__
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
		.def("hadamard", &qpandalite::Simulator::hadamard)
		.def("u22", &qpandalite::Simulator::u22)
		.def("x", &qpandalite::Simulator::x)
		.def("sx", &qpandalite::Simulator::sx)
		.def("y", &qpandalite::Simulator::y)
		.def("z", &qpandalite::Simulator::z)
		.def("cz", &qpandalite::Simulator::cz)
		.def("iswap", &qpandalite::Simulator::iswap)
		.def("xy", &qpandalite::Simulator::xy)
		.def("cnot", &qpandalite::Simulator::cnot)
		.def("rx", &qpandalite::Simulator::rx)
		.def("ry", &qpandalite::Simulator::ry)
		.def("rz", &qpandalite::Simulator::rz)
		.def("rphi90", &qpandalite::Simulator::rphi90)
		.def("rphi180", &qpandalite::Simulator::rphi180)
		.def("rphi", &qpandalite::Simulator::rphi)
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

	// py::class_<NoiseSimulatorImpl, Simulator>(m, "NoiseSimulatorImpl")
	//     .def("depolarizing", &NoiseSimulatorImpl::depolarizing)
	//     .def("damping", &NoiseSimulatorImpl::damping)
	//     .def("bitflip", &NoiseSimulatorImpl::bitflip)
	//     .def("phaseflip", &NoiseSimulatorImpl::phaseflip)
	//     ;

	// py::enum_<qpandalite::SupportOperationType>(m, "SupportOperationType")
	//     .value("HADAMARD", SupportOperationType::HADAMARD)
	//     // ... Add other values similarly
	//     .export_values();

	py::class_<qpandalite::OpcodeType>(m, "OpcodeType")
		.def(py::init<uint32_t, const std::vector<size_t>&, const std::vector<double>&, bool, const std::vector<size_t>&>())
		.def_readwrite("op", &qpandalite::OpcodeType::op)
		// ... Similarly bind other members
		;

	py::class_<qpandalite::NoisySimulator>(m, "NoisySimulator")
		.def(py::init<size_t, 
			const std::map<std::string, double>&, 
			const std::vector<std::array<double, 2>>&>())
		.def_readonly("total_qubit", &qpandalite::NoisySimulator::nqubit)
		.def_readonly("noise", &qpandalite::NoisySimulator::noise)
		.def("_load_noise", &qpandalite::NoisySimulator::_load_noise)
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