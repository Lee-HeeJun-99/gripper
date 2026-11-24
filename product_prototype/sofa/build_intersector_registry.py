"""Bounded installed-SDK-only compile; not contact qualification."""
import argparse,json,subprocess
from pathlib import Path
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'sofa/native_intersector_registry';build=BASE/'cad'/('build_'+a.tag);assert not build.exists()
 for f in ('Registry.cpp','CMakeLists.txt'):(out/f).write_bytes((src/f).read_bytes())
 stages=[]
 for i,cmd in enumerate([['cmake','-S',str(src),'-B',str(build),'-DCMAKE_PREFIX_PATH=/home/ubuntu/SOFA/v26.06.00','-DCMAKE_BUILD_TYPE=Release'],['cmake','--build',str(build),'--parallel','2']]):
  stages.append(guarded(cmd,out/f'build{i}',120))
  if stages[-1]['exit_code']!=0:break
 binary=build/'libReGripIntersectorRegistry.so';ok=len(stages)==2 and all(r['exit_code']==0 for r in stages) and binary.exists();d=dict(status='PASS_BUILD_ONLY' if ok else 'FAIL_BUILD',process=stages,binary=str(binary) if ok else None,binary_sha256=sha(binary) if ok else None,compiled_source_sha256=sha(out/'Registry.cpp'),source_sha256=sha(Path(__file__)),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),SDK='/home/ubuntu/SOFA/v26.06.00',scope='Read-only public registered-pair query,not newlyregisteredcollisioncallback,SDK patch ornewphysics. Runtimeobserverpurity required.');(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
