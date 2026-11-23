"""Finite-radius geometry contrast,not a repaired layer or unsupported grasp."""
import argparse,csv,json,subprocess,math
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--mu',type=float,choices=[0,.3],required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 src=BASE/'results'/('layer_fixture_slip1206' if a.mu==0 else 'layer_fixture_friction1207');tree=ET.parse(src/'scene.scn');root=tree.getroot();node=root.find("./Node[@name='layer']");radius=.005;mass=.000112
 node.remove(node.find('Node'));node.find('MechanicalObject').set('position',f'0 0 {radius+.000002:.17g} 0 0 0 1');I=.4*radius**2;node.find('UniformMass').set('vertexMass',' '.join(map(str,[mass,4*math.pi*radius**3/3,I,0,0,0,I,0,0,0,I])));ET.SubElement(node,'SphereCollisionModel',template='Rigid3d',radius=str(radius),group='2')
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','100','--hideProgressBar',str(out/'scene.scn')]
 pre=dict(command=cmd,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),SDK='/home/ubuntu/SOFA/v26.06.00',source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),binary_hashes={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')},mass_kg=mass,radius_m=radius,normalized_inertia_m2=I,mu=a.mu,dt_s=.0002,initial_gap_m=.000002,estimated_runtime_s=1,child_limit_s=60,memory_GiB=4,scope='NEW analytical sphere vs mesh support;proper sphere inertia,orientation fixture unchanged;not original thin-layer physics or jamming or grasp')
 (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',60);rows=list(csv.DictReader((out/'rigid.csv').open())) if (out/'rigid.csv').exists() else [];logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));q=np.array([np.fromstring(r['rigid_q'],sep=' ') for r in rows]);finite=bool(len(q)) and bool(np.isfinite(q).all());d=dict(status='PRIMITIVE_COMPONENT_STATES_ONLY' if proc['exit_code']==0 and '[ERROR]'not in logs and len(rows)==100 and finite else 'FAIL_EXECUTION',process=proc,outputs=len(rows),finite=finite,final_x_m=float(q[-1,0]) if finite else None,minimum_bottom_gap_m=float((q[:,2]-radius).min()) if finite else None,physical_validation='NOT QUALIFIED',grasp='NOT TESTED')
 (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
