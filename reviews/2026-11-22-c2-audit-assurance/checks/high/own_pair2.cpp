// C++ port of my independent pairwise search (same algorithm as own_pair.py; own code, no packet code).
// usage: own_pair setup_file stars_file mode [maxdepth]
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <array>
#include <map>
#include <fstream>
#include <iostream>
#include <algorithm>
using namespace std;
typedef unsigned long long U; typedef long long ll;
struct Att{int y;U mask,twin;int rho,cond;ll n;int key[12];int fI[11],m[11];ll f[12],G[12];int rk;};
int rankF,dco,nd,mode;ll den;int cw[6][6],ow[15][6];vector<Att> att;vector<int> att_of[30];U base[39];
int oy[30][3];int pairidx[6][6];
vector<array<int,3>> vecs;vector<vector<int>> R;map<pair<int,int>,int> rkid;vector<vector<signed char>> ipv;int nullv[3];
vector<U> repmask;int normalise=1;
ll st_arcs=0,st_cauchy=0,st_caps=0,st_nodes=0;int st_depth=0;
int ip(const array<int,3>&v,const array<int,3>&w){return nd==2?(v[0]*w[0]+dco*v[1]*w[1])%7:(v[0]*w[0]+v[1]*w[1]+dco*v[2]*w[2])%7;}
bool literal(const Att&x,const Att&y,bool like,bool opp){
  U A[43];for(int i=0;i<39;i++)A[i]=base[i];A[39]=x.mask;A[40]=x.twin;A[41]=y.mask;A[42]=y.twin;
  for(int i=0;i<39;i++){if(x.mask>>i&1)A[i]|=1ULL<<39;if(x.twin>>i&1)A[i]|=1ULL<<40;if(y.mask>>i&1)A[i]|=1ULL<<41;if(y.twin>>i&1)A[i]|=1ULL<<42;}
  if(like){A[39]|=1ULL<<41;A[41]|=1ULL<<39;A[40]|=1ULL<<42;A[42]|=1ULL<<40;}
  if(opp){A[39]|=1ULL<<42;A[42]|=1ULL<<39;A[40]|=1ULL<<41;A[41]|=1ULL<<40;}
  for(int a=0;a<43;a++)for(int b=a+1;b<43;b++)if(__builtin_popcountll(A[a]&A[b])>2-(int)((A[a]>>b)&1))return false;
  return true;}
struct Cand{int a;int ws,wn;U rem;};
int zz(int y1,int y2){int v1[6]={0},v2[6]={0};v1[oy[y1][0]]=1;v1[oy[y1][1]]=oy[y1][2]?-1:1;v2[oy[y2][0]]=1;v2[oy[y2][1]]=oy[y2][2]?-1:1;int s=0;for(int i=0;i<6;i++)s+=v1[i]*v2[i];return s;}
int axc(int y1,int y2){int c=0;for(int a=0;a<2;a++)for(int b=0;b<2;b++)c+=oy[y1][a]==oy[y2][b];return c;}
U arc(const Cand&c1,int v1,const Cand&c2){
  st_arcs++;const Att&a1=att[c1.a],&a2=att[c2.a];int cm=c1.ws&c2.ws;int dot=__builtin_popcount(cm)-2*__builtin_popcount((c1.wn^c2.wn)&cm);
  int t=1-axc(a1.y,a2.y)-dot;if(t<0||t>4||(t&1))return 0;t/=2;int z=zz(a1.y,a2.y);int b7=-z;for(int r=0;r<rankF;r++)b7-=a1.m[r]*a2.fI[r];b7=((b7%7)+7)%7;
  U out=0;const vector<int>&r2=R[a2.rk];
  for(int L=(t==1?1:0);;L-=2){
    int target=(((b7-4*L)%7)+7)%7;U cand=0;for(U s=c2.rem;s;s&=s-1){int k=__builtin_ctzll(s);if(ipv[v1][r2[k]]==target)cand|=1ULL<<k;}
    if(cand){__int128 cross=(__int128)den*(-4*L-z);for(int i=0;i<12;i++)cross-=(__int128)a2.f[i]*a1.G[i];
      if(cross*cross>(__int128)a1.n*a2.n)st_cauchy++;
      else{st_caps++;if(literal(a1,a2,t==2||L==1,t==2||L==-1))out|=cand;}}
    if(t!=1||L==-1)break;}
  return out;}
