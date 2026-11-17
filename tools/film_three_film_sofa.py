"""Actual3 FilmRailTendon + ONE free Rigid3,narrow REST/T0 persistent IVP."""
import argparse,copy,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--reference',required=True);p.add_argument('--reuse');p.add_argument('--profile');p.add_argument('--pilot-profile')
 p.add_argument('--field-profile',action='store_true',help='opt-in actual Field passive timers;does NOT measure custom-owner internals');p.add_argument('--owner-profile',action='store_true',help='passive owner force/Hessian/geometry inclusive timers')
 p.add_argument('--mass-journal',action='store_true',help='record public nodal mass and rigid mass/inertia without modifying solve')
 p.add_argument('--radius',type=float,default=30.01,help='actual XML Data;unsupported values must be rejected by runtime owner');a=p.parse_args();ref=ROOT/'results'/('autonomous_film_'+a.reference);rs=json.loads((ref/'summary.json').read_text());uniform='completed_rows' in rs
 physics=rs;steps=1;duration=.0001;reference_file=ref/'state.csv'
 if uniform:
  physics=json.loads((ROOT/'results'/('autonomous_film_'+rs['profile'])/'summary.json').read_text());steps=rs['steps'];duration=rs['duration'];reference_file=ref/'states.csv'
  if steps not in (4,8,16,32) or rs['completed_rows']!=steps or duration!=.0001:raise ValueError('completed bounded three-film uniform reference required')
 driven='maximum_tension_N' in rs
 if driven:
  steps=rs['steps'];duration=rs['duration'];reference_file=ref/'states.csv'
  if rs['status']!='PASS' or steps not in ((8,16,32) if rs.get('exact_order_fallback',False) else (8,)) or duration!=.01 or rs['maximum_tension_N']!=.0001 or rs.get('adaptive_gap_control',False):raise ValueError('completed supported uniform10ms common C2 pilot required')
 elif rs['status']!='PASS' or not physics.get('precise_ties') or physics['dt']!=.0001 or physics['external_force_N']!=[0,0,-.001] or not reference_file.exists():raise ValueError('completed independently precise3film,REST100us,-1mN reference required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()}
 for name,digest in rs['sources'].items():
  if name.endswith('.h') and sources.get(name)!=digest:raise ValueError('qualified independent header differs:'+name)
 build=ROOT/'build'/('three_film_'+a.tag)
 if a.reuse:
  prior=ROOT/'results'/('autonomous_film_'+a.reuse);pm=json.loads((prior/'identity.json').read_text());ps=json.loads((prior/'summary.json').read_text());build=ROOT/'build'/('three_film_'+a.reuse)
  compiled=lambda values:{k:v for k,v in values.items() if k.endswith(('.h','.cpp')) or k.endswith('/CMakeLists.txt')}
  if ps['status']!='PASS' or compiled(pm['sources'])!=compiled(sources) or sha(build/'libReGripThreeFilmContact.so')!=pm['binary_sha256']:raise ValueError('three-film compiled source/binary reuse mismatch;only noncompiled documents excluded')
  configure=compile=dict(exit_code=0,reused=a.reuse)
 else:
  build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',archive/'models/film_three_finger','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None
 identity=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources=sources,reference=a.reference,reference_state_sha256=sha(reference_file),actual_solver='ThreeFilmPersistentODE same three-row Lobatto,precision ranking;NOT impact/closing',steps=steps,dt=duration/steps,duration=duration,material_parameters='archived research rectangular Assembly default E250MPa nu0,not measured',geometry='3 proper120degree frames,root-centre50mm,100mm rectangular coupons,R30 sphere',external_force_N=[0,0,-.001],tension_per_rail_N=0,friction=False,gravity=[0,0,0],self_collision=False,initial_state='REST,already touching;NOT closing or fresh impact',scope='actual3film/oneFREEsphere100us contact IVP;NOT grasp,lift,fullcycle or mesh/time certificate')
 identity['field_profile']=a.field_profile
 identity['owner_profile']=a.owner_profile
 identity['mass_journal']=a.mass_journal
 if driven:identity.update(actual_solver=('ThreeFilmDrivenExactODE' if rs.get('exact_order_fallback',False) else 'ThreeFilmDrivenODE')+' common C2 Lobatto persistent rows',exact_order_fallback=rs.get('exact_order_fallback',False),tension_per_rail_N=.0001,scope='actual three-film common C2 10ms already-touching pilot;NOT fresh impact,full closing,wrapping or grasp')
 if driven and rs.get('exact_order_fallback',False):identity.update(actual_solver='ThreeFilmDrivenExactODE common C2 exact unresolved-distance order',exact_order_fallback=True)
 result=dict(status='FAIL',scope=identity['scope'],configure=configure,compile=compile)
 if compile and compile['exit_code']==0:
  binary=build/'libReGripThreeFilmContact.so';identity['binary_sha256']=sha(binary);deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in line and '=> /' in line and str(SDK) not in line for line in deps.splitlines()):raise ValueError('Installed SDK ABI mismatch')
  if driven:
   if a.pilot_profile:raise ValueError('driven pilot requires independent or actual same-DLL profile,not T0 pilot')
   if a.profile:
    prior=ROOT/'results'/('autonomous_film_'+a.profile);pm=json.loads((prior/'identity.json').read_text());ps=json.loads((prior/'summary.json').read_text())
    if ps['status']!='PASS' or pm['binary_sha256']!=identity['binary_sha256'] or any(pm[k]!=identity[k] for k in ('duration','actual_solver','tension_per_rail_N','external_force_N')):raise ValueError('driven actual runtime profile must have identical DLL and physical input')
    estimate=2*ps['process']['runtime_s']*steps/pm['steps'];identity.update(profile=a.profile,profile_kind='two times measured same-DLL driven runtime per step')
   else:estimate=4*rs['run']['runtime_s'];identity.update(profile=a.reference,profile_kind='four times completed same-input independent nonlinear runtime')
   identity['predicted_runtime_s']=estimate
   if estimate>480:write_json(out/'identity.json',identity);write_json(out/'summary.json',dict(status='BLOCKED',predicted_runtime_s=estimate));return
  elif steps>1:
   profile=a.profile or a.pilot_profile
   if not profile or (a.profile and a.pilot_profile):raise ValueError('one measured actual runtime profile required')
   prior=ROOT/'results'/('autonomous_film_'+profile);pm=json.loads((prior/'identity.json').read_text());ps=json.loads((prior/'summary.json').read_text());estimate=2*ps['process']['runtime_s']*steps/pm['steps']
   if ps['status']!='PASS' or pm['external_force_N']!=identity['external_force_N'] or pm['tension_per_rail_N']!=0:raise ValueError('actual runtime physics profile mismatch')
   if a.profile and pm['binary_sha256']!=identity['binary_sha256']:raise ValueError('actual same-binary profile required')
   if a.pilot_profile:
    if steps>8 or a.reuse:raise ValueError('new repeated-owner pilot<=8steps only')
    for name,digest in pm['sources'].items():
     if name.endswith('.h') and sources.get(name)!=digest:raise ValueError('actual profiled physical kernel changed:'+name)
   identity.update(predicted_runtime_s=estimate,profile=profile,profile_kind='changed one-step-to-repeat owner pilot,same kernel headers' if a.pilot_profile else 'same binary')
   if estimate>480:write_json(out/'identity.json',identity);write_json(out/'summary.json',dict(status='BLOCKED',scope='measured child runtime policy,NOT OS exhaustion',predicted_runtime_s=estimate));return
  original=ROOT/'results/autonomous_film_20261117_combined_sparse_1ms821';original_tree=ET.parse(original/'scene.scn');old=original_tree.getroot();scene=ET.Element('Node',dict(name='actual_three_film_rest_IVP',dt=format(duration/steps,'.17g'),gravity='0 0 0'))
  for element in old:
   if element.tag in ('RequiredPlugin','DefaultAnimationLoop'):
    node=copy.deepcopy(element)
    if 'libReGripCombinedContact.so' in node.get('pluginName',''):node.set('pluginName',str(binary))
    scene.append(node)
  for f in range(3):
   finger=ET.SubElement(scene,'Node',dict(name='finger'+str(f)))
   for node in old:
    if node.tag in ('MechanicalObject','FixedProjectiveConstraint','PartialFixedProjectiveConstraint') or (node.tag=='Node' and node.get('name')=='assembly'):finger.append(copy.deepcopy(node))
   root=finger.find('MechanicalObject');zero=' '.join('0' for _ in root.get('position').split());root.set('position',zero);root.set('velocity',zero);surface=finger.find('.//MechanicalObject[@name="surface"]');surface.set('position',zero);surface.set('velocity',zero);field=finger.find('.//FilmRailTendon');field.set('maximumTension','0');field.set('guideOffset','5');field.set('guideIntervals','4');field.set('rootGuideSecondOrder','1');field.set('c2Control','1');field.set('filename',str(out/('film_'+str(f)+'.csv')));field.set('displacementFilename',str(out/('displacement_'+str(f)+'.csv')))
  if driven:
   for field in scene.findall('.//FilmRailTendon'):
    for key,value in dict(maximumTension='.0001',rampTime='.01',releaseBegin='.02',releaseEnd='.03',c2Control='1').items():field.set(key,value)
  if a.field_profile:
   for f,field in enumerate(scene.findall('.//FilmRailTendon')):field.set('costProfileFilename',str(out/('field_cost_'+str(f)+'.csv')))
  body=copy.deepcopy(old.find('Node[@name="free_object"]'));body.find('MechanicalObject').set('position','0 0 -63.44761697652639 0 0 0 1');body.find('MechanicalObject').set('velocity','0 0 0 0 0 0');body.find('UniformMass').set('vertexMass','.0001 1 360 0 0 0 360 0 0 0 360');scene.append(body)
  ET.SubElement(scene,'ThreeFilmPersistentODE',dict(name='ode',root='@finger0/dofs',root1='@finger1/dofs',root2='@finger2/dofs',field='@finger0/assembly/filmField',field1='@finger1/assembly/filmField',field2='@finger2/assembly/filmField',body='@free_object/body',radius=str(a.radius),rayleighMass='2',maxSteps=str(steps),externalForce='0 0 -.001',filename=str(out/'three')));ET.ElementTree(scene).write(out/'scene.scn')
  if a.owner_profile:scene.find('ThreeFilmPersistentODE').set('ownerCostFilename',str(out/'owner_cost.csv'));ET.ElementTree(scene).write(out/'scene.scn')
  if a.mass_journal:scene.find('ThreeFilmPersistentODE').set('publicMassFilename',str(out/'public_mass.txt'));ET.ElementTree(scene).write(out/'scene.scn')
  if driven:scene.find('ThreeFilmPersistentODE').tag='ThreeFilmDrivenExactODE' if rs.get('exact_order_fallback',False) else 'ThreeFilmDrivenODE';ET.ElementTree(scene).write(out/'scene.scn')
  identity['source_scene_sha256']=sha(original/'scene.scn');identity['sdk_library_paths']=[str(SDK)];identity['plugin_sha256']={node.get('pluginName'):sha(node.get('pluginName')) for node in scene.findall('RequiredPlugin') if node.get('pluginName','').startswith('/')};write_json(out/'identity.json',identity)
  process=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',out/'scene.scn'],out/'process',120 if steps==1 else 480);result['process']=process
  errors=sum((out/'process'/name).read_text(errors='replace').count('[ERROR]') for name in ('stdout.log','stderr.log'));result['sofa_error_count']=errors
  path=out/'three.states.csv'
  if process['exit_code']==0 and not errors and path.exists():
   actual=list(csv.DictReader(path.open()));reference=list(csv.DictReader(reference_file.open()));policies=list(csv.DictReader((out/'three.policy.csv').open()));rows=list(csv.DictReader((out/'three.rows.csv').open()));eq={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(actual,reference)) for k in ('q','v')} if len(actual)==len(reference)==steps else {};policy_ok=len(policies)==1 and policies[0]['component']=='ThreeFilmPersistentODE' and policies[0]['films']=='3' and policies[0]['rigid_bodies']=='1' and float(policies[0]['external_Fz'])==-.001 and float(policies[0]['radius'])==a.radius==30.01 and int(policies[0]['maximum_steps'])==steps
   if driven:policy_ok=len(policies)==1 and policies[0]['component']==('ThreeFilmDrivenExactODE' if rs.get('exact_order_fallback',False) else 'ThreeFilmDrivenODE') and policies[0]['films']=='3' and policies[0]['rigid_bodies']=='1' and float(policies[0]['external_Fz'])==-.001 and float(policies[0]['radius'])==a.radius==30.01 and int(policies[0]['maximum_steps'])==steps
   aligned=not (uniform or driven) or (len(actual)==steps and max(abs(float(x['time'])-float(y['time'])) for x,y in zip(actual,reference))<1e-12)
   minimum=min(float(x['minimum_gap']) for x in actual) if actual else None
   result.update(status='PASS' if eq and max(eq.values())<1e-12 and policy_ok and aligned and len(rows)==9*steps and minimum>=-1e-10 else 'FAIL',independent_state_errors=eq,runtime_policy=policies,owned_rows=len(rows),minimum_gap=minimum)
 write_json(out/'identity.json',identity);write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k in ('status','independent_state_errors','minimum_gap','process','sofa_error_count')}))
if __name__=='__main__':main()
