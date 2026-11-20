// Missing gyroscopic force ONLY. Native mass,ODE,linear solver and contact retained.
#include <sofa/core/behavior/ForceField.h>
#include <sofa/core/MechanicalParams.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/linearalgebra/BaseMatrix.h>
#include <fstream>
#include <iomanip>
namespace regrip {
using R=sofa::defaulttype::Rigid3Types;using FF=sofa::core::behavior::ForceField<R>;
using V=sofa::type::Vec<3,SReal>;using M=sofa::type::Mat<3,3,SReal>;
class NativeInertiaForce:public FF {
public:
 SOFA_CLASS(NativeInertiaForce,FF);
 sofa::core::objectmodel::Data<M> localInertia;
 sofa::core::objectmodel::Data<std::string> filename;std::ofstream log;
 unsigned forceCalls=0,kCalls=0,bCalls=0,dCalls=0;
 NativeInertiaForce():localInertia(initData(&localInertia,M(),"localInertia","Actual geometric COM inertia kg m2 in body coordinates")),filename(initData(&filename,std::string(),"filename","Exclusive force and derivative validation journal")){}
 struct Value{V force;M K,B,I;};
 Value evaluate(const R::Coord&q,const V&w)const{
  M rot;q.getOrientation().toMatrix(rot);Value a{};a.I=rot*localInertia.getValue()*rot.transposed();const auto L=a.I*w;a.force=-sofa::type::cross(w,L);
  for(unsigned j=0;j<3;++j){V e{};e[j]=1;M dI; // left/world infinitesimal rotation
   for(unsigned k=0;k<3;++k){V column;for(unsigned h=0;h<3;++h)column[h]=a.I[h][k];const auto c=sofa::type::cross(e,column)-a.I*sofa::type::cross(e,V(k==0,k==1,k==2));for(unsigned h=0;h<3;++h)dI[h][k]=c[h];}
   const auto dq=-sofa::type::cross(w,dI*w);const auto dv=-sofa::type::cross(e,L)-sofa::type::cross(w,a.I*e);
   for(unsigned k=0;k<3;++k){a.K[k][j]=dq[k];a.B[k][j]=dv[k];}
  }return a;
 }
 Value current()const{const auto&q=this->mstate->read(sofa::core::vec_id::read_access::position)->getValue();const auto&v=this->mstate->read(sofa::core::vec_id::read_access::velocity)->getValue();if(q.size()!=1||v.size()!=1)throw std::runtime_error("single COM body only");return evaluate(q[0],v[0].getVOrientation());}
 void init()override{
  FF::init();if(!this->mstate||std::ifstream(filename.getValue()))throw std::runtime_error("explicit COM state and unique journal required");
  const auto I=localInertia.getValue();if(I[0][0]<=0||I[1][1]<=0||I[2][2]<=0)throw std::runtime_error("nonpositive inertia");
  log.open(filename.getValue());log<<std::setprecision(17)<<"kind,time_s,force_calls,K_calls,B_calls,D_calls,value0,value1\n";
  const auto q=this->mstate->read(sofa::core::vec_id::read_access::position)->getValue()[0];const auto w=this->mstate->read(sofa::core::vec_id::read_access::velocity)->getValue()[0].getVOrientation();const auto a=evaluate(q,w);SReal eK=0,eB=0,nK=0,nB=0;const SReal h=1e-5;
  for(unsigned j=0;j<3;++j){V e{};e[j]=1;auto qp=q,qm=q;sofa::type::Quat<SReal> dp(e,h),dm(e,-h);qp.getOrientation()=dp*q.getOrientation();qm.getOrientation()=dm*q.getOrientation();const auto K=(evaluate(qp,w).force-evaluate(qm,w).force)/(2*h);const auto B=(evaluate(q,w+e*h).force-evaluate(q,w-e*h).force)/(2*h);
   for(unsigned k=0;k<3;++k){eK+=(K[k]-a.K[k][j])*(K[k]-a.K[k][j]);nK+=a.K[k][j]*a.K[k][j];eB+=(B[k]-a.B[k][j])*(B[k]-a.B[k][j]);nB+=a.B[k][j]*a.B[k][j];}}
  log<<"FD,0,0,0,0,0,"<<(nK?std::sqrt(eK/nK):std::sqrt(eK))<<','<<(nB?std::sqrt(eB/nB):std::sqrt(eB))<<'\n';log.flush();
 }
 void addForce(const sofa::core::MechanicalParams*,DataVecDeriv&f,const DataVecCoord&q,const DataVecDeriv&v)override{if(q.getValue().size()!=1)throw std::runtime_error("single body only");const auto a=evaluate(q.getValue()[0],v.getValue()[0].getVOrientation());auto*o=f.beginEdit();o->resize(1);(*o)[0].getVOrientation()+=a.force;f.endEdit();++forceCalls;log<<"FORCE,"<<getContext()->getTime()<<','<<forceCalls<<','<<kCalls<<','<<bCalls<<','<<dCalls<<",\""<<a.force<<"\",0\n";log.flush();}
 void addDForce(const sofa::core::MechanicalParams*p,DataVecDeriv&df,const DataVecDeriv&dx)override{auto a=current();auto*out=df.beginEdit();out->resize(1);(*out)[0].getVOrientation()+=(a.K*p->kFactor()+a.B*p->bFactor())*dx.getValue()[0].getVOrientation();df.endEdit();++dCalls;}
 void addKToMatrix(sofa::linearalgebra::BaseMatrix*mat,SReal factor,unsigned&offset)override{const auto a=current();for(unsigned i=0;i<3;++i)for(unsigned j=0;j<3;++j)mat->add(offset+3+i,offset+3+j,factor*a.K[i][j]);++kCalls;log<<"K,"<<getContext()->getTime()<<','<<forceCalls<<','<<kCalls<<','<<bCalls<<','<<dCalls<<",0,0\n";log.flush();}
 void addBToMatrix(sofa::linearalgebra::BaseMatrix*mat,SReal factor,unsigned&offset)override{const auto a=current();for(unsigned i=0;i<3;++i)for(unsigned j=0;j<3;++j)mat->add(offset+3+i,offset+3+j,factor*a.B[i][j]);++bCalls;log<<"B,"<<getContext()->getTime()<<','<<forceCalls<<','<<kCalls<<','<<bCalls<<','<<dCalls<<",0,0\n";log.flush();}
 SReal getPotentialEnergy(const sofa::core::MechanicalParams*,const DataVecCoord&)const override{return 0;}
};
}
extern "C" {
__attribute__((visibility("default"))) void initExternalModule(){}
__attribute__((visibility("default"))) const char*getModuleName(){return "ReGripInertiaForce";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Scoped missing gyroscopic force with nonsymmetric world rotation/velocity derivatives;NO ODE/contact solver").add<regrip::NativeInertiaForce>());}
}
