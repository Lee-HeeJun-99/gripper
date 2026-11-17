#include "../models/film_coupled_contact/ReintegratedStep.h"
#include <iostream>
using namespace regrip_coupled;
int main(){try{
 Assembly model(5);auto mass=model.masses();std::vector<Point>q(model.size()),v(model.size()),zero(model.size());unsigned tip=model.id(0,4,2);v[tip][2]=-3;
 std::vector<std::array<unsigned,3>>triangles;
 for(unsigned part=0;part<3;++part)for(unsigned i=0;i+1<model.nx;++i)for(unsigned j=0;j+1<model.parts[part].ny;++j){unsigned a=model.id(part,i,j),b=model.id(part,i+1,j),c=model.id(part,i,j+1),d=model.id(part,i+1,j+1);triangles.push_back({a,b,c});triangles.push_back({b,d,c});}
 Body body;body.center=vector(model.rest()[tip])-Eigen::Vector3d(0,0,1.001);body.linear={.1,0,.03};EventControl control{.001,4,6,8,true};double start=.9;
 auto system=[&](double h,Body b){return System(CoupledPlaneStep(model,mass,h,2,control.sample(start).tension,q,v,zero,0),triangles,b,1,true,true,true,1e-17,1e-14);};
 auto base=system(.001,body);auto root=resolveCoupledBirthBracket(base,start,control);
 if(root.timeIncoming.size()!=base.n||root.gap< -1e-12||root.mechanicalResidual>1e-14)throw std::runtime_error("family root state/residual/IFT");
 double parentDifference=0;
 for(double h:{.002,.0005,.0017,.0007}){auto other=resolveCoupledBirthBracket(system(h,body),start,control);parentDifference=std::max(parentDifference,(base.pack(other.state)-base.pack(root.state)).norm());if(std::abs(other.time-root.time)>2e-13)throw std::runtime_error("family time depends on parent bracket");}
 if(parentDifference>1e-8)throw std::runtime_error("family pre-impact velocity depends on parent bracket");
 double delta=1e-4;Body plus=body,minus=body;plus.linear.z()+=delta;minus.linear.z()-=delta;
 auto rp=resolveCoupledBirthBracket(system(.001,plus),start,control),rm=resolveCoupledBirthBracket(system(.001,minus),start,control);
 double timeFD=(rp.time-rm.time)/(2*delta),iftError=std::abs(timeFD-root.timeIncoming(base.nf+2));
 Eigen::VectorXd velocityFD=(base.pack(rp.state)-base.pack(rm.state))/(2*delta);double velocityError=(velocityFD-root.velocityIncoming.col(base.nf+2)).norm();
 if(iftError>1e-8||velocityError>1e-5){std::cerr<<"time IFT error "<<iftError<<" velocity IFT error "<<velocityError<<'\n';throw std::runtime_error("reintegrated coupled root/velocity IFT FD");}
 auto impulse=manyRowImpact(base.M,root.J,base.pack(root.state),1e-10);if(impulse.state.momentumResidual>1e-14||impulse.state.normalVelocity.minCoeff()< -1e-10)throw std::runtime_error("family impact momentum/normal velocity");
 auto step=reintegratedStep(base,start,control);if(!step.event||step.minimumGap< -1e-10||step.preImpact.v!=root.state.v)throw std::runtime_error("reintegrated impact/remainder/clearance consistency");
 double dt=1e-5;auto tp=resolveCoupledBirthBracket(base,start+dt,control),tm=resolveCoupledBirthBracket(base,start-dt,control);double startFD=1+(tp.time-tm.time)/(2*dt);if(!root.absoluteStartSensitivity||std::abs(startFD-*root.absoluteStartSensitivity)>1e-7)throw std::runtime_error("common C2 start-time IFT");
 std::cout<<"PASS coupled midpoint endpoint-family bracket time "<<root.time<<" parentVelocityDifference "<<parentDifference<<" rootIFT "<<iftError<<" velocityIFT "<<velocityError<<" residual "<<root.mechanicalResidual<<";NOT global earliest CCD or SOFA\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
