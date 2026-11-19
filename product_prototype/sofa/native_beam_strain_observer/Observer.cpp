#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <BeamAdapter/component/BeamInterpolation.h>
#include <fstream>
#include <iomanip>

// Queries the installed interpolation API only;no ForceField,ODE or state update.
class NativeBeamStrainObserver:public sofa::core::objectmodel::BaseObject {
public:
    SOFA_CLASS(NativeBeamStrainObserver,sofa::core::objectmodel::BaseObject);
    using Types=sofa::defaulttype::Rigid3Types;
    using State=sofa::core::behavior::MechanicalState<Types>;
    using Interpolation=beamadapter::BeamInterpolation<Types>;
    using Transform=Interpolation::Transform;
    using BaseLink=sofa::core::objectmodel::BaseLink;
    sofa::core::objectmodel::SingleLink<NativeBeamStrainObserver,State,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>body;
    sofa::core::objectmodel::SingleLink<NativeBeamStrainObserver,Interpolation,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>interpolation;
    sofa::core::objectmodel::Data<std::string>filename;
    sofa::core::objectmodel::Data<Types::VecCoord>privatePositions;
    NativeBeamStrainObserver():body(initLink("body","Actual unchanged state")),interpolation(initLink("interpolation","Installed native interpolation")),filename(initData(&filename,std::string(),"filename","Exclusive PRIVATE strain journal")),privatePositions(initData(&privatePositions,Types::VecCoord(),"privatePositions","PRIVATE pose;never installed")){}
    void bwdInit()override {
        BaseObject::bwdInit();
        if(!body||!interpolation||std::ifstream(filename.getValue()))throw std::runtime_error("unique explicit strain observer required");
        const auto actual=body->read(sofa::core::vec_id::read_access::position)->getValue();
        const auto velocity=body->read(sofa::core::vec_id::read_access::velocity)->getValue();
        const auto q=privatePositions.getValue();if(q.size()!=actual.size())throw std::runtime_error("private size mismatch");
        std::ofstream out(filename.getValue());out<<std::setprecision(17)<<"beam,node0,node1,L_m,EA_N,local0_x_m,rest0_x_m,local1_x_m,rest1_x_m,u0x_m,u1x_m,delta_axial_m,axial0_N,axis_x,axis_y,axis_z,chord_m,relative_projected_m,absolute_projected_m\n";
        for(sofa::Index b=0;b<interpolation->getNumBeams();++b){
            sofa::Index n0,n1;interpolation->getNodeIndices(b,n0,n1);
            Transform g0,g1,mid,r0,r1;interpolation->computeTransform(b,n0,n1,g0,g1,q);
            const double L=interpolation->getLength(b);
            interpolation->InterpolateTransformUsingSpline(mid,.5,g0,g1,L);
            auto local0=mid.inversed()*g0,local1=mid.inversed()*g1;
            interpolation->getSplineRestTransform(b,r0,r1);
            const auto u0=local0.CreateSpatialVector()-r0.CreateSpatialVector();
            const auto u1=local1.CreateSpatialVector()-r1.CreateSpatialVector();
            double length,area,Iy,Iz,Asy,Asz,J,E,nu,rho;
            interpolation->getInterpolationParameters(b,length,area,Iy,Iz,Asy,Asz,J);
            interpolation->getMechanicalParameters(b,E,nu,rho);
            const auto axis=mid.getOrientation().rotate(Interpolation::Vec3(1,0,0));
            const auto relative=mid.getOrientation().inverseRotate(g1.getOrigin()-g0.getOrigin());
            const double delta=u1.getLinearVelocity()[0]-u0.getLinearVelocity()[0];
            out<<b<<','<<n0<<','<<n1<<','<<L<<','<<E*area<<','<<local0.getOrigin()[0]<<','<<r0.getOrigin()[0]<<','<<local1.getOrigin()[0]<<','<<r1.getOrigin()[0]<<','<<u0.getLinearVelocity()[0]<<','<<u1.getLinearVelocity()[0]<<','<<delta<<','<<E*area/length*delta<<','<<axis[0]<<','<<axis[1]<<','<<axis[2]<<','<<(g1.getOrigin()-g0.getOrigin()).norm()<<','<<relative[0]<<','<<local1.getOrigin()[0]-local0.getOrigin()[0]<<'\n';
        }
        if(actual!=body->read(sofa::core::vec_id::read_access::position)->getValue()||velocity!=body->read(sofa::core::vec_id::read_access::velocity)->getValue())throw std::runtime_error("strain observer mutated q/v");
    }
};
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripNativeStrainObserver";}
__attribute__((visibility("default")))const char*getModuleVersion(){return "1";}
__attribute__((visibility("default")))const char*getModuleLicense(){return "Research";}
__attribute__((visibility("default")))const char*getModuleDescription(){return "Read-only installed BeamAdapter strain diagnostic";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("PRIVATE native beam strain query;no physics update").add<NativeBeamStrainObserver>());}
}
