#include "noisy_simulator.h"
#include "rng.h"

namespace qpandalite {

	void NoiseSimulatorImpl::depolarizing(size_t qn, double p)
	{
		double r = rand();
		if (r > p)
			return;
		if (r < p / 3)
			x(qn);
		else if (r < p / 3 * 2)
			y(qn);
		else
			z(qn);
	}

	void NoiseSimulatorImpl::bitflip(size_t qn, double p)
	{
		double r = rand();
		if (r > p)
			return
		else
			x(qn);
	}

	void NoiseSimulatorImpl::phaseflip(size_t qn, double p)
	{
		double r = rand();
		if (r > p)
			return
		else
			z(qn);
	}

	void NoisySimulator::insert_error(std::vector<size_t> qubits)
	{
		if (noise.empty()) return;

		auto it_depol = noise.find(NoiseType::Depolarizing);
		auto it_damp = noise.find(NoiseType::Damping);
		auto it_bitflip = noise.find(NoiseType::BitFlip);
		auto it_phaseflip = noise.find(NoiseType::PhaseFlip);

		auto it_end = noise.end();

		if (it_depol != it_end)
		{
			opcodes.emplace_back(
				NoiseType::Depolarizing,
				qubits,
				{ it_depol->second },
				false,
				{}
			);
		}

		if (it_damp != it_end)
		{
			opcodes.emplace_back(
				NoiseType::Damping,
				qubits,
				{ it_depol->second },
				false,
				{}
			);
		}

		if (it_bitflip != it_end)
		{
			opcodes.emplace_back(
				NoiseType::BitFlip,
				qubits,
				{ it_depol->second },
				false,
				{}
			);
		}

		if (it_phaseflip != it_end)
		{
			opcodes.emplace_back(
				NoiseType::PhaseFlip,
				qubits,
				{ it_depol->second },
				false,
				{}
			);
		}
	}

	void NoisySimulator::hadamard(size_t qn, bool is_dagger)
	{
		hadamard_cont(qn, {}, is_dagger);
	}

	void NoisySimulator::u22(size_t qn, const u22_t& unitary, bool is_dagger)
	{
		u22_cont(qn, unitary, {}, is_dagger);
	}

	void NoisySimulator::x(size_t qn, bool is_dagger)
	{
		x_cont(qn, {}, is_dagger);
	}

	void NoisySimulator::y(size_t qn, bool is_dagger)
	{
		y_cont(qn, {}, is_dagger);
	}

	void NoisySimulator::z(size_t qn, bool is_dagger)
	{
		z_cont(qn, {}, is_dagger);
	}

	void NoisySimulator::sx(size_t qn, bool is_dagger)
	{
		sx_cont(qn, {}, is_dagger);
	}

	void NoisySimulator::cz(size_t qn1, size_t qn2, bool is_dagger)
	{
		cz_cont(qn1, qn2, {}, is_dagger);
	}

	void NoisySimulator::iswap(size_t qn1, size_t qn2, bool is_dagger)
	{
		iswap_cont(qn1, qn2, {}, is_dagger);
	}

	void NoisySimulator::xy(size_t qn1, size_t qn2, double theta, bool is_dagger)
	{
		xy_cont(qn1, qn2, {}, is_dagger);
	}

	void NoisySimulator::cnot(size_t qn1, size_t qn2, bool is_dagger)
	{
		cnot_cont(qn1, qn2, {}, is_dagger);
	}

	void NoisySimulator::hadamard_cont(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
	{
		opcodes.emplace_back(
			SupportOperationType::HADAMARD,
			{ qn },
			{},
			is_dagger,
			global_controller
		);
		insert_error({ qn });
	}

	void NoisySimulator::measure(const std::vector<size_t> measure_qubits_)
	{
		measure_qubits = measure_qubits_;
	}

	void NoisySimulator::execute_once()
	{
		simulator.init_n_qubit(nqubit);
		for (const auto &opcode : opcodes)
		{
			switch (opcode.op)
			{
			case NoiseType::Depolarizing:
				simulator.depolarizing(opcode.qubits[0], opcode.parameters[0]);
				break;
			case SupportOperationType::HADAMARD:
				simulator.depolarizing(opcode.qubits[0]);
				break;
			default:
				ThrowRuntimeError(fmt::format("Failed to handle opcode = {}\nPlease check.", opcode.op));
			}
		}
	}

	void measure_shots()
	{
		std::map<size_t, size_t> measured_result;
		for (size_t i = 0; i < shots; ++i)
		{
			execute_once();
			size_t meas = get_measure();
			auto it = measured_result.find(meas);
			if (it != measured_result.end())
			{
				it->second++;
			}
			else
			{
				measured_result.emplace(meas, 1);
			}
		}
		return measure_result;
	}

}

