#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <sstream>
#include <string>
#include <vector>
using U = std::uint64_t;
struct Pattern {
    int n;
    int req[7][7]{};
    int po[7]{}, pi[7]{}, no[7]{}, ni[7]{};
    std::vector<int> order;
    Pattern(int size, U pos, U neg): n(size) {
        if (pos & neg) throw std::runtime_error("contradictory pattern");
        int bit = 0;
        for (int a=0; a<n; ++a) for(int b=0; b<n; ++b) if(a!=b) {
            req[a][b] = (pos>>bit & 1) ? 1 : ((neg>>bit & 1) ? -1 : 0);
            if(req[a][b]==1) { ++po[a]; ++pi[b]; }
            if(req[a][b]==-1) { ++no[a]; ++ni[b]; }
            ++bit;
        }
        if ((pos|neg)>>bit) throw std::runtime_error("excess bits");
        for(int a=0;a<n;++a) if(po[a]+pi[a]+no[a]+ni[a]) order.push_back(a);
        std::sort(order.begin(),order.end(),[&](int a,int b) {
            return po[a]+pi[a]+no[a]+ni[a] > po[b]+pi[b]+no[b]+ni[b];
        });
    }
    bool matches(U code) const {
        int graph[7][7]{}, od[7]{}, id[7]{}, bit=0;
        for(int a=0;a<n;++a) for(int b=0;b<n;++b) if(a!=b) {
            graph[a][b]=int(code>>bit++ & 1); od[a]+=graph[a][b]; id[b]+=graph[a][b];
        }
        int mapped[7]; std::fill(mapped,mapped+7,-1);
        return search(0,0,mapped,graph,od,id);
    }
    bool search(unsigned depth, unsigned used, int *mapped, const int graph[7][7], const int *od, const int *id) const {
        if(depth==order.size()) return true;
        int a=order[depth];
        for(int v=0;v<n;++v) if(!(used>>v&1)) {
            if(od[v]<po[a] || id[v]<pi[a] || n-1-od[v]<no[a] || n-1-id[v]<ni[a]) continue;
            bool ok=true;
            for(unsigned j=0;j<depth && ok;++j) {
                int b=order[j], w=mapped[b];
                if(req[a][b] && graph[v][w]!=(req[a][b]==1)) ok=false;
                if(req[b][a] && graph[w][v]!=(req[b][a]==1)) ok=false;
            }
            if(ok) { mapped[a]=v; if(search(depth+1,used|(1u<<v),mapped,graph,od,id)) return true; mapped[a]=-1; }
        }
        return false;
    }
};
int main(int argc,char **argv) {
    try {
        if(argc!=5) throw std::runtime_error("usage: coverage N patterns.txt reps.tsv uncovered.tsv");
        int n=std::stoi(argv[1]); if(n<2||n>7) throw std::runtime_error("invalid N");
        std::ifstream patterns(argv[2]), reps(argv[3]); std::ofstream uncovered(argv[4]);
        if(!patterns||!reps||!uncovered) throw std::runtime_error("file open failed");
        std::vector<Pattern> ps; U pos,neg;
        while(patterns>>pos>>neg) ps.emplace_back(n,pos,neg);
        if(!patterns.eof()) throw std::runtime_error("invalid pattern input");
        std::vector<U> hits(ps.size(),0); U total=0,covered=0,code,aut,mu;
        std::string line;
        bool first=true;
        while(std::getline(reps,line)) {
            if(first && line=="code\taut\tmutual_edges\tdegrees\tstratum") {
                uncovered<<line<<'\n'; first=false; continue;
            }
            first=false;
            std::istringstream record(line);
            if(!(record>>code>>aut>>mu)) throw std::runtime_error("invalid representative record");
            bool any=false;
            for(unsigned i=0;i<ps.size();++i) if(ps[i].matches(code)) {++hits[i]; any=true;}
            ++total; if(any) ++covered; else uncovered<<line<<'\n';
        }
        if(!reps.eof()||!uncovered) throw std::runtime_error("input/output error");
        uncovered.close(); if(!uncovered) throw std::runtime_error("output close error");
        std::cout<<"{\"total\":"<<total<<",\"covered\":"<<covered<<",\"remaining\":"<<total-covered<<",\"hits\":[";
        for(unsigned i=0;i<hits.size();++i) {if(i) std::cout<<',';std::cout<<hits[i];}
        std::cout<<"]}\n";
        return 0;
    } catch(const std::exception &e) { std::cerr<<e.what()<<'\n'; return 1; }
}
