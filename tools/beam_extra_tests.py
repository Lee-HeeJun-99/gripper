"""Separate API and sanitizer builds, frozen physics binaries not overwritten."""
import argparse,os,resource,subprocess
from beam_common import ROOT,OUT,BUILD,PREFIX,write_json,sha
from closure_validation_suite import logged
def main():
    p=argparse.ArgumentParser();p.add_argument('--asan',action='store_true');p.add_argument('--run-only',action='store_true');p.add_argument('--name');a=p.parse_args();name=a.name or ('asan' if a.asan else 'extra_unit');out=OUT/name;out.mkdir(exist_ok=False);build=BUILD/('asan' if a.asan else 'extra_unit')
    if not a.run_only:
        command=['cmake','-S','tests/conservative_beam','-B',str(build),'-DCMAKE_BUILD_TYPE=Debug' if a.asan else '-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(PREFIX)]
        if a.asan:command+=['-DCMAKE_CXX_FLAGS=-fsanitize=address,undefined -fno-omit-frame-pointer','-DCMAKE_EXE_LINKER_FLAGS=-fsanitize=address,undefined']
        for stage,cmd in [('configure',command),('build',['cmake','--build',str(build),'-j2'])]:
            r=logged(cmd,out/stage,180)
            if r['exit_code']:write_json(out/'summary.json',dict(status='FAIL',build=r));return
    cmd=[str(build/'test_beam_api')];env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1:halt_on_error=1:hard_rss_limit_mb=2048:max_allocation_size_mb=256',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1');write_json(out/'command.json',cmd);write_json(out/'environment.json',{k:env[k] for k in ('ASAN_OPTIONS','UBSAN_OPTIONS')})
    with (out/'stdout.log').open('x') as f,(out/'stderr.log').open('x') as e:
        try:r=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=e,timeout=60,preexec_fn=lambda:resource.setrlimit(resource.RLIMIT_CORE,(0,0)));code=r.returncode
        except subprocess.TimeoutExpired:code=None
    log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();write_json(out/'summary.json',dict(status='PASS' if code==0 and 'PASS extra API' in log and 'ERROR:' not in log and 'runtime error:' not in log else 'FAIL',exit_code=code,binary_sha256=sha(build/'test_beam_api'),scope='new forcefield translation unit ASan/UBSan/LSan only,external SDK not instrumented;ASan2GiBphysicalRSS not4GiBvirtual shadow cap,timeout60s',log=log));print(code,log[-1200:])
if __name__=='__main__':main()
