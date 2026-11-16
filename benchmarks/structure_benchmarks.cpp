#include "BinarySearchTree.h"
#include "BinaryHeap.h"
#include "PriorityQueue.h"
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

using Clock = std::chrono::steady_clock;
volatile std::uint64_t checksum = 0;
template<typename Function> double Measure(Function action) {
    const auto begin = Clock::now(); action();
    return std::chrono::duration<double, std::milli>(Clock::now() - begin).count();
}
struct Times { double insert, search, remove; };
Times Run(const std::string& kind, const std::vector<int>& values) {
    BinarySearchTree<int> tree; BinaryHeap<int> heap(false); PriorityQueue<int> queue;
    std::uint64_t sum = 0;
    const double insert = Measure([&] {
        for (int value : values) {
            if (kind == "avl") tree.Insert(value);
            else if (kind == "heap") heap.Push(value);
            else queue.Push(value, value);
        }
    });
    const double search = Measure([&] {
        for (int value : values) {
            if (kind == "avl") sum += tree.Contains(value);
            else if (kind == "heap") { checksum = static_cast<std::uint64_t>(heap.Top()); }
            else { checksum = static_cast<std::uint64_t>(queue.Top()); }
        }
    });
    const double remove = Measure([&] {
        for (int value : values) {
            if (kind == "avl") sum += tree.Remove(value);
            else if (kind == "heap") sum += heap.Pop();
            else sum += queue.Pop();
        }
    });
    checksum = sum;
    return {insert, search, remove};
}
int main(int argc, char** argv) {
    const std::string output = argc > 1 ? argv[1] : "benchmark-results.csv";
    std::ofstream file(output);
    if (!file) { std::cerr << "Cannot write " << output << '\n'; return 1; }
    file << "structure,n,insert_ms,search_or_top_ms,remove_ms\n" << std::fixed << std::setprecision(6);
    for (int n : {10000, 30000, 100000, 300000, 1000000}) {
        std::vector<int> values(n); std::iota(values.begin(), values.end(), 0);
        std::mt19937 random(2026); std::shuffle(values.begin(), values.end(), random);
        for (const std::string kind : {"avl", "heap", "queue"}) {
            std::vector<double> insert, search, remove;
            for (int repeat = 0; repeat < 3; ++repeat) {
                auto times = Run(kind, values);
                insert.push_back(times.insert); search.push_back(times.search); remove.push_back(times.remove);
            }
            std::sort(insert.begin(), insert.end()); std::sort(search.begin(), search.end()); std::sort(remove.begin(), remove.end());
            file << kind << ',' << n << ',' << insert[1] << ',' << search[1] << ',' << remove[1] << '\n';
            file.flush();
            std::cout << kind << " n=" << n << " insert=" << insert[1] << "ms\n";
        }
    }
}
