"""Generate separate physical rail-aspect Field and reuse the validated ODE API."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();baseline=ROOT/'results/autonomous_film_20261119_stationary_gauss_resume1637';bm=json.loads((baseline/'summary.json').read_text());math=ROOT/'results/autonomous_film_20261119_rail_aspect_math1649';mm=json.loads((math/'summary.json').read_text());api=ROOT/'results/autonomous_film_20261118_lateral_api_build1356';am=json.loads((api/'summary.json').read_text())
 if any(x['status']!='PASS' for x in (bm,mm,am)):raise ValueError('qualified baseline,design math and actual API required')
 for f,d in bm['source_hashes'].items():
  if sha(baseline/'sources'/f)!=d:raise ValueError('frozen baseline changed')
 if sha(ROOT/'models/film_rail_aspect/Design.h')!=mm['source_hashes']['models/film_rail_aspect/Design.h']:raise ValueError('qualified physical design changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(baseline/'sources/models',archive/'models');shutil.copytree(ROOT/'models/film_rail_aspect',archive/'models/film_rail_aspect')
 # Only a virtual default assembly factory is added to the historical ODE.
 old=(archive/'models/film_transmission/Owner.cpp').read_text();new=(ROOT/'models/film_transmission/Owner.cpp').read_text();normalized=new.replace(' virtual Assembly assembly()const{return model(parameter<double>("bondStiffness"),parameter<double>("guideOffset"));}\n','').replace('  assembly();if(filename','  model(parameter<double>("bondStiffness"),parameter<double>("guideOffset"));if(filename').replace('auto m=assembly();','auto m=model(parameter<double>("bondStiffness"),parameter<double>("guideOffset"));')
 if normalized!=old:raise ValueError('ONLY default-preserving ODE model factory hook allowed')
 (archive/'models/film_transmission/Owner.cpp').write_text(new)
 text=(archive/'models/film_lateral_tendon/Field.generated.cpp').read_text().replace('FilmLateralTendon','FilmAspectTendon').replace('registerFilmLateralField','registerFilmAspectField').replace('#include "Route.h"','#include "../film_lateral_tendon/Route.h"')
 anchor=' Assembly model()const{Assembly m(nx.getValue());'
 if text.count(anchor)!=1:raise ValueError('unique physical model factory required')
 text='#include "Design.h"\n'+text;text=text.replace(anchor,' sofa::core::objectmodel::Data<double>railThickness{initData(&railThickness,.1,"railThickness","Frozen physical rail thickness at fixed core cross section;not stiffness control")};\n mutable double frozenRailThickness=-1;\n Assembly model()const{if(nx.getValue()!=21)throw std::runtime_error("qualified21-row rail design only");double h=railThickness.getValue();if(frozenRailThickness<0)frozenRailThickness=h;if(h!=frozenRailThickness)throw std::runtime_error("physical geometry change without parameter work rejected");Assembly m=regrip_rail_aspect::design(h);')
 (archive/'models/film_rail_aspect/Field.generated.cpp').write_text(text)
 original=api/'sources/tests/test_film_lateral_api.generated.cpp'
 if sha(original)!=am['source_hashes']['tests/test_film_lateral_api.generated.cpp']:raise ValueError('qualified API test changed')
 test=original.read_text().replace('film_lateral_tendon/Field.generated.cpp','film_rail_aspect/Field.generated.cpp').replace('FilmLateralTendon','FilmAspectTendon').replace('regrip_film_rail::Assembly model(21);','auto model=regrip_rail_aspect::design(std::stod(argv[1]));').replace('field->nx.setValue(model.nx);','field->railThickness.setValue(model.railT);field->nx.setValue(model.nx);').replace('field->lateralOffset.setValue(argc>1?std::stod(argv[1]):6);','field->lateralOffset.setValue(6.);').replace('field->stepT=.001;','field->stepT=.0001;')
 tests=archive/'tests';tests.mkdir();(tests/'test_film_rail_aspect_api.generated.cpp').write_text(test);build=ROOT/'build'/('film_rail_aspect_'+a.tag);build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',archive/'models/film_rail_aspect','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'--target','ReGripFilmRailAspect','-j','1'],out/'compile',180) if configure['exit_code']==0 else None;tc=guarded(['cmake','--build',build,'--target','test_film_rail_aspect_api','-j','1'],out/'api_compile',120) if compile and compile['exit_code']==0 else None;trials={}
 if tc and tc['exit_code']==0:
  for h in (.075,.1,.125):trials[str(h)]=guarded([build/'test_film_rail_aspect_api',str(h)],out/('api'+str(h)),120)
 good=len(trials)==3 and all(x['exit_code']==0 for x in trials.values());r=dict(status='PASS' if good else 'FAIL',scope='actual SOFA Force/dForce/matrix/FD/query-purity of physical rail aspect ONLY;NOT dynamics/time/contact/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),baseline_summary_sha256=sha(baseline/'summary.json'),design_math_summary_sha256=sha(math/'summary.json'),old_api_summary_sha256=sha(api/'summary.json'),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),build_relative=str(build.relative_to(ROOT)),configure=configure,compile=compile,api_compile=tc,api_trials=trials,selected_design=None)
 if good:
  binary=build/'libReGripFilmRailAspect.so';deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in z and '=> /' in z and str(SDK) not in z for z in deps.splitlines()):raise ValueError('SDK ABI mismatch')
  r.update(binary_sha256=sha(binary),api_binary_sha256=sha(build/'test_film_rail_aspect_api'))
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','configure','compile','api_compile','api_trials')}))
if __name__=='__main__':main()
