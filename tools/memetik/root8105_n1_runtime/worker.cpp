#include "cadical.hpp"
#include <atomic>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <fcntl.h>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <thread>
#include <unistd.h>

static void durable(const std::string &path, const std::string &text) {
    std::string tmp = path + ".tmp";
    FILE *f = fopen(tmp.c_str(), "wx");
    if (!f) throw std::runtime_error("open output");
    bool bad = fwrite(text.data(), 1, text.size(), f) != text.size();
    bad = fflush(f) || bad;
    bad = fsync(fileno(f)) || bad;
    bad = fclose(f) || bad;
    if (bad || rename(tmp.c_str(), path.c_str())) throw std::runtime_error("save");
    int d = open(".", O_RDONLY | O_DIRECTORY);
    if (d < 0 || fsync(d)) throw std::runtime_error("directory sync");
    close(d);
}

int main(int argc, char **argv) {
    if (argc != 2) return 2;
    try {
        CaDiCaL::Solver solver;
        solver.set("quiet", 1);
        solver.set("binary", 1);
        solver.set("lrat", 0);
        solver.set("frat", 0);
        solver.set("veripb", 0);
        FILE *proof = fopen("proof.partial", "wx");
        if (!proof) throw std::runtime_error("proof open");
        if (setvbuf(proof, nullptr, _IONBF, 0) ||
            !solver.trace_proof(proof, "proof.partial")) {
            throw std::runtime_error("proof setup");
        }
        std::atomic<bool> stop(false), done(false);
        // Only terminate() is called from this thread, as allowed by the API.
        std::thread control([&]() {
            while (!done.load()) {
                if (access("STOP", F_OK) == 0) {
                    stop.store(true);
                    solver.terminate();
                }
                std::this_thread::sleep_for(std::chrono::milliseconds(20));
            }
        });
        int result = 0;
        int vars = 0;
        long expected = -1, clauses = 0;
        bool ended = true, header = false;
        std::string error;
        try {
            std::ifstream input(argv[1]);
            if (!input) throw std::runtime_error("input open");
            std::string line;
            while (!stop.load() && std::getline(input, line)) {
                std::istringstream row(line);
                std::string first;
                if (!(row >> first) || first == "c") continue;
                if (first == "p") {
                    std::string kind, extra;
                    if (header || !(row >> kind >> vars >> expected) ||
                        kind != "cnf" || vars < 0 || expected < 0 ||
                        (row >> extra)) throw std::runtime_error("header");
                    solver.reserve(vars);
                    header = true;
                    continue;
                }
                if (!header) throw std::runtime_error("missing header");
                row.clear();
                row.str(line);
                std::string token;
                while (!stop.load() && row >> token) {
                    size_t used = 0;
                    long value = std::stol(token, &used);
                    if (used != token.size() || value < -long(vars) ||
                        value > long(vars)) throw std::runtime_error("literal");
                    solver.add(static_cast<int>(value));
                    ended = value == 0;
                    if (ended) ++clauses;
                }
            }
            if (!stop.load()) {
                if (!header || !ended || clauses != expected || input.bad())
                    throw std::runtime_error("incomplete input");
                result = solver.solve();
            }
            if (result == 10) {
                std::ostringstream model;
                for (int v = 1; v <= vars; ++v) {
                    int value = solver.val(v);
                    model << (value < 0 ? -v : v) << " ";
                }
                model << "0\n";
                durable("model.txt", model.str());
            }
        } catch (const std::exception &e) {
            error = e.what();
        }
        done.store(true);
        control.join();
        solver.close_proof_trace();
        bool bad = ferror(proof) || fflush(proof);
        bad = fsync(fileno(proof)) || bad;
        bad = fclose(proof) || bad;
        if (bad) throw std::runtime_error("proof write/sync");
        if (!error.empty()) throw std::runtime_error(error);
        durable("worker.json", "{\"result\":" + std::to_string(result) +
            ",\"stop_seen\":" + (stop.load() ? "true" : "false") +
            ",\"solver_version\":\"" + solver.version() + "\"}\n");
        return result;
    } catch (const std::exception &e) {
        std::cerr << "worker error: " << e.what() << "\n";
        return 2;
    }
}
