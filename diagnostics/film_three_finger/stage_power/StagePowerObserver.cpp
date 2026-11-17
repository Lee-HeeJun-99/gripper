#include "../../../models/film_three_finger/FrameLayout.h"
#include "../RoutedCablePower.h"
#include "../../../models/film_rail_tendon/ControlProfile.h"
#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/helper/logging/Messaging.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <fstream>
#include <iomanip>
#include <sstream>
namespace regrip_stage_power {
using SofaObject=sofa::core::objectmodel::BaseObject;
class ThreeFilmStagePowerObserver final:public SofaObject {
public:
 SOFA_CLASS(ThreeFilmStagePowerObserver,SofaObject);
 using Link=sofa::core::objectmodel::BaseLink;
 sofa::core::objectmodel::SingleLink<ThreeFilmStagePowerObserver,SofaObject,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK>owner{initLink("owner","Accepted three-film C2 owner;read-only public journal")},field{initLink("field","Actual common C2 FilmRailTendon input Data")};
 sofa::core::objectmodel::Data<std::string>filename{initData(&filename,std::string(),"filename","Exclusive stage-power journal;no physical state writes")};
 std::ifstream rows;std::ofstream output;std::unique_ptr<regrip_three_finger::SharedPointSystem>shared;unsigned steps=0;double work=0,last=-1;bool valid=false,headerRead=false;
 ThreeFilmStagePowerObserver(){f_listening.setValue(true);}
 template<class T>static T read(SofaObject*object,const char*name){auto*data=dynamic_cast<sofa::core::objectmodel::Data<T>*>(object->findData(name));if(!data)throw std::runtime_error("public observer Data missing");return data->getValue();}
 void init()override{SofaObject::init();try{
  if(!owner||!field||owner->getClassName().find("ThreeFilmDriven")!=0||field->getClassName()!="FilmRailTendon"||filename.getValue().empty()||std::ifstream(filename.getValue()))throw std::runtime_error("explicit driven owner/field and new observer path required");
  if(read<unsigned>(field.get(),"nx")!=21||read<unsigned>(field.get(),"guideIntervals")!=4||read<double>(field.get(),"guideOffset")!=5||!read<bool>(field.get(),"rootGuideSecondOrder"))throw std::runtime_error("observer mapped geometry differs from qualified owner");
  shared=std::make_unique<regrip_three_finger::SharedPointSystem>(regrip_three_finger::sharedPointReference(regrip_three_finger::Layout()));output.open(filename.getValue());if(!output)throw std::runtime_error("cannot open stage work output");output<<std::setprecision(17)<<"macro,stage,time,tension_N,cable_length_mm,shortening_rate_mm_s,power_Nmm_s,weight_s,stage_work_Nmm,cumulative_macro_work_Nmm\n";valid=true;
 }catch(const std::exception&e){msg_error(this)<<e.what();}}
 static std::vector<std::string>parseRow(const std::string&line){std::vector<std::string>cells;std::string value;bool quoted=false;for(char c:line){if(c=='\"')quoted=!quoted;else if(c==','&&!quoted){cells.push_back(value);value.clear();}else value+=c;}if(quoted)throw std::runtime_error("incomplete quoted state");cells.push_back(value);return cells;}
 static Eigen::VectorXd vector(const std::string&text,unsigned n){Eigen::VectorXd x(n);std::istringstream in(text);for(double&v:x)in>>v;double extra;if(!in||in>>extra||!x.allFinite())throw std::runtime_error("finite exact state dimension required");return x;}
 void handleEvent(sofa::core::objectmodel::Event*event)override{
  if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(event)||!valid)return;
  try{
   double end=getContext()->getTime(),h=getContext()->getDt();if(end==last)return;if(!(end>last)||!(h>0)||steps>=read<unsigned>(owner.get(),"maxSteps"))throw std::runtime_error("once-per-accepted-step observer ownership");
   if(!headerRead){rows.open(read<std::string>(owner.get(),"filename")+".rows.csv");std::string header;std::getline(rows,header);if(header!="time,owner_finger,triangle,feature,gap,force,normal_velocity,nx,ny,nz,px,py,pz,jacobian,stage_q,stage_v")throw std::runtime_error("unsupported accepted-row journal schema/order");headerRead=true;}
   struct Stage{double time,tension,length,rate,power,weight,increment;};std::array<Stage,3>sample;double increment=0;rows.clear();
   for(unsigned k=0;k<3;++k){std::vector<std::string>first;for(unsigned f=0;f<3;++f){std::string line;if(!std::getline(rows,line))throw std::runtime_error("accepted row transaction incomplete");auto cells=parseRow(line);if(cells.size()!=16||std::stoul(cells[1])!=f)throw std::runtime_error("accepted row order mismatch");if(f==0)first=cells;else if(cells[0]!=first[0]||cells[14]!=first[14]||cells[15]!=first[15])throw std::runtime_error("shared accepted stage differs across fingers");}
    auto q=vector(first[14],shared->M.rows()),v=vector(first[15],shared->M.rows());double t=std::stod(first[0]);if(std::abs(t-(end-h+h*(k==0?0:k==1?.5:1)))>1e-12)throw std::runtime_error("physical stage clock mismatch");
    double tension=regrip_film_rail::ControlProfile::evaluate(t,read<double>(field.get(),"maximumTension"),read<double>(field.get(),"rampTime"),read<double>(field.get(),"releaseBegin"),read<double>(field.get(),"releaseEnd"),read<bool>(field.get(),"c2Control")).tension,length=0,rate=0;
    for(unsigned f=0;f<3;++f){auto&film=shared->films[f].film;auto power=regrip_cable_observer::evaluate(film.model,film.expand(q.segment(f*shared->nf,shared->nf)),film.expand(v.segment(f*shared->nf,shared->nf)));length+=power.length;rate+=power.shorteningRate;}
    double weight=h*(k==1?2./3:1./6);sample[k]={t,tension,length,rate,tension*rate,weight,weight*tension*rate};increment+=sample[k].increment;
   }
   work+=increment;for(unsigned k=0;k<3;++k){const auto&s=sample[k];output<<steps<<','<<k<<','<<s.time<<','<<s.tension<<','<<s.length<<','<<s.rate<<','<<s.power<<','<<s.weight<<','<<s.increment<<','<<work<<'\n';}output.flush();last=end;++steps;
  }catch(const std::exception&e){valid=false;msg_error(this)<<"Accepted stage-power observer rejected: "<<e.what();}
 }
};
}
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripStagePower";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Read-only accepted three-film stage power;not a physical force/state correction").add<regrip_stage_power::ThreeFilmStagePowerObserver>());}
}
