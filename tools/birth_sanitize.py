import os,subprocess,time,resource
from birth_common import ROOT,OUT,write_json,sha
from closure_validation_suite import logged
def main():
    out=OUT/'sanitizer';out.mkdir(exist_ok=False);exe=ROOT/'build/birth_20261115/birth_math_asan';source=ROOT/'tests/test_birth_events_math.cpp';r=logged(['g++','-std=c++17','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer',source,'-o',exe],out/'compile',120)
    if r['exit_code']:raise RuntimeError('sanitizer compile')
    results={}
    for name,leaks in [('asan_ubsan',0),('lsan',1)]:
        env=dict(os.environ,ASAN_OPTIONS=f'detect_leaks={leaks}:soft_rss_limit_mb=1024:hard_rss_limit_mb=2048');start=time.monotonic()
        try:
            p=subprocess.run([str(exe)],cwd=ROOT,env=env,text=True,capture_output=True,timeout=60,preexec_fn=lambda:resource.setrlimit(resource.RLIMIT_CORE,(0,0)));(out/(name+'.stdout.log')).write_text(p.stdout);(out/(name+'.stderr.log')).write_text(p.stderr);status='PASS' if p.returncode==0 and 'PASS birth/'in p.stdout else 'FAIL'
            if 'LeakSanitizer does not work under ptrace'in p.stderr:status='BLOCKED'
            results[name]=dict(status=status,exit_code=p.returncode,runtime=time.monotonic()-start,environment={'ASAN_OPTIONS':env['ASAN_OPTIONS']})
        except subprocess.TimeoutExpired:results[name]=dict(status='FAIL',reason='timeout')
    write_json(out/'summary.json',dict(results=results,binary_sha256=sha(exe),source_sha256=sha(source),scope='own mathematical birth kernel only, NOT sanitizer-built SOFA engine; hard2GiB RSS and60s'));print(results)
if __name__=='__main__':main()
