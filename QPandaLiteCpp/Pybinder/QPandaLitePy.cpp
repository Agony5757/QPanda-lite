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
}

#ifdef __GNUC__
#pragma GCC diagnostic pop
#endif