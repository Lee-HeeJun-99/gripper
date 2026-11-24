"""Bounded build of registration-only adapter;freeze actual compiled identities."""
import argparse,json,subprocess
from pathlib import Path
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'sofa/native_rigid_sphere_dispatch';build=BASE/'cad'/('build_'+a.tag);assert not build.exists()
 for f in ('Dispatch.cpp','CMakeLists.txt'):(out/f).write_bytes((src/f).read_bytes())
 pre=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(src/'Dispatch.cpp'),cmake_sha256=sha(src/'CMakeLists.txt'),SDK='/home/ubuntu/SOFA/v26.06.00',dependency_hashes={str(p):sha(p) for p in [Path('/home/ubuntu/SOFA/v26.06.00/lib/libSofa.Component.Collision.Detection.Intersection.so.26.06.00'),Path('/home/ubuntu/SOFA/v26.06.00/include/Sofa.Component.Collision.Detection.Intersection/sofa/component/collision/detection/intersection/MeshMinProximityIntersection.h')]},scope='Compatibility registration only;no new contact/ODE/constraint solver;buildPASS isNOTphysicsPASS');(out/'preflight.json').write_text(json.dumps(pre,indent=2));commands=[['cmake','-S',str(src),'-B',str(build),'-DCMAKE_PREFIX_PATH=/home/ubuntu/SOFA/v26.06.00','-DCMAKE_BUILD_TYPE=Release'],['cmake','--build',str(build),'--parallel','2']];process=[]
 for k,cmd in enumerate(commands):
  r=guarded(cmd,out/f'build{k}',120);process.append(r)
  if r['exit_code']!=0:break
 binary=build/'libReGripRigidSphereDispatch.so';ok=len(process)==2 and all(r['exit_code']==0 for r in process) and binary.exists();d=dict(status='PASS_BUILD_ONLY_NOT_PHYSICS' if ok else 'FAIL_BUILD',process=process,binary=str(binary) if ok else None,binary_sha256=sha(binary) if ok else None,compiled_source_sha256=sha(out/'Dispatch.cpp'),SDK=pre['SDK'],scope=pre['scope']);(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
