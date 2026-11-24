"""Actual force-to-geometric-length input switch,stock straight Native cable."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded,add
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--no-latch',action='store_true');p.add_argument('--ramp-target',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/force_profile334';root=ET.parse(src/'scene.scn').getroot();binary=BASE/'cad/build_cable_latch1454/libReGripCableLatch.so';plugin=add(root,'RequiredPlugin',pluginName=str(binary));root.remove(plugin);root.insert(0,plugin);n=root.find('Node');control=n.find('NativeCableSequence');control.set('closing','.05')
 if not a.no_latch:
  latch=add(n,'NativeCableLatch',cable0='@cable0/actuator',cable1='@cable1/actuator',start=.1,filename=str(out/'latch.csv'))
  if a.ramp_target:latch.set('final0','.0012');latch.set('final1','.0013');latch.set('end','.15')
 for node in root.iter():
  for k,v in list(node.attrib.items()):node.set(k,v.replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'scene.scn');snapshot=out/'source';snapshot.mkdir()
 for f in ('CableLatch.cpp','CMakeLists.txt'):(snapshot/f).write_bytes((BASE/'sofa/cable_latch'/f).read_bytes())
 command=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','80','--hideProgressBar',str(out/'scene.scn')];process=guarded(command,out/'process',60);logs=''.join((out/'process'/x).read_text(errors='replace') for x in ('stdout.log','stderr.log'));rows=list(csv.DictReader((out/'states.csv').open())) if (out/'states.csv').exists() else [];latch=list(csv.DictReader((out/'latch.csv').open())) if (out/'latch.csv').exists() else [];errors=[]
 for r in latch:
  if int(r['latched']):errors.extend(abs(float(r[f'target{j}_m'])-float(r[f'geometric{j}_m'])) for j in range(2))
 result=dict(status='PASS_STRAIGHT_NATIVE_LENGTH_LATCH_ONLY' if process['exit_code']==0 and '[ERROR]'not in logs and len(rows)==80 and (a.no_latch or errors and max(errors)<=1e-12) else 'FAIL_NATIVE_LATCH_COUPON',no_latch=a.no_latch,process=process,command=command,outputs=len(rows),maximum_geometric_latch_error_m=max(errors) if errors else None,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),scene_sha256=sha(out/'scene.scn'),binary_sha256=sha(binary),compiled_source_sha256={f:sha(snapshot/f) for f in ('CableLatch.cpp','CMakeLists.txt')},scope='Input-only public CableConstraint.value/valueType;native spring-mass1g/1000N/m,dt2.5ms. No q/v correction,newphysicslaw/ODE/SDK changes. Originalcontrol.csvcommand_N/command_Ns are PRE-OVERRIDE REQUESTS afterlatch,not actual forces. Readlatch.csv for actual NativeλNs and geometriclength. No curvedguide/contact/grasp/time/mesh or hardwarePASS.');(out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result,indent=2))
if __name__=='__main__':main()
