"""Actual3 FilmRailTendon + ONE free Rigid3,narrow REST/T0 persistent IVP."""
import argparse,copy,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--reference',required=True);p.add_argument('--reuse');p.add_argument('--radius',type=float,default=30.01,help='actual XML Data;unsupported values must be rejected by runtime owner');a=p.parse_args();ref=ROOT/'results'/('autonomous_film_'+a.reference);rs=json.loads((ref/'summary.json').read_text())
 if rs['status']!='PASS' or not rs.get('precise_ties') or rs['dt']!=.0001 or rs['external_force_N']!=[0,0,-.001] or not (ref/'state.csv').exists():raise ValueError('completed independently precise3film,REST100us,-1mN reference required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()}
 for name,digest in rs['sources'].items():
  if name.endswith('.h') and sources.get(name)!=digest:raise ValueError('qualified independent header differs:'+name)
 build=ROOT/'build'/('three_film_'+a.tag)
 if a.reuse:
  prior=ROOT/'results'/('autonomous_film_'+a.reuse);pm=json.loads((prior/'identity.json').read_text());ps=json.loads((prior/'summary.json').read_text());build=ROOT/'build'/('three_film_'+a.reuse)
  if ps['status']!='PASS' or pm['sources']!=sources or sha(build/'libReGripThreeFilmContact.so')!=pm['binary_sha256']:raise ValueError('three-film source/binary reuse mismatch')
  configure=compile=dict(exit_code=0,reused=a.reuse)
 else:
  build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',archive/'models/film_three_finger','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None
 identity=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources=sources,reference=a.reference,reference_state_sha256=sha(ref/'state.csv'),actual_solver='ThreeFilmPersistentODE same three-row Lobatto,precision ranking;NOT impact/closing',steps=1,dt=.0001,material_parameters='archived research rectangular Assembly default E250MPa nu0,not measured',geometry='3 proper120degree frames,root-centre50mm,100mm rectangular coupons,R30 sphere',external_force_N=[0,0,-.001],tension_per_rail_N=0,friction=False,gravity=[0,0,0],self_collision=False,initial_state='REST,already touching;NOT closing or fresh impact',scope='actual3film/oneFREEsphere100us contact IVP;NOT grasp,lift,fullcycle or mesh/time certificate')
 result=dict(status='FAIL',scope=identity['scope'],configure=configure,compile=compile)
 if compile and compile['exit_code']==0:
  binary=build/'libReGripThreeFilmContact.so';identity['binary_sha256']=sha(binary);deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in line and '=> /' in line and str(SDK) not in line for line in deps.splitlines()):raise ValueError('Installed SDK ABI mismatch')
  original=ROOT/'results/autonomous_film_20261117_combined_sparse_1ms821';original_tree=ET.parse(original/'scene.scn');old=original_tree.getroot();scene=ET.Element('Node',dict(name='actual_three_film_rest_IVP',dt='.0001',gravity='0 0 0'))
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
  body=copy.deepcopy(old.find('Node[@name="free_object"]'));body.find('MechanicalObject').set('position','0 0 -63.44761697652639 0 0 0 1');body.find('MechanicalObject').set('velocity','0 0 0 0 0 0');body.find('UniformMass').set('vertexMass','.0001 1 360 0 0 0 360 0 0 0 360');scene.append(body)
  ET.SubElement(scene,'ThreeFilmPersistentODE',dict(name='ode',root='@finger0/dofs',root1='@finger1/dofs',root2='@finger2/dofs',field='@finger0/assembly/filmField',field1='@finger1/assembly/filmField',field2='@finger2/assembly/filmField',body='@free_object/body',radius=str(a.radius),rayleighMass='2',maxSteps='1',externalForce='0 0 -.001',filename=str(out/'three')));ET.ElementTree(scene).write(out/'scene.scn')
  identity['source_scene_sha256']=sha(original/'scene.scn');identity['sdk_library_paths']=[str(SDK)];identity['plugin_sha256']={node.get('pluginName'):sha(node.get('pluginName')) for node in scene.findall('RequiredPlugin') if node.get('pluginName','').startswith('/')};write_json(out/'identity.json',identity)
  process=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',out/'scene.scn'],out/'process',120);result['process']=process
  errors=sum((out/'process'/name).read_text(errors='replace').count('[ERROR]') for name in ('stdout.log','stderr.log'));result['sofa_error_count']=errors
  path=out/'three.states.csv'
  if process['exit_code']==0 and not errors and path.exists():
   actual=list(csv.DictReader(path.open()));reference=list(csv.DictReader((ref/'state.csv').open()));policies=list(csv.DictReader((out/'three.policy.csv').open()));rows=list(csv.DictReader((out/'three.rows.csv').open()));eq={k:float(np.max(abs(np.fromstring(actual[0][k],sep=' ')-np.fromstring(reference[0][k],sep=' ')))) for k in ('q','v')} if len(actual)==len(reference)==1 else {};policy_ok=len(policies)==1 and policies[0]['component']=='ThreeFilmPersistentODE' and policies[0]['films']=='3' and policies[0]['rigid_bodies']=='1' and float(policies[0]['external_Fz'])==-.001 and float(policies[0]['radius'])==a.radius==30.01
   result.update(status='PASS' if eq and max(eq.values())<1e-12 and policy_ok and len(rows)==9 and float(actual[0]['minimum_gap'])>=-1e-10 else 'FAIL',independent_state_errors=eq,runtime_policy=policies,owned_rows=len(rows),minimum_gap=float(actual[0]['minimum_gap']) if actual else None)
 write_json(out/'identity.json',identity);write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k in ('status','independent_state_errors','minimum_gap','process','sofa_error_count')}))
if __name__=='__main__':main()
