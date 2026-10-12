// Reuse the newly audited row recursion, not the historical Profile46 enumerator.
#define main profile346_unused_main
#include "../c2_completeness_20261012/count_labelled.cpp"
#undef main

int main() {
    Counter counter(7);
    std::uint64_t total = 0;
    for (unsigned six = 0; six <= 7; ++six) {
        for (unsigned i = 0; i < 7; ++i) counter.degrees[i] = i < six ? 6 : 4;
        std::uint64_t sorted_count = counter.visit(0);
        unsigned multiplier = factorial(7) / factorial(six) / factorial(7 - six);
        std::uint64_t labelled = sorted_count * multiplier;
        total += labelled;
        std::cout << "PROFILE46\t" << six << '\t' << sorted_count << '\t' << multiplier << '\t' << labelled << std::endl;
    }
    std::cout << "TOTAL46\t" << total << std::endl;
    return 0;
}
