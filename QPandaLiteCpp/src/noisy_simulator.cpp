#include "noisy_simulator.h"
#include "rng.h"

namespace qpandalite {

	void NoiseSimulatorImpl::depolarizing(size_t qn, double p)
	{
		double r = qpandalite::rand();
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
		double r = qpandalite::rand();
		if (r > p)
			return;
		else
			x(qn);
	}

	void NoiseSimulatorImpl::phaseflip(size_t qn, double p)
	{
		double r = qpandalite::rand();
		if (r > p)
			return;
		else
			z(qn);
	}

	NoisySimulator::NoisySimulator(size_t n_qubit, 
		const std::map<std::string, double>& noise_description, 
		const std::vector<std::array<double, 2>>& measurement_error)
		: nqubit(n_qubit),
		measurement_error_matrices(measurement_error)
	{
		// process the noise description and store the relevant noise types and their parameters.
		_load_noise(noise_description);
	}

	void NoisySimulator::_load_noise(std::map<std::string, double> noise_description)
	{
		auto it_depol = noise_description.find("depolarizing");
		if (it_depol != noise_description.end())
		{
			noise[NoiseType::Depolarizing] = it_depol->second;
		}
		auto it_damp = noise_description.find("damping");
		if (it_damp != noise_description.end())
		{
			noise[NoiseType::Damping] = it_damp->second;
		}

		auto it_bitflip = noise_description.find("bitflip");
		if (it_bitflip != noise_description.end())
		{
			noise[NoiseType::BitFlip] = it_bitflip->second;
		}

		auto it_phaseflip = noise_description.find("phaseflip");
		if (it_phaseflip != noise_description.end())
		{
			noise[NoiseType::PhaseFlip] = it_phaseflip->second;
		}
		
	}

