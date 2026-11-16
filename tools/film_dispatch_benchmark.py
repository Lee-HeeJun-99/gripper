"""Compile-time dispatch qualification,not model calibration."""
import argparse,json,statistics,subprocess
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    if not a.tag.replace('_','').isalnum():raise ValueError('tag')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);derivatives={};source=ROOT/'diagnostics/film_rail_tendon/DerivativeDump.cpp'
    for name,flags in [('base',['-O3','-march=native','-fno-fast-math']),('native',['-O3','-march=native','-fno-fast-math','-DREGRIP_FILM_DIRECT_VISITOR'])]:
        build=logged(['g++','-std=c++17','-ffp-contract=off',*flags,source,'-o',out/name],out/(name+'_compile'),180)
        if build['exit_code']:raise RuntimeError('compile')
        run=logged([out/name,out/(name+'.bin')],out/(name+'_derivatives'),60)
        if run['exit_code']:raise RuntimeError('derivative dump')
        derivatives[name]=sha(out/(name+'.bin'))
    pairs=[]
    for repeat in range(3):
        results={}
        for name in (['base','native'] if repeat%2==0 else ['native','base']):
            tag=a.tag+'_'+str(repeat)+'_'+name;source_case='20261116_cost_parts149' if name=='base' else '20261116_dispatch153'
            process=logged([__import__('sys').executable,ROOT/'tools/film_rail_run.py','--tag',tag,'--steps','20','--duration','.2','--tension','.001','--reuse',source_case],out/(str(repeat)+'_'+name),120)
            if process['exit_code']:raise RuntimeError('driver')
            path=ROOT/'results'/('autonomous_film_'+tag);summary=json.loads((path/'summary.json').read_text())
            if summary['status']!='PASS':raise RuntimeError('actual trial failed')
            results[name]=dict(seconds=summary['stages']['physics']['runtime_s'],journal_sha256=sha(path/'1/journal.csv'))
        pairs.append(dict(results=results,bitwise_equal=results['base']['journal_sha256']==results['native']['journal_sha256']))
    ratio=statistics.median(p['results']['native']['seconds']/p['results']['base']['seconds'] for p in pairs);exact=derivatives['base']==derivatives['native']
    result=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_sha256=sha(source),derivative_dumps=derivatives,derivative_bitwise_equal=exact,pairs=pairs,median_direct_over_indirect=ratio,
        status='PASS' if exact and all(p['bitwise_equal'] for p in pairs) and ratio<1 else 'FAIL',scope='compiler speed/identity on current host and limited deformations,not nonlinear/grasp approval')
    write_json(out/'summary.json',result);print(json.dumps(dict(exact=exact,actual_states_exact=all(p['bitwise_equal'] for p in pairs),ratio=ratio)))
if __name__=='__main__':main()

