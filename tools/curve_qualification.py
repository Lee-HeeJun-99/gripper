"""One runtime-binary pair,one physical hardware and derived mass scheme."""
import json
from curve_common import OUT,write_json
from curve_assess import layout_signature
from birth_assess import same_physics,observables
from history_assess import comparison
def main():
    records={};transactions={};checks={};completed=json.loads((OUT/'canonical_completed.json').read_text())
    for p in(OUT/'grasp').glob('*/metrics.json'):
        r=json.loads(p.read_text())
        if r['config']['profile_only']:continue
        records[p.parent.name]=r;stats=[json.loads(s[len('BIRTH_EVENT_STATS '):])for s in(p.parent/'stdout.log').read_text().splitlines()if s.startswith('BIRTH_EVENT_STATS ')]
        transactions[p.parent.name]=dict(status='PASS'if stats and stats[-1]['commits']==round(r['config']['duration']/r['config']['dt'])and stats[-1]['point_commit_plastic']==stats[-1]['observer_plastic']else'FAIL',stats=stats[-1]if stats else None)
    for a,b,limit in(('n21','n41',.01),('n21','history_fine',.01),('n21','halfdt',.001),('halfdt','quarterdt',.001),('n21','quarterdt',.001),('n21','repeat24',1e-6)):
        name=a+'_'+b
        if a not in records or b not in records:
            blocked=any(completed.get('full_'+n,{}).get('status')=='BLOCKED'for n in(a,b));checks[name]=dict(status='BLOCKED'if blocked else'NOT RUN',reason='profile-qualified resource policy'if blocked else'in progress/unexecuted');continue
        x,y=records[a],records[b];same_physics(x,y)
        if x['identity']['curved']!=y['identity']['curved']or x['identity']['inherited']['inherited']['beam']['plugin_sha256']!=y['identity']['inherited']['inherited']['beam']['plugin_sha256']:raise ValueError('runtime-binary pair differs')
        for k in('layout_policy','mass_quadrature','solver_template'):
            if x['config'].get(k)!=y['config'].get(k):raise ValueError('different experiment definition: '+k)
        if layout_signature(a)!=layout_signature(b):raise ValueError('physical connector/cable layout differs')
        if not(x.get('bounded_hold_pass')and y.get('bounded_hold_pass')):checks[name]=dict(status='FAIL',reason='underlying physical gate');continue
        r=comparison(x,y,limit);u,v=observables(OUT/'grasp'/a),observables(OUT/'grasp'/b);r['same_hold_observables']={k:dict(absolute=abs(u[k]-v[k]),relative=abs(u[k]-v[k])/abs(v[k])if v[k]else(0 if u[k]==0 else None))for k in u};d=r['same_hold_observables']['friction_dissipation']['relative'];r['loss_status']='PASS'if d is not None and d<=limit else'FAIL';checks[name]=r
    result=dict(status='EXPERIMENTAL',checks=checks,transactions=transactions,recovery_24=records.get('repeat24',{}).get('recovery_pass'),grasp_optimization='BLOCKED',global_stored_energy='BLOCKED',scope='21node production candidate against41,coarse11failure preserved elsewhere;space1percent,time.1percent,repeat1e-6;no new full grasp certification')
    write_json(OUT/'qualification.json',result);print({k:(r['status'],r.get('relative_difference'),r.get('loss_status'))for k,r in checks.items()})
if __name__=='__main__':main()
