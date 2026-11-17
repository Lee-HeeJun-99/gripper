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
 auto uncached=System(m,triangles,b,1,false,false).advance(0,control);check(uncached.state.q==result.state.q&&uncached.state.v==result.state.v&&uncached.state.body.center==result.state.body.center&&uncached.state.body.linear==result.state.body.linear,"exact accepted cache changes physical states");check(result.acceptedReuses>0&&uncached.acceptedReuses==0&&uncached.evaluations>result.evaluations,"cache call-count coverage absent");
 Body bp=b,bm=b;double delta=1e-4;bp.linear.z()+=delta;bm.linear.z()-=delta;auto plusEvent=System(m,triangles,bp,1).advance(0,control),minusEvent=System(m,triangles,bm,1).advance(0,control);check(result.eventIncomingSensitivity.size()==system.n&&plusEvent.event&&minusEvent.event,"unique event sensitivity unavailable");double eventFD=(plusEvent.event->fraction-minusEvent.event->fraction)/(2*delta);check(std::abs(eventFD-result.eventIncomingSensitivity(system.nf+2))<1e-6,"coupled moving-body event IFT FD");
 // Smooth face branch: all reduced-film and center cross-Hessian entries.
 unsigned id=8;State state=system.before;state.body.center={38,8,-1.4};auto row=system.geometry(state,id);double dg=0,dh=0,h=1e-5;
 for(unsigned k=0;k<system.nf+3;++k){State plus=state,minus=state;if(k<system.nf){Eigen::VectorXd e=Eigen::VectorXd::Zero(system.nf);e(k)=h;auto delta=m.expand(e);for(unsigned i=0;i<q.size();++i)for(unsigned d=0;d<3;++d){plus.q[i][d]+=delta[i][d];minus.q[i][d]-=delta[i][d];}}else{plus.body.center(k-system.nf)+=h;minus.body.center(k-system.nf)-=h;}auto a=system.geometry(plus,id),c=system.geometry(minus,id);check(a.feature==row.feature&&c.feature==row.feature,"FD crossed nonsmooth feature");dg=std::max(dg,std::abs((a.gap-c.gap)/(2*h)-row.gradient(k)));dh=std::max(dh,((a.gradient-c.gradient)/(2*h)-row.hessian.col(k)).norm());}
 check(dg<1e-8&&dh<1e-7,"shared relative geometry gradient/Hessian FD");
 State touching=system.before;touching.v=zero;touching.body.center=vector(model.rest()[tip])-Eigen::Vector3d(0,0,1);touching.body.linear.setZero();CoupledPlaneStep hold(model,mass,1e-5,2,0,touching.q,touching.v,zero,0);System held(hold,triangles,touching.body,1);auto atRest=held.advance(0,control);check(atRest.minimumGap>=-1e-10,"rest touching gap");
 touching.body.linear.z()=-.1;System releasing(hold,triangles,touching.body,1);auto release=releasing.advance(0,control);check(release.minimumGap>0&&release.constraintImpulse.size()==0,"physical outward release");
 // Independent loaded constrained solve: full 2G=J^T p,not selected gap only.
 Body loadedBody=touching.body;loadedBody.linear.setZero();loadedBody.force.z()=.01;System loaded(hold,triangles,loadedBody,1);auto load=loaded.smooth(0,control,true);Eigen::VectorXd middle=(loaded.pack(load.state)+loaded.pack(loaded.before))/2;Eigen::VectorXd residual=2*loaded.evaluate(middle,load.tension).gradient;
 for(unsigned k=0;k<load.contactRows.size();++k)residual-=load.contactRows[k].gradient*load.constraintImpulse(k);check(load.minimumGap>=-1e-10&&load.sustained&&residual.norm()<1e-14,"coupled constrained physical momentum");
 std::cout<<"PASS moving whole-surface event fraction "<<result.event->fraction<<" rows "<<result.event->rows.size()<<" gap "<<result.minimumGap<<" geometryFD "<<dg<<' '<<dh<<" loadedResidual "<<residual.norm()<<" eventIFTerror "<<std::abs(eventFD-result.eventIncomingSensitivity(system.nf+2))<<" stageCalls "<<result.evaluations<<'/'<<uncached.evaluations<<";independent model,NOT SOFA/grasp\n";
 System midpointSystem(hold,triangles,loadedBody,1,false,true,true);
 auto midpointLoad=midpointSystem.smooth(0,control,true);check(midpointLoad.minimumGap>=-1e-10&&midpointLoad.sustained,"midpoint contact solve missing");
 Eigen::VectorXd ym=(midpointSystem.pack(midpointLoad.state)+midpointSystem.pack(midpointSystem.before))/2;
 Eigen::VectorXd rm=2*midpointSystem.evaluate(ym,midpointLoad.tension).gradient;
 for(unsigned k=0;k<midpointLoad.contactRows.size();++k)rm-=midpointLoad.contactRows[k].gradient*midpointLoad.constraintImpulse(k);
 check(rm.norm()<1e-14,"midpoint force/Jacobian ownership residual");
 // Actual force-geometry chain rule dJ_mid/dy = h/2 H_mid,not h H_end.
 auto gm=midpointSystem.forceGeometry(midpointLoad.state);auto rmid=midpointSystem.geometry(gm,8);double midpointFD=0;
 for(unsigned k=0;k<midpointSystem.nf+3;++k){auto yp=ym,yn=ym;yp(k)+=1e-4;yn(k)-=1e-4;
  auto rp=midpointSystem.geometry(midpointSystem.forceGeometry(midpointSystem.endpoint(yp)),8);
  auto rn=midpointSystem.geometry(midpointSystem.forceGeometry(midpointSystem.endpoint(yn)),8);
  midpointFD=std::max(midpointFD,((rp.gradient-rn.gradient)/2e-4-.5*hold.h*rmid.hessian.col(k)).norm());}
 check(midpointFD<1e-8,"midpoint geometry consistent tangent FD");
 System tighter(hold,triangles,loadedBody,1,true,true,true,1e-17);check(tighter.residualThreshold(0)==1e-17,"explicit tighter absolute residual not applied");
 bool looseRejected=false;try{System invalid(hold,triangles,loadedBody,1,false,true,false,1e-14);}catch(const std::invalid_argument&){looseRejected=true;}check(looseRejected,"new solver setting weakens original tolerance");
 Eigen::MatrixXd tinyW=Eigen::MatrixXd::Identity(1,1);Eigen::VectorXd tinyD(1);tinyD(0)=-1e-12;auto oldTiny=CoupledContactStep::dual(tinyW,tinyD,Eigen::VectorXd::Zero(1)),tightTiny=accurateDual(tinyW,tinyD,Eigen::VectorXd::Zero(1),1e-14);
 check(oldTiny(0)==0&&std::abs(tightTiny(0)-1e-12)<1e-25,"validation threshold used as solve stopping floor counterexample");
 std::cout<<"PASS experimental midpoint force chain-rule FD "<<midpointFD<<" momentum "<<rm.norm()<<";NOT time/energy qualified\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
