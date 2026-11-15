 sofa::core::objectmodel::Data<std::string>journalFilename;
 std::ofstream journal;
 double wireWork=0;std::vector<double>wireLength0,wireTension0;
 void openJournal(){if(journalFilename.getValue().empty())return;std::ifstream exists(journalFilename.getValue());if(exists)throw std::invalid_argument("refusing old energy journal");journal.open(journalFilename.getValue());if(!journal)throw std::runtime_error("journal file");journal<<std::setprecision(17)<<"time,step,stage,beam_U,layer_U,wire_virtual_potential,contact_U,kinetic_K,contact_plastic_D,detachment_loss,wire_work_endpoint,unknown_pressure_work,unknown_stiffness_damping,unknown_total_closure\n";}
 void journalStage(const char*stage,double contactEnergy){
  if(!journal)return;
  auto*x=mstate->read(sofa::core::vec_id::read_access::position);auto*v=mstate->read(sofa::core::vec_id::read_access::velocity);sofa::core::MechanicalParams parameters;auto*ctx=getContext();double beam=0,layer=0,wire=0,K=0;std::vector<double>lengths,tensions;
  for(auto*f:ctx->getObjects<Inherit>(sofa::core::objectmodel::BaseContext::Local)){if(f==this)continue;auto name=f->getClassName();if(name=="ConservativeBeam")beam+=f->getPotentialEnergy(&parameters,*x);else if(name=="FrameLayerNetwork")layer+=f->getPotentialEnergy(&parameters,*x);else if(name=="RoutedCable"){auto*c=dynamic_cast<RoutedCable*>(f);if(!c||c->stiffness.getValue()!=0)throw std::invalid_argument("journal actuator work scope: ideal tension only");auto result=c->assemble(x->getValue());wire+=result.energy;lengths.push_back(result.cableLength);tensions.push_back(result.tension);}}
  for(auto*m:ctx->getObjects<sofa::core::behavior::Mass<Types>>(sofa::core::objectmodel::BaseContext::Local))K+=m->getKineticEnergy(&parameters,*v);
  if(std::string(stage)=="begin"){wireLength0=lengths;wireTension0=tensions;}
  if(std::string(stage)=="pre_commit"&&lengths.size()==wireLength0.size())for(size_t i=0;i<lengths.size();++i)wireWork-=wireTension0[i]*(lengths[i]-wireLength0[i]);
  journal<<getContext()->getTime()<<','<<steps<<','<<stage<<','<<beam<<','<<layer<<','<<wire<<','<<contactEnergy<<','<<K<<','<<plastic<<','<<released<<','<<wireWork<<",null,null,null\n";journal.flush();
 }
 void addForce(const sofa::core::MechanicalParams*p,DataVecDeriv&f,const DataVecCoord&x,const DataVecDeriv&v)override{EnergyField::addForce(p,f,x,v);if(journal)journalStage("force_evaluation",assemble(x.getValue()).energy);}
