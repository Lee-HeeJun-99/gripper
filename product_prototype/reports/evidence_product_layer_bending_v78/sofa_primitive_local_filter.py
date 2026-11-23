"""Finite-radius line/face cone-filter contrast;not old thin-mesh LMD replay."""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--source',required=True,choices=['primitive_sphere_slip1225','primitive_sphere_slip1228']);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.source;tree=ET.parse(src/'scene.scn');root=tree.getroot();detector=root.find('MinProximityIntersection');assert detector is not None;detector.tag='LocalMinDistance'
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());pre=json.loads((src/'preflight.json').read_text());cmd=pre['command'][:-1]+[str(out/'scene.scn')];pre.update(command=cmd,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),estimated_runtime_s=1,child_limit_s=5,hypothesis='Actual nearly parallel line/face contact pair caused saturation at finite-radius departure. Native local normal-cone filtering only;all collision models,geometry,load,dt,mass,solver tolerances unchanged. Prior thin mesh LMD NaN is NOT erased.')
 (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',5);logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));rows=list(csv.DictReader((out/'rigid.csv').open())) if (out/'rigid.csv').exists() else [];q=np.array([np.fromstring(r['rigid_q'],sep=' ') for r in rows]);finite=bool(q.size) and bool(np.isfinite(q).all());d=dict(status='LOCAL_FILTER_COMPONENT_STATES_ONLY' if proc['exit_code']==0 and '[ERROR]'not in logs and len(rows)==100 and finite else 'FAIL_EXECUTION_OR_NONFINITE',process=proc,outputs=len(rows),finite=finite,physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
