#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/core/behavior/ForceField.h>
#include <sofa/core/MechanicalParams.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/linearalgebra/FullMatrix.h>
#include <sofa/core/behavior/BaseMatrixLinearSystem.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <fstream>
#include <iomanip>
#include <cmath>

namespace diagnostic {
// Isolated initial-state query only. Never participates in force/ODE/constraint solve.
// Native internal-cache query effects must be checked against unobserved q/v.
class NativeElasticMatrixObserver:public sofa::core::objectmodel::BaseObject {
public:
    SOFA_CLASS(NativeElasticMatrixObserver,sofa::core::objectmodel::BaseObject);
    using Types=sofa::defaulttype::Vec3Types;
    using State=sofa::core::behavior::MechanicalState<Types>;
    using Field=sofa::core::behavior::ForceField<Types>;
    using BaseLink=sofa::core::objectmodel::BaseLink;
    sofa::core::objectmodel::SingleLink<NativeElasticMatrixObserver,State,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>body;
    sofa::core::objectmodel::SingleLink<NativeElasticMatrixObserver,Field,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>elastic;
    sofa::core::objectmodel::Data<std::string> filename;
    sofa::core::objectmodel::Data<Types::VecCoord> probePositions;
    NativeElasticMatrixObserver():body(initLink("body","Observed Vec3 native state")),elastic(initLink("elastic","Native elastic ForceField")),filename(initData(&filename,std::string(),"filename","Exclusive initial diagnostic prefix")),probePositions(initData(&probePositions,Types::VecCoord(),"probePositions","Optional PRIVATE force-query positions;never assigned to actual state")){}
    void bwdInit() override {
        BaseObject::bwdInit();
        if(!body||!elastic||std::ifstream(filename.getValue()+".matrix.csv"))throw std::runtime_error("unique explicitly linked native elastic diagnostic required");
        const auto q=body->read(sofa::core::vec_id::read_access::position)->getValue();
        const auto velocity=body->read(sofa::core::vec_id::read_access::velocity)->getValue();
        const unsigned n=q.size()*3;
        sofa::linearalgebra::FullMatrix<double> K(n,n);K.clear();unsigned offset=0;
        elastic->addKToMatrix(&K,-1.,offset); // positive stored-energy stiffness=-df/dq
        std::ofstream matrix(filename.getValue()+".matrix.csv");matrix<<std::setprecision(17)<<"i,j,K_N_per_m\n";
        for(unsigned i=0;i<n;++i)for(unsigned j=0;j<n;++j)if(K.element(i,j)!=0)matrix<<i<<','<<j<<','<<K.element(i,j)<<'\n';
        std::ofstream fd(filename.getValue()+".fd.csv");fd<<std::setprecision(17)<<"epsilon_m,force_fd_error_N_per_m,force_fd_norm_N_per_m\n";
        Types::VecDeriv direction(q.size());for(unsigned i=0;i<n;++i)direction[i/3][i%3]=std::sin(double(i+1));
        sofa::core::MechanicalParams params;
        auto evaluate=[&](double step){Field::DataVecCoord x;Field::DataVecDeriv v,f;auto displaced=q;
            for(unsigned i=0;i<q.size();++i)displaced[i]+=direction[i]*step;
            x.setValue(displaced);v.setValue(velocity);f.setValue(Types::VecDeriv(q.size()));
            elastic->addForce(&params,f,x,v);return f.getValue();};
        for(double epsilon:{1e-7,1e-8,1e-9}){
            auto plus=evaluate(epsilon),minus=evaluate(-epsilon);double error=0,norm=0;
            for(unsigned i=0;i<n;++i){double exact=0;for(unsigned j=0;j<n;++j)exact-=K.element(i,j)*direction[j/3][j%3];
                double derivative=(plus[i/3][i%3]-minus[i/3][i%3])/(2*epsilon);
                error+=(derivative-exact)*(derivative-exact);norm+=derivative*derivative;}
            fd<<epsilon<<','<<std::sqrt(error)<<','<<std::sqrt(norm)<<'\n';
        }
        if(!probePositions.getValue().empty()){
            if(probePositions.getValue().size()!=q.size())throw std::runtime_error("probe size mismatch");
            Field::DataVecCoord x;Field::DataVecDeriv v,f;
            x.setValue(probePositions.getValue());v.setValue(velocity);f.setValue(Types::VecDeriv(q.size()));
            elastic->addForce(&params,f,x,v);
            std::ofstream probe(filename.getValue()+".probe.csv");probe<<std::setprecision(17)<<"node,fx_N,fy_N,fz_N\n";
            const auto force=f.getValue();for(unsigned i=0;i<force.size();++i)probe<<i<<','<<force[i][0]<<','<<force[i][1]<<','<<force[i][2]<<'\n';
        }
        evaluate(0.); // restore the native force-query cache to the actual initial state
        if(q!=body->read(sofa::core::vec_id::read_access::position)->getValue()||velocity!=body->read(sofa::core::vec_id::read_access::velocity)->getValue())throw std::runtime_error("observer modified actual initial state");
    }
};
class NativeAssembledMatrixObserver:public sofa::core::objectmodel::BaseObject {
public:
    SOFA_CLASS(NativeAssembledMatrixObserver,sofa::core::objectmodel::BaseObject);
    using BaseLink=sofa::core::objectmodel::BaseLink;
    sofa::core::objectmodel::SingleLink<NativeAssembledMatrixObserver,sofa::core::behavior::BaseMatrixLinearSystem,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>system;
    sofa::core::objectmodel::Data<std::string>filename;bool written=false;
    NativeAssembledMatrixObserver():system(initLink("system","Actual native assembled matrix system")),filename(initData(&filename,std::string(),"filename","Exclusive post-step matrix CSV")){f_listening.setValue(true);}
    void handleEvent(sofa::core::objectmodel::Event* event) override {
        if(written||!dynamic_cast<sofa::simulation::AnimateEndEvent*>(event))return;
        if(!system||std::ifstream(filename.getValue()))throw std::runtime_error("unique explicit native matrix link required");
        auto* matrix=system->getSystemBaseMatrix();if(!matrix)throw std::runtime_error("native assembled matrix unavailable");
        std::ofstream output(filename.getValue());output<<std::setprecision(17)<<"i,j,A\n";
        for(sofa::Index i=0;i<matrix->rowSize();++i)for(sofa::Index j=0;j<matrix->colSize();++j)if(matrix->element(i,j)!=0)output<<i<<','<<j<<','<<matrix->element(i,j)<<'\n';
        written=true;
    }
};
}
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripElasticObserver";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Initial native elastic matrix and force FD query; no physics update").add<diagnostic::NativeElasticMatrixObserver>());f->registerObjects(sofa::core::ObjectRegistrationData("Read-only post-step native assembled matrix").add<diagnostic::NativeAssembledMatrixObserver>());}
}
