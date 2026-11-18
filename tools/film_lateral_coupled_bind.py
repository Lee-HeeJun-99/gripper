"""Narrow source-bound outboard substitution after preserved coupled generator."""
import json,shutil
from curve_common import ROOT,sha
def bind(archive):
 provider=ROOT/'results/autonomous_film_20261118_lateral_api_build1356';m=json.loads((provider/'summary.json').read_text());gate=ROOT/'results/autonomous_film_20261118_lateral_contact_force1412';g=json.loads((gate/'summary.json').read_text())
 if m['status']!='PASS' or g['status']!='PASS':raise ValueError('qualified actual lateral Field and implicit-stage FD required')
 for f,d in m['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('qualified Field source changed')
 for name in ('models/film_lateral_tendon/Route.h','models/film_lateral_tendon/Force.h'):
  if sha(archive/name)!=g['source_hashes'][name]:raise ValueError('new physical force adapter differs from independent gate')
 if sha(archive/'models/film_lateral_tendon/Route.h')!=m['source_hashes']['models/film_lateral_tendon/Route.h']:raise ValueError('Field/event cable geometry differs')
 field=archive/'models/film_lateral_tendon/Field.generated.cpp';shutil.copy2(provider/'sources/models/film_lateral_tendon/Field.generated.cpp',field);changes={str(field.relative_to(archive)):sha(field)}
 def patch(name,old,new):
  path=archive/name;text=path.read_text()
  if text.count(old)!=1:raise ValueError('unique lateral coupled binding anchor differs:'+name)
  path.write_text(text.replace(old,new));changes[name]=sha(path)
 patch('models/film_coupled_contact/CoupledSphere.h','#include "../film_routed_contact/Force.h"','#include "../film_lateral_tendon/Force.h"')
 patch('models/film_coupled_contact/CoupledSphere.h','regrip_routed_contact::evaluate(stage,y.head(nf),4.5)','regrip_lateral_contact::evaluate(stage,y.head(nf),6.)')
 patch('models/film_three_finger/SharedFilmSystem.h','regrip_routed_tendon::elements(s.film.model,state.q,tension,4.5,','regrip_lateral_tendon::elements(s.film.model,state.q,tension,6.,')
 patch('models/film_three_finger_event/BlockFree.h','regrip_routed_tendon::elements(single.film.model,qmid,1.,4.5,','regrip_lateral_tendon::elements(single.film.model,qmid,1.,6.,')
 patch('models/film_three_finger/ThreeFilmOwner.cpp','f->getClassName()!="FilmRoutedTendon"||read<double>(f,"routeAmplitude")!=4.5','f->getClassName()!="FilmLateralTendon"||read<double>(f,"lateralOffset")!=6.')
 cpp=archive/'models/film_three_finger_event/ThreeFilmEventOwner.cpp';text=cpp.read_text()
 if text.count('registerFilmRoutedField')!=2:raise ValueError('Field declaration/registration differ')
 cpp.write_text(text.replace('registerFilmRoutedField','registerFilmLateralField'));changes[str(cpp.relative_to(archive))]=sha(cpp)
 patch('models/film_three_finger_event/CMakeLists.txt','../film_routed_tendon/Field.generated.cpp','../film_lateral_tendon/Field.generated.cpp')
 return dict(changed_sources=changes,field_api_summary_sha256=sha(provider/'summary.json'),implicit_stage_math_sha256=sha(gate/'summary.json'),binding='SAME lateral6 in Shared force/H,implicit stage,event family derivative,actual registered Field;original laws/mass/root/control unchanged',hardware='wire/guide finite geometry,mass/friction/selfcollision NOT represented')
