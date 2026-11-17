#pragma once
#include "../film_coupled_contact/CoupledSphere.h"
#include <array>
namespace regrip_three_finger {
using namespace regrip_coupled;
struct Mount {Eigen::Matrix3d R;Eigen::Vector3d origin,rootCenter;};
struct Layout {
 std::array<Mount,3>mount;Eigen::Vector3d bodyCenter;double palmRadius,bodyRadius,bufferRadius,angle;
 // Research FIXED mount design for a chosen object,not automatic reconfiguration.
 Layout(double palm=50,double body=30,double materialContactX=75,double clearance=0):palmRadius(palm),bodyRadius(body),bufferRadius(body+.01){
  double normalDistance=bufferRadius+clearance,square=materialContactX*materialContactX+normalDistance*normalDistance-palm*palm;
  if(!(palm>0&&body>0&&materialContactX>0&&materialContactX<100&&clearance>=0&&square>0))throw std::invalid_argument("film palm/object design domain");
  double depth=std::sqrt(square);bodyCenter={0,0,-depth};angle=std::atan2(palm,depth)-std::atan2(normalDistance,materialContactX);
  for(unsigned i=0;i<3;++i){double phi=2*std::acos(-1.)*i/3;Eigen::Vector3d radial(std::cos(phi),std::sin(phi),0),tangent(-std::sin(phi),std::cos(phi),0),z(0,0,1);auto&m=mount[i];m.R.col(0)=-std::sin(angle)*radial-std::cos(angle)*z;m.R.col(1)=tangent;m.R.col(2)=std::cos(angle)*radial-std::sin(angle)*z;m.rootCenter=palm*radial;m.origin=m.rootCenter-12*m.R.col(1);
   if((m.R.transpose()*m.R-Eigen::Matrix3d::Identity()).norm()>1e-12||std::abs(m.R.determinant()-1)>1e-12)throw std::runtime_error("proper film mount frame");
  }
 }
 Eigen::Vector3d world(unsigned finger,Point x)const{return mount.at(finger).origin+mount.at(finger).R*vector(x);}
};
struct SharedPointSystem {Eigen::MatrixXd M,J;Eigen::VectorXd velocity;unsigned nf,node;std::array<System,3>films;};
inline SharedPointSystem sharedPointReference(const Layout&layout){
 Assembly model(21);model.guideIntervals=4;model.guideOffset=5;model.rootGuideSecondOrder=true;auto mass=model.masses();std::vector<Point>q(model.size()),v(q.size()),zero(q.size());unsigned node=model.id(0,15,2);v[node][2]=-1;
 std::vector<std::array<unsigned,3>>tri;for(unsigned part=0;part<3;++part)for(unsigned i=0;i+1<model.nx;++i)for(unsigned j=0;j+1<model.parts[part].ny;++j){unsigned a=model.id(part,i,j),b=model.id(part,i+1,j),c=model.id(part,i,j+1),d=model.id(part,i+1,j+1);tri.push_back({a,b,c});tri.push_back({b,d,c});}
 auto make=[&](unsigned f){Body b;b.mass=.0001;b.inertia=.4*b.mass*layout.bodyRadius*layout.bodyRadius;b.center=layout.mount[f].R.transpose()*(layout.bodyCenter-layout.mount[f].origin);return System(CoupledPlaneStep(model,mass,1e-5,2,0,q,v,zero,0),tri,b,layout.bufferRadius);};
 std::array<System,3>films={make(0),make(1),make(2)};unsigned nf=films[0].nf,n=3*nf+6;SharedPointSystem out{Eigen::MatrixXd::Zero(n,n),Eigen::MatrixXd::Zero(3,n),Eigen::VectorXd::Zero(n),nf,node,std::move(films)};
 for(unsigned f=0;f<3;++f){auto&film=out.films[f];out.M.block(f*nf,f*nf,nf,nf)=film.M.topLeftCorner(nf,nf);out.velocity.segment(f*nf,nf)=film.film.pack(v);Eigen::Vector3d point=layout.world(f,model.rest()[node]),normal=(point-layout.bodyCenter).normalized(),local=layout.mount[f].R.transpose()*normal;
  for(unsigned d=0;d<3;++d){unsigned a=3*node+d;if(film.film.index[a]>=0)out.J(f,f*nf+film.film.index[a])+=film.film.weight[a]*local(d);}out.J.block<1,3>(f,3*nf)=-normal.transpose();
 }
 out.M.block<3,3>(3*nf,3*nf).diagonal().setConstant(.0001);out.M.block<3,3>(3*nf+3,3*nf+3).diagonal().setConstant(.4*.0001*layout.bodyRadius*layout.bodyRadius);out.velocity.tail<3>()=Eigen::Vector3d(.1,.2,.3);return out;
}
}
