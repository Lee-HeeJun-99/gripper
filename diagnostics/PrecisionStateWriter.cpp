// Observational component only: writes state at full double precision.
#include <sofa/core/ObjectFactory.h>
#include <sofa/core/objectmodel/BaseComponent.h>
#include <sofa/core/objectmodel/BaseContext.h>
#include <sofa/core/behavior/BaseMechanicalState.h>
#include <sofa/core/behavior/ForceField.h>
#include <sofa/core/MechanicalParams.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <fstream>
#include <iomanip>
#include <filesystem>

class PrecisionStateWriter final : public sofa::core::objectmodel::BaseComponent {
public:
    SOFA_CLASS(PrecisionStateWriter, sofa::core::objectmodel::BaseComponent);
    sofa::core::objectmodel::Data<std::string> d_filename;
    sofa::core::objectmodel::Data<bool> d_residual;
    std::ofstream stream;
    sofa::core::behavior::BaseMechanicalState* state = nullptr;
    PrecisionStateWriter(): d_filename(initData(&d_filename, std::string("state.txt"), "filename", "Output file")),
        d_residual(initData(&d_residual,true,"writeResidual","Recompute static force balance in a scratch vector")) {
        f_listening.setValue(true);
    }
    void init() override {
        BaseComponent::init();
        state = getContext()->getMechanicalState();
        if(std::filesystem::exists(d_filename.getValue())) {msg_error()<<"Refusing existing output file";return;}
        stream.open(d_filename.getValue());
        stream << std::setprecision(17);
        if (!state || !stream) { msg_error() << "State or output unavailable"; return; }
        write(getContext()->getTime());
    }
    void write(double time) {
        stream << "T= " << time << "\nX= ";
        state->writeVec(sofa::core::vec_id::read_access::position, stream);
        stream << "\nV= ";
        state->writeVec(sofa::core::vec_id::read_access::velocity, stream);
        stream << '\n';
        stream.flush();
    }
    void handleEvent(sofa::core::objectmodel::Event* event) override {
        if (dynamic_cast<sofa::simulation::AnimateEndEvent*>(event))
            if(state && stream) {
                write(getContext()->getTime());
                // Scratch-vector static force balance; no simulation vector is modified.
                using T=sofa::defaulttype::Rigid3Types;
                using Field=sofa::core::behavior::ForceField<T>;
                auto* rigid=dynamic_cast<sofa::core::behavior::MechanicalState<T>*>(state);
                if(rigid && d_residual.getValue()) {
                    Field::DataVecDeriv residual;
                    residual.setValue(T::VecDeriv(rigid->getSize()));
                    sofa::core::MechanicalParams params;
                    for(auto* ff:getContext()->getObjects<Field>(sofa::core::objectmodel::BaseContext::Local))
                        ff->addForce(&params,residual,*rigid->read(sofa::core::vec_id::read_access::position),
                                     *rigid->read(sofa::core::vec_id::read_access::velocity));
                    stream<<"R= "<<residual.getValue()<<'\n';
                    stream.flush();
                }
            }
    }
};

extern "C" {
void initExternalModule() {}
const char* getModuleName() { return "ReGripDiagnostics"; }
const char* getModuleVersion() { return "0.1.0"; }
const char* getModuleLicense() { return "Research prototype"; }
const char* getModuleDescription() { return "Read-only full-precision state recorder"; }
const char* getModuleComponentList() { return "PrecisionStateWriter"; }
void registerObjects(sofa::core::ObjectFactory* factory) {
    factory->registerObjects(sofa::core::ObjectRegistrationData("Full precision state output")
        .add<PrecisionStateWriter>());
}
}
