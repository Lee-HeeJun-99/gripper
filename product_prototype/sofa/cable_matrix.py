"""One-factor stock Cable/FEM isolation, immutable scene/compiled provenance."""
import argparse,csv,json,hashlib,subprocess,shutil,sys,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parent;SDK=Path('/home/ubuntu/SOFA/v26.06.00')
sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(BASE/'cad'))
from film_guarded_process import guarded
from generate import world,width
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def flat(v):return ' '.join(format(float(x),'.17g') for row in v for x in row)
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cables',type=int,choices=(1,2),default=2);p.add_argument('--guide',choices=('surface','outboard'),default='outboard');p.add_argument('--stroke',type=float,default=8);p.add_argument('--steps',type=int,default=800);p.add_argument('--dt',type=float,default=.0025);p.add_argument('--reuse-build');p.add_argument('--no-journal',action='store_true');a=p.parse_args()
 if not(0<=a.stroke<=8 and 0<a.steps<=3200):raise ValueError('bounded diagnostic')
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=out/'source';src.mkdir()
 for name in ('Controller.cpp','CMakeLists.txt','cable_matrix.py'):shutil.copy2(BASE/'sofa'/name,src/name)
 source_hashes={f.name:sha(f) for f in src.iterdir()};r=dict(status='FAIL',scope='stock Cable/FEM diagnostic NOT grasp certification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=source_hashes,command=sys.argv,sdk=str(SDK),cables=a.cables,guide=a.guide,stroke_mm=a.stroke,dt_s=a.dt,steps=a.steps)
 build=BASE/'cad'/('build_'+(a.reuse_build or a.tag))
 if a.reuse_build:
  prior=json.loads((BASE/'results'/a.reuse_build/'summary.json').read_text())
  if any(source_hashes[k]!=prior['source_hashes'][k] for k in ('Controller.cpp','CMakeLists.txt')) or sha(build/'libReGripProductSequence.so')!=prior['binary_sha256']:raise ValueError('compiled source/binary mismatch')
 else:
  r['configure']=guarded(['cmake','-S',src,'-B',build,'-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);r['compile']=guarded(['cmake','--build',build,'-j','1'],out/'compile',180)
  if r['compile']['exit_code']:raise RuntimeError('compile failed;preserve process evidence')
 binary=build/'libReGripProductSequence.so';r.update(binary_sha256=sha(binary),build=str(build.relative_to(ROOT)))
 original=BASE/'results/native_R20_hold_044';tree=ET.parse(original/'scene.scn');root=tree.getroot();root.set('gravity','0 0 0');root.set('dt',str(a.dt));c=json.loads((original/'config.json').read_text());m=json.loads((original/'mesh.json').read_text())
 for node in list(root):
  if node.tag=='Node' and node.get('name')!='finger0':root.remove(node)
  if node.tag=='RequiredPlugin' and 'libReGripProductSequence.so' in node.get('pluginName',''):node.set('pluginName',str(binary))
 finger=root.find('./Node');control=finger.find('NativeCableSequence');control.set('filename',str(out/'finger0.csv'));control.set('stroke',str(a.stroke*.001));control.set('hold','1');control.set('release','1.5')
 if a.guide=='surface':
  for j,side in enumerate((-1,1)):
   cable=finger.find(f"./Node[@name='cable{j}']");positions=[[x,side*(width(c,x)/2-1),c['finger']['skin_thickness']] for x in c['tendon']['guide_stations']];cable.find('MechanicalObject').set('position',flat(np.array([world(c,x,0) for x in positions])*.001));cable.find('CableConstraint').set('pullPoint',flat([np.array(world(c,[0,side*(width(c,0)/2-1),c['finger']['skin_thickness']],0))*.001]))
 if a.cables==1:
  finger.remove(finger.find("./Node[@name='cable1']"));control.set('cable1','@cable0/actuator');r['single_logging']='two CSV cable columns intentionally alias one physical constraint;count once'
 if not a.no_journal:
  ET.SubElement(root,'NativeConstraintJournal',solver='@constraints',filename=str(out/'constraints.csv'))
  ET.SubElement(finger,'NativeCableAudit',body='@dofs',cable='@cable0/actuator',filename=str(out/'cable_audit.csv'))
 c['diagnostic']=dict(cables=a.cables,guide=a.guide,normal_offset_mm=.1 if a.guide=='surface' else 3,outboard_mm=-1 if a.guide=='surface' else 14);c['simulation']['dt_s']=a.dt;c['simulation']['hold_end_s']=1;c['simulation']['release_end_s']=1.5
 (out/'config.json').write_text(json.dumps(c,indent=2));shutil.copy2(original/'mesh.json',out/'mesh.json');tree.write(out/'scene.scn');r.update(scene_sha256=sha(out/'scene.scn'),config_sha256=sha(out/'config.json'),mesh_sha256=sha(out/'mesh.json'),original_scene_sha256=sha(original/'scene.scn'));r['process']=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',a.steps,'--hideProgressBar',out/'scene.scn'],out/'process',480)
 if r['process']['exit_code']==0:
  rows=list(csv.DictReader((out/'finger0.csv').open()));metrics=[];time=np.array([float(x['time_s']) for x in rows]);command=np.array([float(x['command_m']) for x in rows]);hold=np.flatnonzero((time>=.6)&(time<=1+1e-12))
  for j in range(a.cables):
   cable=finger.find(f"./Node[@name='cable{j}']");pull=np.fromstring(cable.find('CableConstraint').get('pullPoint'),sep=' ');initial=np.fromstring(cable.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);L0=np.linalg.norm(np.diff(np.vstack([pull,initial]),axis=0),axis=1).sum();actual=np.array([L0-np.linalg.norm(np.diff(np.vstack([pull,np.fromstring(row[f'guide{j}_q_m'],sep=' ').reshape(-1,3)]),axis=0),axis=1).sum() for row in rows]);internal=np.array([float(row[f'cable{j}_displacement_m']) for row in rows]);force=np.array([float(row[f'cable{j}_force_raw'])/a.dt for row in rows]);metrics.append(dict(cable=j,L0_m=float(L0),hold_end_shortening_mm=float(actual[hold[-1]]*1000) if len(hold) else None,maximum_hold_error_mm=float(np.max(np.abs(actual[hold]-command[hold]))*1000) if len(hold) else None,max_error_mm=float(np.max(np.abs(actual-command))*1000),internal_final_mm=float(internal[-1]*1000),peak_force_N=float(force.max())))
  r.update(status='RUN_COMPLETED_NOT_QUALIFIED',rows=len(rows),tracking=metrics)
  if (out/'constraints.csv').exists():
   solver=list(csv.DictReader((out/'constraints.csv').open()));r['solver']=dict(max_error=max(float(x['error']) for x in solver),max_iterations=max(int(x['iterations']) for x in solver))
 r['raw_hashes']={f.name:sha(f) for f in out.glob('*.csv')};(out/'summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
if __name__=='__main__':main()
