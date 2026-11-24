"""One actuation-topology contrast: terminate at existing90mm guide,not98mm.

All hardware, FEM, reference states and collision models remain present.
This is an ideal cable anchor hypothesis,not a qualified physical termination.
"""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
 src=BASE/'results/b3_railback_grasp1001298';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 tree=ET.parse(src/'scene.scn');root=tree.getroot();changes=[]
 for cable in root.iter('CableConstraint'):
  assert cable.get('indices')=='0 1 2 3 4 5'
  cable.set('indices','0 1 2 3 4');changes.append('existing90mm guide becomes terminal;98mm guide retained unactuated')
 assert len(changes)==6
 for node in root.iter():
  for k,v in list(node.attrib.items()):node.set(k,v.replace(str(src),str(out)))
 tree.write(out/'scene.scn')
 for f in ('mesh.json','config.json'):(out/f).write_bytes((src/f).read_bytes())
 (out/'producer.py').write_bytes(Path(__file__).read_bytes())
 # Exact inverse-edit audit: no hidden material,geometry,collision or solver change.
 audit=ET.parse(out/'scene.scn')
 for node in audit.getroot().iter():
  if node.tag=='CableConstraint':node.set('indices','0 1 2 3 4 5')
  for k,v in list(node.attrib.items()):node.set(k,v.replace(str(out),str(src)))
 assert ET.tostring(audit.getroot())==ET.tostring(ET.parse(src/'scene.scn').getroot())
 cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','240','--hideProgressBar',str(out/'scene.scn')]
 bins={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')}
 pre=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),baseline_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),binary_sha256=bins,command=cmd,changes=changes,inverse_edit_equal=True,duration_s=.6,dt_s=.0025,forecast_s=100,child_limit_s=180,memory_GiB=4,hypothesis='Reduce direct distal bending by moving ideal terminal98to90mm without changing initial geometry or force. Test whether distal contact orientation changes;not assumed improvement.',initial_geometry='Identical FEM/hardware;wire removes final segment only. Full dynamic hardware clearance NOT QUALIFIED.',config_note='Copied baseline config;scene cable indices are authoritative changed actuation topology',physics='NOT QUALIFIED')
 (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',180)
 tet=np.array(json.loads((src/'mesh.json').read_text())['tetrahedra']);quality=[]
 for i in range(3):
  rows=list(csv.DictReader((out/f'finger{i}.csv').open()));q0=np.fromstring(root.find(f"./Node[@name='finger{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)
  q=np.array([np.fromstring(r['q_m'],sep=' ').reshape(-1,3) for r in rows]);d0=np.linalg.det((q0[tet[:,1:]]-q0[tet[:,0,None]]).transpose(0,2,1));ratio=np.linalg.det((q[:,tet[:,1:]]-q[:,tet[:,0,None]]).transpose(0,1,3,2))/d0
  quality.append(dict(outputs=len(rows),minimum_volume_ratio=float(ratio.min()),finite=bool(np.isfinite(q).all())))
 logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'))
 valid=proc['exit_code']==0 and '[ERROR]'not in logs and all(x['outputs']==240 and x['finite'] and x['minimum_volume_ratio']>0 for x in quality)
 result=dict(status='BOUNDED_EXECUTION_ONLY' if valid else 'FAIL_EXECUTION_OR_ELEMENTS',process=proc,quality=quality,holding='NOT MEASURED',time_convergence='NOT MEASURED',hardware_termination='IDEAL_ASSUMPTION',physical_validation='NOT QUALIFIED')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
