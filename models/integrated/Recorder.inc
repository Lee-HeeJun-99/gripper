// Included in the component namespace. Reusable residual Data avoids per-frame Data construction.
class IntegratedRecorder final:public sofa::core::objectmodel::BaseComponent{
public:
 SOFA_CLASS(IntegratedRecorder,sofa::core::objectmodel::BaseComponent);
 sofa::core::objectmodel::Data<std::string> filename;
 sofa::core::objectmodel::Data<unsigned> stride;
 sofa::core::behavior::MechanicalState<Types>*state=nullptr;
 Inherit::DataVecDeriv residual;std::ofstream raw,metrics;unsigned steps=0;
 IntegratedRecorder():filename(initData(&filename,std::string("state.txt"),"filename","Raw state output")),stride(initData(&stride,20u,"stride","Record every n simulation steps")){f_listening.setValue(true);}
 void init()override{
  BaseComponent::init();state=dynamic_cast<sofa::core::behavior::MechanicalState<Types>*>(getContext()->getMechanicalState());
  if(!state||stride.getValue()==0){msg_error()<<"Invalid recorder state/stride";return;}
  std::ifstream existing(filename.getValue()),existingMetrics(filename.getValue()+".csv");if(existing||existingMetrics){msg_error()<<"Refusing existing state/metrics output";return;}
  raw.open(filename.getValue());metrics.open(filename.getValue()+".csv");raw<<std::setprecision(17);metrics<<std::setprecision(17);
  metrics<<"time,component_energy,friction_dissipation,max_connector_slip,cable_length,cable_tension,contact_count,contact_force\n";
  if(!raw||!metrics){msg_error()<<"Cannot open recorder outputs";return;}
  residual.setValue(Types::VecDeriv(state->getSize()));write();
 }
 void write(){
  if(!state||!raw)return;
  const auto*x=state->read(sofa::core::vec_id::read_access::position);const auto*v=state->read(sofa::core::vec_id::read_access::velocity);
  residual.setValue(Types::VecDeriv(state->getSize()));sofa::core::MechanicalParams params;
  for(auto*ff:getContext()->getObjects<Inherit>(sofa::core::objectmodel::BaseContext::Local))ff->addForce(&params,residual,*x,*v);
  raw<<"T= "<<getContext()->getTime()<<"\nX= ";state->writeVec(sofa::core::vec_id::read_access::position,raw);raw<<"\nV= ";state->writeVec(sofa::core::vec_id::read_access::velocity,raw);raw<<"\nR= "<<residual.getValue()<<"\n";
  double energy=0,diss=0,slip=0,len=0,T=0,count=0,F=0;
  for(auto*ff:getContext()->getObjects<EnergyField>(sofa::core::objectmodel::BaseContext::Local)){
   try{auto a=ff->assemble(x->getValue());energy+=a.energy;slip=std::max(slip,a.slip);len+=a.cableLength;T+=a.tension;count+=a.contacts;F+=a.contactForce;if(auto*layer=dynamic_cast<LayerNetwork*>(ff))diss+=layer->dissipated;}
   catch(const std::exception&e){msg_error()<<e.what();}}
  metrics<<getContext()->getTime()<<','<<energy<<','<<diss<<','<<slip<<','<<len<<','<<T<<','<<count<<','<<F<<'\n';raw.flush();metrics.flush();
 }
 void handleEvent(sofa::core::objectmodel::Event*event)override{const auto interval=stride.getValue();if(!interval)return;if(dynamic_cast<sofa::simulation::AnimateEndEvent*>(event)&&++steps%interval==0)write();}
};
