#include <fcntl.h>
#include <unistd.h>
#include <cerrno>
// Independent replay checker: the proof chooses rows; all their admissible values must be covered.
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
#include <sstream>
#include <set>
using Word=uint64_t;
std::vector<int> sym;
uint64_t symmask(uint64_t v) {
    uint64_t out=0;
    for(size_t c=0;c<sym.size();++c)if((v>>c)&1)out|=uint64_t(1)<<sym[c];
    return out;
}
bool canonical_pair(uint64_t a,uint64_t b) {
    uint64_t x=symmask(a),y=symmask(b);
    std::pair<uint64_t,uint64_t> original(a,b);
    return a!=b && original==std::min({original,std::make_pair(b,a),std::make_pair(x,y),std::make_pair(y,x)});
}
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
                if(u==2 && x>symmask(x))continue;
                if(u==2 && r==3 && !canonical_pair(x,chosen[r]))continue;
                if(u==3 && r==2 && !canonical_pair(chosen[r],x))continue;
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
        require(argc==5,"Usage: batch-verify input comma-indices directory action");
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
        std::ifstream action(argv[4]);sym.resize(cols);
        for(int& c:sym)require(bool(action>>c),"Missing action");
        for(int c=0;c<cols;++c)require(sym[c]>=0&&sym[c]<cols,"Invalid action");
        for(int c=0;c<cols;++c)require(sym[sym[c]]==c && sym[flip[c]]==flip[sym[c]],"Not commuting involution");
        for(int r=0;r<rows;++r){
            bool duplicate=false;for(int j=0;j<r;++j)if(domain[j]==domain[r]){duplicate=true;break;}
            if(!duplicate)for(Word x:domain[r])require(std::binary_search(domain[r].begin(),domain[r].end(),symmask(x)),"Action changes domain");
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
        int boundary_count;model>>boundary_count;require(boundary_count>0,"Invalid boundary count");
        std::vector<std::pair<Word,Word>> boundaries(boundary_count);
        for(auto& pair:boundaries)model>>pair.first>>pair.second;
        require(bool(model),"Incomplete model");
        std::vector<int> tasks;std::set<int> unique;std::stringstream stream(argv[2]);std::string token;
        while(std::getline(stream,token,',')){
            size_t end=0;int i=std::stoi(token,&end);
            require(end==token.size()&&i>=0&&i<boundary_count&&unique.insert(i).second,"Invalid task");tasks.push_back(i);
        }
        require(!tasks.empty()&&std::string(argv[2]).back()!=',',"Empty task");
        std::vector<std::vector<int>> prefix(rows);Word prefix_a=0;bool have_prefix=false;
        for(int which:tasks){
        visited=0;evidence.close();evidence.clear();
        chosen.assign(rows,0);chosen[0]=boundaries[which].first;chosen[1]=boundaries[which].second;
        for(int r=0;r<2;++r)require(std::binary_search(domain[r].begin(),domain[r].end(),chosen[r]),"Boundary outside domain");
        require(__builtin_popcountll(chosen[0]&chosen[1])==ordinary[0][1],"Invalid boundary Gram");
        require(__builtin_popcountll(chosen[0]&permute(chosen[1]))==twisted[0][1],"Invalid boundary twist");
        require(symmask(chosen[0])==chosen[0] && symmask(chosen[1])==chosen[1],"Action changes boundary");
        if(!have_prefix || prefix_a!=chosen[0]){
            for(int r=2;r<rows;++r){
                prefix[r].clear();
                for(int candidate=0;candidate<int(domain[r].size());++candidate){
                    Word x=domain[r][candidate];
                    if((r!=2 || x<=symmask(x)) && __builtin_popcountll(x&chosen[0])==ordinary[r][0] && __builtin_popcountll(mirror[r][candidate]&chosen[0])==twisted[r][0])prefix[r].push_back(candidate);
                }
            }
            prefix_a=chosen[0];have_prefix=true;
        }
        std::vector<std::vector<int>> available(rows);
        Word forbidden=chosen[0]&chosen[1];
        for(int r=2;r<rows;++r)for(int candidate:prefix[r]){
            Word x=domain[r][candidate];
            if(!(x&forbidden) && __builtin_popcountll(x&chosen[1])==ordinary[r][1] && __builtin_popcountll(mirror[r][candidate]&chosen[1])==twisted[r][1])available[r].push_back(candidate);
        }
        evidence.open(std::string(argv[3])+"/boundary_"+std::to_string(which)+".proof",std::ios::binary);char header[4]={};evidence.read(header,4);require(evidence.gcount()==4 && bool(evidence),"Missing or incomplete proof header");require(std::string(header,4)=="C2S2","Wrong proof format");
        unsigned encoded=0;for(int i=0;i<4;++i){int b=evidence.get();require(b!=EOF,"Missing index");encoded|=unsigned(b)<<(8*i);}require(encoded==unsigned(which),"Boundary/proof mismatch");
        check(available,3u);require(evidence.get()==EOF,"Trailing proof data");
        // A native decision for this exact index, only after complete EOF replay.
        std::string receipt=std::string(argv[3])+"/boundary_"+std::to_string(which)+".verified.json";
        std::string temporary=receipt+".pending";
        std::string decision="{\"boundary\":"+std::to_string(which)+",\"status\":\"VERIFIED_BOUNDARY_UNSAT\",\"format\":\"C2S2\"}\n";
        int fd=::open(temporary.c_str(),O_WRONLY|O_CREAT|O_EXCL,0600);
        require(fd>=0,"Receipt open failed");
        ssize_t sent=::write(fd,decision.data(),decision.size());
        bool written=sent==static_cast<ssize_t>(decision.size()) && ::fsync(fd)==0;
        int closed=::close(fd);
        require(written && closed==0,"Receipt write failed");
        require(::link(temporary.c_str(),receipt.c_str())==0,"Receipt publication failed");
        require(::unlink(temporary.c_str())==0,"Receipt cleanup failed");
        int directory=::open(argv[3],O_RDONLY|O_DIRECTORY);
        require(directory>=0,"Receipt directory open failed");
        bool synced=::fsync(directory)==0;
        int dirclosed=::close(directory);
        require(synced && dirclosed==0,"Receipt directory sync failed");
        std::cout<<"s VERIFIED BOUNDARY UNSAT\nc proof_nodes "<<visited<<" boundary "<<which<<"\n";
        }
        return 0;
    }catch(const std::exception& e){std::cerr<<"REJECTED: "<<e.what()<<"\n";return 1;}
}
