#include "../../models/film_three_finger/SharedFilmSystem.h"
#include <fstream>
#include <iomanip>
using namespace regrip_three_finger;
int main(int argc,char**argv){try{
 if(argc!=3&&argc!=4)throw std::runtime_error("actual checkpoint,prefix[,current] required");bool current=argc==4;std::ifstream in(argv[1]);std::string magic,token;double time,h;unsigned step;in>>magic>>time>>h>>step>>token;if(magic!="REGRIP_FREE_V3")throw std::runtime_error("actual released checkpoint required");
 SharedFilmSystem s(Layout(),{0,0,0},true,true);s.exactUnresolved=true;unsigned n=s.initial.size(),nf=s.shared.nf;Eigen::VectorXd q(n),v(n);for(double&x:q)in>>x;for(double&x:v)in>>x;double unused;for(unsigned i=0;i<4;++i)in>>unused;std::vector<double>mass;
 for(unsigned f=0;f<3;++f){auto&m=s.shared.films[f].film;for(unsigned i=0;i<m.mass.size();++i){in>>m.mass[i];if(f==0)mass.push_back(m.mass[i]);else if(m.mass[i]!=mass[i])throw std::runtime_error("one repeated-film spectrum requires identical measured masses");}}
 if(!in)throw std::runtime_error("actual q/v/mass incomplete");auto response=s.force(current?q:s.initial,0);Eigen::MatrixXd K=response.negativeTangent.topLeftCorner(nf,nf);if((!current&&response.value.norm()>1e-12)||(K-K.transpose()).norm()>1e-12)throw std::runtime_error("symmetric tangent/reference equilibrium gate");Eigen::VectorXd M=Eigen::VectorXd::Zero(nf);const auto&m=s.shared.films[0].film;for(unsigned a=0;a<m.index.size();++a)if(m.index[a]>=0)M(m.index[a])+=m.mass[a/3]*m.weight[a]*m.weight[a];if(M.minCoeff()<=0)throw std::runtime_error("projected modal mass not positive");
 std::string prefix=argv[2];std::ofstream matrix(prefix+".matrix.txt");matrix<<std::setprecision(17)<<nf<<'\n'<<M.transpose()<<'\n'<<K<<'\n';std::ofstream state(prefix+".state.txt");state<<std::setprecision(17)<<time<<'\n'<<q.head(3*nf).transpose()<<'\n'<<v.head(3*nf).transpose()<<'\n';return 0;
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
