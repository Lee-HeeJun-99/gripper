"""Own-component sanitizer diagnostics, not an instrumented full SOFA engine."""
import os,resource,subprocess,time
from grasp_common import ROOT,OUT,BUILD,SOFA,write_json,sha

def main():
    out=OUT/'sanitizer';out.mkdir(exist_ok=False);build=BUILD/'asan_v4';records={}
    def invoke(label,command,env=None,limit=120):
        started=time.monotonic()
        try:
            p=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,timeout=limit,preexec_fn=lambda:resource.setrlimit(resource.RLIMIT_CORE,(0,0)));code=p.returncode;log=p.stdout+p.stderr
        except subprocess.TimeoutExpired as e:code=None;log=str(e)
        (out/(label+'.log')).write_text(log);records[label]=dict(command=command,exit_code=code,runtime_s=time.monotonic()-started);write_json(out/'commands.json',records);return code,log
    code,_=invoke('configure',['cmake','-S','models/grasp','-B',str(build),'-DCMAKE_PREFIX_PATH='+str(SOFA),'-DCMAKE_BUILD_TYPE=Debug','-DCMAKE_CXX_FLAGS=-fsanitize=address,undefined -fno-omit-frame-pointer','-DCMAKE_EXE_LINKER_FLAGS=-fsanitize=address,undefined'])
    if code:return
    code,_=invoke('build',['cmake','--build',str(build),'--target','test_grasp_stick','-j2'])
    if code:return
    statuses={}
    for label,leaks in [('asan_ubsan',0),('lsan',1)]:
        code,log=invoke(label,[str(build/'test_grasp_stick')],env=dict(os.environ,ASAN_OPTIONS=f'detect_leaks={leaks}:soft_rss_limit_mb=1024'),limit=30);statuses[label]='PASS' if code==0 and 'PASS stick/slip' in log else 'FAIL'
    write_json(out/'summary.json',dict(status=statuses,binary_sha256=sha(build/'test_grasp_stick'),source_sha256={p:sha(ROOT/p) for p in ('models/grasp/StickSlip.h','models/grasp/StickSlip.cpp','tests/test_grasp_stick.cpp')},scope='our unit source instrumented; distributed SOFA binaries are NOT rebuilt under sanitizers; ASan virtual shadow is not constrained by4GiB RLIMIT_AS'))
    print(statuses)

if __name__=='__main__':main()
