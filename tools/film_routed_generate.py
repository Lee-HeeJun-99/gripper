"""Generate an isolated class from the preserved ForceField;original file untouched."""
import re
from curve_common import sha
def generate(archive,core_only=False):
 core_identity=None
 if core_only:
  kernel=archive/'models/film_rail_tendon/Kernel.h';body=kernel.read_text();begin='  if(guideIntervals==0||(nx-1)%guideIntervals)';end='\n double energy(';remove_begin='  // Actual eccentric routed path:';remove_end='  PassiveProfile::Scope contactTimer'
  if any(body.count(s)!=1 for s in (begin,end,remove_begin,remove_end)):raise ValueError('exact original core extraction anchors differ')
  body=body[body.index(begin):body.index(end)];body=body[:body.index(remove_begin)]+body[body.index(remove_end):]
  generated=archive/'models/film_routed_tendon/Core.generated.h'
  if generated.exists():raise ValueError('generated core exists')
  generated.write_text('#pragma once\n#include "../film_rail_tendon/Kernel.h"\nnamespace regrip_routed_tendon {\nusing namespace regrip_film_rail;\nstruct CoreAssembly:Assembly {explicit CoreAssembly(const Assembly&m):Assembly(m){}\nvoid elements(const std::vector<Point>&u,double tension,const Visitor&visit,const PassiveProfile*profile=nullptr)const{\n'+body+'\n};\n}\n')
  route=archive/'models/film_routed_tendon/Route.h';r=route.read_text();anchor=' m.elements(u,0,'
  if r.count(anchor)!=1:raise ValueError('exact zero-baseline dispatch anchor differs')
  r=r.replace('#include "../film_rail_tendon/Kernel.h"','#include "../film_rail_tendon/Kernel.h"\n#include "Core.generated.h"').replace(anchor,' CoreAssembly(m).elements(u,0,');route.write_text(r)
  core_identity=dict(original_kernel_sha256=sha(kernel),generated_core_sha256=sha(generated),generated_route_sha256=sha(route),change='omit ONLY discarded zero-tension baseline cable AD;original core body extracted verbatim;ephemeral derived Assembly copy,no layout change',domain_note='extraneous zero-baseline-cable degeneracy rejection removed for new routed variant;large-wrap/self-contact still NOT qualified')
 original=archive/'models/film_rail_tendon/FilmRailTendon.cpp';source=original.read_text();text=re.sub(r'\bFilmRailTendon\b','FilmRoutedTendon',source)
 def replace(old,new):
  nonlocal text
  if text.count(old)!=1:raise ValueError('exact generated-field source anchor differs: '+old[:70])
  text=text.replace(old,new)
 replace('#include "Kernel.h"','#include "Route.h"');replace('#include "ControlProfile.h"','#include "../film_rail_tendon/ControlProfile.h"')
 replace(' mutable bool cached=false;',' sofa::core::objectmodel::Data<double>routeAmplitude{initData(&routeAmplitude,0.,"routeAmplitude","Frozen quadratic material-coordinate offset amplitude0 or4.5mm;not runtime stiffness control")};\n mutable double frozenAmplitude=-1;\n mutable bool cached=false;')
 replace(' Assembly model()const{',' double amplitude()const{double a=routeAmplitude.getValue();regrip_routed_tendon::validate(model(),a);if(frozenAmplitude<0)frozenAmplitude=a;if(a!=frozenAmplitude)throw std::runtime_error("route geometry changed without parameter-work model");return a;}\n Assembly model()const{')
 replace('const std::vector<Element>&values(const VecCoord&x)const{','const std::vector<Element>&values(const VecCoord&x)const{amplitude();')
 replace('m.elements(q,stepT,','regrip_routed_tendon::elements(m,q,stepT,amplitude(),')
 replace('double length=m.cableLength(u);','double length=regrip_routed_tendon::length(m,u,amplitude());')
 replace('Base::init();if(!mstate)','Base::init();if(!mstate)') # assert preserved init path
 replace('values(mstate->read(sofa::core::vec_id::read_access::position)->getValue());if(!filename', 'values(mstate->read(sofa::core::vec_id::read_access::position)->getValue());previousLength=regrip_routed_tendon::length(model(),std::vector<Point>(model().size()),amplitude());if(!filename')
 anchor='\nextern "C" {'
 if text.count(anchor)!=1:raise ValueError('exact isolated registration boundary required')
 text=text[:text.index(anchor)]+'\nvoid registerFilmRoutedField(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL separate quadratic routed-tendon field;no wire collision/grasp qualification").add<regrip_film_rail::FilmRoutedTendon>());}\n'
 output=archive/'models/film_routed_tendon/Field.generated.cpp'
 if output.exists():raise ValueError('generated field exists;do not overwrite')
 output.write_text(text)
 test=archive/'tests/test_film_rail_tendon_api.cpp';api=test.read_text();api=re.sub(r'\bFilmRailTendon\b','FilmRoutedTendon',api);api=api.replace('#include "../models/film_rail_tendon/FilmRoutedTendon.cpp"','#include "../models/film_routed_tendon/Field.generated.cpp"')
 anchors={ 'Assembly model(argc>1&&std::string(argv[1])=="distributed"?21:5);':'Assembly model(21);', 'field->guideIntervals.setValue(model.nx==21?10:4);':'field->guideIntervals.setValue(4);', 'field->rootGuideSecondOrder.setValue(argc>1&&std::string(argv[1])=="root");':'field->rootGuideSecondOrder.setValue(true);field->guideOffset.setValue(5.);field->routeAmplitude.setValue(argc>1?std::stod(argv[1]):4.5);'}
 for old,new in anchors.items():
  if api.count(old)!=1:raise ValueError('exact API reuse source anchor differs')
  api=api.replace(old,new)
 marker=' std::cout<<"PASS actual SOFA assembly'
 if api.count(marker)!=1:raise ValueError('API result boundary differs')
 api=api.replace(marker,' double frozen=field->routeAmplitude.getValue();field->routeAmplitude.setValue(frozen==0?4.5:0);bool ampRejected=false;try{field->getPotentialEnergy(&mp,position);}catch(const std::runtime_error&){ampRejected=true;}if(!ampRejected)throw std::runtime_error("mutable route geometry accepted");field->routeAmplitude.setValue(frozen);if(field->getPotentialEnergy(&mp,position)!=baselineEnergy)throw std::runtime_error("route query rejection changed state");\n'+marker)
 target=archive/'tests/test_film_routed_api.generated.cpp';target.write_text(api)
 return dict(original_field_sha256=sha(original),generated_field_sha256=sha(output),original_api_sha256=sha(test),generated_api_sha256=sha(target),registration='unique Field/Owner classes;legacy plugin retained ONLY for unchanged mappings;Assembly layout untouched',core_only=core_only,core_identity=core_identity)
