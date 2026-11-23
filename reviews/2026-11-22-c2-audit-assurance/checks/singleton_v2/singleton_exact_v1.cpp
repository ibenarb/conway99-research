// Independent singleton-root search, derived from SingletonSearch.md and RootsBridge.md.
// Input attachments come from the referee's separately written literal local model.
// No original search header is included. All nontrivial Gram arithmetic is GMP rational.
#include <gmpxx.h>
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <string>
#include <vector>

using Q = mpq_class;
using Z = mpz_class;
using Vec = std::vector<Q>;
using Mat = std::vector<Vec>;
using Graph = std::vector<uint64_t>;
using Links = std::vector<std::vector<int>>;
using Key = std::array<int,18>;

int mod7(int x) { x %= 7; return x < 0 ? x+7 : x; }
int inverse7(int x) {
    for (int y=1; y<7; ++y) if (mod7(x*y)==1) return y;
    throw std::runtime_error("No inverse in F7");
}
int rank7(std::vector<std::vector<int>> a) {
    int r=0, rows=a.size(), cols=rows ? a[0].size() : 0;
    for (auto &row:a) for (auto &v:row) v=mod7(v);
    for (int c=0;c<cols && r<rows;++c) {
        int p=r; while(p<rows && !a[p][c]) ++p;
        if (p==rows) continue;
        std::swap(a[r],a[p]); int iv=inverse7(a[r][c]);
        for (int j=c;j<cols;++j) a[r][j]=mod7(a[r][j]*iv);
        for (int i=0;i<rows;++i) if(i!=r) {
            int f=a[i][c];
            for(int j=c;j<cols;++j) a[i][j]=mod7(a[i][j]-f*a[r][j]);
        }
        ++r;
    }
    return r;
}
Mat inverse(Mat a) {
    int n=a.size(); Mat b(n,Vec(n));
    for(int i=0;i<n;++i) b[i][i]=1;
    for(int c=0;c<n;++c) {
        int p=c; while(p<n && a[p][c]==0) ++p;
        if(p==n) throw std::runtime_error("Singular inverse");
        std::swap(a[c],a[p]); std::swap(b[c],b[p]); Q d=a[c][c];
        for(int j=0;j<n;++j) {a[c][j]/=d;b[c][j]/=d;}
        for(int i=0;i<n;++i) if(i!=c) {
            Q f=a[i][c];
            for(int j=0;j<n;++j) {a[i][j]-=f*a[c][j];b[i][j]-=f*b[c][j];}
        }
    }
    return b;
}
Q dot(const Vec &a,const Vec &b) {
    assert(a.size()==b.size()); Q s=0;
    for(size_t i=0;i<a.size();++i) s+=a[i]*b[i];
    return s;
}
Vec multiply(const Mat &m,const Vec &v) {
    Vec r; for(const auto &row:m) r.push_back(dot(row,v)); return r;
}
struct Gram {
    bool psd=true;
    std::vector<int> basis;
    Q determinant=1;
};
Gram inspect(Mat a) {
    Gram answer; int n=a.size(); std::vector<int> order(n);
    std::iota(order.begin(),order.end(),0);
    for(int k=0;k<n;++k) {
        int p=-1;
        for(int i=k;i<n;++i) {
            if(a[i][i]<0) {answer.psd=false;return answer;}
            if(a[i][i]>0 && p<0) p=i;
        }
        if(p<0) {
            for(int i=k;i<n;++i) for(int j=k;j<n;++j)
                if(a[i][j]!=0) answer.psd=false;
            return answer;
        }
        std::swap(a[k],a[p]);
        for(int i=0;i<n;++i) std::swap(a[i][k],a[i][p]);
        std::swap(order[k],order[p]);
        answer.basis.push_back(order[k]); Q d=a[k][k]; answer.determinant*=d;
        for(int i=k+1;i<n;++i) for(int j=i;j<n;++j) {
            a[i][j]-=a[i][k]*a[k][j]/d; a[j][i]=a[i][j];
        }
    }
    return answer;
}
bool integral_square(const Q &q) {
    return q>=0 && q.get_den()==1 && mpz_perfect_square_p(q.get_num().get_mpz_t());
}
bool caps(const Graph &g) {
    for(size_t i=0;i<g.size();++i) {
        if(__builtin_popcountll(g[i])>14) return false;
        for(size_t j=0;j<i;++j)
            if(__builtin_popcountll(g[i]&g[j])>2-int((g[i]>>j)&1)) return false;
    }
    return true;
}
struct Label {int j,k,t;};
std::vector<Label> labels;
int bdot(int a,int b) {
    auto x=labels.at(a),y=labels.at(b);
    return int(x.j==y.j)+int(x.j==y.k)+int(x.k==y.j)+int(x.k==y.k);
}
int zdot(int a,int b) {
    auto x=labels.at(a),y=labels.at(b); int sx=x.t ? -1:1,sy=y.t ? -1:1;
    return int(x.j==y.j)+sy*int(x.j==y.k)+sx*int(x.k==y.j)+sx*sy*int(x.k==y.k);
}
struct Att {
    int label;
    uint64_t mask,twin;
    std::array<int,12> key;
    Vec f,u,gf,gu;
    Q nf,nu;
};
struct Unsigned {
    int label;
    Key key{};
    Vec u,gu;
    Q nu;
    std::vector<int> lifts;
};
struct Input {
    int chart,hrank;
    Q dh,df;
    std::vector<int> roots,p,n;
    Graph graph;
    Mat hi,fi;
    std::vector<std::vector<int>> fa;
    std::vector<Att> attachments;
    std::vector<Unsigned> unsigneds;
    std::array<std::vector<int>,30> domains;
};
Input read_input(const std::string &name) {
    Input in; std::ifstream f(name); if(!f) throw std::runtime_error("Missing setup");
    int nr,na; f>>in.chart>>in.hrank>>in.dh>>in.df>>nr>>na;
    in.roots.resize(nr); for(int &x:in.roots) f>>x;
    in.p.resize(12);in.n.resize(12);in.graph.resize(39);
    for(int &x:in.p) f>>x;for(int &x:in.n) f>>x;
    for(auto &x:in.graph) f>>x;
    for(Mat *matrix:{&in.hi,&in.fi}) {
        matrix->assign(12,Vec(12));
        for(auto &row:*matrix) for(Q &x:row) f>>x;
    }
    in.fa.assign(12,std::vector<int>(12));
    for(auto &row:in.fa) for(int &x:row) f>>x;
    std::map<std::pair<int,std::array<int,12>>,int> unique;
    for(int i=0;i<na;++i) {
        Att a;f>>a.label>>a.mask>>a.twin;
        for(int &x:a.key) f>>x;
        a.f.resize(12);a.u.resize(12);
        for(Q &x:a.f) f>>x;for(Q &x:a.u) f>>x;
        a.gf=multiply(in.fi,a.f);a.gu=multiply(in.hi,a.u);
        a.nf=10-dot(a.f,a.gf);a.nu=5-dot(a.u,a.gu);
        if(a.nf<0 || a.nu<0) throw std::runtime_error("Bad unary input");
        auto id=std::make_pair(a.label,a.key);
        if(!unique.count(id)) {
            int index=in.unsigneds.size();unique[id]=index;
            Unsigned u;u.label=a.label;u.u=a.u;u.gu=a.gu;u.nu=a.nu;
            for(int j=0;j<12;++j) u.key[j]=a.key[j];
            auto lab=labels[a.label];u.key[12+lab.j]=1;u.key[12+lab.k]=1;
            in.unsigneds.push_back(u);
        }
        in.unsigneds[unique.at(id)].lifts.push_back(i);
        in.attachments.push_back(a);in.domains[a.label].push_back(i);
    }
    if(!f || !caps(in.graph)) throw std::runtime_error("Invalid setup or base");
    std::string extra;if(f>>extra) throw std::runtime_error("Trailing setup input");
    return in;
}
Graph append_graph(const Graph &base,const Att &a,const std::vector<int> &t,const std::vector<int> &l) {
    assert(t.size()==l.size() && base.size()==39+2*t.size());
    int old=base.size(); uint64_t m=a.mask,mm=a.twin;
    for(size_t i=0;i<t.size();++i) {
        int p=39+2*i,n=p+1;
        assert(t[i]>=0 && t[i]<=2);
        if(t[i]==2 || (t[i]==1 && l[i]==1)) {m|=1ULL<<p;mm|=1ULL<<n;}
        if(t[i]==2 || (t[i]==1 && l[i]==-1)) {m|=1ULL<<n;mm|=1ULL<<p;}
        assert((t[i]==1 && (l[i]==1 || l[i]==-1)) || (t[i]!=1 && l[i]==0));
    }
    Graph g=base;g.push_back(m);g.push_back(mm);
    for(int i=0;i<old;++i) {
        if((m>>i)&1) g[i]|=1ULL<<old;
        if((mm>>i)&1) g[i]|=1ULL<<(old+1);
    }
    return g;
}
bool t_caps(const Input &in,const std::vector<int> &aid,const Links &tt) {
    int k=aid.size(),n=12+k;
    std::vector<std::vector<int>> t(n,std::vector<int>(n));
    std::vector<unsigned> support(n);
    for(int i=0;i<12;++i) {
        support[i]=1U|(1U<<(1+i/2));
        for(int j=0;j<12;++j) t[i][j]=int(in.p[i]==j)+int(in.n[i]==j);
    }
    for(int a=0;a<k;++a) {
        const auto &att=in.attachments[aid[a]];auto y=labels[att.label];
        support[12+a]=(1U<<(y.j+1))|(1U<<(y.k+1));
        for(int i=0;i<12;++i) t[i][12+a]=t[12+a][i]=att.key[i];
        for(int b=0;b<k;++b) t[12+a][12+b]=tt[a][b];
    }
    for(int i=0;i<n;++i) {
        if(std::count(t[i].begin(),t[i].end(),2)>1) return false;
        for(int j=0;j<i;++j) {
            int sum=t[i][j]+__builtin_popcount(support[i]&support[j]);
            for(int a=0;a<n;++a) sum+=t[i][a]*t[a][j];
            if(sum>4) return false;
        }
    }
    return true;
}
int signed_rank(const Input &in,const std::vector<int> &aid,const Links &ll) {
    int k=aid.size();std::vector<std::vector<int>> a(12+k,std::vector<int>(12+k));
    for(int i=0;i<12;++i) for(int j=0;j<12;++j) a[i][j]=in.fa[i][j];
    for(int i=0;i<k;++i) {
        auto &x=in.attachments[aid[i]];
        for(int j=0;j<12;++j) {assert(x.f[j].get_den()==1);a[j][12+i]=a[12+i][j]=x.f[j].get_num().get_si();}
        a[12+i][12+i]=10;
        for(int j=0;j<i;++j) a[12+i][12+j]=a[12+j][12+i]=-zdot(x.label,in.attachments[aid[j]].label)-4*ll[i][j];
    }
    return rank7(a);
}
Mat residual(const Input &in,const std::vector<int> &aid,const Links &link,bool is_signed) {
    int k=aid.size();Mat a(k,Vec(k));
    for(int i=0;i<k;++i) {
        const auto &x=in.attachments[aid[i]];a[i][i]=is_signed?x.nf:x.nu;
        for(int j=0;j<i;++j) {
            const auto &y=in.attachments[aid[j]];
            a[i][j]=a[j][i]=is_signed
                ? Q(-zdot(x.label,y.label)-4*link[i][j])-dot(x.f,y.gf)
                : Q(1-bdot(x.label,y.label)-2*link[i][j])-dot(x.u,y.gu);
        }
    }
    return a;
}
struct Projection { Vec cross,weights; Q norm; };
struct State {
    Mat gram,inv;
    Gram data;
    int dimension;
    Q determinant;
    bool valid;
    State(const Mat &m,int star_rank,const Q &star_det):gram(m),data(inspect(m)) {
        dimension=star_rank+data.basis.size();determinant=star_det*data.determinant;
        valid=data.psd && dimension<=15;
        if(!valid) return;
        Mat b(data.basis.size(),Vec(data.basis.size()));
        for(size_t i=0;i<data.basis.size();++i) for(size_t j=0;j<data.basis.size();++j)
            b[i][j]=gram[data.basis[i]][data.basis[j]];
        inv=inverse(b);
    }
    bool extend(const Vec &cross,const Q &norm,Projection &out) const {
        assert(valid);Vec c;for(int i:data.basis) c.push_back(cross[i]);
        Vec w=multiply(inv,c);
        for(size_t i=0;i<gram.size();++i) {
            Q predicted=0;
            for(size_t j=0;j<data.basis.size();++j) predicted+=gram[i][data.basis[j]]*w[j];
            if(predicted!=cross[i]) return false;
        }
        Q n=norm-dot(c,w);
        if(n<0 || (dimension==15 && n!=0)) return false;
        if(dimension==14 && !integral_square(determinant*n)) return false;
        out={c,w,n};return true;
    }
    bool pair(const Projection &x,const Projection &y,const Q &cross) const {
        Q c=cross-dot(x.cross,y.weights),d=x.norm*y.norm-c*c;
        if(d<0) return false;
        int r=(d>0?2:((x.norm>0 || y.norm>0)?1:0));
        if(r==0 && c!=0) return false;
        if(dimension+r>15) return false;
        if(r==2 && dimension==13 && !integral_square(determinant*d)) return false;
        return true;
    }
};
Links add_links(const Links &a,const std::vector<int> &column) {
    assert(a.size()==column.size());Links b=a;
    for(size_t i=0;i<a.size();++i) b[i].push_back(column[i]);
    b.push_back(column);b.back().push_back(0);return b;
}
struct Extension {
    int aid;
    std::vector<int> t,l;
    Projection h,f;
};
struct Counts {
    uint64_t matches=0,quartets=0,tcap=0,hpsd=0,hdet=0,lifts=0,fpsd=0,fdet=0,
        rank=0,first=0,second=0,pair_calls=0,pair_pass=0;
};
struct Search {
    const Input &in;Counts count; bool open=false;
    std::vector<int> g;
    Search(const Input &input):in(input) {}
    bool extra_pair(const Extension &x,const Extension &y,const std::vector<int> &heavy,
                    const Links &tt,const Links &ll,const Graph &graph,const State &hs,const State &fs) {
        ++count.pair_calls;
        const Att &a=in.attachments[x.aid],&b=in.attachments[y.aid];
        assert(a.label!=b.label);
        auto first_graph=append_graph(graph,a,x.t,x.l);
        auto ids=heavy;ids.push_back(x.aid);ids.push_back(y.aid);
        Links tbase=add_links(tt,x.t),lbase=add_links(ll,x.l);
        for(int t=0;t<=2;++t) {
            auto ty=y.t;ty.push_back(t);
            auto tall=add_links(tbase,ty);
            if(!t_caps(in,ids,tall)) continue;
            Q hcross=Q(1-bdot(a.label,b.label)-2*t)-dot(a.u,b.gu);
            if(!hs.pair(x.h,y.h,hcross)) continue;
            std::vector<int> signs=t==1?std::vector<int>{-1,1}:std::vector<int>{0};
            for(int l:signs) {
                Q fcross=Q(-zdot(a.label,b.label)-4*l)-dot(a.f,b.gf);
                if(!fs.pair(x.f,y.f,fcross)) continue;
                auto ly=y.l;ly.push_back(l);auto lall=add_links(lbase,ly);
                if(signed_rank(in,ids,lall)>13) continue;
                auto full=append_graph(first_graph,b,ty,ly);
                if(caps(full)) {++count.pair_pass;return true;}
            }
        }
        return false;
    }
    bool second_layer(const std::vector<std::vector<Extension>> &all,const std::vector<int> &heavy,
                      const Links &tt,const Links &ll,const Graph &graph,const State &hs,const State &fs) {
        ++count.second;
        std::vector<int> order;
        for(int y=0;y<30;++y) if(!all[y].empty()) order.push_back(y);
        assert(order.size()==26);
        std::sort(order.begin(),order.end(),[&](int x,int y) {
            return all[x].size()!=all[y].size()?all[x].size()<all[y].size():x<y;
        });
        order.resize(8);
        std::vector<const Extension*> selected;
        std::map<std::array<int,4>,bool> cache;
        std::vector<std::pair<int,int>> selected_ids;
        std::function<bool(int)> dfs=[&](int depth) {
            if(depth==8) return true;
            int y=order[depth];
            for(size_t i=0;i<all[y].size();++i) {
                bool okay=true;
                for(size_t j=0;j<selected.size() && okay;++j) {
                    std::array<int,4> key={selected_ids[j].first,selected_ids[j].second,y,int(i)};
                    auto it=cache.find(key);
                    if(it==cache.end()) it=cache.emplace(key,extra_pair(*selected[j],all[y][i],heavy,tt,ll,graph,hs,fs)).first;
                    okay=it->second;
                }
                if(okay) {
                    selected.push_back(&all[y][i]);selected_ids.push_back({y,int(i)});
                    if(dfs(depth+1)) return true;
                    selected.pop_back();selected_ids.pop_back();
                }
            }
            return false;
        };
        return dfs(0);
    }
    bool all_outside(const std::vector<int> &heavy,const Links &tt,const Links &ll,
                     const Graph &graph,const State &hs,const State &fs) {
        std::set<int> used;for(int id:heavy) used.insert(in.attachments[id].label);
        std::vector<std::vector<Extension>> domains(30);
        const int root_sign[4]={1,1,-1,-1};
        for(int y=0;y<30;++y) if(!used.count(y)) {
            for(int aid:in.domains[y]) {
                const auto &a=in.attachments[aid];
                int tg=0;for(int i=0;i<12;++i) tg+=a.key[i]*g[i];
                for(int code=0;code<81;++code) {
                    int c=code,s=tg;std::vector<int> t(4);
                    for(int i=0;i<4;++i) {t[i]=c%3;c/=3;s+=2*t[i]*root_sign[i];}
                    if(s) continue;
                    auto ids=heavy;ids.push_back(aid);
                    if(!t_caps(in,ids,add_links(tt,t))) continue;
                    Vec hu(4);
                    for(int i=0;i<4;++i) {
                        const auto &b=in.attachments[heavy[i]];
                        hu[i]=Q(1-bdot(y,b.label)-2*t[i])-dot(a.u,b.gu);
                    }
                    Projection hp;
                    if(!hs.extend(hu,a.nu,hp)) continue;
                    std::vector<int> ones;
                    for(int i=0;i<4;++i) if(t[i]==1) ones.push_back(i);
                    for(int mask=0;mask<(1<<ones.size());++mask) {
                        std::vector<int> l(4);
                        for(size_t j=0;j<ones.size();++j) l[ones[j]]=(mask>>j&1)?1:-1;
                        Graph full=append_graph(graph,a,t,l);
                        if(!caps(full)) continue;
                        if(signed_rank(in,ids,add_links(ll,l))>13) continue;
                        Vec fc(4);
                        for(int i=0;i<4;++i) {
                            const auto &b=in.attachments[heavy[i]];
                            fc[i]=Q(-zdot(y,b.label)-4*l[i])-dot(a.f,b.gf);
                        }
                        Projection fp;
                        if(!fs.extend(fc,a.nf,fp)) continue;
                        domains[y].push_back({aid,t,l,hp,fp});
                    }
                }
            }
            if(domains[y].empty()) return false;
        }
        ++count.first;
        std::cout<<"FIRST chart "<<in.chart<<" root ";
        for(int x:g) std::cout<<(x>0?'1':'0');
        std::cout<<" labels";
        for(int id:heavy) std::cout<<' '<<in.attachments[id].label;
        std::cout<<" domains";
        for(int y=0;y<30;++y) if(!used.count(y)) std::cout<<' '<<y<<':'<<domains[y].size();
        std::cout<<std::endl;
        return second_layer(domains,heavy,tt,ll,graph,hs,fs);
    }
    void lift_quartet(const std::array<int,4> &us,const Links &tt,const State &hs) {
        std::vector<int> chosen; Links ll;Graph graph=in.graph;
        std::function<void(int,const Graph&)> rec=[&](int depth,const Graph &old) {
            if(open) return;
            if(depth==4) {
                ++count.lifts;
                State fs(residual(in,chosen,ll,true),11,in.df);
                if(!fs.valid) return;++count.fpsd;
                if(fs.dimension==15 && !integral_square(fs.determinant/Q(1024*49))) return;
                ++count.fdet;
                if(signed_rank(in,chosen,ll)>13) return;++count.rank;
                if(all_outside(chosen,tt,ll,old,hs,fs)) open=true;
                return;
            }
            std::vector<int> t(depth),ones;
            for(int i=0;i<depth;++i) {t[i]=tt[depth][i];if(t[i]==1) ones.push_back(i);}
            for(int aid:in.unsigneds[us[depth]].lifts) {
                for(int mask=0;mask<(1<<ones.size());++mask) {
                    std::vector<int> l(depth);
                    for(size_t j=0;j<ones.size();++j) l[ones[j]]=(mask>>j&1)?1:-1;
                    auto next=append_graph(old,in.attachments[aid],t,l);
                    if(!caps(next)) continue;
                    auto saved=ll;ll=add_links(ll,l);chosen.push_back(aid);
                    rec(depth+1,next);chosen.pop_back();ll=std::move(saved);
                    if(open) return;
                }
            }
        };
        rec(0,graph);
    }
    void quartet(const std::array<int,4> &us) {
        std::vector<int> ids;std::array<int,4> own{};
        for(int i=0;i<4;++i) {
            const auto &u=in.unsigneds[us[i]];ids.push_back(u.lifts[0]);
            for(int j=0;j<12;++j) if(g[j]==(i<2?1:-1)) own[i]+=u.key[j];
        }
        for(int p=0;p<=2;++p) for(int n=0;n<=2;++n) for(int b=0;b<=2;++b) {
            int c=2+own[0]+p-b,d=2+own[2]+n-b,e=2+own[1]+p-d;
            if(c<0 || c>2 || d<0 || d>2 || e<0 || e>2 || c+e-n!=2+own[3]) continue;
            ++count.quartets;Links tt={{0,p,b,c},{p,0,d,e},{b,d,0,n},{c,e,n,0}};
            if(!t_caps(in,ids,tt)) continue;++count.tcap;
            State hs(residual(in,ids,tt,false),in.hrank,in.dh);
            if(!hs.valid) continue;++count.hpsd;
            if(hs.dimension==15 && !integral_square(hs.determinant/Q(16*7*16*7))) continue;
            ++count.hdet;
            lift_quartet(us,tt,hs);
            if(open) return;
        }
    }
    void root(int mask) {
        g.resize(12);for(int i=0;i<12;++i) g[i]=(mask>>i&1)?1:-1;
        Vec qg(g.begin(),g.end());Vec ig=multiply(in.hi,qg);Q root_norm=2-dot(qg,ig);
        assert(root_norm>=0);
        std::array<int,12> same{};int edges=0;
        for(int i=0;i<12;++i) {
            same[i]=int(g[i]==g[in.p[i]])+int(g[i]==g[in.n[i]]);
            edges+=same[i];
        }
        assert(edges%2==0);edges/=2;assert(edges==0 || edges==2);
        std::vector<int> plus,minus;
        for(size_t i=0;i<in.unsigneds.size();++i) {
            const auto &u=in.unsigneds[i];
            for(int sign:{1,-1}) {
                int own=0;for(int j=0;j<12;++j) if(g[j]==sign) own+=u.key[j];
                if(own>std::min(1,2-edges)) continue;
                Q c=2*sign-dot(qg,u.gu);
                if(c*c>root_norm*u.nu) continue;
                (sign==1?plus:minus).push_back(i);
            }
        }
        Key target{};
        for(int i=0;i<12;++i) target[i]=-g[i]*(1+same[i]);
        for(int j=0;j<6;++j) target[12+j]=-(g[2*j]+g[2*j+1])/2;
        std::map<Key,std::vector<std::pair<int,int>>> pairs;
        for(size_t i=0;i<plus.size();++i) for(size_t j=i+1;j<plus.size();++j) {
            int a=plus[i],b=plus[j];
            if(in.unsigneds[a].label==in.unsigneds[b].label) continue;
            Key key;for(int k=0;k<18;++k) key[k]=in.unsigneds[a].key[k]+in.unsigneds[b].key[k];
            pairs[key].push_back({a,b});
        }
        for(size_t i=0;i<minus.size();++i) for(size_t j=i+1;j<minus.size();++j) {
            int c=minus[i],d=minus[j];
            if(in.unsigneds[c].label==in.unsigneds[d].label) continue;
            Key key;for(int k=0;k<18;++k) key[k]=target[k]+in.unsigneds[c].key[k]+in.unsigneds[d].key[k];
            auto it=pairs.find(key);if(it==pairs.end()) continue;
            for(auto [a,b]:it->second) {
                std::set<int> used={in.unsigneds[a].label,in.unsigneds[b].label,in.unsigneds[c].label,in.unsigneds[d].label};
                if(used.size()!=4) continue;
                ++count.matches;quartet({a,b,c,d});if(open) return;
            }
        }
    }
    void print(const std::string &prefix,int processed) {
        std::cout<<prefix<<" chart "<<in.chart<<" roots "<<processed<<" planned "<<in.roots.size()
            <<" open "<<open<<" matches "<<count.matches<<" quartets "<<count.quartets
            <<" tcaps "<<count.tcap<<" hpsd "<<count.hpsd<<" hdet "<<count.hdet
            <<" lifts "<<count.lifts<<" fpsd "<<count.fpsd<<" fdet "<<count.fdet
            <<" rank "<<count.rank<<" first "<<count.first<<" second "<<count.second
            <<" pair_calls "<<count.pair_calls<<" pair_pass "<<count.pair_pass<<std::endl;
    }
};
int main(int argc,char **argv) {
    try {
        if(argc!=2) throw std::runtime_error("Usage: singleton_exact setup.txt");
        for(int j=0;j<6;++j) for(int k=j+1;k<6;++k) for(int t=0;t<2;++t) labels.push_back({j,k,t});
        Input in=read_input(argv[1]);Search search(in);int done=0;
        for(int mask:in.roots) {
            search.root(mask);++done;search.print("ROOT",done);
            if(search.open) break;
        }
        search.print("FINAL",done);
        return search.open?3:0;
    } catch(const std::exception &e) {
        std::cerr<<"ERROR "<<e.what()<<std::endl;return 2;
    }
}
