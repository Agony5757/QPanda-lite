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

	void NoiseSimulatorImpl::damping(size_t qn, double p)
	{
	    // // Damping noise involves the kraus operator that is not unitary,
	    // // so the state might need to be re-normalized in both cases of Kraus operators.
	    // double r = qpandalite::rand();

	    // // Only apply damping if the qubit is in the |1> state
	    // if (is_qubit_one(qn))
	    // {
	    //     if (r < p)
	    //     {
	    //         // With probability p, we set the qubit qn to the ground state |0>
	    //         reset(qn);
	    //     }
	    //     else
	    //     {
	    //         // With probability (1-p), we scale the amplitude of the |1> state
	    //         // E0 operation: the qubit remains in |1> but its amplitude is scaled by sqrt(1 - p)
	    //         scale_amplitude(qn, std::sqrt(1 - p));
	    //     }
	    // }
	    // // No need to apply E1 if the qubit is already in |0>, as it has no effect.

		// Kraus operators for amplitude damping
	    double E0 = std::sqrt(1 - p);
	    double E1 = std::sqrt(p);

	    // Calculate the probabilities for the no-decay and decay cases
	    double p0 = 0.0;
	    double p1 = 0.0;
	    for (size_t i = 0; i < pow2(total_qubit); ++i) {
	        if ((i >> qn) & 1) { // qubit qn is in the |1> state
	            p1 += abs_sqr(state[i] * E1); // Probability of decay

	            p0 += (abs_sqr(state[i] * E0) + abs_sqr(state[i - pow2(qn)])); // Probability of no decay
	        }
	    }


	    // Check if p0 + p1 equals 1
	    if (std::abs(p0 + p1 - 1.0) > 1e-10) { // Use a small epsilon for floating-point comparison
	        std::cout << p0 + p1 << " ";
	        ThrowRuntimeError("Error: Probabilities after applying Kraus operators do not sum up to 1.");
	    }

	    // Generate a random number between 0 and 1
	    double r = qpandalite::rand();

	    // Apply the appropriate Kraus operator based on the random number
	    if (r < p1) {
	        // Apply E1 - decay to the ground state |0>
	        for (size_t i = 0; i < pow2(total_qubit); ++i) {
	            if ((i >> qn) & 1) {
	                size_t zero_state_index = i - pow2(qn);
	                state[zero_state_index] = state[i]; // Transfer amplitude
	                state[i] = 0; // Qubit has decayed
	            }
	        }
	    } else {
	        // Apply E0 - scale the amplitude of the |1> state
	        for (size_t i = 0; i < pow2(total_qubit); ++i) {
	            if ((i >> qn) & 1) {
	                state[i] *= E0; // Scale amplitude
	            }
	        }
	    }
	    // Re-normalize the state if necessary
	    normalize_state_vector();

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

	void NoiseSimulatorImpl::reset(size_t qn)
	{
	    if (qn >= total_qubit)
	    {
	        auto errstr = fmt::format("Exceed total (total_qubit = {}, input = {})", total_qubit, qn);
	        ThrowInvalidArgument(errstr);
	    }

	    for (size_t i = 0; i < pow2(total_qubit); ++i)
	    {
	        if ((i >> qn) & 1)  // If the qubit is in the |1⟩ state
	        {
	            // We find the corresponding |0⟩ state for this qubit
	            size_t corresponding_zero_state = i & ~(1ULL << qn);

	            // Add the amplitude from the |1⟩ state to the |0⟩ state
	            state[corresponding_zero_state] = std::norm(abs_sqr(state[i]));

	            // Set the amplitude for the |1⟩ state to zero
	            state[i] = 0;
	            
	        }
	    }
	}

	bool NoiseSimulatorImpl::is_qubit_one(size_t qn)
	{
	    // You will need to check if the qubit qn is in the |1> state.
	    // This requires knowledge about how the quantum state is represented in your simulator.
	    // Assuming a state vector representation, you might do the following:

	    bool qubit_is_one = false;
	    for (size_t i = 0; i < pow2(total_qubit); ++i)
	    {
	        if (((i >> qn) & 1) && std::norm(state[i]) > 0)
	        {
	            qubit_is_one = true;
	            break;
	        }
	    }
	    return qubit_is_one;
	}

	void NoiseSimulatorImpl::scale_amplitude(size_t qn, double scale_factor)
	{
	    // This function is to scale the amplitude of the |1> state of qn by scale_factor due to the damping noise.
	    for (size_t i = 0; i < pow2(total_qubit); ++i)
	    {
	        if ((i >> qn) & 1)  // If the qubit is in the |1> state
	        {
	            state[i] *= scale_factor;
	        }
	    }
	}

	void NoiseSimulatorImpl::normalize_state_vector() 
	{
	    double norm = 0;

	    // Sum the squares of the absolute values of the amplitudes
	    for (size_t i = 0; i < pow2(total_qubit); ++i) {
	        norm += abs_sqr(state[i]);
	    }
	    // Take the square root to get the normalization factor
	    norm = std::sqrt(norm);
	    // Divide each amplitude by the normalization factor
	    for (size_t i = 0; i < pow2(total_qubit); ++i) {
	        state[i] /= norm;
	    }
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
				{ it_damp->second },
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
				{ it_bitflip->second },
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
				{ it_phaseflip->second },
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

	// void NoisySimulator::iswap(size_t qn1, size_t qn2, bool is_dagger)
	// {
	// 	iswap_cont(qn1, qn2, {}, is_dagger);
	// }

	void NoisySimulator::xy(size_t qn1, size_t qn2, double theta, bool is_dagger)
	{
		xy_cont(qn1, qn2, theta, {}, is_dagger);
	}

	void NoisySimulator::cnot(size_t controller, size_t target, bool is_dagger)
	{
		cnot_cont(controller, target, {}, is_dagger);
	}

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

	// IT NEEDS ONE MORE PARAMETER, THE UNITARY MATRIX
	// void NoisySimulator::u22_cont(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
	// {
	// 	opcodes.emplace_back(
	// 		OpcodeType(
	// 		(uint32_t)SupportOperationType::u22,
	// 		{ qn },
	// 		{},
	// 		is_dagger,
	// 		global_controller)
	// 	);
	// 	insert_error({ qn });
	// }

	void NoisySimulator::x_cont(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
	{
		opcodes.emplace_back(
			OpcodeType(
			(uint32_t)SupportOperationType::X,
			{ qn },
			{},
			is_dagger,
			global_controller)
		);
		insert_error({ qn });
	}

	void NoisySimulator::y_cont(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
	{
		opcodes.emplace_back(
			OpcodeType(
			(uint32_t)SupportOperationType::Y,
			{ qn },
			{},
			is_dagger,
			global_controller)
		);
		insert_error({ qn });
	}

	void NoisySimulator::z_cont(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
	{
		opcodes.emplace_back(
			OpcodeType(
			(uint32_t)SupportOperationType::Z,
			{ qn },
			{},
			is_dagger,
			global_controller)
		);
		insert_error({ qn });
	}

	void NoisySimulator::sx_cont(size_t qn, const std::vector<size_t>& global_controller, bool is_dagger)
	{
		opcodes.emplace_back(
			OpcodeType(
			(uint32_t)SupportOperationType::SX,
			{ qn },
			{},
			is_dagger,
			global_controller)
		);
		insert_error({ qn });
	}

	void NoisySimulator::cz_cont(size_t qn1, size_t qn2, const std::vector<size_t>& global_controller, bool is_dagger)
	{
		opcodes.emplace_back(
			OpcodeType(
			(uint32_t)SupportOperationType::CZ,
			{ qn1, qn2 },
			{},
			is_dagger,
			global_controller)
		);
		insert_error({ qn1, qn2 });
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

	void NoisySimulator::cnot_cont(size_t controller, size_t target, const std::vector<size_t>& global_controller, bool is_dagger)
	{
		opcodes.emplace_back(
			OpcodeType(
			(uint32_t)SupportOperationType::CNOT,
			{ controller, target },
			{},
			is_dagger,
			global_controller)
		);
		insert_error({ controller, target });
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
		// std::cout << "once" << " ";
		// Currently, the iteration only supports Hadamard gates and depolarizing noise 2023/11/02
		for (const auto &opcode : opcodes)
		{
			switch (opcode.op)
			{
			case (uint32_t)NoiseType::Depolarizing:
				for (const auto &q : opcode.qubits)
				{
					simulator.depolarizing(q, opcode.parameters[0]);
				}				
				break;
			case (uint32_t)NoiseType::Damping:
				for (const auto &q : opcode.qubits)
				{
					simulator.damping(q, opcode.parameters[0]);
				}
				break;
			case (uint32_t)NoiseType::BitFlip:
				for (const auto &q : opcode.qubits)
				{
					simulator.bitflip(q, opcode.parameters[0]);
				}				
				break;
			case (uint32_t)NoiseType::PhaseFlip:
				for (const auto &q : opcode.qubits)
				{
					simulator.phaseflip(q, opcode.parameters[0]);
				}				
				break;
			case (uint32_t)SupportOperationType::HADAMARD:
    			simulator.hadamard(opcode.qubits[0]);
    			break;
			case (uint32_t)SupportOperationType::X:
				simulator.x(opcode.qubits[0]);
				break;
			case (uint32_t)SupportOperationType::Y:
				simulator.y(opcode.qubits[0]);
				break;
			case (uint32_t)SupportOperationType::Z:
				simulator.z(opcode.qubits[0]);
				break;
			case (uint32_t)SupportOperationType::CZ:
				simulator.cz(opcode.qubits[0], opcode.qubits[1]);
				break;
			case (uint32_t)SupportOperationType::CNOT:
				simulator.cnot(opcode.qubits[0], opcode.qubits[1]);
				// std::cout << 11111 << " ";
				break;
			default:
				ThrowRuntimeError(fmt::format("Failed to handle opcode = {}\nPlease check.", opcode.op));
			}
		}
		
		// This block could print the state after all operations(make sure the noiseless simulation is correct).
		// for (const auto &amp : simulator.state) {
		// 	    std::cout << amp << " ";
		// 	}
		// std::cout << std::endl;
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
		// std::cout << r << " ";
		for (size_t i = 0; i < pow2(simulator.total_qubit); ++i)
		{
			// std::cout << simulator.state[i] << " ";
			// Is this random number landing in this probability range?
			if (r < abs_sqr(simulator.state[i]))
			{
				// std::cout << r << " ";		
				return i;
			}
			// No, move to the next one, and subtract the current prob from the r
			else
			{
				r -= abs_sqr(simulator.state[i]);
				// std::cout << r << " ";
			}
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

