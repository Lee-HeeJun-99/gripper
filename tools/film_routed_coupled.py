"""Separate generated THREE-film/free-sphere routed event coupon;not grasp."""
import argparse,csv,json,re,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
from film_routed_generate import generate
from film_compiled_sources import compiled_sources
def specialize(archive):
 changes={}
 def patch(name,old,new):
  path=archive/name;text=path.read_text()
  if text.count(old)!=1:raise ValueError('exact coupled source anchor differs: '+name+' '+old[:50])
  text=text.replace(old,new);path.write_text(text);changes[name]=sha(path)
 patch('models/film_coupled_contact/CoupledSphere.h','#include "AccurateDual.h"','#include "AccurateDual.h"\n#include "../film_routed_contact/Force.h"')
 patch('models/film_coupled_contact/CoupledSphere.h','auto f=stage.evaluate(y.head(nf));','auto f=regrip_routed_contact::evaluate(stage,y.head(nf),4.5);')
 patch('models/film_three_finger/SharedFilmSystem.h','s.film.model.elements(state.q,tension,','regrip_routed_tendon::elements(s.film.model,state.q,tension,4.5,')
 patch('models/film_three_finger_event/BlockFree.h','single.film.model.elements(qmid,1.,','regrip_routed_tendon::elements(single.film.model,qmid,1.,4.5,')
 patch('models/film_three_finger/ThreeFilmOwner.cpp','f->getClassName()!="FilmRailTendon"','f->getClassName()!="FilmRoutedTendon"||read<double>(f,"routeAmplitude")!=4.5')
 for name in ('models/film_three_finger/ThreeFilmOwner.cpp','models/film_three_finger_event/ThreeFilmEventOwner.cpp'):
  path=archive/name;text=path.read_text();text=re.sub(r'\bThreeFilm[A-Za-z0-9_]*(?:ODE|Clock)\b',lambda m:'Routed'+m.group(),text);path.write_text(text);changes[name]=sha(path)
 name='models/film_three_finger_event/ThreeFilmEventOwner.cpp'
 patch(name,'extern "C" {','void registerFilmRoutedField(sofa::core::ObjectFactory*);\nextern "C" {')
 patch(name,'void registerObjects(sofa::core::ObjectFactory*f){','void registerObjects(sofa::core::ObjectFactory*f){registerFilmRoutedField(f);')
 patch(name,'return "ReGripThreeFilmEvent";','return "ReGripRoutedThreeFilmEvent";')
 patch('models/film_three_finger_event/CMakeLists.txt','SHARED ThreeFilmEventOwner.cpp)','SHARED ThreeFilmEventOwner.cpp ../film_routed_tendon/Field.generated.cpp)')
 return changes
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--reference-provider');p.add_argument('--build-provider');p.add_argument('--steps',type=int,choices=(1,8,50),default=1);p.add_argument('--cost-pair',nargs=2);a=p.parse_args();gate=ROOT/'results/autonomous_film_20261118_routed_contact_force1265';g=json.loads((gate/'summary.json').read_text())
 if a.steps>1 and (a.reference_provider or not a.build_provider):raise ValueError('continuation requires its own reference path and completed actual first-impact build profile')
 if a.steps==50 and not a.cost_pair:raise ValueError('50step first-peak needs measured startup+continuation cost model')
 if g['status']!='PASS':raise ValueError('independent implicit force/tangent/control prerequisite failed')
 for name,d in g['source_hashes'].items():
  if name=='models/film_routed_contact/Force.h' and sha(ROOT/name)!=d:raise ValueError('qualified force adapter changed')
 parent=ROOT/'results/autonomous_film_20261118_three_film_first_peak_actual1002';meta=json.loads((parent/'summary.json').read_text());scene_hash=meta.get('scene_sha256',meta.get('scene_hash'))
 if meta['status']!='PASS' or not scene_hash or sha(parent/'scene.scn')!=scene_hash:raise ValueError('actual1002 scene identity required')
 ledger=json.loads((ROOT/'reports/FILM_CONTACT_EVIDENCE_20261118_three_film_v10.json').read_text())
 for file in ('public_mass_reference.txt','scene.scn'):
  path=parent/file
  if sha(path)!=ledger['files'][str(path.relative_to(ROOT))]:raise ValueError('immutable original1002 input changed')
 for path,digest in meta['plugins'].items():
  if sha(path)!=digest:raise ValueError('original scene plugin/mapping binary changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(ROOT/'tools/film_routed_generate.py',out/'field_generator.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));test=archive/'tests/test_three_film_birth.cpp';test.parent.mkdir();shutil.copy2(ROOT/'tests/test_three_film_birth.cpp',test);shutil.copy2(ROOT/'tests/test_film_rail_tendon_api.cpp',test.parent/'test_film_rail_tendon_api.cpp');generated=generate(archive);modified=specialize(archive);sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};shutil.copy2(parent/'public_mass_reference.txt',out/'public_mass_reference.txt');r=dict(status='FAIL',scope='actual separate quadratic-route THREE-film/ONE free sphere externally bracketed first impact+compressive remainder;NOT wrapping/holding/CCD/thickness/friction/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,generated_source_identity=generated,coupled_specialization=modified,sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),actual_steps=1,dt_s=.0002,control='original shared C2 .0001N/rail,ramp10ms,release20..30ms',initial='films REST;sphere incoming vz=-1mm/s,offset+.0001mm;NOT capture from stationary separation',gravity=[0,0,0],external_force_N=[0,0,-.001],contact_model='triangle midsurface buffered sphereR30.01;frictionless perfectly inelastic;finite wire/guide contact absent',force_adapter_gate_sha256=sha(gate/'summary.json'),public_mass_sha256=sha(out/'public_mass_reference.txt'))
 ref=out/'reference'
 provider=None
 if a.build_provider:
  provider=ROOT/'results'/('autonomous_film_'+a.build_provider);bm=json.loads((provider/'summary.json').read_text())
  if bm['status']!='PASS' or compiled_sources(bm['source_hashes'])!=compiled_sources(sources) or bm['public_mass_sha256']!=r['public_mass_sha256'] or bm['sdk_runner_sha256']!=r['sdk_runner_sha256']:raise ValueError('EXACT qualified coupled source/input/SDK closure required')
  for f,d in bm['source_hashes'].items():
   if sha(provider/'sources'/f)!=d:raise ValueError('coupled provider source changed')
  if sha(ROOT/bm['build_relative']/'libReGripThreeFilmEvent.so')!=bm['binary_sha256'] or sha(provider/'reference')!=bm['reference_binary_sha256']:raise ValueError('coupled binary changed')
  forecast=2*bm['process']['runtime_s']*a.steps+30;r.update(predicted_child_runtime_s=forecast,build_provider_summary_sha256=sha(provider/'summary.json'),actual_steps=a.steps)
  if a.cost_pair:
   costs=[]
   for name in a.cost_pair:
    path=ROOT/'results'/('autonomous_film_'+name);cm=json.loads((path/'summary.json').read_text())
    if cm['status']!='PASS' or cm['binary_sha256']!=bm['binary_sha256'] or cm['reference_binary_sha256']!=bm['reference_binary_sha256'] or cm['public_mass_sha256']!=r['public_mass_sha256'] or cm['control']!=r['control']:raise ValueError('same completed contact cost family required')
    reference=cm['reference_process'];chain=[]
    for depth in range(4):
     if 'runtime_s' in reference:break
     source=ROOT/'results'/('autonomous_film_'+reference['reused_from']);digest=reference['provider_summary_sha256']
     if sha(source/'summary.json')!=digest:raise ValueError('reference cost source changed')
     chain.append(dict(case=source.name,summary_sha256=digest));reference=json.loads((source/'summary.json').read_text())['reference_process']
    else:raise ValueError('reference cost chain unresolved')
    costs.append(dict(case=name,summary_sha256=sha(path/'summary.json'),steps=cm['actual_steps'],actual_s=cm['process']['runtime_s'],reference_s=reference['runtime_s'],reference_cost_chain=chain))
   costs.sort(key=lambda c:c['steps'])
   if [c['steps'] for c in costs]!=[1,8] or a.steps!=50:raise ValueError('explicit one-impact/eight-step fixed-dimension startup model only')
   estimates={}
   for key in ('actual_s','reference_s'):
    marginal=(costs[1][key]-costs[0][key])/7
    if marginal<=0:raise ValueError('nonpositive marginal cost cannot extrapolate')
    estimates[key]=1.2*(costs[0][key]+(a.steps-1)*marginal)+30
   forecast=max(estimates.values());r.update(predicted_child_runtime_s=forecast,cost_evidence=costs,cost_model='measured startup+49 identical-size sustained steps,20% margin+30s;480s hard unchanged',child_cost_estimates_s=estimates)
  if forecast>480:r.update(status='BLOCKED',failure_reason='measured first-impact conservative forecast>480s;NOT OS exhaustion');write_json(out/'summary.json',r);return
 if a.reference_provider:
  prev=ROOT/'results'/('autonomous_film_'+a.reference_provider);old=json.loads((prev/'summary.json').read_text());left=compiled_sources(old['source_hashes']);right=compiled_sources(sources);owners={'models/film_three_finger/ThreeFilmOwner.cpp','models/film_three_finger_event/ThreeFilmEventOwner.cpp'}
  if old['reference_process']['exit_code'] or old['public_mass_sha256']!=r['public_mass_sha256'] or {k:v for k,v in left.items() if k not in owners}!={k:v for k,v in right.items() if k not in owners}:raise ValueError('reference compiled closure differs beyond SOFA-only owner files')
  for f,d in old['source_hashes'].items():
   if sha(prev/'sources'/f)!=d:raise ValueError('archived reference source changed')
  if sha(prev/'reference')!=old['reference_binary_sha256']:raise ValueError('reference binary changed')
  shutil.copy2(prev/'reference',ref);shutil.copy2(prev/'reference.csv',out/'reference.csv');rc=dict(exit_code=0,reused_from=a.reference_provider,scope='reference closure unchanged;only SOFA translation units differ');rr=dict(exit_code=0,reused_from=a.reference_provider,scope='completed reference output reused;NOT rerun',output_sha256=sha(prev/'reference.csv'),provider_summary_sha256=sha(prev/'summary.json'))
 elif provider:shutil.copy2(provider/'reference',ref);rc=dict(exit_code=0,reused_from=a.build_provider,scope='EXACT full compiled/input closure')
 else:rc=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',test,'-o',ref],out/'reference_compile',120)
 r['reference_compile']=rc;write_json(out/'summary.json',r)
 if rc['exit_code']!=0:return
 if not a.reference_provider:rr=guarded([ref,out/'public_mass_reference.txt',out/'reference.csv']+([str(a.steps),'accumulated'] if a.steps>1 else []),out/'reference_process',480)
 r.update(reference_process=rr,reference_binary_sha256=sha(ref));write_json(out/'summary.json',r)
 if rr['exit_code']!=0:return
 if provider:build=ROOT/bm['build_relative'];configure=compile=dict(exit_code=0,reused_from=a.build_provider)
 else:
  build=ROOT/'build'/('routed_coupled_'+a.tag);build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',archive/'models/film_three_finger_event','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None
 r.update(configure=configure,compile=compile,build_relative=str(build.relative_to(ROOT)));write_json(out/'summary.json',r)
 if not compile or compile['exit_code']!=0:return
 binary=build/'libReGripThreeFilmEvent.so';deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
 if 'not found' in deps or any('libSofa.' in l and '=> /' in l and str(SDK) not in l for l in deps.splitlines()):raise ValueError('coupled routed SDK ABI mismatch')
 tree=ET.parse(parent/'scene.scn');scene=tree.getroot();scene.set('dt','.0002')
 for node in scene.iter():
  if node.tag=='RequiredPlugin' and 'libReGripThreeFilmEvent.so' in node.get('pluginName',''):node.set('pluginName',str(binary))
  if node.tag=='FilmRailTendon':node.tag='FilmRoutedTendon';node.set('routeAmplitude','4.5')
  for key,value in list(node.attrib.items()):
   if key in ('filename','displacementFilename','ownerCostFilename','costProfileFilename','publicMassFilename') and value.startswith(str(parent)):node.set(key,str(out)+value[len(str(parent)):])
 owner=scene.find('ThreeFilmFirstPeakODE');owner.tag='RoutedThreeFilmBracketedEventODE' if a.steps==1 else 'RoutedThreeFilmEventContinuationODE' if a.steps==8 else 'RoutedThreeFilmFirstPeakODE';owner.set('maxSteps','64' if a.steps==50 else '8');owner.set('firstIntervalJournal','true')
 for key in ('ownerCostFilename','publicMassFilename','reuseJournalRows'):owner.attrib.pop(key,None)
 tree.write(out/'scene.scn');r.update(binary_sha256=sha(binary),scene_sha256=sha(out/'scene.scn'),plugins={node.get('pluginName'):sha(node.get('pluginName')) for node in scene.findall('RequiredPlugin') if node.get('pluginName','').startswith('/')});run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',out/'scene.scn'],out/'process',480);errors=sum((out/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log'));r.update(process=run,sofa_errors=errors)
 if run['exit_code']==0 and not errors and (out/'three.event.csv').exists():
  actual=list(csv.DictReader((out/'three.event.csv').open()));expected=list(csv.DictReader((out/'reference.csv').open()));states=list(csv.DictReader((out/'three.states.csv').open()))
  if len(actual)!=1 or len(expected)!=1 or len(states)!=a.steps:raise ValueError('complete actual event records required')
  differences={k:float(np.max(abs(np.fromstring(actual[0][k],sep=' ')-np.fromstring(expected[0][k],sep=' ')))) for k in actual[0]};gap=float(states[0]['minimum_gap']);momentum=float(states[0]['momentum_residual']);velocity=float(states[0]['normal_velocity_residual']);r.update(status='PASS' if max(differences.values())<=1e-12 and gap>=-1e-10 and momentum<=1e-17 and velocity<=1e-10 else 'FAIL',reference_max_abs=differences,minimum_whole_stage_gap_mm=gap,momentum_residual_Ns=momentum,normal_velocity_residual_mm_s=velocity,api_gate=1e-12)
  if a.steps>1:
   expected_states=list(csv.DictReader((out/'reference.csv.states.csv').open()))
   if len(expected_states)!=a.steps:raise ValueError('complete accumulated reference continuation required')
   api={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(states,expected_states)) for k in ('q','v')};clock=all(x['time']==y['time'] for x,y in zip(states,expected_states));gap=min(float(x['minimum_gap']) for x in states);momentum=max(float(x['momentum_residual']) for x in states);velocity=max(float(x['normal_velocity_residual']) for x in states);r.update(continued_reference_max_abs=api,accumulated_clock_exact=clock,minimum_whole_stage_gap_mm=gap,momentum_residual_Ns=momentum,normal_velocity_residual_mm_s=velocity)
   if max(api.values())>1e-12 or not clock or gap< -1e-10 or momentum>1e-17 or velocity>1e-10:r['status']='FAIL'
 r['raw_hashes']={f.name:sha(f) for f in out.glob('*.csv')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','configure','reference_compile','reference_process','process','raw_hashes')}))
if __name__=='__main__':main()
