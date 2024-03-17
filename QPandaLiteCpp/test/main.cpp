/*#include <iostream>
#include "fmt/core.h"
int main() 
{	
	fmt::print("Hello quantum!");
	return 0;
}*/

#include <iostream>
#include <vector>
#include <bitset>
#include <string>
#include <random>
#include <cmath>
#include <numeric>

std::vector<double> generateRandomState(int n_qubits) {
    std::vector<double> state(pow(2, n_qubits));
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0.0, 1.0);

    double sum = 0.0;
    for (double& value : state) {
        value = dis(gen);
        sum += value;
    }

    // Normalize the state vector
    for (double& value : state) {
        value /= sum;
    }

    return state;
}

std::vector<double> measure(const std::vector<double>& state, const std::vector<int>& measure_list, const std::vector<int>& used_qubit_list) {
    int n_q = used_qubit_list.size();
    int n_m = measure_list.size();
    int n_s = n_q - n_m;
    std::vector<double> new_state(pow(2, n_m), 0.0);
    std::vector<std::vector<double>> intermediate_state(pow(2, n_m), std::vector<double>(pow(2, n_s), 0.0));
    if (n_s == 0) {
        return state;
    }
    for (int t = 0; t < pow(2, n_q); ++t) {
        std::string binary_str = std::bitset<32>(t).to_string().substr(32 - n_q, n_q);
        std::string str1 = "", str2 = "";

        for (int i = 0; i < binary_str.size(); ++i) {
            if (std::find(measure_list.begin(), measure_list.end(), i) != measure_list.end()) {
                str1 += binary_str[i];
            }
            else {
                str2 += binary_str[i];
            }
        }

        int k = std::stoi(str1, nullptr, 2);
        int l = std::stoi(str2, nullptr, 2);
        intermediate_state[k][l] = state[t];
    }

    for (int i = 0; i < intermediate_state.size(); ++i) {
        new_state[i] = std::accumulate(intermediate_state[i].begin(), intermediate_state[i].end(), 0.0);
    }

    return new_state;
}

int main() {
    int n_qubits = 5;
    std::vector<int> measure_list = { 0, 1, 2, 3, };
    std::vector<int> used_qubit_list = { 0, 1, 2, 3, 4 };

    std::vector<double> state = generateRandomState(n_qubits);
    std::vector<double> new_state = measure(state, measure_list, used_qubit_list);

    std::cout << "new_state: ";
    for (const auto& value : new_state) {
        std::cout << value << " ";
    }
    std::cout << "\nSum of new state: " << std::accumulate(new_state.begin(), new_state.end(), 0.0) << std::endl;

    return 0;
}