	void NoisySimulator::insert_error(const std::vector<size_t> &qubits)
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
				OpcodeType(
				(uint32_t)NoiseType::Depolarizing,
				qubits,
				{ it_depol->second },
				false,
				{})
			);
		}

		if (it_damp != it_end)
		{
			opcodes.emplace_back(
				OpcodeType(
				(uint32_t)NoiseType::Damping,
				qubits,
				{ it_depol->second },
				false,
				{})
			);
		}

		if (it_bitflip != it_end)
		{
			opcodes.emplace_back(
				OpcodeType(
					(uint32_t)NoiseType::BitFlip,
				qubits,
				{ it_depol->second },
				false,
				{})
			);
		}

		if (it_phaseflip != it_end)
		{
			opcodes.emplace_back(
				OpcodeType(
				(uint32_t)NoiseType::PhaseFlip,
				qubits,
				{ it_depol->second },
				false,
				{})
			);
		}
	}

	void NoisySimulator::hadamard(size_t qn, bool is_dagger)
	{
		hadamard_cont(qn, {}, is_dagger);
	}

	// void NoisySimulator::u22(size_t qn, const u22_t& unitary, bool is_dagger)
	// {
	// 	u22_cont(qn, unitary, {}, is_dagger);
	// }

	// void NoisySimulator::x(size_t qn, bool is_dagger)
	// {
	// 	x_cont(qn, {}, is_dagger);
	// }

	// void NoisySimulator::y(size_t qn, bool is_dagger)
	// {
	// 	y_cont(qn, {}, is_dagger);
	// }

	// void NoisySimulator::z(size_t qn, bool is_dagger)
	// {
	// 	z_cont(qn, {}, is_dagger);
	// }

	// void NoisySimulator::sx(size_t qn, bool is_dagger)
	// {
	// 	sx_cont(qn, {}, is_dagger);
	// }

	// void NoisySimulator::cz(size_t qn1, size_t qn2, bool is_dagger)
	// {
	// 	cz_cont(qn1, qn2, {}, is_dagger);
	// }

	// void NoisySimulator::iswap(size_t qn1, size_t qn2, bool is_dagger)
	// {
	// 	iswap_cont(qn1, qn2, {}, is_dagger);
	// }

	// void NoisySimulator::xy(size_t qn1, size_t qn2, double theta, bool is_dagger)
	// {
	// 	xy_cont(qn1, qn2, theta, {}, is_dagger);
	// }

	// void NoisySimulator::cnot(size_t qn1, size_t qn2, bool is_dagger)
	// {
	// 	cnot_cont(qn1, qn2, {}, is_dagger);
	// }

	void NoisySimulator::hadamard_cont(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
	{
		opcodes.emplace_back(
			OpcodeType(
			(uint32_t)SupportOperationType::HADAMARD,
			{ qn },
			{},
			is_dagger,
			global_controller)
		);
		insert_error({ qn });
	}

	void NoisySimulator::xy_cont(size_t qn1, size_t qn2, double theta, const std::vector<size_t>& global_controller, bool is_dagger)
	{
		opcodes.emplace_back(
			OpcodeType(
			(uint32_t)SupportOperationType::XY,
			{ qn1, qn2 },
			{},
			is_dagger,
			global_controller)
		);
		insert_error({ qn1, qn2 });
	}

	void NoisySimulator::measure(const std::vector<size_t> measure_qubits_)
	{
		measure_qubits = measure_qubits_;
		measure_map = preprocess_measure_list(measure_qubits, simulator.total_qubit);
	}

	void NoisySimulator::execute_once()
	{
		// It initializes the simulator object with a specified number of qubits, given by nqubit.
		simulator.init_n_qubit(nqubit);

		// Currently, the iteration only supports Hadamard gates and depolarizing noise 2023/11/02
		for (const auto &opcode : opcodes)
		{
			switch (opcode.op)
			{
			case (uint32_t)NoiseType::Depolarizing:
				simulator.depolarizing(opcode.qubits[0], opcode.parameters[0]);
				break;
			case (uint32_t)SupportOperationType::HADAMARD:
    			simulator.hadamard(opcode.qubits[0]);
				// for (const auto &amp : simulator.state) {
				//     std::cout << amp << " ";
				// }
				// std::cout << std::endl;
    			break;
			default:
				ThrowRuntimeError(fmt::format("Failed to handle opcode = {}\nPlease check.", opcode.op));
			}
		}
	}

	std::pair<size_t, double> NoisySimulator::_get_state_prob(size_t i)
	{
		auto measure_map = preprocess_measure_list(measure_qubits, simulator.total_qubit);
		size_t meas_idx = get_state_with_qubit(i, measure_map);
		double prob = abs_sqr(simulator.state[i]);
		return { meas_idx, prob };
	}

	size_t NoisySimulator::get_measure()
	{
		// Generate a random number between 0 and 1
		double r = qpandalite::rand();
		for (size_t i = 0; i < pow2(simulator.total_qubit); ++i)
		{
			// Is this random number landing in this probability range?
			if (r < abs_sqr(simulator.state[i]))		
				return i;
			// No, move to the next one, and subtract the current prob from the r
			else
				r -= abs_sqr(simulator.state[i]);
		}
		ThrowRuntimeError("NoisySimulator::get_measure() internal fatal error!");
	}

	std::map<size_t, size_t> NoisySimulator::measure_shots(size_t shots)
	{
		// Initialize an empty map to hold the frequency of each measured quantum state.
		std::map<size_t, size_t> measured_result;

		for (size_t i = 0; i < shots; ++i)
		{
			// Execute the quantum circuit once and Measure the quantum state after executing the circuit.
			execute_once();
			size_t meas = get_measure();
			// std::cout << meas << " ";
			// Search the histogram to see if this state has been observed before.
			auto it = measured_result.find(meas);

			// If the state has been observed before, increment its count.
			if (it != measured_result.end())
			{
				it->second++;
			}
			// If this is the first time observing this state, add it to the histogram with a count of 1.
			else
			{
				measured_result.emplace(meas, 1);
			}
		}
		return measured_result;
	}

}

