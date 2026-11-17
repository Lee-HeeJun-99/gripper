#include "../../models/film_three_finger/SharedFilmSystem.h"
#include <iostream>
#include <iomanip>
using namespace regrip_three_finger;
int main(int argc,char**argv){try{
 if(argc!=3)throw std::runtime_error("rejected CSV and output required");std::ifstream in(argv[1]);std::string line;std::getline(in,line);std::getline(in,line);auto first=line.find('"'),last=line.find('"',first+1);if(first==std::string::npos||last==std::string::npos)throw std::runtime_error("rejected q missing");std::stringstream prefix(line.substr(0,first));std::vector<std::string>fields;std::string field;while(std::getline(prefix,field,','))fields.push_back(field);
 unsigned finger=std::stoul(fields.at(0)),ids[2]={unsigned(std::stoul(fields.at(1))),unsigned(std::stoul(fields.at(4)))};SharedFilmSystem system;Eigen::VectorXd q(system.initial.size());std::stringstream values(line.substr(first+1,last-first-1));for(double&x:q)if(!(values>>x))throw std::runtime_error("rejected q dimension");auto state=system.local(q,finger);const auto&s=system.shared.films[finger];auto rest=s.film.model.rest();std::ofstream out(argv[2]);out<<std::setprecision(17)<<"triangle,radius,double_gap,double_feature,relative_points\n";
 for(unsigned id:ids){auto e=s.primitive(state,id);out<<id<<','<<s.radius<<','<<e.gap.v<<','<<e.feature<<",\"";for(unsigned node:s.triangles.at(id)){auto p=sub(add(rest.at(node),state.q.at(node)),point(state.body.center));for(double x:p)out<<x<<' ';}out<<"\"\n";}
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
