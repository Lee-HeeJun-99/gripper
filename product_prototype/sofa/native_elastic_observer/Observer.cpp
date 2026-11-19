#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/core/behavior/ForceField.h>
#include <sofa/core/MechanicalParams.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/defaulttype/RigidTypes.h>
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
class NativeRigidTangentObserver:public sofa::core::objectmodel::BaseObject {
public:
    SOFA_CLASS(NativeRigidTangentObserver,sofa::core::objectmodel::BaseObject);
    using Types=sofa::defaulttype::Rigid3Types;
    using State=sofa::core::behavior::MechanicalState<Types>;
    using Field=sofa::core::behavior::ForceField<Types>;
    using BaseLink=sofa::core::objectmodel::BaseLink;
    sofa::core::objectmodel::SingleLink<NativeRigidTangentObserver,State,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>body;
    sofa::core::objectmodel::SingleLink<NativeRigidTangentObserver,Field,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>elastic;
    sofa::core::objectmodel::Data<std::string>filename;
    sofa::core::objectmodel::Data<double>amplitude;
    sofa::core::objectmodel::Data<Types::VecCoord>privatePositions;
    sofa::core::objectmodel::SingleLink<NativeRigidTangentObserver,sofa::core::behavior::BaseMatrixLinearSystem,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>system;
    sofa::core::objectmodel::SingleLink<NativeRigidTangentObserver,sofa::core::objectmodel::BaseObject,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>interpolation;
    NativeRigidTangentObserver():body(initLink("body","Observed native Rigid3 state")),elastic(initLink("elastic","Native Rigid3 ForceField")),filename(initData(&filename,std::string(),"filename","Exclusive private tangent diagnostic")),amplitude(initData(&amplitude,0.,"amplitude","Dimensionless PRIVATE probe amplitude; translation scale .1m,rotation scale1rad")),privatePositions(initData(&privatePositions,Types::VecCoord(),"privatePositions","Optional PRIVATE Rigid3 force-query coordinates;never installed in state")),system(initLink("system","Optional DIAGNOSTIC native matrix assembly at initial state")),interpolation(initLink("interpolation","Optional native interpolation data inventory")){}
    void bwdInit()override {
        BaseObject::bwdInit();if(!body||!elastic||std::ifstream(filename.getValue()))throw std::runtime_error("unique Rigid3 observer required");
        const auto original=body->read(sofa::core::vec_id::read_access::position)->getValue();
        const auto velocity=body->read(sofa::core::vec_id::read_access::velocity)->getValue();
        Types::VecDeriv direction(original.size());
        for(unsigned i=2;i<original.size();++i)for(unsigned j=0;j<6;++j)direction[i][j]=(j<3?.1:1.)*std::sin(double(6*i+j+1));
        auto perturb=[&](const Types::VecCoord&q,double h){auto result=q;
            for(unsigned i=0;i<q.size();++i){for(unsigned j=0;j<3;++j)result[i].getCenter()[j]+=h*direction[i][j];
                double norm=0;for(unsigned j=3;j<6;++j)norm+=direction[i][j]*direction[i][j];norm=std::sqrt(norm);
                if(norm>0){double s=std::sin(h*norm/2)/norm;sofa::type::Quat<double>delta(s*direction[i][3],s*direction[i][4],s*direction[i][5],std::cos(h*norm/2));
                    result[i].getOrientation()=delta*q[i].getOrientation();}}
            return result;};
        sofa::core::MechanicalParams params;
        auto force=[&](const Types::VecCoord&q){Field::DataVecCoord x;Field::DataVecDeriv v,f;x.setValue(q);v.setValue(velocity);f.setValue(Types::VecDeriv(q.size()));elastic->addForce(&params,f,x,v);return f.getValue();};
        const auto initial=force(original);
        std::ofstream initialOutput(filename.getValue()+".initial.csv");initialOutput<<std::setprecision(17)<<"node,fx_N,fy_N,fz_N,tx_Nm,ty_Nm,tz_Nm\n";
        for(unsigned i=0;i<initial.size();++i){initialOutput<<i;for(unsigned j=0;j<6;++j)initialOutput<<','<<initial[i][j];initialOutput<<'\n';}
        if(interpolation){std::ofstream data(filename.getValue()+".lengths.txt");auto* lengths=dynamic_cast<sofa::core::objectmodel::Data<sofa::type::vector<double>>*>(interpolation->findData("lengthList"));if(!lengths)throw std::runtime_error("typed native lengthList unavailable");data<<std::setprecision(17);for(double length:lengths->getValue())data<<length<<' ';}
        if(system){
            params.setMFactor(0.).setBFactor(0.).setKFactor(-1.);system->buildSystemMatrix(&params);
            const auto* A=system->getSystemBaseMatrix();if(!A)throw std::runtime_error("initial native assembled matrix missing");
            std::ofstream matrix(filename.getValue()+".assembled.csv");matrix<<std::setprecision(17)<<"i,j,K\n";
            for(int i=0;i<A->rowSize();++i)for(int j=0;j<A->colSize();++j)if(A->element(i,j)!=0)matrix<<i<<','<<j<<','<<A->element(i,j)<<'\n';
            force(original);params.setKFactor(1.);
            std::ofstream tangentOutput(filename.getValue()+".dforce.csv");tangentOutput<<std::setprecision(17)<<"i,j,K\n";
            for(unsigned column=0;column<6*original.size();++column){Types::VecDeriv basis(original.size());basis[column/6][column%6]=1.;Field::DataVecDeriv dx,df;dx.setValue(basis);df.setValue(Types::VecDeriv(original.size()));elastic->addDForce(&params,df,dx);const auto values=df.getValue();
                for(unsigned i=0;i<values.size();++i)for(unsigned k=0;k<6;++k)if(values[i][k]!=0)tangentOutput<<6*i+k<<','<<column<<','<<-values[i][k]<<'\n';}
        }
        const auto probe=privatePositions.getValue().empty()?perturb(original,amplitude.getValue()):privatePositions.getValue();
        if(probe.size()!=original.size())throw std::runtime_error("private Rigid3 query size mismatch");
        const auto probeForce=force(probe);
        std::ofstream probeOutput(filename.getValue()+".probe.csv");probeOutput<<std::setprecision(17)<<"node,fx_N,fy_N,fz_N,tx_Nm,ty_Nm,tz_Nm\n";
        for(unsigned i=0;i<probeForce.size();++i){probeOutput<<i;for(unsigned j=0;j<6;++j)probeOutput<<','<<probeForce[i][j];probeOutput<<'\n';}
        // BeamAdapter overrides addDForce/MultiMatrixAccessor, NOT the scalar
        // convenience addKToMatrix used by the Vec3 observer. Query its real path.
        Field::DataVecDeriv dx,df;dx.setValue(direction);df.setValue(Types::VecDeriv(probe.size()));
        params.setKFactor(1.).setBFactor(0.);elastic->addDForce(&params,df,dx);const auto tangent=df.getValue();
        std::ofstream out(filename.getValue());out<<std::setprecision(17)<<"epsilon,force_error_N,force_derivative_norm_N,torque_error_Nm,torque_derivative_norm_Nm\n";
        for(double eps:{1e-6,1e-7,1e-8}){auto plus=force(perturb(probe,eps)),minus=force(perturb(probe,-eps));double ef=0,nf=0,et=0,nt=0;
            for(unsigned i=2;i<probe.size();++i)for(unsigned k=0;k<6;++k){double exact=tangent[i][k];
                double fd=(plus[i][k]-minus[i][k])/(2*eps);if(k<3){ef+=(fd-exact)*(fd-exact);nf+=fd*fd;}else{et+=(fd-exact)*(fd-exact);nt+=fd*fd;}}
            out<<eps<<','<<std::sqrt(ef)<<','<<std::sqrt(nf)<<','<<std::sqrt(et)<<','<<std::sqrt(nt)<<'\n';}
        force(original);
        if(original!=body->read(sofa::core::vec_id::read_access::position)->getValue()||velocity!=body->read(sofa::core::vec_id::read_access::velocity)->getValue())throw std::runtime_error("Rigid3 observer changed actual q/v");
    }
};
class NativeRigidAcceptedObserver:public sofa::core::objectmodel::BaseObject {
public:
    SOFA_CLASS(NativeRigidAcceptedObserver,sofa::core::objectmodel::BaseObject);
    using Types=sofa::defaulttype::Rigid3Types;using State=sofa::core::behavior::MechanicalState<Types>;using Field=sofa::core::behavior::ForceField<Types>;using BaseLink=sofa::core::objectmodel::BaseLink;
    sofa::core::objectmodel::SingleLink<NativeRigidAcceptedObserver,State,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>body;
    sofa::core::objectmodel::SingleLink<NativeRigidAcceptedObserver,Field,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>elastic;
    sofa::core::objectmodel::Data<std::string>filename;sofa::core::objectmodel::Data<double>lengthToM;std::ofstream output;unsigned step=0;
    NativeRigidAcceptedObserver():body(initLink("body","Actual native Rigid3 state")),elastic(initLink("elastic","Native elastic field")),filename(initData(&filename,std::string(),"filename","Exclusive actual end-event state/force journal")),lengthToM(initData(&lengthToM,1.,"lengthToM","Native length unit in metres;force unit must be N;SI journal only")){f_listening.setValue(true);}
    void handleEvent(sofa::core::objectmodel::Event*event)override{
        if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(event))return;
        if(!body||!elastic||!std::isfinite(lengthToM.getValue())||lengthToM.getValue()<=0)throw std::runtime_error("Explicit accepted observer links and positive units required");
        if(!output.is_open()){if(std::ifstream(filename.getValue()))throw std::runtime_error("Unique accepted journal required");output.open(filename.getValue());output<<std::setprecision(17)<<"step,time_s,node,x_m,y_m,z_m,qx,qy,qz,qw,fx_N,fy_N,fz_N,tx_Nm,ty_Nm,tz_Nm\n";}
        const auto q=body->read(sofa::core::vec_id::read_access::position)->getValue();const auto velocity=body->read(sofa::core::vec_id::read_access::velocity)->getValue();
        Field::DataVecCoord x;Field::DataVecDeriv v,f;x.setValue(q);v.setValue(velocity);f.setValue(Types::VecDeriv(q.size()));sofa::core::MechanicalParams params;elastic->addForce(&params,f,x,v);const auto force=f.getValue();
        ++step;for(unsigned i=0;i<q.size();++i){output<<step<<','<<getContext()->getTime()<<','<<i;for(unsigned j=0;j<3;++j)output<<','<<q[i].getCenter()[j]*lengthToM.getValue();for(unsigned j=0;j<4;++j)output<<','<<q[i].getOrientation()[j];for(unsigned j=0;j<6;++j)output<<','<<force[i][j]*(j<3?1.:lengthToM.getValue());output<<'\n';}output.flush();
        if(q!=body->read(sofa::core::vec_id::read_access::position)->getValue()||velocity!=body->read(sofa::core::vec_id::read_access::velocity)->getValue())throw std::runtime_error("accepted force observer changed actual state");
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
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Initial native elastic matrix and force FD query; no physics update").add<diagnostic::NativeElasticMatrixObserver>());f->registerObjects(sofa::core::ObjectRegistrationData("Read-only native Rigid3 force/tangent query").add<diagnostic::NativeRigidTangentObserver>());f->registerObjects(sofa::core::ObjectRegistrationData("Read-only actual Rigid3 state/force").add<diagnostic::NativeRigidAcceptedObserver>());f->registerObjects(sofa::core::ObjectRegistrationData("Read-only post-step native assembled matrix").add<diagnostic::NativeAssembledMatrixObserver>());}
}
