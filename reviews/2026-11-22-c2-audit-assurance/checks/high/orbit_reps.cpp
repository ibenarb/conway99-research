// Own orbit count of chart automorphisms on the raw set of sign-normalised 12-word star assignments.
#include <cstdio>
#include <vector>
#include <array>
#include <algorithm>
#include <fstream>
#include <sstream>
#include <iostream>
#include <numeric>
using namespace std;
int geo[2][6][6];int Hm[12][12];int supp[12],sgn[12];typedef array<int,12> Row;vector<Row> raw;
static inline int dot(int s1,int g1,int s2,int g2){int c=s1&s2;return __builtin_popcount(c)-2*__builtin_popcount((g1^g2)&c);}
void rec(int i,int used,const int (*g)[6]){
  if(i==12){Row r;for(int k=0;k<12;k++)r[k]=(supp[k]<<15)|sgn[k];raw.push_back(r);return;}
  int j=i/2;for(int k=0;k<6;k++){int s=g[j][k];int old=s&used;int sub=old;while(true){bool ok=true;for(int a=0;a<i&&ok;a++)if(dot(supp[a],sgn[a],s,sub)!=Hm[a][i])ok=false;
    if(ok){supp[i]=s;sgn[i]=sub;rec(i+1,used|s,g);}if(sub==0)break;sub=(sub-1)&old;}}}
int fnd(vector<int>&u,int x){while(u[x]!=x){u[x]=u[u[x]];x=u[x];}return x;}
int main(int argc,char**argv){
  {ifstream f("geometry_own.txt");for(int p=0;p<2;p++)for(int j=0;j<6;j++)for(int k=0;k<6;k++)f>>geo[p][j][k];}
  vector<array<int,25>> L;{ifstream f(argv[1]);array<int,25>v;while(f>>v[0]){for(int i=1;i<25;i++)f>>v[i];L.push_back(v);}}
  ifstream G("orbit_groups.txt");int cid,par,order,ngen;
  while(G>>cid>>par>>order>>ngen){
    vector<array<int,12>> gp(ngen);vector<array<int,15>> gs(ngen);
    for(int k=0;k<ngen;k++){for(int i=0;i<12;i++)G>>gp[k][i];for(int i=0;i<15;i++)G>>gs[k][i];}
    int *P=&L[cid][1],*N=&L[cid][13];
    for(int a=0;a<12;a++)for(int b=0;b<12;b++)Hm[a][b]=5*(a==b)-(b==(a^1))-2*(b==P[a])-2*(b==N[a]);
    raw.clear();rec(0,0,geo[par]);sort(raw.begin(),raw.end());
    vector<int> uf(raw.size());iota(uf.begin(),uf.end(),0);long long bad=0;
    for(int k=0;k<ngen;k++){
      for(size_t x=0;x<raw.size();x++){
        int m2[12],n2[12];
        for(int i=0;i<12;i++){int m=raw[x][i]>>15,n=raw[x][i]&32767,mm=0,nn=0;for(int c=0;c<15;c++){if(m>>c&1)mm|=1<<gs[k][c];if(n>>c&1)nn|=1<<gs[k][c];}m2[gp[k][i]]=mm;n2[gp[k][i]]=nn;}
        int seen=0,flip=0;Row b;for(int i=0;i<12;i++){flip|=n2[i]&~seen;seen|=m2[i];b[i]=(m2[i]<<15)|(n2[i]^(flip&m2[i]));}
        auto it=lower_bound(raw.begin(),raw.end(),b);if(it==raw.end()||*it!=b){bad++;continue;}
        int y=it-raw.begin();int rx=fnd(uf,x),ry=fnd(uf,y);if(rx!=ry)uf[rx]=ry;
      }}
    long long orb=0;for(size_t x=0;x<raw.size();x++)if(fnd(uf,x)==(int)x)orb++;
    printf("%d %d raw %zu group %d orbits %lld images_outside_raw %lld\n",cid,par,raw.size(),order,orb,bad);fflush(stdout);{char nm[64];sprintf(nm,"reps/%d.%d.txt",cid,par);FILE*fo=fopen(nm,"w");for(size_t x=0;x<raw.size();x++)if(fnd(uf,x)==(int)x){for(int i=0;i<12;i++)fprintf(fo,"%d %d ",raw[x][i]>>15,raw[x][i]&32767);fprintf(fo,"\n");}fclose(fo);}
  }
}
