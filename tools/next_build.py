"""Build the separate experimental component and bind tests, sources and binary."""
import argparse
import os
from pathlib import Path
import subprocess
from verification_common import ROOT,SOFA,sha,write_json

def main():
    p=argparse.ArgumentParser();p.add_argument('--sanitize',action='store_true');p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False)
    build=ROOT/'build'/('next_finite_rotation_asan' if a.sanitize else 'next_finite_rotation')
    sources=[ROOT/'models/finite_rotation'/name for name in ('Kernel.h','FiniteRotationShear.cpp','CMakeLists.txt')]+[ROOT/'tests/test_finite_rotation.cpp']
    before={str(p.relative_to(ROOT)):sha(p) for p in sources}
    cmd=['cmake','-S',str(ROOT/'models/finite_rotation'),'-B',str(build),'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SOFA)]
    if a.sanitize:cmd+=['-DCMAKE_CXX_FLAGS=-fsanitize=address,undefined -fno-omit-frame-pointer','-DCMAKE_SHARED_LINKER_FLAGS=-fsanitize=address,undefined','-DCMAKE_EXE_LINKER_FLAGS=-fsanitize=address,undefined']
    env=os.environ.copy();env['ASAN_OPTIONS']='detect_leaks=0';env['UBSAN_OPTIONS']='halt_on_error=1'
    for name,cmd in [('configure',cmd),('build',['cmake','--build',str(build),'-j','2']),('unit',[str(build/'test_finite_rotation')])]:
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=120,env=env)
        (a.out/(name+'.log')).write_text(r.stdout+r.stderr);write_json(a.out/(name+'.command.json'),cmd)
        if r.returncode:raise RuntimeError(name+' failed; inspect '+str(a.out))
    if before!={str(p.relative_to(ROOT)):sha(p) for p in sources}:raise RuntimeError('sources changed during build')
    manifest=dict(sources=before,binary=sha(build/'libReGripFiniteRotation.so'),sanitized=a.sanitize,logs=str(a.out))
    write_json(build/'manifest.json',manifest);write_json(a.out/'build_manifest.json',manifest)
    print((a.out/'unit.log').read_text())

if __name__=='__main__':main()
