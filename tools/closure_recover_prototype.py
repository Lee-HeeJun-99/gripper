"""Reproduce the pre-runtime-guard pilot binary by its recorded cryptographic hash.

The pilot was excluded from qualification; canonical sources/binaries are never
temporarily changed. A file/macro path map reproduces its exact release object.
"""
import json,subprocess,shlex
from closure_common import ROOT,OUT,BUILD,sha,write_json
def main():
    record=json.loads((OUT/'trials/sphere_n11q8/metrics.json').read_text());source=ROOT/'.runtime/closure_prototype/AdaptiveContact.cpp';original=ROOT/'models/closure/AdaptiveContact.cpp'
    if sha(source)!=record['identity']['source_sha256'][str(original.relative_to(ROOT))]:raise ValueError('pilot source hash mismatch')
    out=OUT/'prototype_recovery';out.mkdir(exist_ok=False);directory=BUILD/'prototype';directory.mkdir(exist_ok=False);flags=(BUILD/'release/CMakeFiles/ReGripClosure.dir/flags.make').read_text().splitlines();args=[]
    for key in ('CXX_DEFINES','CXX_INCLUDES','CXX_FLAGS'):
        args+=shlex.split(next(line.split('=',1)[1] for line in flags if line.startswith(key+' =')))
    obj=directory/'AdaptiveContact.cpp.o';commands=[['/usr/bin/c++',*args,'-I'+str(ROOT/'models/closure'),'-ffile-prefix-map='+str(source)+'='+str(original),'-fmacro-prefix-map='+str(source)+'='+str(original),'-c',str(source),'-o',str(obj)]]
    linker=shlex.split((BUILD/'release/CMakeFiles/ReGripClosure.dir/link.txt').read_text());linker=[str(obj) if s=='CMakeFiles/ReGripClosure.dir/AdaptiveContact.cpp.o' else (str(directory/'libReGripClosure.so') if s=='libReGripClosure.so' else s) for s in linker];commands.append(linker)
    for i,command in enumerate(commands):
        p=subprocess.run(command,cwd=BUILD/'release',capture_output=True,text=True,timeout=90);(out/(str(i)+'.log')).write_text(p.stdout+p.stderr)
        if p.returncode:raise RuntimeError('prototype compilation failed')
    actual=sha(directory/'libReGripClosure.so');write_json(out/'result.json',dict(status='PASS' if actual==record['identity']['binary_sha256'] else 'FAIL',expected_sha256=record['identity']['binary_sha256'],actual_sha256=actual,commands=commands,scope='pilot version reproducibility only; main convergence/wrench results use guarded4a3827e source'))
    print(actual==record['identity']['binary_sha256'],actual)
if __name__=='__main__':main()
