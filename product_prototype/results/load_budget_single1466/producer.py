"""One preregistered actuator load-sizing contrast,not a force parameter search."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--single',action='store_true');p.add_argument('--duration',type=float,choices=[.25,.8,1.2,2.],default=.8);p.add_argument('--pilot');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_railback_grasp1001298';root=ET.parse(src/'scene.scn').getroot();budget_src=BASE/'results/grasp_load_budget1465/summary.json';budget=json.loads(budget_src.read_text());assert budget['status']=='READY_SINGLE_LOAD_SIZING_HYPOTHESIS';force=budget['proposed_force_N_per_cable'];assert 2.<force<=2.5
 for control in root.iter('NativeCableSequence'):control.set('maximumForceN',format(force,'.17g'))
 if a.single:
  for n in list(root):
   if n.tag=='Node' and n.get('name') not in ('finger0','guides0','free0'):root.remove(n)
   elif n.tag.startswith('Native'):root.remove(n)
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'scene.scn');(out/'mesh.json').write_bytes((src/'mesh.json').read_bytes());(out/'config.json').write_bytes((src/'config.json').read_bytes());(out/'producer.py').write_bytes(Path(__file__).read_bytes());protocol=json.loads((BASE/'results/nonuniform_hold1001438/holding_protocol.json').read_text());(out/'holding_protocol.json').write_text(json.dumps(protocol,indent=2));forecast=30.
 if not a.single:
  assert a.pilot;pr=json.loads((BASE/'results'/a.pilot/'summary.json').read_text());assert pr['status']=='VALID_BOUNDED_EXPLORATION_ONLY' and pr['force_N_per_cable']==force;forecast=pr['process']['runtime_s']*a.duration/pr['duration_s']*(40 if pr.get('single') else 2);assert forecast<420
 command=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(round(a.duration/.0025)),'--hideProgressBar',str(out/'scene.scn')];pre=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),scene_sha256=sha(out/'scene.scn'),source_scene_sha256=sha(src/'scene.scn'),load_budget_sha256=sha(budget_src),force_N_per_cable=force,command=command,single=a.single,duration_s=a.duration,forecast_s=forecast,memory_GiB=4,child_limit_s=420,SDK='/home/ubuntu/SOFA/v26.06.00',binary_hashes={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')},hypothesis='Single derived load-sizing case:old measured .55–.65s SkinFz secant targets1.1*100gweight BEFOREwithdrawal. Not structural-efficiency gain or motor specification. Original1298 geometry/joint/material/mass/mu/controlshape unchanged,forceamplitude only. No additional increments if this candidate fails.');(out/'preflight.json').write_text(json.dumps(pre,indent=2));process=guarded(command,out/'process',420);logs=''.join((out/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));quality=[];counts=[];first=None;tet=np.array(json.loads((out/'mesh.json').read_text())['tetrahedra']);force_error=0.
 for i in range(1 if a.single else 3):
  rows=list(csv.DictReader((out/f'finger{i}.csv').open())) if (out/f'finger{i}.csv').exists() else [];counts.append(len(rows));q0=np.fromstring(root.find(f"Node[@name='finger{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);det0=np.linalg.det((q0[tet[:,1:]]-q0[tet[:,0,None]]).transpose(0,2,1));minimum=1.;finite=True
  for row in rows:
   q=np.fromstring(row['q_m'],sep=' ').reshape(-1,3);finite&=bool(np.isfinite(q).all());ratio=np.linalg.det((q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1))/det0;minimum=min(minimum,float(ratio.min()));force_error=max(force_error,*[abs(float(row[f'cable{j}_force_raw'])-float(row['command_Ns'])) for j in range(2)])
   if ratio.min()<=0 and first is None:first=dict(finger=i,time_s=float(row['time_s']),tet=int(np.argmin(ratio)))
  quality.append(dict(minimum_saved_volume_ratio=minimum,finite=finite))
 valid=process['exit_code']==0 and '[ERROR]'not in logs and counts==[round(a.duration/.0025)]*len(counts) and all(r['finite'] and r['minimum_saved_volume_ratio']>0 for r in quality);result=dict(status='VALID_BOUNDED_EXPLORATION_ONLY' if valid else 'FAIL_EXECUTION_OR_INVERSION',duration_s=a.duration,single=a.single,force_N_per_cable=force,maximum_native_force_command_impulse_error_Ns=force_error,process=process,outputs=counts,qualities=quality,first_inversion=first,holding='NOT ASSESSED',physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
