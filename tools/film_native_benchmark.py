"""Cross-compiler derivatives plus sequential actual-SOFA wall-clock pairs."""
import argparse,json,subprocess,statistics
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    if not a.tag.replace('_','').isalnum():raise ValueError('tag')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);result={}
    source=ROOT/'diagnostics/film_shell/DerivativeDump.cpp'
    for name,flags in [('o2',['-O2']),('native',['-O3','-march=native','-fno-fast-math'])]:
        process=logged(['g++','-std=c++17','-ffp-contract=off',*flags,source,'-o',out/name],out/(name+'_build'),180)
        if process['exit_code']:raise RuntimeError('compile failed')
        process=logged([out/name,out/(name+'.bin')],out/(name+'_dump'),30)
        if process['exit_code']:raise RuntimeError('dump failed')
        result[name]=dict(derivative_sha256=sha(out/(name+'.bin')),binary_sha256=sha(out/name))
    exact=result['o2']['derivative_sha256']==result['native']['derivative_sha256']
    pairs=[]
    for repeat in range(3):
        runs={}
        # Alternate order; sequential execution and no other scheduled physics.
        order=['base','native'] if repeat%2==0 else ['native','base']
        for variant in order:
            tag=a.tag+'_'+str(repeat)+'_'+variant
            source_tag='20261116_endpoint_ramp50' if variant=='base' else '20261116_native_opt60'
            process=logged([__import__('sys').executable,ROOT/'tools/film_followup_run.py','--tag',tag,'--source',source_tag,'--steps','150','--duration','1.5','--no-tangent-probe'],out/(str(repeat)+'_'+variant),120)
            path=ROOT/'results'/('autonomous_film_'+tag)
            if process['exit_code']:raise RuntimeError('benchmark driver failed')
            summary=json.loads((path/'summary.json').read_text())
            if summary['process_status']!='PASS' or summary['newton_failed_steps']:raise RuntimeError('benchmark actual physics failed')
            runs[variant]=dict(seconds=summary['process']['runtime_s'],journal_sha256=sha(path/'1/journal.csv'),source=str(path.relative_to(ROOT)))
        pairs.append(dict(runs=runs,actual_state_bitwise_equal=runs['base']['journal_sha256']==runs['native']['journal_sha256']))
    ratio=statistics.median(p['runs']['native']['seconds']/p['runs']['base']['seconds'] for p in pairs)
    write_json(out/'summary.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_sha256=sha(source),tool_sha256=sha(__file__),derivatives=result,
        derivative_bitwise_equal=exact,pairs=pairs,median_native_over_base=ratio,
        status='PASS' if exact and all(p['actual_state_bitwise_equal'] for p in pairs) and ratio<1 else 'FAIL',
        scope='compiler optimization on this host and coupon only;does not alter convergence gate or certify grasp'))
    print(json.dumps(dict(derivative_exact=exact,median_native_over_base=ratio,state_exact=all(p['actual_state_bitwise_equal'] for p in pairs))))

if __name__=='__main__':main()
