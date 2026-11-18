"""Separate route-bound checkpoint owner;strict continuation vs actual1272."""
import argparse,csv,hashlib,json,re,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
from film_routed_generate import generate
from film_routed_coupled import specialize
from film_three_film_resume import export_checkpoint
from film_compiled_sources import compiled_sources
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--step',type=int,default=40);p.add_argument('--steps',type=int,default=4);p.add_argument('--design',choices=('quadratic','lateral'),default='quadratic');a=p.parse_args();magic='REGRIP_LATERAL_PERSISTENT_V1' if a.design=='lateral' else 'REGRIP_ROUTED_PERSISTENT_V1'
 if not 1<=a.steps<=4 or not 1<=a.step<50 or a.step+a.steps>50:raise ValueError('initial strict replay stays inside actual1272 known horizon')
 src=ROOT/'results'/('autonomous_film_20261118_lateral_coupled_peak1416' if a.design=='lateral' else 'autonomous_film_20261118_routed_coupled_peak1272');m=json.loads((src/'summary.json').read_text())
 if m['status']!='PASS' or not m['accumulated_clock_exact']:raise ValueError('completed actual new-route horizon required')
 if m.get('design','quadratic')!=a.design or sha(src/'public_mass_reference.txt')!=m['public_mass_sha256']:raise ValueError('actual design/public mass differs')
 for f,d in m['raw_hashes'].items():
  if sha(src/f)!=d:raise ValueError('actual route raw changed')
 for f,d in m['source_hashes'].items():
  if sha(src/'sources'/f)!=d:raise ValueError('actual source archive changed')
 for path,digest in m['plugins'].items():
  if sha(path)!=digest:raise ValueError('actual parent/legacy mapping binary changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(ROOT/'tools/film_three_film_resume.py',out/'checkpoint_exporter.py');archive=out/'sources'
 if a.design=='lateral':
  shutil.copytree(src/'sources/models',archive/'models');generated=m['generated_source_identity']
 else:
  shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));(archive/'tests').mkdir();shutil.copy2(ROOT/'tests/test_film_rail_tendon_api.cpp',archive/'tests/test_film_rail_tendon_api.cpp');generated=generate(archive);specialize(archive)
 path=archive/'models/film_three_finger_resume/ThreeFilmResume.cpp';text=path.read_text();text=re.sub(r'\bThreeFilm[A-Za-z0-9_]*(?:ODE|Clock)\b',lambda m:'Routed'+m.group(),text)
 changes={'extern "C" {':'void registerFilmRoutedField(sofa::core::ObjectFactory*);\nextern "C" {','void registerObjects(sofa::core::ObjectFactory*f){':'void registerObjects(sofa::core::ObjectFactory*f){registerFilmRoutedField(f);','return "ReGripThreeFilmResume";':'return "ReGripRoutedThreeFilmResume";'}
 if a.design=='lateral':changes={k:v.replace('registerFilmRoutedField','registerFilmLateralField') for k,v in changes.items()}
 for old,new in changes.items():
  if text.count(old)!=1:raise ValueError('exact route resume source anchor differs')
  text=text.replace(old,new)
 if text.count('"REGRIP_PERSISTENT_V1"')!=2:raise ValueError('exact checkpoint magic anchors differ')
 text=text.replace('"REGRIP_PERSISTENT_V1"','"'+magic+'"');path.write_text(text);cmake=archive/'models/film_three_finger_resume/CMakeLists.txt';text=cmake.read_text();old='SHARED ThreeFilmResume.cpp)'
 if text.count(old)!=1:raise ValueError('exact route resume CMake anchor differs')
 cmake.write_text(text.replace(old,('SHARED ThreeFilmResume.cpp ../film_lateral_tendon/Field.generated.cpp)' if a.design=='lateral' else 'SHARED ThreeFilmResume.cpp ../film_routed_tendon/Field.generated.cpp)')));sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()}
 if a.design=='lateral':
  excluded={'models/film_three_finger_resume/ThreeFilmResume.cpp','models/film_three_finger_resume/CMakeLists.txt'}
  old={k:v for k,v in compiled_sources(m['source_hashes']).items() if k.startswith('models/') and k not in excluded};new={k:v for k,v in compiled_sources(sources).items() if k.startswith('models/') and k not in excluded}
  if old!=new:raise ValueError('lateral physical model closure changed outside explicit checkpoint owner/build')
 build=ROOT/'build'/('routed_resume_'+a.tag);build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',archive/'models/film_three_finger_resume','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None;r=dict(status='FAIL',design=a.design,scope='actual NEW route-bound persistent checkpoint replay;NOT time/energy/wrapping/holding/lift certification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,generated_source_identity=generated,sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),configure=configure,compile=compile,build_relative=str(build.relative_to(ROOT)),checkpoint_step=a.step,actual_steps=a.steps,route_parameter_mm=(6. if a.design=='lateral' else 4.5),checkpoint_magic=magic,legacy_field_work='NOT RESTORED;exclude ALL sampled-work values from physical/spliced work claims',stage_work_origin='checkpoint time;prior inventory NULL for lateral,old1276 hash-bound ONLY for quadratic',prior_stage_work_sha256=(None if a.design=='lateral' else sha(ROOT/'results/autonomous_film_20261118_routed_coupled_peak_work1276/summary.json')),root_reaction_work=None);write_json(out/'summary.json',r)
 if not compile or compile['exit_code']!=0:return
 binary=build/'libReGripThreeFilmResume.so';deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
 if 'not found' in deps or any('libSofa.' in line and '=> /' in line and str(SDK) not in line for line in deps.splitlines()):raise ValueError('route resume SDK ABI mismatch')
 token=hashlib.sha256(json.dumps(dict(source=sources,binary=sha(binary),continuous_summary=sha(src/'summary.json'),route_parameter_mm=(6. if a.design=='lateral' else 4.5),checkpoint_magic=r['checkpoint_magic']),sort_keys=True).encode()).hexdigest();states,state=export_checkpoint(src,out,a.step,token);checkpoint=out/'input.checkpoint';text=checkpoint.read_text()
 if not text.startswith('REGRIP_PERSISTENT_V1 '):raise ValueError('exported checkpoint source schema differs')
 checkpoint.write_text(text.replace('REGRIP_PERSISTENT_V1 ',magic+' ',1));tree=ET.parse(src/'scene.scn');scene=tree.getroot();scene.set('time',state['time'])
 for node in scene.iter():
  if node.tag=='RequiredPlugin' and node.get('pluginName','').endswith('/libReGripThreeFilmEvent.so'):node.set('pluginName',str(binary))
  for key,value in list(node.attrib.items()):
   if key in ('filename','displacementFilename','publicMassFilename') and value.startswith(str(src)):node.set(key,str(out)+value[len(str(src)):])
 owner=scene.find('RoutedThreeFilmFirstPeakODE');owner.tag='RoutedThreeFilmResumeODE';owner.set('checkpoint',str(checkpoint));owner.set('identity',token);owner.set('endTime',states[a.step+a.steps-1]['time']);owner.attrib.pop('firstIntervalJournal',None);tree.write(out/'scene.scn');forecast=2*m['process']['runtime_s']*a.steps/50+30;r.update(binary_sha256=sha(binary),identity=token,checkpoint_sha256=sha(checkpoint),scene_sha256=sha(out/'scene.scn'),continuous_summary_sha256=sha(src/'summary.json'),predicted_child_runtime_s=forecast,quaternion_origin='initial actual Scene quaternion plus proven ZERO spin/chart at EVERY prior actual step;no arbitrary historical rotation reconstruction',checkpoint_exporter_sha256=sha(out/'checkpoint_exporter.py'))
 if forecast>480:r.update(status='BLOCKED',failure_reason='measured policy forecast>480s;NOT OS exhaustion');write_json(out/'summary.json',r);return
 run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',out/'scene.scn'],out/'process',480);errors=sum((out/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log'));r.update(process=run,sofa_errors=errors)
 if run['exit_code']==0 and not errors:
  actual=list(csv.DictReader((out/'three.states.csv').open()));expected=states[a.step:a.step+a.steps];rows=list(csv.DictReader((out/'three.rows.csv').open()));expected_rows=list(csv.DictReader((src/'three.rows.csv').open()))[(a.step-1)*9:(a.step+a.steps-1)*9]
  if len(actual)!=a.steps:raise ValueError('incomplete route resume')
  api={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(actual,expected)) for k in ('q','v')};clock=all(x['time']==y['time'] for x,y in zip(actual,expected));field_error=0
  for f in range(3):
   xx=list(csv.DictReader((out/f'film_{f}.csv').open()));yy=list(csv.DictReader((src/f'film_{f}.csv').open()))[a.step:a.step+a.steps]
   if len(xx)!=a.steps:raise ValueError('incomplete actual field journal')
   field_error=max(field_error,max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(xx,yy) for k in y if k!='tendon_work'))
  gap=min(float(x['minimum_gap']) for x in actual);momentum=max(float(x['momentum_residual']) for x in actual);vn=max(float(x['normal_velocity_residual']) for x in actual);r.update(status='PASS' if max(api.values())<1e-12 and clock and rows==expected_rows and field_error<1e-12 and gap>=-1e-10 and momentum<=1e-17 and vn<=1e-10 else 'FAIL',reference_max_abs=api,accumulated_clock_exact=clock,whole_stage_rows_exact=rows==expected_rows,actual_field_max_abs_excluding_legacy_work=field_error,minimum_whole_stage_gap_mm=gap,momentum_residual_Ns=momentum,normal_velocity_residual_mm_s=vn,api_gate=1e-12)
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.suffix in ('.csv','.txt','.checkpoint')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','configure','compile','process','raw_hashes')}))
if __name__=='__main__':main()
