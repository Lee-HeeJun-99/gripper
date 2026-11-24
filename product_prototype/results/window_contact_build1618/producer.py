"""Freeze/bounded-build existing read-only probe with configurable time window."""
import argparse,json,subprocess
from pathlib import Path
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'sofa/native_contact_gap';build=BASE/'cad'/('build_'+a.tag);assert not build.exists()
 for file in ('Probe.cpp','CMakeLists.txt'):(out/file).write_bytes((src/file).read_bytes())
 pre=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),compiled_source_sha256=sha(out/'Probe.cpp'),legacy_binary_sha256=sha(BASE/'cad/build_contact_gap1211/libReGripContactGapProbe.so'),scope='Only configurable read-only sampling window extends existingProbe;legacy1211binary/source snapshot preserved. SDK/solver/state untouched.',SDK='/home/ubuntu/SOFA/v26.06.00',memory_GiB=4,child_limit_s=120);(out/'preflight.json').write_text(json.dumps(pre,indent=2));process=[]
 for k,cmd in enumerate([['cmake','-S',str(src),'-B',str(build),'-DCMAKE_PREFIX_PATH=/home/ubuntu/SOFA/v26.06.00','-DCMAKE_BUILD_TYPE=Release'],['cmake','--build',str(build),'--parallel','2']]):
  process.append(guarded(cmd,out/f'build{k}',120))
  if process[-1]['exit_code']!=0:break
 binary=build/'libReGripContactGapProbe.so';ok=len(process)==2 and all(r['exit_code']==0 for r in process) and binary.exists();d=dict(status='PASS_BUILD_ONLY_NOT_OBSERVER_QUALIFICATION' if ok else 'FAIL_BUILD',process=process,binary=str(binary) if ok else None,binary_sha256=sha(binary) if ok else None,compiled_source_sha256=pre['compiled_source_sha256'],source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
