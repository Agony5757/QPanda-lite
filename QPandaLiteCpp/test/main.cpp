/*#include <iostream>
#include "fmt/core.h"
int main() 
{	
	fmt::print("Hello quantum!");
	return 0;
}*/

#include <iostream>
#include <vector>

unsigned int transform(unsigned int i, const std::vector<int>& measure_list) {
    unsigned int j = 0;
    for (int k = 0; k < measure_list.size(); ++k) {
        if (i & (1 << measure_list[k])) {
            j |= (1 << k);
        }
    }
    return j;
}

int main() {
    // Example usage
    unsigned int i = 13; // Binary: 1101
    std::vector<int> measure_list = { 0, 1, 3 }; // Positions in the binary representation of i

    unsigned int j = transform(i, measure_list);
    std::cout << "i: " << i << ", j: " << j << std::endl; // Should print the value of j as the new binary representation

    return 0;
}


