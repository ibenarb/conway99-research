#define main singleton_research_main
#include "singleton_exact_v1.cpp"
#undef main
int main() {
    try {
        for(int j=0;j<6;++j) for(int k=j+1;k<6;++k) for(int t=0;t<2;++t) labels.push_back({j,k,t});
        std::string kind;
        while(std::cin>>kind) {
            if(kind=="G") {
                int n;std::cin>>n;Mat a(n,Vec(n));
                for(auto &row:a) for(Q &x:row) std::cin>>x;
                auto result=inspect(a);
                std::cout<<result.psd<<' '<<result.basis.size()<<' '<<result.determinant<<std::endl;
            } else if(kind=="S") {
                int n,sr,k;Q sd;std::cin>>n>>sr>>sd>>k;Mat a(n+k,Vec(n+k));
                for(auto &row:a) for(Q &x:row) std::cin>>x;
                Mat b(n,Vec(n));
                for(int i=0;i<n;++i) for(int j=0;j<n;++j) b[i][j]=a[i][j];
                State state(b,sr,sd);bool okay=state.valid;std::vector<Projection> p(k);
                for(int i=0;i<k && okay;++i) {
                    Vec c(a[n+i].begin(),a[n+i].begin()+n);
                    okay=state.extend(c,a[n+i][n+i],p[i]);
                }
                if(okay && k==2) okay=state.pair(p[0],p[1],a[n][n+1]);
                std::cout<<okay<<std::endl;
            } else if(kind=="F") {
                std::string file;std::cin>>file;Input in=read_input(file);
                Links tt(4,std::vector<int>(4)),ll=tt;
                for(int i=0;i<4;++i) for(int j=0;j<i;++j) {
                    std::cin>>tt[i][j]>>ll[i][j];tt[j][i]=tt[i][j];ll[j][i]=ll[i][j];
                }
                Graph graph=in.graph;
                for(int i=0;i<4;++i) graph=append_graph(graph,in.attachments[i],
                    std::vector<int>(tt[i].begin(),tt[i].begin()+i),std::vector<int>(ll[i].begin(),ll[i].begin()+i));
                std::vector<int> ids={0,1,2,3};
                State h(residual(in,ids,tt,false),in.hrank,in.dh),f(residual(in,ids,ll,true),11,in.df);
                bool hd=h.valid && (h.dimension<15 || integral_square(h.determinant/Q(112*112)));
                bool fd=f.valid && (f.dimension<15 || integral_square(f.determinant/Q(224*224)));
                std::cout<<caps(graph)<<' '<<t_caps(in,ids,tt)<<' '<<hd<<' '<<fd<<' '
                    <<h.dimension<<' '<<f.dimension<<' '<<signed_rank(in,ids,ll)<<std::endl;
            } else throw std::runtime_error("Unknown probe command");
        }
        return 0;
    } catch(const std::exception &e) {std::cerr<<e.what()<<std::endl;return 2;}
}
