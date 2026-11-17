#include "../models/film_coupled_contact/CoupledSphere.h"
#include <iostream>
using namespace regrip_coupled;
void check(bool value,const char*message){if(!value)throw std::runtime_error(message);}
int main(){try{
 Assembly model(5);auto mass=model.masses();std::vector<Point>q(model.size()),v(model.size()),zero(model.size());unsigned tip=model.id(0,4,2);v[tip][2]=-3;
 std::vector<std::array<unsigned,3>>triangles;for(unsigned part=0;part<3;++part)for(unsigned i=0;i+1<model.nx;++i)for(unsigned j=0;j+1<model.parts[part].ny;++j){unsigned a=model.id(part,i,j),b=model.id(part,i+1,j),c=model.id(part,i,j+1),d=model.id(part,i+1,j+1);triangles.push_back({a,b,c});triangles.push_back({b,d,c});}
 Body b;b.center=vector(model.rest()[tip])-Eigen::Vector3d(0,0,1.001);b.linear={.1,0,.03};b.angular={.1,.2,.3};
 CoupledPlaneStep m(model,mass,.001,2,0,q,v,zero,0);System system(m,triangles,b,1);EventControl control;
 auto result=system.advance(0,control);check(bool(result.event)&&bool(result.impact),"coupled moving sphere event absent");check(result.minimumGap>=-1e-10,"coupled endpoint gap");check(result.impact->state.momentumResidual<1e-18,"coupled impact momentum");check(result.impact->state.normalVelocity.minCoeff()>=-1e-10,"relative velocity condition");check((result.postImpact.body.linear-result.preImpact.body.linear).norm()>0,"body impulse omitted");check(result.postImpact.body.angular==result.preImpact.body.angular,"sphere radial normal creates spurious spin");
 Eigen::Vector3d bodyImpulse=b.mass*(result.postImpact.body.linear-result.preImpact.body.linear),expected=Eigen::Vector3d::Zero();for(unsigned k=0;k<result.event->rows.size();++k)expected-=system.geometry(result.eventState,result.event->rows[k].triangle).normal*result.impact->state.impulse(k);check((bodyImpulse-expected).norm()<1e-18,"equal opposite actual sphere impulse");
 auto repeated=system.advance(0,control);check(repeated.state.q==result.state.q&&repeated.state.v==result.state.v&&repeated.state.body.center==result.state.body.center,"impure coupled query");
 // Smooth face branch: all reduced-film and center cross-Hessian entries.
 unsigned id=8;State state=system.before;state.body.center={38,8,-1.4};auto row=system.geometry(state,id);double dg=0,dh=0,h=1e-5;
 for(unsigned k=0;k<system.nf+3;++k){State plus=state,minus=state;if(k<system.nf){Eigen::VectorXd e=Eigen::VectorXd::Zero(system.nf);e(k)=h;auto delta=m.expand(e);for(unsigned i=0;i<q.size();++i)for(unsigned d=0;d<3;++d){plus.q[i][d]+=delta[i][d];minus.q[i][d]-=delta[i][d];}}else{plus.body.center(k-system.nf)+=h;minus.body.center(k-system.nf)-=h;}auto a=system.geometry(plus,id),c=system.geometry(minus,id);check(a.feature==row.feature&&c.feature==row.feature,"FD crossed nonsmooth feature");dg=std::max(dg,std::abs((a.gap-c.gap)/(2*h)-row.gradient(k)));dh=std::max(dh,((a.gradient-c.gradient)/(2*h)-row.hessian.col(k)).norm());}
 check(dg<1e-8&&dh<1e-7,"shared relative geometry gradient/Hessian FD");
 State touching=system.before;touching.v=zero;touching.body.center=vector(model.rest()[tip])-Eigen::Vector3d(0,0,1);touching.body.linear.setZero();CoupledPlaneStep hold(model,mass,1e-5,2,0,touching.q,touching.v,zero,0);System held(hold,triangles,touching.body,1);auto atRest=held.advance(0,control);check(atRest.minimumGap>=-1e-10,"rest touching gap");
 touching.body.linear.z()=-.1;System releasing(hold,triangles,touching.body,1);auto release=releasing.advance(0,control);check(release.minimumGap>0&&release.constraintImpulse.size()==0,"physical outward release");
 // Independent loaded constrained solve: full 2G=J^T p,not selected gap only.
 Body loadedBody=touching.body;loadedBody.linear.setZero();loadedBody.force.z()=.01;System loaded(hold,triangles,loadedBody,1);auto load=loaded.smooth(0,control,true);Eigen::VectorXd middle=(loaded.pack(load.state)+loaded.pack(loaded.before))/2;Eigen::VectorXd residual=2*loaded.evaluate(middle,load.tension).gradient;
 for(unsigned k=0;k<load.contactRows.size();++k)residual-=load.contactRows[k].gradient*load.constraintImpulse(k);check(load.minimumGap>=-1e-10&&load.sustained&&residual.norm()<1e-14,"coupled constrained physical momentum");
 std::cout<<"PASS moving whole-surface event fraction "<<result.event->fraction<<" rows "<<result.event->rows.size()<<" gap "<<result.minimumGap<<" geometryFD "<<dg<<' '<<dh<<" loadedResidual "<<residual.norm()<<";independent model,NOT SOFA/grasp\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
