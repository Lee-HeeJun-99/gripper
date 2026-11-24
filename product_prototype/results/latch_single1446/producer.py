"""Motor-like held Native cable length after force closing;NOT q/v actuation."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded,add
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--single',action='store_true');p.add_argument('--duration',type=float,choices=[.8,1.2,2.],default=.8);p.add_argument('--pilot');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_railback_grasp1001298';root=ET.parse(src/'scene.scn').getroot();binary=BASE/'cad/build_cable_latch1441/libReGripCableLatch.so';metadata=json.loads((BASE/'results/cable_latch_active1444/summary.json').read_text());assert sha(binary)==metadata['binary_sha256'];plugin=add(root,'RequiredPlugin',pluginName=str(binary));root.remove(plugin);root.insert(0,plugin)
 if a.single:
  for n in list(root):
   if n.tag=='Node' and n.get('name') not in ('finger0','guides0','free0'):root.remove(n)
   elif n.tag.startswith('Native'):root.remove(n)
 for i in range(1 if a.single else 3):
  finger=root.find(f"Node[@name='finger{i}']");control=finger.find('NativeCableSequence');add(finger,'NativeCableLatch',cable0=control.get('cable0'),cable1=control.get('cable1'),start=.6,filename=str(out/f'latch{i}.csv'))
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'scene.scn');(out/'mesh.json').write_bytes((src/'mesh.json').read_bytes());(out/'config.json').write_bytes((src/'config.json').read_bytes());(out/'producer.py').write_bytes(Path(__file__).read_bytes());s=out/'source';s.mkdir()
 for f in ('CableLatch.cpp','CMakeLists.txt'):(s/f).write_bytes((BASE/'sofa/cable_latch'/f).read_bytes())
 forecast=30.
 if not a.single:
  assert a.pilot;pr=json.loads((BASE/'results'/a.pilot/'summary.json').read_text());assert pr['status']=='VALID_BOUNDED_EXPLORATION_ONLY';forecast=pr['process']['runtime_s']*a.duration/pr['duration_s']*(4 if pr.get('single') else 2);assert forecast<420
 protocol=json.loads((BASE/'results/nonuniform_hold1001438/holding_protocol.json').read_text());(out/'holding_protocol.json').write_text(json.dumps(protocol,indent=2));steps=round(a.duration/.0025);command=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',str(out/'scene.scn')];pre=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),scene_sha256=sha(out/'scene.scn'),baseline_sha256=sha(src/'scene.scn'),latch_binary_sha256=sha(binary),compiled_source_sha256=metadata['compiled_source_sha256'],single=a.single,duration_s=a.duration,forecast_s=forecast,command=command,memory_GiB=4,child_limit_s=420,SDK='/home/ubuntu/SOFA/v26.06.00',hypothesis='Original1298 geometry/100g/T1.5 unchanged;at.6s hold PREVIOUS ACCEPTED actual cable length via Native displacement input. Not increased prescribedtension/statecorrection. Physicalwire sliding not integrated.',input_journal_note='Originalfingercommand_N/Ns are pre-override requests after.6s. Actual heldtargets/geometricshortening/NativeλNs inlatch*.csv. No release claim from permanentlylatched2s test.');(out/'preflight.json').write_text(json.dumps(pre,indent=2));process=guarded(command,out/'process',420);logs=''.join((out/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));quality=[];counts=[];maximum_length_error=0.;first_bad=None;tet=np.array(json.loads((out/'mesh.json').read_text())['tetrahedra'])
 for i in range(1 if a.single else 3):
  rows=list(csv.DictReader((out/f'finger{i}.csv').open())) if (out/f'finger{i}.csv').exists() else [];counts.append(len(rows));q0=np.fromstring(root.find(f"Node[@name='finger{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);det0=np.linalg.det((q0[tet[:,1:]]-q0[tet[:,0,None]]).transpose(0,2,1));minimum=1.;finite=True
  for row in rows:
   q=np.fromstring(row['q_m'],sep=' ').reshape(-1,3);finite&=bool(np.isfinite(q).all());rat=np.linalg.det((q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1))/det0;minimum=min(minimum,float(rat.min()))
   if rat.min()<=0 and first_bad is None:first_bad=dict(finger=i,time_s=float(row['time_s']),tet=int(np.argmin(rat)))
  quality.append(dict(minimum_saved_volume_ratio=minimum,finite=finite))
  for row in csv.DictReader((out/f'latch{i}.csv').open()):
   if int(row['latched']):maximum_length_error=max(maximum_length_error,*[abs(float(row[f'target{j}_m'])-float(row[f'geometric{j}_m'])) for j in range(2)])
 valid=process['exit_code']==0 and '[ERROR]'not in logs and counts==[steps]*len(counts) and all(r['finite'] and r['minimum_saved_volume_ratio']>0 for r in quality);result=dict(status='VALID_BOUNDED_EXPLORATION_ONLY' if valid else 'FAIL_EXECUTION_OR_INVERSION',single=a.single,duration_s=a.duration,process=process,outputs=counts,qualities=quality,first_inversion=first_bad,maximum_geometric_latch_error_m=maximum_length_error,holding='NOT ASSESSED',physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
