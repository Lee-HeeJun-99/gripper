"""Optional earlier event of existing observer;new build,old binary preserved."""
import argparse,csv,json,subprocess,shutil,xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--build',action='store_true');p.add_argument('--source',default='b3_contact_layer_pilot1337');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);code=BASE/'sofa/native_contact_provenance';build=BASE/'cad/build_contact_phase1344';binary=build/'libReGripContactProvenance.so';(out/'producer.py').write_bytes(Path(__file__).read_bytes())
 if a.build:
  for f in ('Observer.cpp','CMakeLists.txt'):shutil.copy2(code/f,out/f)
  configure=guarded(['cmake','-S',str(code),'-B',str(build),'-DCMAKE_PREFIX_PATH=/home/ubuntu/SOFA/v26.06.00','-DCMAKE_BUILD_TYPE=Release'],out/'configure',120);compile=guarded(['cmake','--build',str(build),'-j','1'],out/'compile',120) if configure['exit_code']==0 else None
  d=dict(status='BUILT_OPTIONAL_COLLISION_PHASE_OBSERVER' if compile and compile['exit_code']==0 else 'FAIL_BUILD',configure=configure,compile=compile,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),compiled_source_sha256=sha(out/'Observer.cpp'),binary_sha256=sha(binary) if binary.exists() else None,SDK='/home/ubuntu/SOFA/v26.06.00');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d));return
 meta=json.loads((BASE/'results/contact_layer_phase_build1344/summary.json').read_text());assert sha(binary)==meta['binary_sha256'];src=BASE/'results'/a.source;tree=ET.parse(src/'scene.scn');root=tree.getroot();root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)));ET.SubElement(root,'ReGripContactProvenance',narrow='@nativeNarrow',filename=str(out/'provenance'),startTime='0',endTime='.00001',atCollisionEnd='1')
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 tree.write(out/'scene.scn');cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',str(out/'scene.scn')];pre=dict(command=cmd,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),scene_sha256=sha(out/'scene.scn'),source_scene_sha256=sha(src/'scene.scn'),observer_binary_sha256=sha(binary),compiled_source_sha256=meta['compiled_source_sha256'],event='CollisionEndEvent,detector only,no constraint row attribution',child_limit_s=15,memory_GiB=4);(out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',15);f=out/'provenance.features.csv';rows=list(csv.DictReader(f.open())) if f.exists() else [];normal=np.array([np.fromstring(r['normal'],sep=' ') for r in rows]);pairs=Counter(r['model0']+' | '+r['model1'] for r in rows);purity={}
 if a.source=='b3_railback_grasp1001298' and proc['exit_code']==0:
  for f in ('object.csv','finger0.csv','finger1.csv','finger2.csv','guide_frames0.csv','guide_frames1.csv','guide_frames2.csv','constraints.csv','support.csv'):
   got=list(csv.DictReader((out/f).open()));expected=list(csv.DictReader((src/f).open()))[:1];purity[f]=len(got)==1 and got==expected
 d=dict(status='PASS_ONE_STEP_OBSERVER_PURITY' if purity and all(purity.values()) else 'PARTIAL_COLLISION_PHASE_DIAGNOSTIC_ONLY' if rows else 'BLOCKED_NO_COLLISION_PHASE_DATA',process=proc,features=len(rows),pairs=dict(pairs),nonfinite_normals=int((~np.isfinite(normal)).any(axis=1).sum()) if len(rows) else None,zero_normals=int((np.linalg.norm(normal,axis=1)==0).sum()) if len(rows) else None,baseline_one_step_exact=purity,physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
