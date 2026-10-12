// Exhaustive degree-sorted C4-free digraph enumeration, split by row 0.
// Canonicalization uses vertex invariants followed by ALL permutations in tie blocks.
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <ctime>
#include <fstream>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

using U = std::uint64_t;
static int n, firstmask;
static std::array<int, 7> out{}, incoming{}, degree{}, order{}, group{};
static std::array<std::vector<int>, 7> options;
static std::array<bool, 7> used{};
static U leaves = 0, nodes = 0, candidates = 0, best;
static int aut;
static double last_report = 0;
struct Record { int aut; int mutual; };
static std::unordered_map<U, Record> representatives;

static int pc(int mask) { return __builtin_popcount((unsigned)mask); }

static bool no_new_c4(int v) {
    int previous = (1 << v) - 1;
    int neighbors = out[v] & incoming[v] & previous;
    for (int a = 0; a < v; ++a) if ((neighbors >> a) & 1) {
        for (int b = a + 1; b < v; ++b) if ((neighbors >> b) & 1) {
            if (out[a] & incoming[a] & out[b] & incoming[b] & previous) return false;
        }
    }
    return true;
}

static U encode() {
    U result = 0;
    int bit = 0;
    for (int a = 0; a < n; ++a) for (int b = 0; b < n; ++b) {
        if (a == b) continue;
        if ((out[order[a]] >> order[b]) & 1) result |= U(1) << bit;
        ++bit;
    }
    return result;
}

static void permute(int position) {
    if (position == n) {
        U code = encode();
        if (code < best) { best = code; aut = 1; }
        else if (code == best) ++aut;
        return;
    }
    for (int vertex = 0; vertex < n; ++vertex) {
        if (used[vertex] || group[vertex] != group[position]) continue;
        used[vertex] = true;
        order[position] = vertex;
        permute(position + 1);
        used[vertex] = false;
    }
}

static void leaf() {
    ++leaves;
    std::array<int, 7> base{};
    std::array<long long, 7> refined{};
    for (int v = 0; v < n; ++v) {
        base[v] = degree[v] * 10000 + pc(incoming[v]) * 100 + pc(out[v] & incoming[v]);
        if (v && base[v - 1] < base[v]) return;
    }
    for (int v = 0; v < n; ++v) {
        long long sum = 0;
        for (int u = 0; u < n; ++u) {
            if ((out[v] >> u) & 1) sum += 3 * base[u];
            if ((incoming[v] >> u) & 1) sum += 7 * base[u];
        }
        refined[v] = base[v] * 1000003LL + sum;
        if (v && base[v - 1] == base[v] && refined[v - 1] < refined[v]) return;
    }
    ++candidates;
    group[0] = 0;
    for (int v = 1; v < n; ++v) {
        group[v] = group[v - 1] + (base[v] != base[v - 1] || refined[v] != refined[v - 1]);
    }
    best = ~U(0);
    aut = 0;
    permute(0);
    int mutual = 0;
    for (int v = 0; v < n; ++v) mutual += pc(out[v] & incoming[v]);
    mutual /= 2;
    auto inserted = representatives.emplace(best, Record{aut, mutual});
    if (!inserted.second && (inserted.first->second.aut != aut || inserted.first->second.mutual != mutual)) {
        throw std::runtime_error("Inconsistent representative");
    }
}

static void report() {
    double cpu = double(std::clock()) / CLOCKS_PER_SEC;
    if (cpu - last_report >= 60) {
        last_report = cpu;
        std::cout << "ENUM_PROGRESS {\"cpu_s\":" << cpu << ",\"nodes\":" << nodes
                  << ",\"leaves\":" << leaves << ",\"representatives\":"
                  << representatives.size() << "}" << std::endl;
    }
}

static void visit(int v) {
    if ((++nodes & ((U(1) << 18) - 1)) == 0) report();
    if (v == n) { leaf(); return; }
    for (int mask : options[v]) {
        if (v == 0 && firstmask >= 0 && mask != firstmask) continue;
        out[v] = mask;
        for (int u = 0; u < n; ++u) if ((mask >> u) & 1) incoming[u] |= 1 << v;
        if (no_new_c4(v)) visit(v + 1);
        for (int u = 0; u < n; ++u) if ((mask >> u) & 1) incoming[u] &= ~(1 << v);
    }
    out[v] = 0;
}

int main(int argc, char **argv) {
    try {
        if (argc != 6) throw std::runtime_error("Usage: enum N degrees_csv firstmask|-1 reps.tsv summary.json");
        n = std::stoi(argv[1]);
        if (n < 2 || n > 7) throw std::runtime_error("N outside 2..7");
        std::stringstream list(argv[2]);
        std::string word;
        int count = 0;
        while (std::getline(list, word, ',')) {
            if (count >= n) throw std::runtime_error("Too many degrees");
            degree[count++] = std::stoi(word);
        }
        if (count != n) throw std::runtime_error("Wrong degree count");
        for (int v = 0; v < n; ++v) {
            if (degree[v] < 0 || degree[v] >= n || (v && degree[v - 1] < degree[v])) {
                throw std::runtime_error("Degrees must be feasible and non-increasing");
            }
            for (int mask = 0; mask < (1 << n); ++mask) {
                if (!((mask >> v) & 1) && pc(mask) == degree[v]) options[v].push_back(mask);
            }
        }
        firstmask = std::stoi(argv[3]);
        if (firstmask != -1 && std::find(options[0].begin(), options[0].end(), firstmask) == options[0].end()) {
            throw std::runtime_error("Invalid first row");
        }
        visit(0);
        std::vector<U> codes;
        codes.reserve(representatives.size());
        for (const auto &item : representatives) codes.push_back(item.first);
        std::sort(codes.begin(), codes.end());
        std::ofstream file(std::string(argv[4]) + ".writing");
        if (!file) throw std::runtime_error("Cannot write representatives");
        for (U code : codes) {
            Record r = representatives.at(code);
            file << code << '\t' << r.aut << '\t' << r.mutual << '\n';
        }
        file.close();
        if (!file || std::rename((std::string(argv[4]) + ".writing").c_str(), argv[4])) {
            throw std::runtime_error("Representative write failed");
        }
        std::ofstream summary(std::string(argv[5]) + ".writing");
        summary << "{\"status\":\"COMPLETE\",\"n\":" << n << ",\"degrees\":[";
        for (int v = 0; v < n; ++v) summary << (v ? "," : "") << degree[v];
        summary << "],\"firstmask\":" << firstmask << ",\"degree_sorted_labelled\":" << leaves
                << ",\"nodes\":" << nodes << ",\"canonical_candidates\":" << candidates
                << ",\"representatives_in_shard\":" << codes.size() << ",\"cpu_s\":"
                << double(std::clock()) / CLOCKS_PER_SEC << "}\n";
        summary.close();
        if (!summary || std::rename((std::string(argv[5]) + ".writing").c_str(), argv[5])) {
            throw std::runtime_error("Summary write failed");
        }
        std::cout << "ENUM_COMPLETE " << codes.size() << " " << leaves << std::endl;
    } catch (const std::exception &e) {
        std::cerr << e.what() << std::endl;
        return 2;
    }
    return 0;
}
