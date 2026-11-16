"""Preserve contact isolation, mapped tangent diagnosis and actual convergence.
All comparisons use completed runs at physical timestamps; never certify grasp.
"""
import argparse,csv,json,subprocess,shutil
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged
from film_nonlinear_assess import read,compare

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--fine',nargs='*',default=[]);a=p.parse_args()
    for tag in [a.tag]+a.fine:
        if not tag.replace('_','').isalnum():raise ValueError('tag')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
    inputs={}
    def campaign(name):return ROOT/'results'/('autonomous_film_'+name)
    def remember(path):inputs[str(path.relative_to(ROOT))]=sha(path)
    def completed(name,index='1'):
        path=campaign(name);summary=json.loads((path/'summary.json').read_text());remember(path/'summary.json')
        if summary.get('process_status')!='PASS':raise RuntimeError('incomplete '+name)
        data=read(path/index);expected=summary.get('rows')
        expected=expected[index]['steps'] if isinstance(expected,dict) else expected
        if len(data['time'])!=expected:raise RuntimeError('row count '+name)
        remember(path/index/'journal.csv');return data
    # Independent mapped matrix, including the BDF1 -> BDF2 factor transition.
    source=ROOT/'diagnostics/film_shell/MappedTangent.cpp';remember(source)
    shutil.copy2(source,out/'MappedTangent.cpp')
    build=logged(['g++','-std=c++17','-O2','-ffp-contract=off','-I/usr/include/eigen3',source,'-o',out/'mapped_tangent'],out/'compile',180)
    if build['exit_code']:raise RuntimeError('diagnostic compile failed')
    tangent={}
    for name in ('20261116_mapped_tangent38','20261116_mass_refresh40'):
        tangent[name]={}
        for step in (0,1):
            prefix=campaign(name)/'1'/f'tangent.{step}'
            for suffix in ('.state.csv','.matrix.csv'):remember(prefix.with_name(prefix.name+suffix))
            stage=out/f'{name}_{step}';process=logged([out/'mapped_tangent',prefix],stage,30)
            tangent[name][step]=dict(process=process,metrics=json.loads((stage/'stdout.log').read_text()))
    baseline=campaign('20261116_hard_transient25')
    updated=campaign('20261116_consistent_tangent41')
    regression={}
    for index in ('1','2','4'):
        old=completed('20261116_hard_transient25',index);new=completed('20261116_consistent_tangent41',index)
        regression[index]=compare(old,new,.001)
    counted=campaign('20261116_counted_contact34')/'1'
    compact=campaign('20261116_compact_contact36')/'1'
    for path in (counted/'journal.csv',compact/'journal.csv',counted/'profile.csv',compact/'profile.csv'):remember(path)
    optimization=dict(actual_journal_bitwise_equal=(counted/'journal.csv').read_bytes()==(compact/'journal.csv').read_bytes(),
        limitation='Single timings overlapped other jobs; compile-time optimization remains opt-in, not a controlled speedup certification')
    totals={}
    for name in ('20261116_counted_contact34','20261116_compact_contact36','20261116_consistent_tangent41'):
        path=campaign(name);index='4' if name.endswith('41') else '1'
        records=list(csv.DictReader((path/index/'profile.csv').open()));remember(path/index/'profile.csv')
        totals[name]=dict(newton_iterations=sum(int(r['newton_iterations']) for r in records),
                         extra_line_search_trials=sum(int(r['extra_line_search_trials']) for r in records),
                         maximum_momentum_residual=max(float(r['momentum_residual_norm']) for r in records),
                         actual_seconds=json.loads((path/'summary.json').read_text())['stages'][index]['runtime_s'])
    fine_data={name:completed(name) for name in a.fine}
    pairs={f'{i}:{j}':compare(fine_data[i],fine_data[j],.001) for n,i in enumerate(a.fine) for j in a.fine[n+1:]}
    result=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),tool_sha256=sha(__file__),
        inputs=inputs,diagnostic_binary_sha256=sha(out/'mapped_tangent'),mapped_tangent=tangent,
        old_vs_refreshed_solver=regression,compact=optimization,actual_profile=totals,refined_time_pairs=pairs,
        original_time_gate='FAIL',mesh_gate='FAIL',whole_energy='BLOCKED',film_rails_tendon='NOT RUN',grasp='NOT RUN',
        interpretation='Mapped mass factor cache defect verified and independent adapter checked; not a contact-force correction. Refinement comparisons cannot erase the original coarse-grid failure.')
    write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('inputs','mapped_tangent','old_vs_refreshed_solver')},indent=2))

if __name__=='__main__':main()
