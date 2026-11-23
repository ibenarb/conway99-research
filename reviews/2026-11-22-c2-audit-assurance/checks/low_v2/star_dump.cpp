// Dump all sign-normalised 12-word star assignments of one chart and parity (own enumeration, as in star_own.cpp).
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include <iostream>
using namespace std;
int geo[2][6][6];int Hm[12][12];int supp[12],sgn[12];long long cnt;
static inline int dot(int s1,int g1,int s2,int g2){int c=s1&s2;return __builtin_popcount(c)-2*__builtin_popcount((g1^g2)&c);}
void rec(int i,int used,const int (*g)[6]){
  if(i==12){cnt++;for(int k=0;k<12;k++)printf("%d %d ",supp[k],sgn[k]);printf("\n");return;}
  int j=i/2;for(int k=0;k<6;k++){int s=g[j][k];int old=s&used;int sub=old;while(true){bool ok=true;for(int a=0;a<i&&ok;a++)if(dot(supp[a],sgn[a],s,sub)!=Hm[a][i])ok=false;
    if(ok){supp[i]=s;sgn[i]=sub;rec(i+1,used|s,g);}if(sub==0)break;sub=(sub-1)&old;}}}
int main(int argc,char**argv){
  {ifstream f("geometry_own.txt");for(int p=0;p<2;p++)for(int j=0;j<6;j++)for(int k=0;k<6;k++)f>>geo[p][j][k];}
  int target=atoi(argv[2]),par=atoi(argv[3]);ifstream L(argv[1]);string line;int id=0;
  while(getline(L,line)){if(id++!=target)continue;istringstream is(line);int r;is>>r;int P[12],N[12];for(int i=0;i<12;i++)is>>P[i];for(int i=0;i<12;i++)is>>N[i];
    for(int a=0;a<12;a++)for(int b=0;b<12;b++)Hm[a][b]=5*(a==b)-(b==(a^1))-2*(b==P[a])-2*(b==N[a]);rec(0,0,geo[par]);}
  return 0;}