size_t sz(const vector<Cand>&d){size_t c=0;for(auto&x:d)c+=__builtin_popcountll(x.rem);return c;}
int maxdepth=30;
bool dfs(vector<vector<Cand>>&ds,int depth,bool fr){st_nodes++;if(depth>st_depth)st_depth=depth;if(depth>=maxdepth||ds.empty())return true;
  int bi=0;size_t best=sz(ds[0]);for(size_t i=1;i<ds.size();i++){size_t s=sz(ds[i]);if(s<best){best=s;bi=i;}}swap(ds[0],ds[bi]);
  if(fr&&normalise)for(auto&c:ds[0])c.rem&=repmask[att[c.a].rk];   // all earlier residual vectors are zero: the whole group still acts
  for(auto&c1:ds[0]){const vector<int>&r1=R[att[c1.a].rk];for(U s=c1.rem;s;s&=s-1){int v1=r1[__builtin_ctzll(s)];
    vector<vector<Cand>> nxt;bool ok=true;for(size_t j=1;j<ds.size()&&ok;j++){vector<Cand> ndm;for(auto c2:ds[j]){U r=arc(c1,v1,c2);if(r){c2.rem=r;ndm.push_back(c2);}}if(ndm.empty())ok=false;else nxt.push_back(move(ndm));}
    if(ok&&dfs(nxt,depth+1,fr&&vecs[v1][0]==0&&vecs[v1][1]==0&&vecs[v1][2]==0))return true;}}
  return false;}
