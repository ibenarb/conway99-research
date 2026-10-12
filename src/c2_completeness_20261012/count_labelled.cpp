#include <array>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

// Exhaust all rows of every fixed degree sequence; do not use canonicalization.
// The only pruning is that the mutual graph on assigned vertices has no C4.
class Counter {
public:
    unsigned n;
    std::array<unsigned, 7> degrees{}, rows{}, mutual{};
    std::array<std::array<std::vector<unsigned>, 7>, 7> options;
    explicit Counter(unsigned size) : n(size) {
        for (unsigned i = 0; i < n; ++i) {
            for (unsigned mask = 0; mask < (1U << n); ++mask) {
                if (!(mask & (1U << i))) options[i][__builtin_popcount(mask)].push_back(mask);
            }
        }
    }
    std::uint64_t visit(unsigned v) {
        unsigned incoming = 0;
        for (unsigned u = 0; u < v; ++u) if (rows[u] & (1U << v)) incoming |= 1U << u;
        // bad[u] contains old vertices sharing an old mutual neighbor with u.
        std::array<unsigned, 7> bad{};
        for (unsigned rem = incoming; rem; rem &= rem - 1) {
            unsigned u = __builtin_ctz(rem);
            for (unsigned neighbors = mutual[u]; neighbors; neighbors &= neighbors - 1) bad[u] |= mutual[__builtin_ctz(neighbors)];
        }
        std::uint64_t total = 0;
        for (unsigned mask : options[v][degrees[v]]) {
            unsigned neighbors = mask & incoming;
            bool valid = true;
            for (unsigned rem = neighbors; rem;) {
                unsigned u = __builtin_ctz(rem);
                rem &= rem - 1;
                if (bad[u] & rem) { valid = false; break; }
            }
            if (!valid) continue;
            if (v + 1 == n) { ++total; continue; }
            rows[v] = mask;
            mutual[v] = neighbors;
            for (unsigned rem = neighbors; rem; rem &= rem - 1) mutual[__builtin_ctz(rem)] |= 1U << v;
            total += visit(v + 1);
            for (unsigned rem = neighbors; rem; rem &= rem - 1) mutual[__builtin_ctz(rem)] &= ~(1U << v);
            mutual[v] = 0;
        }
        return total;
    }
};

unsigned factorial(unsigned n) {
    unsigned answer = 1;
    for (unsigned i = 2; i <= n; ++i) answer *= i;
    return answer;
}

int main(int argc, char** argv) {
    try {
        if (argc != 2) throw std::runtime_error("Specify --control4 or --count7");
        bool control = std::string(argv[1]) == "--control4";
        if (!control && std::string(argv[1]) != "--count7") throw std::runtime_error("Unknown mode");
        unsigned n = control ? 4 : 7;
        std::vector<unsigned> allowed = control ? std::vector<unsigned>{3, 2, 1, 0} : std::vector<unsigned>{6, 4, 3};
        Counter counter(n);
        std::uint64_t total = 0;
        unsigned profiles = 0;
        auto start = std::chrono::steady_clock::now();
        auto profile = [&](auto&& self, unsigned position, unsigned first) -> void {
            if (position != n) {
                for (unsigned i = first; i < allowed.size(); ++i) {
                    counter.degrees[position] = allowed[i];
                    self(self, position + 1, i);
                }
                return;
            }
            if (!control && counter.degrees[n - 1] != 3) return;
            auto count = counter.visit(0);
            unsigned denominator = 1;
            for (unsigned d : allowed) {
                unsigned multiplicity = 0;
                for (unsigned i = 0; i < n; ++i) multiplicity += counter.degrees[i] == d;
                denominator *= factorial(multiplicity);
            }
            unsigned multiplier = factorial(n) / denominator;
            total += count * multiplier;
            ++profiles;
            std::cout << "PROFILE\t";
            for (unsigned i = 0; i < n; ++i) std::cout << (i ? "," : "") << counter.degrees[i];
            std::cout << '\t' << count << '\t' << multiplier << '\t' << count * multiplier << std::endl;
        };
        profile(profile, 0, 0);
        double elapsed = std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count();
        std::cout << "TOTAL\t" << profiles << '\t' << total << '\t' << elapsed << std::endl;
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "FAIL " << error.what() << '\n';
        return 1;
    }
}
