// Independent replay checker: the proof chooses rows; all their admissible values must be covered.
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using Word=uint64_t;
int rows,cols;
std::vector<int> flip;
std::vector<std::vector<int>> ordinary,twisted;
std::vector<std::vector<Word>> domain,mirror;
std::vector<Word> chosen;
std::ifstream evidence;
std::vector<std::vector<int>> frames[13];
uint64_t visited=0;
Word permute(Word value){Word answer=0;for(int c=0;c<cols;++c)if((value>>c)&1)answer|=Word(1)<<flip[c];return answer;}
void require(bool condition,const char* message){if(!condition)throw std::runtime_error(message);}
void check(std::vector<std::vector<int>>& remaining,unsigned used){
    int code=evidence.get();require(code!=EOF,"Incomplete proof");++visited;
    if(code<rows){require(!(used&(1u<<code)),"Leaf refers to assigned row");require(remaining[code].empty(),"False empty-domain leaf");return;}
    int r=code-rows;require(r>=0&&r<rows&&!(used&(1u<<r)),"Invalid branch row");
    require(!remaining[r].empty(),"Empty branch must be a leaf");
    for(int value:remaining[r]){
        chosen[r]=domain[r][value];
        unsigned after=used|(1u<<r);
        Word occupied=0,forbidden=0;
        for(int u=0;u<rows;++u)if(after&(1u<<u)){
            require(!(forbidden&chosen[u]),"Third incidence in a column");
            forbidden|=occupied&chosen[u];occupied|=chosen[u];
        }
        int next_code=evidence.peek();
        require(next_code!=EOF,"Incomplete proof");
        // A claimed empty-domain leaf needs only that domain reconstructed.
        // Its emptiness is still checked independently by check().
        bool leaf=next_code<rows;
        auto& next=frames[__builtin_popcount(after)];
        next.resize(rows);
        for(auto& d:next)d.clear();
        for(int u=0;u<rows;++u)if(!(after&(1u<<u)) && (!leaf || u==next_code)){
            for(int candidate:remaining[u]){
                Word x=domain[u][candidate];
                if(u==2 && r==3 && !(x<chosen[r]))continue;
                if(u==3 && r==2 && !(x>chosen[r]))continue;
                if(x&forbidden)continue;
                if(__builtin_popcountll(x&chosen[r])!=ordinary[u][r])continue;
                if(__builtin_popcountll(mirror[u][candidate]&chosen[r])!=twisted[u][r])continue;
                next[u].push_back(candidate);
            }
        }
        check(next,after);
    }
}
int main(int argc,char**argv){
    try{
        require(argc==4,"Usage: row-verify input boundary-index proof");
        std::ifstream model(argv[1]);model>>rows>>cols;
        require(rows>=2&&rows<=12&&cols>=1&&cols<=60,"Invalid dimensions");
        flip.resize(cols);for(int& x:flip)model>>x;
        for(int c=0;c<cols;++c)require(flip[c]>=0&&flip[c]<cols&&flip[flip[c]]==c,"Invalid involution");
        ordinary.assign(rows,std::vector<int>(rows));twisted=ordinary;
        for(auto& r:ordinary)for(int& x:r)model>>x;
        for(auto& r:twisted)for(int& x:r)model>>x;
        for(int r=0;r<rows;++r)for(int s=0;s<rows;++s)require(ordinary[r][s]==ordinary[s][r]&&twisted[r][s]==twisted[s][r],"Nonsymmetric targets");
        domain.resize(rows);mirror.resize(rows);
        for(int r=0;r<rows;++r){
            int count;model>>count;require(count>=0,"Invalid domain size");domain[r].resize(count);
            for(Word& x:domain[r]){
                model>>x;require((x>>cols)==0,"Out-of-range column");
                require(__builtin_popcountll(x)==ordinary[r][r],"Invalid row cardinality");
                Word px=permute(x);require(__builtin_popcountll(x&px)==twisted[r][r],"Invalid diagonal twist");mirror[r].push_back(px);
            }
            require(std::is_sorted(domain[r].begin(),domain[r].end()),"Unsorted domain");
            require(std::adjacent_find(domain[r].begin(),domain[r].end())==domain[r].end(),"Duplicate row state");
        }
        require(rows>=4,"Swap requires four rows");
        require(domain[2]==domain[3],"Different swap domains");
        require(ordinary[2][2]>ordinary[2][3],"Identical rows not excluded");
        std::vector<int> swap(rows);for(int i=0;i<rows;++i)swap[i]=i;
        swap[2]=3;swap[3]=2;
        for(int i=0;i<rows;++i)for(int j=0;j<rows;++j){
            require(ordinary[i][j]==ordinary[swap[i]][swap[j]],"Swap changes Gram");
            require(twisted[i][j]==twisted[swap[i]][swap[j]],"Swap changes twist");
        }
        int boundary_count,which=std::stoi(argv[2]);model>>boundary_count;require(which>=0&&which<boundary_count,"Invalid boundary");
        chosen.assign(rows,0);for(int i=0;i<=which;++i)model>>chosen[0]>>chosen[1];require(bool(model),"Incomplete model");
        for(int r=0;r<2;++r)require(std::binary_search(domain[r].begin(),domain[r].end(),chosen[r]),"Boundary outside domain");
        require(__builtin_popcountll(chosen[0]&chosen[1])==ordinary[0][1],"Invalid boundary Gram");
        require(__builtin_popcountll(chosen[0]&permute(chosen[1]))==twisted[0][1],"Invalid boundary twist");
        std::vector<std::vector<int>> available(rows);
        Word forbidden=chosen[0]&chosen[1];
        for(int r=2;r<rows;++r)for(int candidate=0;candidate<int(domain[r].size());++candidate){
            Word x=domain[r][candidate];bool valid=!(x&forbidden);
            for(int a=0;a<2;++a)valid=valid&&__builtin_popcountll(x&chosen[a])==ordinary[r][a]&&__builtin_popcountll(mirror[r][candidate]&chosen[a])==twisted[r][a];
            if(valid)available[r].push_back(candidate);
        }
        evidence.open(argv[3],std::ios::binary);char header[4];evidence.read(header,4);require(std::string(header,4)=="C2S1","Wrong proof format");
        unsigned encoded=0;for(int i=0;i<4;++i){int b=evidence.get();require(b!=EOF,"Missing index");encoded|=unsigned(b)<<(8*i);}require(encoded==unsigned(which),"Boundary/proof mismatch");
        check(available,3u);require(evidence.get()==EOF,"Trailing proof data");
        std::cout<<"s VERIFIED BOUNDARY UNSAT\nc proof_nodes "<<visited<<"\n";return 0;
    }catch(const std::exception& e){std::cerr<<"REJECTED: "<<e.what()<<"\n";return 1;}
}
