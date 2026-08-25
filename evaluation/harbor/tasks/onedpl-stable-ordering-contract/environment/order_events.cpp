#include <oneapi/dpl/algorithm>
#include <oneapi/dpl/execution>

#include <algorithm>
#include <cstdlib>
#include <iostream>
#include <vector>

struct event {
    int key;
    int arrival;
};

int main(int argc, char** argv) {
    const int count = argc > 1 ? std::atoi(argv[1]) : 257;
    const int key_count = argc > 2 ? std::atoi(argv[2]) : 7;
    if (count < 1 || key_count < 1) return 2;

    std::vector<event> events;
    events.reserve(count);
    for (int arrival = 0; arrival < count; ++arrival) {
        const int key = (arrival * 37 + arrival / 3 + 11) % key_count;
        events.push_back({key, arrival});
    }

    std::sort(oneapi::dpl::execution::par,
              events.begin(),
              events.end(),
              [](const event& left, const event& right) { return left.key < right.key; });

    for (const auto& item : events) {
        std::cout << item.key << ':' << item.arrival << '\n';
    }
}
