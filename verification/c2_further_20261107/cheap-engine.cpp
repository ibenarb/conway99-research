// Whole-row search. Output is a replay tree, not a trusted UNSAT assertion.
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
#include <sstream>
#include <set>
#include <filesystem>
#include <utility>
using U=uint64_t;
struct State { std::vector<std::vector<int>> domains; unsigned remaining; U once,twice; };
State frames[13];
std::vector<int> sym;
uint64_t symmask(uint64_t v) {
    uint64_t out=0;
    while(v){int c=__builtin_ctzll(v);v&=v-1;out|=uint64_t(1)<<sym[c];}
    return out;
}
bool canonical_pair(uint64_t a,uint64_t b) {
    uint64_t x=symmask(a),y=symmask(b);
    return a<b && (a<x || (a==x && b<=y)) && (a<y || (a==y && b<=x));
}
int n,columns;
std::vector<int> permutation;
std::vector<std::vector<int>> gram,twist;
std::vector<std::vector<U>> values,paired;
std::vector<U> assignment,witness;
std::ofstream proof;
uint64_t nodes=0;
double limit;
std::chrono::steady_clock::time_point started;
U transform(U value) {
    U result=0;
    while(value) { int c=__builtin_ctzll(value);value&=value-1;result|=U(1)<<permutation[c]; }
    return result;
}
bool allowed(int row,int candidate,int other,U mask,U saturated) {
    U value=values[row][candidate];
    if((value&saturated) || __builtin_popcountll(value&mask)!=gram[row][other]
        || __builtin_popcountll(paired[row][candidate]&mask)!=twist[row][other]) return false;
    if(row==2 && value>symmask(value)) return false;
    if(row==2 && other==3 && !canonical_pair(value,mask)) return false;
    if(row==3 && other==2 && !canonical_pair(mask,value)) return false;
    return true;
}
int visit(const State& state) {
    ++nodes;
    if((nodes&1023)==1 && std::chrono::duration<double>(std::chrono::steady_clock::now()-started).count()>limit) return -1;
    if(!state.remaining) {
        U all=columns==64 ? ~U(0) : (U(1)<<columns)-1;
        if(state.twice!=all) throw std::runtime_error("Full assignment violates column sums");
        witness=assignment;return 1;
    }
    int row=-1;
    for(int r=0;r<n;++r) if((state.remaining>>r)&1)
        if(row<0 || state.domains[r].size()<state.domains[row].size()) row=r;
    if(state.domains[row].empty()) {proof.put(static_cast<char>(row));return 0;}
    proof.put(static_cast<char>(n+row));
    for(int chosen:state.domains[row]) {
        U mask=values[row][chosen];
        State& child=frames[__builtin_popcount(state.remaining)];
        child.remaining=state.remaining&~(1u<<row);
        child.once=state.once|mask;
        child.twice=state.twice|(state.once&mask);
        child.domains.resize(n);
        int empty=-1;
        for(int r=0;r<n;++r) if((child.remaining>>r)&1) {
            auto& result=child.domains[r];
            result.clear();
            result.reserve(state.domains[r].size());
            for(int index:state.domains[r]) if(allowed(r,index,row,mask,child.twice)) result.push_back(index);
            if(result.empty()) {empty=r;break;}
        }
        assignment[row]=mask;
        if(empty>=0) proof.put(static_cast<char>(empty));
        else {int result=visit(child); if(result) return result;}
    }
    return 0;
}
int main(int argc,char** argv) {
    try {
        if(argc!=6) throw std::runtime_error("Usage: batch-engine input comma-separated-indices new-output-directory seconds-per-task action-file");
        std::ifstream input(argv[1]);
        if(!(input>>n>>columns)||n<2||n>12||columns<1||columns>60) throw std::runtime_error("Invalid dimensions");
        permutation.resize(columns);for(int& p:permutation)input>>p;
        gram.assign(n,std::vector<int>(n));twist=gram;
        for(auto& row:gram)for(int& x:row)input>>x;
        for(auto& row:twist)for(int& x:row)input>>x;
        values.resize(n);paired.resize(n);
        for(int r=0;r<n;++r){int count;input>>count;values[r].resize(count);for(U& mask:values[r])input>>mask;for(U mask:values[r])paired[r].push_back(transform(mask));}
        std::ifstream action(argv[5]);sym.resize(columns);
        for(int& c:sym)if(!(action>>c))throw std::runtime_error("Missing action");
        for(int c=0;c<columns;++c)if(sym[c]<0||sym[c]>=columns)throw std::runtime_error("Invalid action");
        for(int c=0;c<columns;++c)if(sym[sym[c]]!=c || sym[permutation[c]]!=permutation[sym[c]])throw std::runtime_error("Action not commuting involution");
        for(int r=0;r<n;++r){
            bool duplicate=false;for(int j=0;j<r;++j)if(values[j]==values[r]){duplicate=true;break;}
            if(!duplicate)for(U x:values[r])if(!std::binary_search(values[r].begin(),values[r].end(),symmask(x)))throw std::runtime_error("Action changes domain");
        }
        if(n<4 || values[2]!=values[3] || gram[2][2]<=gram[2][3]) throw std::runtime_error("Unproved swap contract");
        for(int r=0;r<n;++r) for(int t=0;t<n;++t) {
            int rr=r==2?3:r==3?2:r,tt=t==2?3:t==3?2:t;
            if(gram[r][t]!=gram[rr][tt] || twist[r][t]!=twist[rr][tt]) throw std::runtime_error("Swap changes targets");
        }
        int count=0; input>>count;if(!input || count<=0)throw std::runtime_error("Invalid boundary count");
        std::vector<std::pair<U,U>> boundaries(count);
        for(auto& pair:boundaries) input>>pair.first>>pair.second;
        if(!input) throw std::runtime_error("Incomplete input");
        std::vector<int> tasks; std::stringstream taskstream(argv[2]); std::string token;
        std::set<int> unique;
        while(std::getline(taskstream,token,',')) {
            size_t end=0;int i=std::stoi(token,&end);
            if(end!=token.size() || i<0 || i>=count || !unique.insert(i).second) throw std::runtime_error("Invalid or duplicate task");
            tasks.push_back(i);
        }
        if(tasks.empty() || std::string(argv[2]).back()==',') throw std::runtime_error("Empty task");
        for(int i:tasks) {
            std::string stem=std::string(argv[3])+"/boundary_"+std::to_string(i);
            if(std::filesystem::exists(stem+".proof") || std::filesystem::exists(stem+".json")) throw std::runtime_error("Existing output");
        }
        std::vector<std::vector<int>> cache(n); U cached_a=0; bool have_cache=false;
        for(int index:tasks) {
        if(index<0||index>=count)throw std::runtime_error("Invalid boundary index");
        U a=boundaries[index].first,b=boundaries[index].second;
        nodes=0; witness.clear(); proof.clear();
        if(symmask(a)!=a || symmask(b)!=b)throw std::runtime_error("Action changes boundary");
        if(!have_cache || a!=cached_a) {
            for(int r=2;r<n;++r) {
                cache[r].clear();
                for(int i=0;i<int(values[r].size());++i)
                    if(allowed(r,i,0,a,0)) cache[r].push_back(i);
            }
            cached_a=a;have_cache=true;
        }
        if(__builtin_popcountll(a&b)!=gram[0][1]||__builtin_popcountll(a&transform(b))!=twist[0][1]) throw std::runtime_error("Invalid boundary");
        State initial;initial.remaining=((1u<<n)-1)&~3u;initial.once=a|b;initial.twice=a&b;initial.domains.resize(n);
        for(int r=2;r<n;++r)for(int i:cache[r])
            if(allowed(r,i,1,b,initial.twice))initial.domains[r].push_back(i);
        assignment.assign(n,0);assignment[0]=a;assignment[1]=b;
        std::string stem=std::string(argv[3])+"/boundary_"+std::to_string(index);
        proof.open(stem+".proof",std::ios::binary);if(!proof) throw std::runtime_error("Proof open failed");proof.write("C2S2",4);
        for(int j=0;j<4;++j)proof.put(static_cast<char>((index>>(8*j))&255));
        limit=std::stod(argv[4]);started=std::chrono::steady_clock::now();
        int result=visit(initial);proof.close();
        if(!proof)throw std::runtime_error("Proof write failed");
        double elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-started).count();
        std::ofstream report(stem+".json");report<<"{\"boundary\":"<<index<<",\"status\":\""<<(result==0?"UNSAT_CANDIDATE":result==1?"SAT_CANDIDATE":"UNKNOWN")<<"\",\"nodes\":"<<nodes<<",\"seconds\":"<<elapsed;
        if(result==1){report<<",\"rows\":[";for(int r=0;r<n;++r){if(r)report<<",";report<<witness[r];}report<<"]";}
        report<<"}\n";report.close();if(!report) throw std::runtime_error("Report write failed");
        std::cout<<(result==0?"s UNSATISFIABLE":result==1?"s SATISFIABLE":"s UNKNOWN")<<"\nc nodes "<<nodes<<" seconds "<<elapsed<<"\n";
        if(result!=0) return result==1?10:0;
        }
        return 20;
    }catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 1;}
}
