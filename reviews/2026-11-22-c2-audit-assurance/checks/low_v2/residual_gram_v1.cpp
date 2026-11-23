// New independent low-rank solver derived from Theorem.md, not the author's low solvers.
// All selected residual vectors use one common Gram matrix. No depth cutoff.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>
using namespace std;
using U = uint64_t;
using I = int64_t;
using Matrix = vector<vector<int>>;
int mod(int x) { x %= 7; return x < 0 ? x + 7 : x; }
int inv7[7] = {0,1,4,5,2,3,6};
bool square7(int x) { return x == 1 || x == 2 || x == 4; }
struct Invariant { int rank; int det; };
Invariant invariant(const Matrix &g) {
    int size = int(g.size()), r = 0;
    Matrix a = g;
    vector<int> piv;
    for (int c = 0; c < size; ++c) {
        int k = r;
        while (k < size && a[k][c] == 0) ++k;
        if (k == size) continue;
        swap(a[k], a[r]);
        int inverse = inv7[a[r][c]];
        for (int j = c; j < size; ++j) a[r][j] = mod(a[r][j] * inverse);
        for (int i = r + 1; i < size; ++i) {
            int factor = a[i][c];
            for (int j = c; j < size; ++j) a[i][j] = mod(a[i][j] - factor * a[r][j]);
        }
        piv.push_back(c);
        ++r;
    }
    Matrix b(r, vector<int>(r));
    for (int i = 0; i < r; ++i)
        for (int j = 0; j < r; ++j) b[i][j] = g[piv[i]][piv[j]];
    int det = 1;
    for (int c = 0; c < r; ++c) {
        int k = c;
        while (k < r && !b[k][c]) ++k;
        if (k == r) throw runtime_error("Singular principal column-basis minor");
        if (k != c) { swap(b[k], b[c]); det = mod(-det); }
        det = mod(det * b[c][c]);
        int inverse = inv7[b[c][c]];
        for (int i = c + 1; i < r; ++i) {
            int factor = mod(b[i][c] * inverse);
            for (int j = c; j < r; ++j) b[i][j] = mod(b[i][j] - factor * b[c][j]);
        }
    }
    return {r, det};
}
bool fits(const Matrix &g, int dim, int type) {
    auto value = invariant(g);
    return value.rank <= dim && (value.rank < dim || square7(value.det) == square7(type));
}
int local_rank, ambient_dim, anchors, determinant;
I denominator;
struct Attachment {
    int label, norm;
    U positive, negative;
    I real_norm;
    array<int,12> key, pivot_column, projected_column;
    array<I,12> f, projected_real;
    vector<int> h;
};
struct Choice { int attachment, support, signs; };
vector<Attachment> attachments;
vector<int> by_label[30];
array<array<int,6>,15> outer_words;
array<array<int,3>,30> labels;
int pair_index[6][6];
array<U,39> base;
uint64_t nodes = 0, pair_tests = 0, gram_tests = 0, literal_tests = 0;
int maximum_depth = 0;
unordered_map<U, unsigned> pair_cache;
int common_axes(int x, int y) {
    int out = 0;
    for (int i = 0; i < 2; ++i)
        for (int j = 0; j < 2; ++j) out += labels[x][i] == labels[y][j];
    return out;
}
int signed_axes(int x, int y) {
    int v[6] = {}, w[6] = {};
    v[labels[x][0]] = 1; v[labels[x][1]] = labels[x][2] ? -1 : 1;
    w[labels[y][0]] = 1; w[labels[y][1]] = labels[y][2] ? -1 : 1;
    int out = 0;
    for (int i = 0; i < 6; ++i) out += v[i] * w[i];
    return out;
}
bool capacity(const Attachment &a, const Attachment &b, int unsigned_link, int signed_link) {
    ++literal_tests;
    array<U,43> graph{};
    for (int i = 0; i < 39; ++i) graph[i] = base[i];
    graph[39] = a.positive; graph[40] = a.negative;
    graph[41] = b.positive; graph[42] = b.negative;
    for (int k = 39; k < 43; ++k)
        for (int i = 0; i < 39; ++i)
            if ((graph[k] >> i) & 1) graph[i] |= U(1) << k;
    auto edge = [&](int x, int y) { graph[x] |= U(1) << y; graph[y] |= U(1) << x; };
    if (unsigned_link == 2 || signed_link == 1) { edge(39,41); edge(40,42); }
    if (unsigned_link == 2 || signed_link == -1) { edge(39,42); edge(40,41); }
    for (int i = 0; i < 43; ++i)
        for (int j = i + 1; j < 43; ++j)
            if (__builtin_popcountll(graph[i] & graph[j]) > 2 - int((graph[i] >> j) & 1)) return false;
    return true;
}
unsigned allowed_cross(const Choice &x, const Choice &y) {
    ++pair_tests;
    int overlap = x.support & y.support;
    int dot = __builtin_popcount(unsigned(overlap)) -
              2 * __builtin_popcount(unsigned(overlap & (x.signs ^ y.signs)));
    const auto &a = attachments[x.attachment];
    const auto &b = attachments[y.attachment];
    int twice_t = 1 - common_axes(a.label, b.label) - dot;
    if (twice_t < 0 || twice_t > 4 || (twice_t & 1)) return 0;
    int t = twice_t / 2;
    U ai = min(x.attachment, y.attachment), bi = max(x.attachment, y.attachment);
    U cache_key = (ai * attachments.size() + bi) * 3 + t;
    auto previous = pair_cache.find(cache_key);
    if (previous != pair_cache.end()) return previous->second;
    unsigned out = 0;
    int z = signed_axes(a.label, b.label);
    for (int link = (t == 1 ? -1 : 0); link <= (t == 1 ? 1 : 0); link += 2) {
        __int128 cross = __int128(denominator) * (-4 * link - z);
        for (int i = 0; i < 12; ++i) cross -= __int128(b.f[i]) * a.projected_real[i];
        if (cross * cross > __int128(a.real_norm) * b.real_norm) continue;
        if (!capacity(a, b, t, link)) continue;
        int residual = -4 * link - z;
        for (int i = 0; i < local_rank; ++i) residual -= a.projected_column[i] * b.pivot_column[i];
        out |= 1u << mod(residual);
    }
    if (pair_cache.size() >= 1000000) pair_cache.clear();
    pair_cache[cache_key] = out;
    return out;
}
// Enumerate every coherent choice of links to the selected clique.
bool extensions(const Choice &candidate, const vector<Choice> &selected, const Matrix &gram,
                const function<bool(const Matrix&)> &accept) {
    vector<unsigned> edges;
    for (const auto &prior : selected) {
        unsigned options = allowed_cross(candidate, prior);
        if (!options) return false;
        edges.push_back(options);
    }
    int old_size = int(gram.size());
    Matrix next = gram;
    for (auto &row : next) row.push_back(0);
    next.emplace_back(old_size + 1, 0);
    const auto &a = attachments[candidate.attachment];
    for (int i = 0; i < anchors; ++i) next[i][old_size] = next[old_size][i] = a.h[i];
    next[old_size][old_size] = a.norm;
    function<bool(int)> assign = [&](int index) {
        if (index == int(edges.size())) {
            ++gram_tests;
            return fits(next, ambient_dim, determinant) && accept(next);
        }
        for (unsigned bits = edges[index]; bits; bits &= bits - 1) {
            int value = __builtin_ctz(bits), position = anchors + index;
            next[position][old_size] = next[old_size][position] = value;
            if (assign(index + 1)) return true;
        }
        return false;
    };
    return assign(0);
}
using Domain = vector<Choice>;
bool search(vector<Domain> domains, vector<Choice> &selected, const Matrix &gram) {
    ++nodes;
    maximum_depth = max(maximum_depth, int(selected.size()));
    if (domains.empty()) return true;
    size_t best = 0;
    for (size_t i = 1; i < domains.size(); ++i)
        if (domains[i].size() < domains[best].size()) best = i;
    swap(domains[0], domains[best]);
    for (const auto &choice : domains[0]) {
        bool found = extensions(choice, selected, gram, [&](const Matrix &new_gram) {
            selected.push_back(choice);
            vector<Domain> next;
            bool viable = true;
            for (size_t i = 1; i < domains.size() && viable; ++i) {
                Domain retained;
                for (const auto &other : domains[i])
                    if (extensions(other, selected, new_gram, [](const Matrix&) { return true; }))
                        retained.push_back(other);
                if (retained.empty()) viable = false;
                else next.push_back(move(retained));
            }
            bool answer = viable && search(move(next), selected, new_gram);
            selected.pop_back();
            return answer;
        });
        if (found) return true;
    }
    return false;
}
vector<vector<int>> plane_equations() {
    vector<vector<int>> out;
    if (anchors == 2 && square7(determinant)) return {vector<int>(2,0)};
    // Kernels of all normalized nonzero linear forms; smaller images included.
    int count = 1;
    for (int i = 0; i < anchors; ++i) count *= 7;
    for (int code = 1; code < count; ++code) {
        int temporary = code;
        vector<int> v(anchors);
        for (int i = 0; i < anchors; ++i) { v[i] = temporary % 7; temporary /= 7; }
        auto first = find_if(v.begin(), v.end(), [](int x) { return x != 0; });
        if (*first == 1) out.push_back(v);
    }
    return out;
}
bool in_plane(const Attachment &a, const vector<int> &normal) {
    int sum = 0;
    for (int i = 0; i < anchors; ++i) sum += a.h[i] * normal[i];
    return sum % 7 == 0;
}
void read_setup(const string &name) {
    ifstream f(name);
    string magic;
    f >> magic >> local_rank >> determinant >> denominator;
    if (magic != "LOWGRAM1" || (local_rank != 8 && local_rank != 9) || determinant == 0 || denominator <= 0)
        throw runtime_error("Invalid setup header");
    ambient_dim = 13 - local_rank; anchors = 11 - local_rank;
    int index = 0, label = 0;
    for (int j = 0; j < 6; ++j) for (int k = j + 1; k < 6; ++k) {
        pair_index[j][k] = index;
        for (int &value : outer_words[index]) f >> value;
        ++index;
        for (int t = 0; t < 2; ++t) labels[label++] = {j,k,t};
    }
    int count;
    f >> count;
    if (!f || count <= 0) throw runtime_error("Missing attachments");
    for (int i = 0; i < count; ++i) {
        Attachment a{};
        f >> a.label >> a.positive >> a.negative >> a.norm >> a.real_norm;
        a.h.resize(anchors);
        for (int &value : a.h) f >> value;
        for (int &value : a.key) f >> value;
        for (int k = 0; k < local_rank; ++k) f >> a.pivot_column[k];
        for (int k = 0; k < local_rank; ++k) f >> a.projected_column[k];
        for (I &value : a.f) f >> value;
        for (I &value : a.projected_real) f >> value;
        if (!f || a.label < 0 || a.label >= 30 || a.norm < 0 || a.norm >= 7 || a.real_norm < 0)
            throw runtime_error("Malformed attachment");
        by_label[a.label].push_back(i);
        attachments.push_back(a);
    }
    for (U &value : base) f >> value;
    if (!f) throw runtime_error("Incomplete base");
    string extra;
    if (f >> extra) throw runtime_error("Trailing setup fields");
}
int main(int argc, char **argv) {
    try {
        if (argc == 2 && string(argv[1]) == "--gram-batch") {
            int size, dim, type;
            while (cin >> size >> dim >> type) {
                Matrix gram(size, vector<int>(size));
                for (auto &row : gram) for (int &x : row) { cin >> x; x = mod(x); }
                if (!cin) throw runtime_error("Incomplete matrix");
                auto value = invariant(gram);
                cout << value.rank << " " << value.det << " " << fits(gram,dim,type) << "\n";
            }
            return 0;
        }
        if (argc != 4) throw runtime_error("Usage: residual_gram_v1 SETUP STARS EXPECTED_STARS");
        read_setup(argv[1]);
        int expected = stoi(argv[3]), stars = 0, opened = 0, closed = 0, dead = 0;
        if (expected <= 0) throw runtime_error("Invalid expected star count");
        uint64_t viable_planes = 0, closed_planes = 0;
        auto planes = plane_equations();
        if (planes.size() != (local_rank == 8 ? 57u : (square7(determinant) ? 1u : 8u)))
            throw runtime_error("Plane coverage mismatch");
        ifstream sf(argv[2]);
        array<int,24> words;
        while (sf >> words[0]) {
            for (int i = 1; i < 24; ++i) sf >> words[i];
            if (!sf) throw runtime_error("Incomplete star");
            ++stars;
            vector<Domain> all;
            bool empty = false;
            for (int y = 0; y < 30; ++y) {
                Domain domain;
                auto edge = labels[y];
                for (int support : outer_words[pair_index[edge[0]][edge[1]]]) {
                    for (int signs = support;; signs = (signs - 1) & support) {
                        array<int,12> key{};
                        bool valid = true;
                        for (int i = 0; i < 12; ++i) {
                            int overlap = support & words[2*i];
                            int dot = __builtin_popcount(unsigned(overlap)) -
                                      2 * __builtin_popcount(unsigned(overlap & (signs ^ words[2*i+1])));
                            int twice = 1 - int(i/2 == edge[0] || i/2 == edge[1]) - dot;
                            if (twice < 0 || twice > 4 || (twice & 1)) { valid = false; break; }
                            key[i] = twice/2;
                        }
                        if (valid) for (int index : by_label[y])
                            if (attachments[index].key == key) domain.push_back({index,support,signs});
                        if (signs == 0) break;
                    }
                }
                if (domain.empty()) empty = true;
                all.push_back(move(domain));
            }
            bool open = false;
            if (!empty) for (const auto &normal : planes) {
                vector<Domain> domains;
                bool valid = true;
                for (const auto &domain : all) {
                    Domain retained;
                    for (const auto &candidate : domain)
                        if (in_plane(attachments[candidate.attachment],normal)) retained.push_back(candidate);
                    if (retained.empty()) { valid = false; break; }
                    domains.push_back(move(retained));
                }
                if (!valid) continue;
                ++viable_planes;
                Matrix gram(anchors, vector<int>(anchors,0));
                vector<Choice> selected;
                if (search(move(domains), selected, gram)) open = true;
                else ++closed_planes;
            }
            if (empty) ++dead;
            if (open) { ++opened; cout << "OPEN star " << stars-1 << "\n"; }
            else ++closed;
            cout << "PROGRESS stars " << stars << " open " << opened << " closed " << closed
                 << " viable_planes " << viable_planes << " nodes " << nodes
                 << " maximum_depth " << maximum_depth << endl;
        }
        if (!sf.eof() || stars != expected) throw runtime_error("Star coverage mismatch");
        cout << "FINAL stars " << stars << " open " << opened << " closed " << closed
             << " viable_planes " << viable_planes << " closed_planes " << closed_planes
             << " empty_domains " << dead << " nodes " << nodes << " pair_tests " << pair_tests
             << " gram_tests " << gram_tests << " literal_tests " << literal_tests
             << " maximum_depth " << maximum_depth << " full_depth 30" << endl;
        return opened ? 3 : 0;
    } catch (const exception &e) { cerr << "ERROR_NOT_EXCLUSION " << e.what() << endl; return 2; }
}
