#include "../models/curved_contact/CurvedContact.cpp"
#include <sofa/component/statecontainer/MechanicalObject.h>
using namespace regrip_integrated;
void require(bool x,const char*why){if(!x)throw std::runtime_error(why);}
template<class Parent>struct Accumulator:Parent{double a[18][18]{};void add(sofa::SignedIndex r,sofa::SignedIndex c,double v)override{a[r][c]+=v;}void add(sofa::SignedIndex r,sofa::SignedIndex c,float v)override{add(r,c,double(v));}};
int main(){try{
 double referenceError=0,sagError=0;
 for(int i=0;i<60;++i){Pose a,b,o;a.p={-.3,.9,.02};b.p={.3,.9,-.01};a.q=exp(V{.01*i,.005*i,-.004*i});b.q=exp(V{-.003*i,-.006*i,.003*i});double s=(i+.5)/60;auto p=regrip_curve::point(a,b,s,.6);Pose pp;for(int j=0;j<3;++j)pp.p[j]=p[j].v;
  auto leaf=regrip_birthlaw::evaluate(pp,o,{},V{0,1.3,.02},0,1,5,.2,1,1,.3);auto ref=regrip_curve::pullback(p,leaf.wrench),fast=regrip_curved::map(a,b,s,.6,leaf.wrench);for(int j=0;j<18;++j)referenceError=std::max(referenceError,std::abs(ref.force[j]-fast.force[j]));for(int j=0;j<324;++j)referenceError=std::max(referenceError,std::abs(ref.jacobian[j]-fast.jacobian[j]));
  auto pos=regrip_curved::position(a,b,s,.6);auto line=add(scale(a.p,1-s),scale(b.p,s));auto delta=sub(pos,line);sagError=std::max(sagError,std::sqrt(dot(delta,delta))-regrip_curved::sagBound(a,b,.6));
 }
 require(referenceError<1e-12&&sagError<1e-14,"dense Hermite reference and conservative sag envelope");
 std::cout<<"PASS curved map reference="<<referenceError<<" sag_excess="<<sagError<<'\\n';

 using State=sofa::component::statecontainer::MechanicalObject<Types>;auto state=sofa::core::objectmodel::New<State>();state->resize(3);Inherit::VecCoord x(3);x[0].getCenter()={-.5,1.01,0};x[1].getCenter()={.5,1.01,0};for(auto&p:x)p.getOrientation()={0,0,0,1};
 state->write(sofa::core::vec_id::write_access::position)->setValue(x);state->write(sofa::core::vec_id::write_access::restPosition)->setValue(x);
 auto field=sofa::core::objectmodel::New<CurvedMaterialContact>(state.get());field->segments.setValue({0,1});field->objectIndex.setValue(2);field->shape.setValue(2);field->radius.setValue(1.);field->pointRadius.setValue(.02);field->mu.setValue(.3);field->lineStiffness.setValue(1.);field->tangentLineStiffness.setValue(1.);field->historySpacing.setValue(.02);field->prepare(x);
 double D=0,error=0;
 for(int step=1;step<=20;++step){x[0].getCenter()[2]=x[1].getCenter()[2]=step*.001;double beforeQuery=field->committedPlastic;auto r=field->compute(x);auto scalar=field->computeValue(x);for(int j=0;j<18;++j)error=std::max(error,std::abs(r.a.f[j]-scalar.a.f[j]));require(field->compute(x).a.f==r.a.f,"repeat pure query");require(field->committedPlastic==beforeQuery,"query never commits");double prior=field->committedPlastic;field->commit(x);D+=r.D;require(std::abs(field->committedPlastic-prior-r.D)<1e-16,"observed and actual point plastic same");}
 require(std::abs(D-.003*(.020-.003))<1e-14,"uniform plane analytic Coulomb dissipation");require(error<1e-13,"AD and scalar wrench same");std::cout<<std::setprecision(17)<<"PASS plane D="<<D<<" scalar_error="<<error<<'\n';
 // Frozen history, smooth stick branch: actual assembly finite differences.
 x[0].getCenter()[2]-=.0001;x[1].getCenter()[2]-=.0001;auto a=field->assemble(x);double fd=0;
 for(int k=0;k<18;++k){auto plus=x,minus=x;auto p=increment(field->pose(x[k/6]),k%6,1e-7),m=increment(field->pose(x[k/6]),k%6,-1e-7);for(int j=0;j<3;++j){plus[k/6].getCenter()[j]=p.p[j];minus[k/6].getCenter()[j]=m.p[j];}for(int j=0;j<4;++j){plus[k/6].getOrientation()[j]=p.q[j];minus[k/6].getOrientation()[j]=m.q[j];}auto ap=field->assemble(plus),am=field->assemble(minus);double J[18]{};for(auto&t:a.J)if(t.c==unsigned(k))J[t.r]+=t.v;for(int j=0;j<18;++j)fd=std::max(fd,std::abs((ap.f[j]-am.f[j])/2e-7-J[j]));}
 require(fd<1e-7,"actual field force Jacobian FD");state->write(sofa::core::vec_id::write_access::position)->setValue(x);Inherit::DataVecDeriv dx,df,force,velocity;Inherit::DataVecCoord pos;pos.setValue(x);Inherit::VecDeriv delta(3);for(auto&v:delta)for(int j=0;j<6;++j)v[j]=.001*(j+1);dx.setValue(delta);velocity.setValue(Inherit::VecDeriv(3));force.setValue(Inherit::VecDeriv(3));sofa::core::MechanicalParams mp;field->addForce(&mp,force,pos,velocity);for(int j=0;j<18;++j)require(std::abs(force.getValue()[j/6][j%6]-a.f[j])<1e-13,"addForce");
 for(double f:{0.,2.5,-.25}){mp.setKFactor(f);df.setValue(Inherit::VecDeriv(3));field->addDForce(&mp,df,dx);double expected[18]{};for(auto&t:a.J)expected[t.r]+=f*t.v*delta[t.c/6][t.c%6];for(int j=0;j<18;++j)require(std::abs(df.getValue()[j/6][j%6]-expected[j])<1e-13,"addDForce factor");}
 Accumulator<sofa::core::behavior::StiffnessMatrixAccumulator>acc;sofa::core::behavior::StiffnessMatrix matrix;matrix.setMatrixAccumulator(&acc,state.get());field->buildStiffnessMatrix(&matrix);double J[18][18]{};for(auto&t:a.J)J[t.r][t.c]+=t.v;for(int i=0;i<18;++i)for(int j=0;j<18;++j)require(std::abs(J[i][j]-acc.a[i][j])<1e-13,"matrix accumulator");
 // Curved patch exists although the straight chord misses the sphere.
 auto curvedState=sofa::core::objectmodel::New<State>();curvedState->resize(3);auto cx=x;cx[0].getCenter()={-1,1.3,0};cx[1].getCenter()={1,1.3,0};auto qa=exp(V{0,0,-.9}),qb=exp(V{0,0,.9});for(int j=0;j<4;++j){cx[0].getOrientation()[j]=qa[j];cx[1].getOrientation()[j]=qb[j];}
 curvedState->write(sofa::core::vec_id::write_access::position)->setValue(cx);curvedState->write(sofa::core::vec_id::write_access::restPosition)->setValue(cx);
 auto curve=sofa::core::objectmodel::New<CurvedMaterialContact>(curvedState.get());curve->segments.setValue({0,1});curve->objectIndex.setValue(2);curve->radius.setValue(1);curve->pointRadius.setValue(.1);curve->historySpacing.setValue(.01);curve->prepare(cx);require(curve->compute(cx).a.contacts>0,"curved patch outside chord is detected");
 auto range=curve->interval(cx,0);for(unsigned i=0;i<curve->grids[0].count;++i){double s=(i+.5)/curve->grids[0].count;auto p=curve->point(cx,0,s);if(regrip_closure::sdf(p.p,0,1,5)<.1)require(s>=range.lo&&s<=range.hi,"broadphase cannot drop active curved point");}
 std::cout<<"PASS actual API FD="<<fd<<" force/dforce/matrix/query/commit\n";return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}

