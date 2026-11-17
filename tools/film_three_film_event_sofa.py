"""One actual separated three-film shared event coupon;NOT generic closing/CCD."""
import argparse,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--sustained',action='store_true');a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));(archive/'tests').mkdir();shutil.copy2(ROOT/'tests/test_three_film_birth.cpp',archive/'tests/test_three_film_birth.cpp')
 profile=ROOT/'results/autonomous_film_20261118_three_film_birth_remainder958';ps=json.loads((profile/'summary.json').read_text());estimate=4*ps['run']['runtime_s']+30
 result=dict(status='FAIL',scope='actual SOFA single externally isolated three-film/ONE free sphere event plus compressive remainder;NOT global earliest CCD,closing from REST,release,grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},predicted_runtime_s=estimate,dt=.0002,gravity=[0,0,0],external_force_N=[0,0,-.001],impact_law='frictionless perfectly inelastic research assumption',initial_state='unstrained stationary films;sphere z offset+.0001mm and vz=-1mm/s',event_bracket_s=[.00005,.0002],control='existing C2 per rail Tmax=.0001N,ramp.01s,release.02-.03s',sdk=str(SDK))
 result['macro_steps']=8 if a.sustained else 1
 if a.sustained:estimate+=4*17.68;result['predicted_runtime_s']=estimate;result['scope']='actual separated event plus eight200us compressive steps,ONE free sphere;NOT general CCD/release/re-impact/time/grasp'
 if ps['status']!='PASS' or estimate>480:result['status']='BLOCKED';write_json(out/'summary.json',result);return
 mass=ROOT/'results/autonomous_film_20261118_three_film_public_mass917/public_mass.txt';shutil.copy2(mass,out/'public_mass_reference.txt');result['public_mass_sha256']=sha(mass);ref=out/'reference';rc=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',archive/'tests/test_three_film_birth.cpp','-o',ref],out/'reference_compile',120);result['reference_compile']=rc
 if rc['exit_code']!=0:write_json(out/'summary.json',result);return
 rr=guarded([ref,out/'public_mass_reference.txt',out/'reference.csv']+(['8'] if a.sustained else []),out/'reference_run',120);result['reference_run']=rr;result['reference_binary_sha256']=sha(ref)
 if rr['exit_code']!=0:write_json(out/'summary.json',result);return
 build=ROOT/'build'/('three_film_event_'+a.tag);build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',archive/'models/film_three_finger_event','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None;result.update(configure=configure,compile=compile)
 if compile and compile['exit_code']==0:
  binary=build/'libReGripThreeFilmEvent.so';result['binary_sha256']=sha(binary);deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in l and '=> /' in l and str(SDK) not in l for l in deps.splitlines()):raise ValueError('event SDK ABI mismatch')
  src=ROOT/'results/autonomous_film_20261118_three_film_actual64_941';meta=json.loads((src/'identity.json').read_text());tree=ET.parse(src/'scene.scn');scene=tree.getroot();scene.set('dt','.0002')
  for node in scene.iter():
   for key,value in list(node.attrib.items()):
    if key in ('filename','displacementFilename','ownerCostFilename','costProfileFilename','publicMassFilename') and value.startswith(str(src)):node.set(key,str(out)+value[len(str(src)):])
   if node.tag=='RequiredPlugin' and 'libReGripThreeFilmContact.so' in node.get('pluginName',''):node.set('pluginName',str(binary))
  owner=scene.find('ThreeFilmDrivenExactODE');owner.tag='ThreeFilmEventContinuationODE' if a.sustained else 'ThreeFilmBracketedEventODE';owner.set('maxSteps','8')
  for key in ('ownerCostFilename','publicMassFilename','reuseJournalRows'):owner.attrib.pop(key,None)
  body=scene.find('Node[@name="free_object"]/MechanicalObject');values=body.get('position').split();values[2]=format(float(values[2])+.0001,'.17g');body.set('position',' '.join(values));body.set('velocity','0 0 -1 0 0 0');tree.write(out/'scene.scn');result['scene_sha256']=sha(out/'scene.scn');result['plugins']={node.get('pluginName'):sha(node.get('pluginName')) for node in scene.findall('RequiredPlugin') if node.get('pluginName','').startswith('/')}
  run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(result['macro_steps']),'--hideProgressBar',out/'scene.scn'],out/'process',480);result['process']=run;errors=sum((out/'process'/n).read_text(errors='replace').count('[ERROR]') for n in ('stdout.log','stderr.log'));result['sofa_errors']=errors
  if run['exit_code']==0 and not errors and (out/'three.event.csv').exists():
   actual=list(csv.DictReader((out/'three.event.csv').open()));reference=list(csv.DictReader((out/'reference.csv').open()));states=list(csv.DictReader((out/'three.states.csv').open()))
   if len(actual)!=1 or len(reference)!=1 or len(states)!=result['macro_steps']:raise ValueError('incomplete event/commit records')
   differences={k:float(np.max(abs(np.fromstring(actual[0][k],sep=' ')-np.fromstring(reference[0][k],sep=' ')))) for k in actual[0]};result.update(reference_max_abs=differences,minimum_gap_mm=float(states[0]['minimum_gap']),momentum_Ns=float(states[0]['momentum_residual']),normal_velocity_mm_s=float(states[0]['normal_velocity_residual']))
   result['status']='PASS' if all(v==0 for v in differences.values()) and result['minimum_gap_mm']>=-1e-10 and result['momentum_Ns']<=1e-17 and result['normal_velocity_mm_s']<=1e-10 else 'FAIL'
   if a.sustained:
    expected=list(csv.DictReader((out/'reference.csv.states.csv').open()));error={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(states,expected)) for k in ('q','v')};result['continued_reference_max_abs']=error;result['minimum_gap_mm']=min(float(x['minimum_gap']) for x in states)
    if len(expected)!=8 or any(error[k]>=1e-12 for k in error) or result['minimum_gap_mm']< -1e-10:result['status']='FAIL'
   result['raw_hashes']={f.name:sha(f) for f in out.glob('*.csv')}
 write_json(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','scope','reference_max_abs','process','sofa_errors') if k in result}))
if __name__=='__main__':main()
