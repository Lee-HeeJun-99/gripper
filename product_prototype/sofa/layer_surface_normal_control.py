"""One Native contact-normal policy contrast,not distance/solver tuning."""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--mu',type=float,choices=[0,.3],required=True);p.add_argument('--local-min-distance',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/('layer_fixture_slip1206' if a.mu==0 else 'layer_fixture_friction1207');tree=ET.parse(src/'scene.scn');root=tree.getroot()
 if a.local_min_distance:root.find('MinProximityIntersection').tag='LocalMinDistance'
 else:root.find('MinProximityIntersection').set('useSurfaceNormals','1')
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','100','--hideProgressBar',str(out/'scene.scn')];pre=json.loads((src/'preflight.json').read_text());pre.update(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_scene_sha256=sha(src/'scene.scn'),command=cmd,change='ONLY Native detector policy:LocalMinDistance(defaults)' if a.local_min_distance else 'ONLY Native MinProximityIntersection.useSurfaceNormals=1;all distances/loads/dt/solver unchanged.');(out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',60);rows=list(csv.DictReader((out/'rigid.csv').open())) if (out/'rigid.csv').exists() else [];logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));q=np.array([np.fromstring(r['rigid_q'],sep=' ') for r in rows]);d=dict(status='NORMAL_POLICY_STATES_ONLY' if proc['exit_code']==0 and '[ERROR]' not in logs and len(rows)==100 else 'FAIL_EXECUTION',process=proc,outputs=len(rows),minimum_centre_z_m=float(q[:,2].min()) if len(q) else None,final_x_m=float(q[-1,0]) if len(q) else None,physical_validation='NOT QUALIFIED',layer_jamming='NOT VALIDATED');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
