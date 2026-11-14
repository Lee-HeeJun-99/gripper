"""Clean-root experimental build and manifest; never changes validated binaries."""
import argparse
import os
from pathlib import Path
import subprocess
from integrated_common import ROOT,SOFA,BUILD,OUT,sha,write_json

def sources():
    paths=list((ROOT/'models/integrated').glob('*'))+[ROOT/'models/finite_rotation/Kernel.h',ROOT/'tests/test_integrated.cpp']
    return {str(p.relative_to(ROOT)):sha(p) for p in paths if p.is_file() and p.suffix in ('.cpp','.h','.inc','.txt')}

def main():
    p=argparse.ArgumentParser();p.add_argument('--sanitize',action='store_true');p.add_argument('--logs',type=Path,required=True);a=p.parse_args()
    a.logs.mkdir(parents=True,exist_ok=False);build=BUILD/('sanitized' if a.sanitize else 'plugin');before=sources()
    cmd=['cmake','-S',str(ROOT/'models/integrated'),'-B',str(build),'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SOFA)]
    if a.sanitize:cmd+=['-DCMAKE_CXX_FLAGS=-fsanitize=address,undefined -fno-omit-frame-pointer','-DCMAKE_SHARED_LINKER_FLAGS=-fsanitize=address,undefined','-DCMAKE_EXE_LINKER_FLAGS=-fsanitize=address,undefined']
    env=os.environ.copy();env['ASAN_OPTIONS']='detect_leaks=0';env['UBSAN_OPTIONS']='halt_on_error=1'
    for name,command in [('configure',cmd),('build',['cmake','--build',str(build),'-j','2']),('test',[str(build/'test_integrated')])]:
        r=subprocess.run(command,capture_output=True,text=True,timeout=180,env=env)
        (a.logs/(name+'.log')).write_text(r.stdout+r.stderr);write_json(a.logs/(name+'.command.json'),command)
        if r.returncode:raise RuntimeError(name+' failed '+str(a.logs))
    if before!=sources():raise RuntimeError('changed source while building')
    m=dict(sources=before,binary_sha256=sha(build/'libReGripIntegrated.so'),sanitized=a.sanitize,logs=str(a.logs))
    write_json(build/'manifest.json',m);write_json(a.logs/'manifest.json',m);print((a.logs/'test.log').read_text())

if __name__=='__main__':main()
