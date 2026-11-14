#include <sofa/core/ObjectFactory.h>
#include <sofa/core/objectmodel/BaseComponent.h>
#include <sofa/core/objectmodel/BaseContext.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <sofa/core/behavior/LinearSolver.h>
#include <sofa/core/behavior/BaseMatrixLinearSystem.h>
#include <sofa/linearalgebra/BaseMatrix.h>
#include <sofa/linearalgebra/BaseVector.h>
#include <vector>
#include <cmath>
#include <fstream>
#include <iomanip>
class SolverTelemetry final:public sofa::core::objectmodel::BaseComponent{
public:
 SOFA_CLASS(SolverTelemetry,sofa::core::objectmodel::BaseComponent);
 sofa::core::objectmodel::Data<std::string> filename;sofa::core::objectmodel::Data<unsigned> stride;sofa::core::objectmodel::Data<double> matrixAfter;std::ofstream file;unsigned steps=0;
 SolverTelemetry():filename(initData(&filename,std::string("solver.tsv"),"filename","Actual solver Data, not reconstructed force")),stride(initData(&stride,20u,"stride","Sampling stride")),matrixAfter(initData(&matrixAfter,0.,"matrixAfter","Start native A*x-b audit")){f_listening.setValue(true);}
 void init()override{BaseComponent::init();std::ifstream old(filename.getValue());if(old||!stride.getValue()){msg_error()<<"Invalid telemetry output";return;}file.open(filename.getValue());file<<std::setprecision(17)<<"time\tclass\tkey\tvalue\n";}
 void handleEvent(sofa::core::objectmodel::Event*event)override{if(!file||!stride.getValue()||!dynamic_cast<sofa::simulation::AnimateEndEvent*>(event)||++steps%stride.getValue())return;
  for(auto*object:getContext()->getObjects<sofa::core::objectmodel::BaseObject>(sofa::core::objectmodel::BaseContext::Local))for(const char*key:{"residual","status"})if(auto*data=object->findData(key))file<<getContext()->getTime()<<'\t'<<object->getClassName()<<'\t'<<key<<'\t'<<data->getValueString()<<'\n';
  if(getContext()->getTime()>=matrixAfter.getValue())for(auto*solver:getContext()->getObjects<sofa::core::behavior::LinearSolver>(sofa::core::objectmodel::BaseContext::Local)){
   auto*system=solver->getLinearSystem();if(!system)continue;auto*A=system->getSystemBaseMatrix();auto*b=system->getSystemRHSBaseVector();auto*x=system->getSystemSolutionBaseVector();if(!A||!b||!x||A->colSize()!=x->size()||A->rowSize()!=b->size())continue;
   std::vector<double>input(x->size()),product(b->size());for(int i=0;i<x->size();++i)input[i]=x->element(i);A->opMulV(product.data(),input.data());double residual=0,rhs=0;for(int i=0;i<b->size();++i){residual=std::max(residual,std::abs(product[i]-b->element(i)));rhs=std::max(rhs,std::abs(b->element(i)));}
   file<<getContext()->getTime()<<'\t'<<solver->getClassName()<<"\tAx_minus_b_absolute\t"<<residual<<'\n'<<getContext()->getTime()<<'\t'<<solver->getClassName()<<"\tAx_minus_b_relative\t"<<(rhs?residual/rhs:residual)<<'\n';
  }
  file.flush();}
};
extern "C" {
__attribute__((visibility("default"))) void initExternalModule(){}
__attribute__((visibility("default"))) const char*getModuleName(){return "ReGripTelemetry";}
__attribute__((visibility("default"))) void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Read-only solver telemetry").add<SolverTelemetry>());}
}
