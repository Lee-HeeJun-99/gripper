"""Bounded read-only feature/child-row observer; separate frozen build identity."""
import argparse,csv,json,shutil,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--build',action='store_true');p.add_argument('--build-tag',default='contact_provenance_build1221');p.add_argument('--source',default='contact_gap_probe1212');a=p.parse_args()
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);code=BASE/'sofa/native_contact_provenance';build=BASE/'cad'/a.build_tag;binary=build/'libReGripContactProvenance.so';(out/'producer.py').write_bytes(Path(__file__).read_bytes())
 identity=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),SDK='/home/ubuntu/SOFA/v26.06.00',memory_GiB=4,scope='read-only Native diagnostic;not physics qualification')
 if a.build:
  if build.exists():raise ValueError('fresh build required')
  for f in ('Observer.cpp','CMakeLists.txt'):shutil.copy2(code/f,out/f)
  c=guarded(['cmake','-S',str(code),'-B',str(build),'-DCMAKE_PREFIX_PATH='+identity['SDK'],'-DCMAKE_BUILD_TYPE=Release'],out/'configure',120)
  b=guarded(['cmake','--build',str(build),'-j','1'],out/'compile',120) if c['exit_code']==0 else None
  d=dict(identity,status='BUILT_READ_ONLY_OBSERVER' if b and b['exit_code']==0 else 'FAIL_BUILD',configure=c,compile=b,binary_sha256=sha(binary) if binary.exists() else None,compiled_source_sha256=sha(out/'Observer.cpp'))
  if (build/'CMakeCache.txt').exists():shutil.copy2(build/'CMakeCache.txt',out/'CMakeCache.txt')
 else:
  meta=json.loads((BASE/'results'/a.build_tag/'summary.json').read_text());assert sha(binary)==meta['binary_sha256'];assert sha(code/'Observer.cpp')==meta['compiled_source_sha256']
  deps=subprocess.check_output(['ldd',str(binary)],text=True);assert not [x for x in deps.splitlines() if 'libSofa' in x and '=>' in x and identity['SDK']+'/' not in x];(out/'ldd.txt').write_text(deps)
  src=BASE/'results'/a.source;tree=ET.parse(src/'scene.scn');root=tree.getroot();root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)));ET.SubElement(root,'ReGripContactProvenance',narrow='@narrow',filename=str(out/'provenance'))
  for n in root.iter():
   for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
  tree.write(out/'scene.scn');cmd=[identity['SDK']+'/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','10','--hideProgressBar',str(out/'scene.scn')]
  (out/'preflight.json').write_text(json.dumps(dict(identity,command=cmd,scene_sha256=sha(out/'scene.scn'),source_scene_sha256=sha(src/'scene.scn'),binary_sha256=sha(binary),compiled_source_sha256=meta['compiled_source_sha256'],estimated_runtime_s=1,child_limit_s=60,purity_gate=1e-12),indent=2))
  proc=guarded(cmd,out/'process',60);rows=list(csv.DictReader((out/'rigid.csv').open())) if (out/'rigid.csv').exists() else [];base=list(csv.DictReader((src/'rigid.csv').open()))[:10];errors={k:max(float(abs(np.fromstring(r[k],sep=' ')-np.fromstring(b[k],sep=' ')).max()) for r,b in zip(rows,base)) if rows else None for k in ('rigid_q','rigid_v','object_impulse_Ns_Nms')};logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'))
  d=dict(identity,status='PASS_READ_ONLY_PROVENANCE_PURITY' if proc['exit_code']==0 and '[ERROR]' not in logs and len(rows)==len(base)==10 and max(errors.values())<=1e-12 else 'FAIL_EXECUTION_OR_PURITY',process=proc,outputs=len(rows),errors=errors)
 (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
