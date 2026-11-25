"""Negative control proves the finite-speed coupon contains active elasticity.
Removing FEM here is a declared no-object control, not a grasp workaround.
"""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results/direct_fem1933';base=json.loads((src/'preflight.json').read_text());assert json.loads((src/'summary.json').read_text())['status']=='PASS_DIRECT_VEC3_FINITE_SPEED_CONSERVATION_COUPON_ONLY';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());root=ET.parse(src/'scene.scn').getroot();node=root.find("Node[@name='support']");node.remove(node.find('TetrahedronFEMForceField'))
 for e in root.iter():
  if e.get('filename'):e.set('filename',e.get('filename').replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'scene.scn');pre=dict(source_sha256=sha(Path(__file__)),base_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),changed_variable='Remove only elastic FF in declared negative control, no object/contact or fullgrasp. Initial q/v and all masses/timing unchanged.');(out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','50','--hideProgressBar',out/'scene.scn'],out/'process',60);logs=''.join((out/'process'/n).read_text(errors='replace') for n in ['stdout.log','stderr.log']);ok=proc['exit_code']==0 and '[ERROR]'not in logs;metrics={}
 if ok:
  read=lambda p:list(csv.DictReader(p.open()));control=read(out/'states.csv');elastic=read(src/'states.csv');assert len(control)==len(elastic)==50;initial=np.array(base['rest_q_m']);v0=np.array(base['initial_v_m_s']);qerr=0.;verr=0.;contrast_v=0.;contrast_q=0.
  for c,e in zip(control,elastic):
   q=np.fromstring(c['q'],sep=' ').reshape(-1,3);v=np.fromstring(c['v'],sep=' ').reshape(-1,3);t=float(c['time_s']);qerr=max(qerr,float(abs(q-initial-v0*t).max()));verr=max(verr,float(abs(v-v0).max()));contrast_v=max(contrast_v,float(abs(v-np.fromstring(e['v'],sep=' ').reshape(-1,3)).max()));contrast_q=max(contrast_q,float(abs(q-np.fromstring(e['q'],sep=' ').reshape(-1,3)).max()))
  metrics=dict(no_FEM_ballistic_q_error_m=qerr,no_FEM_constant_velocity_error_m_s=verr,actual_elastic_minus_noFEM_velocity_difference_m_s=contrast_v,actual_elastic_minus_noFEM_position_difference_m=contrast_q);ok=qerr<=1e-12 and verr<=1e-12 and contrast_v>1e-12 and contrast_q>1e-12
 d=dict(status='PASS_NONEMPTY_FINITE_SPEED_FEM_CONTROL_ONLY' if ok else 'FAIL_FINITE_SPEED_FEM_CONTROL',process=proc,metrics=metrics,source_sha256=sha(Path(__file__)),preflight_sha256=sha(out/'preflight.json'),scope='Actual matched Native negative control confirms1933elastic dynamics rather than an empty/coasting smoke model. NoFEM control is not a proposed guide/grasp candidate. Free-solid conservation only; no actual load/attachment/bore/contact/time/mesh or hardware qualification.');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
