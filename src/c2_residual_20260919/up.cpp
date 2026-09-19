// Deterministic full-scan unit propagation only. No branching, no SAT solver.
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

int main(int argc, char** argv) {
    if (argc < 2) return 2;
    std::ifstream in(argv[1]);
    std::string marker, format;
    int n, m;
    if (!(in >> marker >> format >> n >> m) || marker != "p" || format != "cnf") return 3;
    std::vector<int> data, ends;
    int x;
    while (in >> x) {
        if (x == 0) ends.push_back(data.size());
        else {
            if (std::abs(x) > n) return 4;
            data.push_back(x);
        }
    }
    if (int(ends.size()) != m || (!ends.empty() && ends.back() != int(data.size()))) return 5;
    std::vector<int> value(n+1, 0);
    bool conflict = false;
    auto assign = [&](int lit) {
        int v = std::abs(lit), sign = lit > 0 ? 1 : -1;
        if (v == 0 || v > n) { conflict = true; return false; }
        if (value[v] == -sign) conflict = true;
        if (value[v]) return false;
        value[v] = sign;
        return true;
    };
    for (int i=2; i<argc; ++i) assign(std::stoi(argv[i]));
    bool changed = true;
    int passes = 0;
    while (changed && !conflict) {
        changed = false;
        ++passes;
        int start = 0;
        for (int end : ends) {
            bool satisfied = false;
            int open = 0, unit = 0;
            for (int j=start; j<end; ++j) {
                int lit = data[j], v = value[std::abs(lit)];
                if (v == (lit > 0 ? 1 : -1)) { satisfied = true; break; }
                if (!v) { ++open; unit = lit; }
            }
            start = end;
            if (satisfied) continue;
            if (!open) { conflict = true; break; }
            if (open == 1) changed = assign(unit) || changed;
            if (conflict) break;
        }
    }
    int fixed = 0;
    for (int i=1; i<=n; ++i) fixed += value[i] != 0;
    std::cout << "{\"conflict\":" << (conflict ? "true" : "false")
              << ",\"fixed_total\":" << fixed << ",\"passes\":" << passes
              << ",\"primary_literals\":[";
    bool first = true;
    for (int i=1; i<=n && i<=1722; ++i) if (value[i]) {
        if (!first) std::cout << ',';
        first = false;
        std::cout << i*value[i];
    }
    std::cout << "]}\n";
}
