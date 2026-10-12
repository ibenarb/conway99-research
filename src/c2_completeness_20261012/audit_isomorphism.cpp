#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

// Independent S7 canonicalization using only (outdegree, indegree) color classes.
// Every isomorphism preserves these colors. Enumerating all permutations inside
// sorted color blocks therefore yields a complete isomorphism invariant.
// The number of orders attaining the canonical adjacency matrix is |Aut(D)|.
int main(int argc, char** argv) {
    std::uint64_t count = 0;
    try {
        if (argc < 2 || argc > 3) throw std::runtime_error("Expected TSV path and optional --estimate");
        bool estimate = argc == 3 && std::string(argv[2]) == "--estimate";
        if (argc == 3 && !estimate) throw std::runtime_error("Unknown option");
        std::ifstream input(argv[1]);
        if (!input) throw std::runtime_error("Cannot open input");
        std::string line;
        std::getline(input, line);
        if (line != "code\taut\tmutual_edges\tdegrees\tstratum") throw std::runtime_error("Wrong header");
        std::vector<std::uint64_t> canonical_codes;
        if (!estimate) canonical_codes.reserve(7400000);
        std::uint64_t permutations = 0, labelled = 0, maximum_permutations = 0;
        std::map<unsigned, std::uint64_t> aut_histogram;
        const unsigned factorial[] = {1, 1, 2, 6, 24, 120, 720, 5040};
        auto start = std::chrono::steady_clock::now();
        while (std::getline(input, line)) {
            std::istringstream row(line);
            std::uint64_t code;
            unsigned expected_aut, mutual_count;
            std::string degree_field, stratum, extra;
            if (!(row >> code >> expected_aut >> mutual_count >> degree_field >> stratum) || (row >> extra)) throw std::runtime_error("Malformed row");
            if (code >= (1ULL << 42)) throw std::runtime_error("Excess code bits");
            std::array<unsigned, 7> adjacency{}, indegree{}, outdegree{}, order{};
            for (unsigned i = 0; i < 7; ++i) {
                unsigned six = (code >> (6 * i)) & 63;
                adjacency[i] = (six & ((1U << i) - 1)) | ((six >> i) << (i + 1));
                outdegree[i] = __builtin_popcount(six);
                for (unsigned j = 0; j < 7; ++j) indegree[j] += (adjacency[i] >> j) & 1;
                order[i] = i;
            }
            auto color = [&](unsigned i) { return outdegree[i] * 8 + indegree[i]; };
            std::sort(order.begin(), order.end(), [&](unsigned i, unsigned j) {
                return std::make_pair(color(i), i) < std::make_pair(color(j), j);
            });
            std::vector<std::pair<unsigned, unsigned>> blocks;
            std::uint64_t choices = 1;
            for (unsigned lo = 0; lo < 7;) {
                unsigned hi = lo + 1;
                while (hi < 7 && color(order[hi]) == color(order[lo])) ++hi;
                blocks.emplace_back(lo, hi);
                choices *= factorial[hi - lo];
                lo = hi;
            }
            permutations += choices;
            maximum_permutations = std::max(maximum_permutations, choices);
            if (!estimate) {
                std::uint64_t best = UINT64_MAX, evaluated = 0;
                unsigned aut = 0;
                std::function<void(unsigned)> visit = [&](unsigned block) {
                    if (block == blocks.size()) {
                        std::uint64_t transformed = 0;
                        for (unsigned i = 0; i < 7; ++i) {
                            for (unsigned j = 0; j < 7; ++j) {
                                transformed |= std::uint64_t((adjacency[order[i]] >> order[j]) & 1) << (7 * i + j);
                            }
                        }
                        ++evaluated;
                        if (transformed < best) { best = transformed; aut = 1; }
                        else if (transformed == best) ++aut;
                        return;
                    }
                    auto [lo, hi] = blocks[block];
                    do { visit(block + 1); }
                    while (std::next_permutation(order.begin() + lo, order.begin() + hi));
                };
                visit(0);
                if (evaluated != choices) throw std::runtime_error("Permutation enumeration incomplete");
                if (!aut || 5040 % aut || aut != expected_aut) throw std::runtime_error("Automorphism order mismatch at code " + std::to_string(code));
                canonical_codes.push_back(best);
                labelled += 5040 / aut;
                ++aut_histogram[aut];
            }
            ++count;
            if (count % 1000000 == 0) {
                double elapsed = std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count();
                std::cerr << "PROGRESS records=" << count << " elapsed_seconds=" << elapsed << '\n';
            }
        }
        if (!input.eof()) throw std::runtime_error("Input read failure");
        if (!estimate) {
            std::sort(canonical_codes.begin(), canonical_codes.end());
            if (std::adjacent_find(canonical_codes.begin(), canonical_codes.end()) != canonical_codes.end()) throw std::runtime_error("Isomorphic duplicate");
        }
        double elapsed = std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count();
        std::cout << "{\"status\":\"PASS\",\"mode\":\"" << (estimate ? "estimate" : "full")
                  << "\",\"records\":" << count << ",\"permutations\":" << permutations
                  << ",\"max_permutations_per_record\":" << maximum_permutations
                  << ",\"labelled_orbit_sum\":" << labelled << ",\"elapsed_seconds\":" << elapsed
                  << ",\"automorphism_histogram\":{";
        bool first = true;
        for (const auto& item : aut_histogram) {
            if (!first) std::cout << ',';
            first = false;
            std::cout << '\"' << item.first << "\":" << item.second;
        }
        std::cout << "}}\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "FAIL after " << count << " records: " << error.what() << '\n';
        return 1;
    }
}
