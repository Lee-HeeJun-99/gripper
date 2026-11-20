"""Native API force/potential FD on initially slack elastic string.

Different initial configurations are mathematical probes, not actuation results.
Reuse the frozen read-only697 binary; no source/SDK/physical state repair.
"""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded

def read(path):
 with path.open() as f:return list(csv.DictReader(f))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 source=BASE/'results/b3_native_spring_energy697';meta=json.loads((source/'summary.json').read_text());binary=BASE.parent/meta['build']/'libReGripSpringEnergy.so'
 if sha(binary)!=meta['binary_sha256']:raise ValueError('actual compiled energy observer mismatch')
 records=[];delta=1e-6
 for sign in (-1,1):
  d=out/('minus' if sign<0 else 'plus');d.mkdir();root=ET.parse(source/'initial_slack/scene.scn').getroot();root.find("MechanicalObject[@name='point']").set('position',f'0 0 .1 0 0 {sign*delta:.17g}')
  for node in root.iter():
   if node.get('filename'):node.set('filename',str(d/Path(node.get('filename')).name))
  ET.ElementTree(root).write(d/'scene.scn');proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',d/'scene.scn'],d/'process',480)
  logs=''.join((d/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));r=dict(initial_z_m=sign*delta,process=proc,sofa_errors=logs.count('[ERROR]'),scene_sha256=sha(d/'scene.scn'),status='FAIL_NATIVE_EXECUTION')
  if proc['exit_code']==0 and not r['sofa_errors']:
   point=read(d/'probe.csv.point.csv');energy=read(d/'energy.csv')
   if len(point)!=1 or len(energy)!=1:raise ValueError('partial FD probe')
   r.update(status='ACTUAL_NATIVE_API_PROBE',q=np.fromstring(point[0]['q'],sep=' ').reshape(-1,3).tolist(),v=np.fromstring(point[0]['v'],sep=' ').reshape(-1,3).tolist(),actual_native_force_slot_N=np.fromstring(point[0]['force_slot'],sep=' ').reshape(-1,3).tolist(),actual_native_potential_J=float(energy[0]['actual_native_potential_J']))
  records.append(r)
 derivative=(records[1]['actual_native_potential_J']-records[0]['actual_native_potential_J'])/(2*delta) if all(r['status']=='ACTUAL_NATIVE_API_PROBE' for r in records) else None
 result=dict(status='FAIL_NATIVE_UNILATERAL_FORCE_POTENTIAL_CONSISTENCY' if derivative is not None and abs(derivative)>1e-12 else 'BLOCKED_FD_INPUT',scope='Actual stock SpringForceField elongationOnly1,zero damping,initial slack. These perturbed initial configurations are API mathematics,NOT driven motion/wrapping. No SDK fix or B3 integration.',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),producer_sha256=sha(Path(__file__)),input_summary_sha256=sha(source/'summary.json'),binary_sha256=sha(binary),FD_half_width_m=delta,actual_native_potential_gradient_z_N=derivative,independent_unilateral_potential_gradient_z_N=0.,records=records)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
