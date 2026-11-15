"""ASan needs huge VIRTUAL shadow; bound physical RSS using sanitizer instead."""
import os,subprocess,resource,argparse
from closure_common import OUT,BUILD,sha,write_json
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--name',default='run_shadow_compatible');args=parser.parse_args()
    if not args.name.replace('_','').isalnum():raise ValueError('safe output name required')
    out=OUT/'sanitizers'/args.name;out.mkdir(exist_ok=False);cmd=[str(BUILD/'sanitizers/test_closure')];env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1:halt_on_error=1:hard_rss_limit_mb=2048:max_allocation_size_mb=256',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1');write_json(out/'command.json',cmd);write_json(out/'environment.json',{k:env[k] for k in ('ASAN_OPTIONS','UBSAN_OPTIONS')})
    with (out/'stdout.log').open('x') as stdout,(out/'stderr.log').open('x') as stderr:
        try:r=subprocess.run(cmd,cwd=BUILD/'sanitizers',env=env,stdout=stdout,stderr=stderr,timeout=60,preexec_fn=lambda:resource.setrlimit(resource.RLIMIT_CORE,(0,0)));code=r.returncode
        except subprocess.TimeoutExpired:code=None
    log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();checks=dict(exit_clean=code==0,unit_pass='PASS integrated active interval' in log,no_sanitizer_error='ERROR:' not in log and 'runtime error:' not in log and 'LeakSanitizer' not in log)
    result=dict(status='PASS' if all(checks.values()) else 'FAIL',exit_code=code,checks=checks,scope='ASan/UBSan/LSan new closure unit; SOFA shared libraries NOT instrumented. ASan physical RSS2GiB/time60s; no4GiB virtual-AS cap because shadow requires14TiB address space. Initial incompatible-AS failure preserved.');result['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file()};write_json(out/'result.json',result);print(result['status'],log[-1500:])
if __name__=='__main__':main()
