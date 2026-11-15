"""Project-kernel instrumentation only; external SOFA libraries not instrumented."""
from closure_common import ROOT,OUT,BUILD,write_json,sha
from closure_validation_suite import logged
import os
def main():
    out=OUT/'sanitizers';out.mkdir(exist_ok=False);build=BUILD/'sanitizers';prefix='/home/ubuntu/SOFA/v26.06.00'
    commands=[('configure',['cmake','-S','models/closure','-B',str(build),'-DCMAKE_BUILD_TYPE=Debug','-DCMAKE_PREFIX_PATH='+prefix,'-DCMAKE_CXX_FLAGS=-fsanitize=address,undefined -fno-omit-frame-pointer','-DCMAKE_EXE_LINKER_FLAGS=-fsanitize=address,undefined','-DCMAKE_SHARED_LINKER_FLAGS=-fsanitize=address,undefined']),('build',['cmake','--build',str(build),'--target','test_closure','-j2'])];results={}
    for name,command in commands:
        results[name]=logged(command,out/name,180)
        if results[name]['exit_code']!=0:write_json(out/'summary.json',results);return
    os.environ['ASAN_OPTIONS']='detect_leaks=1:halt_on_error=1';os.environ['UBSAN_OPTIONS']='halt_on_error=1:print_stacktrace=1';write_json(out/'environment.json',dict(ASAN_OPTIONS=os.environ['ASAN_OPTIONS'],UBSAN_OPTIONS=os.environ['UBSAN_OPTIONS'],scope='new closure unit translation unit instrumented; shared installed SOFA not instrumented'))
    results['run']=logged([str(build/'test_closure')],out/'run',60);write_json(out/'summary.json',results);print(results['run'])
if __name__=='__main__':main()
