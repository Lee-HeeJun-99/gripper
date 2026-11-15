"""Bounded own-kernel ASan/UBSan/LSan, NOT the SOFA engine."""
import os,subprocess,time,resource,argparse
from history_common import ROOT,OUT,write_json,sha
from closure_validation_suite import logged
def main():
    p=argparse.ArgumentParser();p.add_argument('--suffix',default='');args=p.parse_args()
    out=OUT/('sanitizer'+args.suffix);out.mkdir(exist_ok=False);exe=ROOT/('build/history_20261115/history_kernel_sanitized'+args.suffix);source=ROOT/'tests/contact_history_extra/prescribed.cpp'
    inputs=[source]+[p for folder in ('models/contact_birth','models/contact_history','models/stabilization','models/integrated','models/finite_rotation') for p in (ROOT/folder).rglob('*.h')];before={str(p.relative_to(ROOT)):sha(p) for p in inputs}
    command=['g++','-std=c++17','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-DHISTORY_KERNEL_ONLY',source,'-o',exe]
    compile_result=logged(command,out/'compile',120)
    if compile_result['exit_code']:raise RuntimeError('sanitizer compile failed')
    results={}
    for name,leaks in [('asan_ubsan',0),('lsan',1)]:
        started=time.monotonic();env=dict(os.environ,ASAN_OPTIONS=f'detect_leaks={leaks}:soft_rss_limit_mb=1024:hard_rss_limit_mb=2048');record=dict(command=[str(exe)],environment={'ASAN_OPTIONS':env['ASAN_OPTIONS']},timeout_seconds=60)
        try:
            p=subprocess.run([str(exe)],cwd=ROOT,env=env,text=True,capture_output=True,timeout=60,preexec_fn=lambda:resource.setrlimit(resource.RLIMIT_CORE,(0,0)))
            record.update(exit_code=p.returncode,status='PASS' if p.returncode==0 and 'PASS prescribed' in p.stdout else 'FAIL');(out/(name+'.stdout.log')).write_text(p.stdout);(out/(name+'.stderr.log')).write_text(p.stderr)
            if 'LeakSanitizer does not work under ptrace' in p.stderr:record['status']='BLOCKED'
        except subprocess.TimeoutExpired:record.update(status='FAIL',reason='timeout')
        record['runtime_seconds']=time.monotonic()-started;results[name]=record
    if before!={str(p.relative_to(ROOT)):sha(p) for p in inputs}:raise ValueError('source changed during sanitizer build/run')
    write_json(out/'metrics.json',dict(results=results,binary_sha256=sha(exe),source_sha256=before,scope='own prescribed contact kernel instrumented; SOFA libraries/whole engine NOT instrumented; ASan virtual shadow has no4GiB RLIMIT_AS, RSS hard2GiB and60s'))
    print({k:v['status'] for k,v in results.items()})
if __name__=='__main__':main()
