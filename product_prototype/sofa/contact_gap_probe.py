import argparse,csv,json,shutil,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--build',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);build=BASE/'cad/build_contact_gap1211';code=BASE/'sofa/native_contact_gap';binary=build/'libReGripContactGapProbe.so';(out/'producer.py').write_bytes(Path(__file__).read_bytes())
 if a.build:
  for f in ('Probe.cpp','CMakeLists.txt'):shutil.copy2(code/f,out/f)
  configure=guarded(['cmake','-S',str(code),'-B',str(build),'-DCMAKE_PREFIX_PATH=/home/ubuntu/SOFA/v26.06.00','-DCMAKE_BUILD_TYPE=Release'],out/'configure',120);compile=guarded(['cmake','--build',str(build),'-j','1'],out/'compile',120) if configure['exit_code']==0 else None;d=dict(status='BUILT_READ_ONLY_PROBE' if compile and compile['exit_code']==0 else 'FAIL_BUILD',configure=configure,compile=compile,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),compiled_source_sha256=sha(out/'Probe.cpp'),binary_sha256=sha(binary) if binary.exists() else None,SDK='/home/ubuntu/SOFA/v26.06.00');
  if (build/'CMakeCache.txt').exists():shutil.copy2(build/'CMakeCache.txt',out/'CMakeCache.txt')
 else:
  meta=json.loads((BASE/'results/contact_gap_build1211/summary.json').read_text());assert sha(binary)==meta['binary_sha256'] and sha(BASE/'results/contact_gap_build1211/Probe.cpp')==meta['compiled_source_sha256'];deps=subprocess.check_output(['ldd',str(binary)],text=True);assert not [l for l in deps.splitlines() if 'libSofa' in l and '=>' in l and '/home/ubuntu/SOFA/v26.06.00/' not in l];(out/'ldd.txt').write_text(deps);src=BASE/'results/layer_fixture_friction1207';tree=ET.parse(src/'scene.scn');root=tree.getroot();root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)));ET.SubElement(root,'ReGripContactGapProbe',body='@layer/rigid',solver='@constraints',filename=str(out/'probe'))
  for n in root.iter():
   for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
  tree.write(out/'scene.scn');cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','10','--hideProgressBar',str(out/'scene.scn')];(out/'preflight.json').write_text(json.dumps(dict(command=cmd,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_scene_sha256=sha(src/'scene.scn'),binary_sha256=sha(binary),compiled_source_sha256=meta['compiled_source_sha256'],SDK='/home/ubuntu/SOFA/v26.06.00',estimated_runtime_s=1,child_limit_s=60,memory_GiB=4,purity_gate=1e-12),indent=2));proc=guarded(cmd,out/'process',60);rows=list(csv.DictReader((out/'rigid.csv').open())) if (out/'rigid.csv').exists() else [];base=list(csv.DictReader((src/'rigid.csv').open()))[:10];error={k:max(float(abs(np.fromstring(r[k],sep=' ')-np.fromstring(b[k],sep=' ')).max()) for r,b in zip(rows,base)) if rows else None for k in ('rigid_q','rigid_v','object_impulse_Ns_Nms')};logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));d=dict(status='PASS_BOUNDED_CONTACT_PROBE_PURITY' if proc['exit_code']==0 and '[ERROR]' not in logs and len(rows)==10 and max(error.values())<=1e-12 else 'FAIL_PROBE_EXECUTION_OR_PURITY',process=proc,outputs=len(rows),errors=error,physical_validation='NOT QUALIFIED')
 (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
