#include <sofa/core/behavior/ForceField.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/VecTypes.h>
#include <cmath>
#include <algorithm>
namespace regrip_film {
// Same continuous ramp as the benchmark, evaluated at each actual step end.
// Unlike shifted LinearForceField keys this remains correct when dt changes.
class FilmRampLoad final:public sofa::core::behavior::ForceField<sofa::defaulttype::Vec3Types>{
public:
 using Types=sofa::defaulttype::Vec3Types;using Base=sofa::core::behavior::ForceField<Types>;
 SOFA_CLASS(FilmRampLoad,Base);
 sofa::core::objectmodel::Data<unsigned>ny;
 sofa::core::objectmodel::Data<double>totalForce,rampTime;
 FilmRampLoad():ny(initData(&ny,5u,"ny","Tip width nodes")),totalForce(initData(&totalForce,1e-6,"totalForce","Research ramp F")),rampTime(initData(&rampTime,10.,"rampTime","Ramp seconds")){}
 double force()const{if(!std::isfinite(totalForce.getValue()+rampTime.getValue())||rampTime.getValue()<=0)throw std::invalid_argument("film endpoint ramp");return totalForce.getValue()*std::clamp((getContext()->getTime()+getContext()->getDt())/rampTime.getValue(),0.,1.);}
 void addForce(const sofa::core::MechanicalParams*,DataVecDeriv&f,const DataVecCoord&x,const DataVecDeriv&)override{auto q=f.getValue();unsigned count=ny.getValue();if(!count||count>x.getValue().size())throw std::invalid_argument("tip width");double value=force()/count;for(unsigned i=q.size()-count;i<q.size();++i)q[i][2]+=value;f.setValue(q);}
 void addDForce(const sofa::core::MechanicalParams*,DataVecDeriv&,const DataVecDeriv&)override{}
 void buildStiffnessMatrix(sofa::core::behavior::StiffnessMatrix*)override{}
 SReal getPotentialEnergy(const sofa::core::MechanicalParams*,const DataVecCoord&x)const override{double value=0;unsigned count=ny.getValue();if(!count||count>x.getValue().size())throw std::invalid_argument("tip width");for(unsigned i=x.getValue().size()-count;i<x.getValue().size();++i)value-=force()*x.getValue()[i][2]/count;return value;}
};
void registerFilmRampLoad(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("End-of-actual-step prescribed ramp;external work is not stored film energy").add<FilmRampLoad>());}
}
