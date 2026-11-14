#include "../models/finite_rotation/FiniteRotationShear.cpp"
#include <sofa/component/statecontainer/MechanicalObject.h>
#include <random>
#include <iostream>
using namespace regrip3d;
using Base=regrip3d::Inherit;
void require(bool b,const char*s){if(!b)throw std::runtime_error(s);}
struct Accumulator:sofa::core::behavior::StiffnessMatrixAccumulator {
 double data[24][24]{};
 void add(sofa::SignedIndex r,sofa::SignedIndex c,double v)override{data[r][c]+=v;}
 void add(sofa::SignedIndex r,sofa::SignedIndex c,float v)override{add(r,c,double(v));}
};
int main(){try{
 std::mt19937 rng(71);std::uniform_real_distribution<double>d(-1.,1.);double eg=0,jg=0,obj=0,balance=0;
 for(int z=0;z<60;++z){Pose l,u;l.p={d(rng),d(rng),d(rng)};u.p=add(l.p,V{.1*d(rng),.1*d(rng),.4+.1*d(rng)});l.q=exp(V{d(rng),d(rng),d(rng)});u.q=exp(V{d(rng),d(rng),d(rng)});
  auto r=evaluate(l,u,1.,.4);
  for(int a=0;a<12;++a){Pose lp=l,lm=l,up=u,um=u;if(a<6){lp=increment(l,a,1e-6);lm=increment(l,a,-1e-6);}else{up=increment(u,a-6,1e-6);um=increment(u,a-6,-1e-6);}auto p=evaluate(lp,up,1.,.4),m=evaluate(lm,um,1.,.4);
   eg=std::max(eg,std::abs((p.energy-m.energy)/2e-6+r.force[a]));
   for(int b=0;b<12;++b){jg=std::max(jg,std::abs((p.force[b]-m.force[b])/2e-6-r.jacobian[12*b+a]));require(std::abs(r.chart_hessian[12*a+b]-r.chart_hessian[12*b+a])<1e-13,"chart Hessian symmetry");}}
  auto Qg=exp(V{d(rng),d(rng),d(rng)});V t{d(rng),d(rng),d(rng)};Pose lr{add(rotate(Qg,l.p),t),multiply(Qg,l.q)},ur{add(rotate(Qg,u.p),t),multiply(Qg,u.q)};auto rr=evaluate(lr,ur,1.,.4);obj=std::max(obj,std::abs(rr.energy-r.energy));
  V fl{r.force[0],r.force[1],r.force[2]},fu{r.force[6],r.force[7],r.force[8]},tl{r.force[3],r.force[4],r.force[5]},tu{r.force[9],r.force[10],r.force[11]};auto moment=add(add(tl,tu),add(cross(l.p,fl),cross(u.p,fu)));for(double v:moment)balance=std::max(balance,std::abs(v));
  for(int o:{0,3,6,9}){auto rf=rotate(Qg,V{r.force[o],r.force[o+1],r.force[o+2]});for(int c=0;c<3;++c)require(std::abs(rf[c]-rr.force[o+c])<1e-12,"force covariance");}
 }
 require(eg<1e-9,"energy gradient FD");require(jg<1e-8,"spatial tangent FD");require(obj<1e-13,"objectivity");require(balance<1e-13,"net moment");
 double previous=1;for(double theta:{.004,.002,.001}){Pose l{{0,0,-.2},exp(V{0,theta,0})},u{{.0001,0,.2},exp(V{0,theta,0})};double error=std::abs(evaluate(l,u,1,.4).slip-(.0001-.4*theta));require(error<previous,"small-angle limit");previous=error;}
 bool rejected=false;try{Pose bad;bad.q={0,0,0,2};evaluate(bad,Pose{},1,.4);}catch(const std::invalid_argument&){rejected=true;}require(rejected,"invalid quaternion rejection");
 auto state=sofa::core::objectmodel::New<sofa::component::statecontainer::MechanicalObject<Types>>();state->resize(4);auto ff=sofa::core::objectmodel::New<FiniteRotationShear>(state.get());ff->nodes.setValue(2);
 Base::VecCoord x(4);for(int i=0;i<4;++i){x[i].getCenter()[0]=i%2;x[i].getCenter()[2]=i<2?-.2:.2;x[i].getOrientation()=sofa::type::Quat<double>(0,0,0,1);}x[3].getCenter()[0]+=.001;state->write(sofa::core::vec_id::write_access::position)->setValue(x);
 Base::DataVecCoord xd;xd.setValue(x);Base::DataVecDeriv f,v,dx,df;f.setValue(Base::VecDeriv(4));v.setValue(Base::VecDeriv(4));ff->addForce(nullptr,f,xd,v);require(std::abs(f.getValue()[3][0]+.001)<1e-14,"SOFA addForce");
 Base::VecDeriv delta(4);delta[3][0]=.01;dx.setValue(delta);df.setValue(Base::VecDeriv(4));sofa::core::MechanicalParams mp;mp.setKFactor(2.5);ff->addDForce(&mp,df,dx);require(std::abs(df.getValue()[3][0]+.025)<1e-14,"SOFA addDForce/kFactor");
 Accumulator acc;sofa::core::behavior::StiffnessMatrix matrix;matrix.setMatrixAccumulator(&acc,state.get());ff->buildStiffnessMatrix(&matrix);auto expected=evaluate(ff->pose(x[1]),ff->pose(x[3]),1,.4);
 for(int a=0;a<12;++a)for(int b=0;b<12;++b)require(std::abs(acc.data[6*(1+2*(a/6))+a%6][6*(1+2*(b/6))+b%6]-expected.jacobian[12*a+b])<1e-14,"SOFA stiffness assembly/6DOF");
 std::cout<<"PASS states=60 energy_fd="<<eg<<" spatial_jacobian_fd="<<jg<<" objectivity="<<obj<<" net_moment="<<balance<<"\n";return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<"\n";return 1;}}