int main(int argc,char**argv){
  ifstream f(argv[1]);mode=atoi(argv[3]);if(argc>4)maxdepth=atoi(argv[4]);if(argc>5)normalise=atoi(argv[5]);
  f>>rankF>>dco>>den;nd=13-rankF;for(int j=0;j<6;j++)for(int k=0;k<6;k++)f>>cw[j][k];int pi=0;for(int j=0;j<6;j++)for(int k=j+1;k<6;k++){pairidx[j][k]=pi;for(int s=0;s<6;s++)f>>ow[pi][s];pi++;}
  {int yi=0;for(int j=0;j<6;j++)for(int k=j+1;k<6;k++)for(int t=0;t<2;t++){oy[yi][0]=j;oy[yi][1]=k;oy[yi][2]=t;yi++;}}
  if(nd==2){if(mode)return 2;for(int a=0;a<7;a++)for(int b=0;b<7;b++)vecs.push_back({a,b,0});}
  else for(int a=0;a<7;a++)for(int b=0;b<7;b++)for(int c=0;c<7;c++)vecs.push_back({a,b,c});
  nullv[0]=nullv[1]=nullv[2]=0;if(nd==3&&mode){for(auto&v:vecs)if((v[0]||v[1]||v[2])&&ip(v,v)==0){nullv[0]=v[0];nullv[1]=v[1];nullv[2]=v[2];break;}}
  array<int,3> nv={nullv[0],nullv[1],nullv[2]};
  for(size_t i=0;i<vecs.size();i++){pair<int,int> key={ip(vecs[i],vecs[i]),nd==3?ip(vecs[i],nv):0};if(!rkid.count(key)){rkid[key]=R.size();R.push_back({});}R[rkid[key]].push_back(i);}
  for(auto&r:R)if(r.size()>64){fprintf(stderr,"class too large\n");return 3;}
  ipv.assign(vecs.size(),vector<signed char>(vecs.size()));for(size_t i=0;i<vecs.size();i++)for(size_t j=0;j<vecs.size();j++)ipv[i][j]=ip(vecs[i],vecs[j]);

  { // group of linear isometries of the complement fixing nullv, by brute force over all matrices; orbits by union-find
    int nv_=vecs.size();vector<int> uf(nv_);for(int i=0;i<nv_;i++)uf[i]=i;auto fnd=[&](int x){while(uf[x]!=x){uf[x]=uf[uf[x]];x=uf[x];}return x;};
    int dim=nd;int g[3]={1,nd==2?dco:1,dco};long total=1;for(int i=0;i<dim*dim;i++)total*=7;long gsize=0;
    for(long code=0;code<total;code++){int M[3][3]={{0}};long c=code;for(int i=0;i<dim;i++)for(int j=0;j<dim;j++){M[i][j]=c%7;c/=7;}
      bool ok=true;for(int a=0;a<dim&&ok;a++)for(int b=a;b<dim&&ok;b++){int s=0;for(int k=0;k<dim;k++)s+=M[k][a]*g[k]*M[k][b];if(s%7!=(a==b?g[a]%7:0))ok=false;}
      if(!ok)continue;int im[3]={0,0,0};for(int i=0;i<dim;i++)for(int j=0;j<dim;j++)im[i]+=M[i][j]*nullv[j];for(int i=0;i<dim&&ok;i++)if(im[i]%7!=nullv[i])ok=false;if(!ok)continue;gsize++;
      for(int x=0;x<nv_;x++){int w[3]={0,0,0};for(int i=0;i<dim;i++)for(int j=0;j<dim;j++)w[i]+=M[i][j]*vecs[x][j];int y=nd==2?(w[0]%7)*7+(w[1]%7):(w[0]%7)*49+(w[1]%7)*7+(w[2]%7);int rx=fnd(x),ry=fnd(y);if(rx!=ry)uf[rx]=ry;}}
    repmask.assign(R.size(),0);for(size_t r=0;r<R.size();r++){vector<int> seen;for(size_t k=0;k<R[r].size();k++){int o=fnd(R[r][k]);if(find(seen.begin(),seen.end(),o)==seen.end()){seen.push_back(o);repmask[r]|=1ULL<<k;}}}
    fprintf(stderr,"isometry group order %ld\n",gsize);
  }
  int n;f>>n;for(int i=0;i<n;i++){Att a;f>>a.y>>a.mask>>a.twin>>a.rho>>a.cond>>a.n;for(int k=0;k<12;k++)f>>a.key[k];for(int k=0;k<rankF;k++)f>>a.fI[k];for(int k=0;k<rankF;k++)f>>a.m[k];for(int k=0;k<12;k++)f>>a.f[k];for(int k=0;k<12;k++)f>>a.G[k];
    auto it=rkid.find({a.rho,a.cond});if(it==rkid.end())continue;a.rk=it->second;att_of[a.y].push_back(att.size());att.push_back(a);}
  for(int i=0;i<39;i++)f>>base[i];
  ifstream sf(argv[2]);int nopen=0,nclosed=0;int hist[32]={0};vector<int> w(24);int nstars=0;
  while(sf>>w[0]){for(int i=1;i<24;i++)sf>>w[i];nstars++;
    vector<vector<Cand>> ds;bool dead=false;
    for(int y=0;y<30&&!dead;y++){vector<Cand> cl;int j=oy[y][0],k=oy[y][1];
      for(int s6=0;s6<6;s6++){int s=ow[pairidx[j][k]][s6];for(int sub=s;;sub=(sub-1)&s){int key[12];bool ok=true;
        for(int i=0;i<12&&ok;i++){int cm=w[2*i]&s;int d=__builtin_popcount(cm)-2*__builtin_popcount((w[2*i+1]^sub)&cm);int v=1-((i/2)==j||(i/2)==k)-d;if(v<0||v>4||(v&1))ok=false;else key[i]=v/2;}
        if(ok)for(int ai:att_of[y]){bool eq=true;for(int i=0;i<12&&eq;i++)eq=att[ai].key[i]==key[i];if(eq){size_t r=R[att[ai].rk].size();cl.push_back({ai,s,sub,r==64?~0ULL:((1ULL<<r)-1)});}}
        if(!sub)break;}}
      if(cl.empty())dead=true;else ds.push_back(move(cl));}
    st_depth=0;bool open=!dead&&dfs(ds,0,true);if(open){nopen++;printf("OPEN star %d\n",nstars-1);}else nclosed++;hist[dead?31:st_depth]++;}
  printf("stars %d open %d closed %d attachments %zu nodes %lld arcs %lld cauchy %lld literal %lld depths",nstars,nopen,nclosed,att.size(),st_nodes,st_arcs,st_cauchy,st_caps);
  for(int i=0;i<31;i++)if(hist[i])printf(" %d:%d",i,hist[i]);if(hist[31])printf(" emptydomain:%d",hist[31]);printf("\n");return 0;}
