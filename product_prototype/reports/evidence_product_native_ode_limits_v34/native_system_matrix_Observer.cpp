#include <sofa/core/objectmodel/BaseComponent.h>
#include <sofa/core/behavior/LinearSolver.h>
#include <sofa/core/behavior/BaseMatrixLinearSystem.h>
#include <sofa/linearalgebra/BaseMatrix.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <fstream>
#include <iomanip>
namespace regrip {
using sofa::core::objectmodel::BaseComponent;using sofa::core::objectmodel::BaseLink;
class NativeSystemMatrix:public BaseComponent {
public:
 SOFA_CLASS(NativeSystemMatrix,BaseComponent);
 sofa::core::objectmodel::SingleLink<NativeSystemMatrix,sofa::core::behavior::LinearSolver,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK> solver;
 sofa::core::objectmodel::Data<std::string> filename;std::ofstream f;
 NativeSystemMatrix():solver(initLink("solver","Actual Native solver,read only public matrix")),filename(initData(&filename,std::string(),"filename","Unique matrix journal")){f_listening.setValue(true);}
 void init()override{BaseComponent::init();if(!solver||std::ifstream(filename.getValue()))throw std::runtime_error("unique linked public matrix required");f.open(filename.getValue());f<<std::setprecision(17)<<"time_s,row,column,value\n";}
 void handleEvent(sofa::core::objectmodel::Event*e)override{if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(e))return;auto*s=solver->getLinearSystem();if(!s||!s->getSystemBaseMatrix())throw std::runtime_error("Native public matrix unavailable");auto*M=s->getSystemBaseMatrix();if(M->rowSize()>100)throw std::runtime_error("reduced matrix diagnostic only");for(int i=0;i<M->rowSize();++i)for(int j=0;j<M->colSize();++j)f<<getContext()->getTime()<<','<<i<<','<<j<<','<<M->element(i,j)<<'\n';f.flush();}
};
}
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripSystemMatrix";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Read-only actual Native global system matrix").add<regrip::NativeSystemMatrix>());}
}
