#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

int main(int argc, char** argv) {
    std::uint64_t line_number = 1;
    try {
        if (argc != 2) throw std::runtime_error("Expected one TSV path");
        std::ifstream input(argv[1]);
        if (!input) throw std::runtime_error("Cannot open input");
        std::string line;
        std::getline(input, line);
        if (line != "code\taut\tmutual_edges\tdegrees\tstratum") throw std::runtime_error("Unexpected header");
        std::vector<std::uint64_t> codes;
        codes.reserve(7400000);
        std::map<std::string, std::array<std::uint64_t, 2>> profiles;
        std::map<std::string, std::uint64_t> strata;
        std::map<unsigned, std::uint64_t> aut_histogram;
        std::uint64_t weight_sum = 0;
        while (std::getline(input, line)) {
            ++line_number;
            std::istringstream row(line);
            std::uint64_t code;
            unsigned aut, stored_mutual;
            std::string stored_degrees, stored_stratum, extra;
            if (!(row >> code >> aut >> stored_mutual >> stored_degrees >> stored_stratum) || (row >> extra)) throw std::runtime_error("Malformed record");
            if (code >= (1ULL << 42)) throw std::runtime_error("Code exceeds 42 bits");
            if (!aut || 5040 % aut) throw std::runtime_error("Invalid stored automorphism order");
            std::array<unsigned, 7> adjacency{}, mutual{}, degrees{};
            std::string degree_key;
            unsigned n3 = 0, n6 = 0;
            for (unsigned i = 0; i < 7; ++i) {
                unsigned six = (code >> (6 * i)) & 63;
                adjacency[i] = (six & ((1U << i) - 1)) | ((six >> i) << (i + 1));
                degrees[i] = __builtin_popcount(adjacency[i]);
                if (degrees[i] != 3 && degrees[i] != 4 && degrees[i] != 6) throw std::runtime_error("Disallowed degree");
                if (i && degrees[i - 1] < degrees[i]) throw std::runtime_error("Unsorted degree sequence");
                if (i) degree_key += ',';
                degree_key += std::to_string(degrees[i]);
                n3 += degrees[i] == 3;
                n6 += degrees[i] == 6;
            }
            if (!n3 || stored_degrees != degree_key) throw std::runtime_error("Degree metadata mismatch");
            unsigned mutual_edges = 0;
            for (unsigned i = 0; i < 7; ++i) {
                for (unsigned j = 0; j < i; ++j) {
                    if ((adjacency[i] & (1U << j)) && (adjacency[j] & (1U << i))) {
                        mutual[i] |= 1U << j;
                        mutual[j] |= 1U << i;
                        ++mutual_edges;
                    }
                }
            }
            if (stored_mutual != mutual_edges) throw std::runtime_error("Mutual-edge metadata mismatch");
            for (unsigned i = 0; i < 7; ++i) {
                for (unsigned j = 0; j < i; ++j) {
                    if (__builtin_popcount(mutual[i] & mutual[j]) >= 2) throw std::runtime_error("Mutual four-cycle present");
                }
            }
            std::string stratum_key = std::to_string(n3) + '_' + std::to_string(n6) + '_' + std::to_string(mutual_edges / 4);
            if (stored_stratum != stratum_key) throw std::runtime_error("Stratum metadata mismatch");
            codes.push_back(code);
            ++profiles[degree_key][0];
            profiles[degree_key][1] += 5040 / aut;
            ++strata[stratum_key];
            ++aut_histogram[aut];
            weight_sum += 5040 / aut;
        }
        if (!input.eof()) throw std::runtime_error("Input read failure");
        std::sort(codes.begin(), codes.end());
        if (std::adjacent_find(codes.begin(), codes.end()) != codes.end()) throw std::runtime_error("Duplicate code");
        std::cout << "TOTAL\t" << codes.size() << '\t' << weight_sum << '\n';
        for (const auto& item : profiles) std::cout << "PROFILE\t" << item.first << '\t' << item.second[0] << '\t' << item.second[1] << '\n';
        for (const auto& item : strata) std::cout << "STRATUM\t" << item.first << '\t' << item.second << '\n';
        for (const auto& item : aut_histogram) std::cout << "AUT\t" << item.first << '\t' << item.second << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "FAIL near TSV line " << line_number << ": " << error.what() << '\n';
        return 1;
    }
}
