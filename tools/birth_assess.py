import json,csv,math
from birth_common import ROOT,OUT,write_json
from history_assess import comparison
PAIRS=[('history_half','base','history_half',.01),('history_quarter','history_half','history_quarter',.01),('mesh11_21','base','n21',.01),('mesh21_41','n21','n41',.01),('normal8_16','base','normal16',.01),('normal16_32','normal16','normal32',.01),('tangent2_4','base','cell4',.01),('time_half','base','dt_half',.001),('time_quarter','dt_half','dt_quarter',.001),('repeat','base','repeat',1e-6)]
def same_physics(a,b):
    for key in ('shape','axis','load','mu','normal_k','tangent_k','tension','pressure','rayleigh_mass','beam_material'):
        if a['config'][key]!=b['config'][key]:raise ValueError('different physical problem: '+key)
def observables(path):
    with(path/'contact.csv').open()as f:rows=[r for r in csv.DictReader(f)if 13.9-1e-8<=float(r['time'])<14-1e-8]
    if not rows:return {}
    keys=('normal_force','elastic_energy','friction_dissipation','release_dissipation','max_ratio')
    return {k:sum(float(r[k])for r in rows)/len(rows)for k in keys}
def main():
    records={};checks={};events={};aux={}
    for path in (OUT/'grasp').iterdir():
        if not (path/'metrics.json').exists():continue
        r=json.loads((path/'metrics.json').read_text())
        if r['config'].get('profile_only'):continue
        records[path.name]=r
        aux[path.name]=observables(path)
        markers=[json.loads(line[len('BIRTH_EVENT_STATS '):]) for line in (path/'stdout.log').read_text().splitlines() if line.startswith('BIRTH_EVENT_STATS ')]
        events[path.name]=dict(status='PASS' if markers and r.get('execution_completed') and markers[-1]['commits']==round(r['config']['duration']/r['config']['dt']) else 'FAIL',counts=markers[-1] if markers else None,scope='actual engine commit count; unresolved samples remain explicit')
    for name,a,b,limit in PAIRS:
        if a not in records or b not in records:checks[name]=dict(status='NOT RUN');continue
        ra,rb=records[a],records[b]
        if ra['identity']['birth_build']!=rb['identity']['birth_build']:raise ValueError('different compiled models')
        same_physics(ra,rb)
        if not ra.get('bounded_hold_pass') or not rb.get('bounded_hold_pass'):checks[name]=dict(status='FAIL',reason='underlying physical/engine gate',coarse=a,fine=b);continue
        checks[name]=dict(comparison(ra,rb,limit),coarse=a,fine=b)
        checks[name]['additional_same_hold_stage_observables']={k:dict(absolute_difference=abs(aux[a][k]-aux[b][k]),relative_difference=abs(aux[a][k]-aux[b][k])/abs(aux[b][k]) if aux[b][k] else(0 if aux[a][k]==0 else None))for k in aux[a]if k in aux[b]}
    if 'history_eighth' in records and 'history_quarter' in records:
        ra,rb=records['history_quarter'],records['history_eighth']
        if ra['identity']['birth_build']!=rb['identity']['birth_build']:raise ValueError('different compiled models')
        same_physics(ra,rb)
        checks['history_eighth']=dict(comparison(ra,rb,.01),coarse='history_quarter',fine='history_eighth') if ra.get('bounded_hold_pass') and rb.get('bounded_hold_pass') else dict(status='FAIL',reason='underlying physical/engine gate')
        checks['history_eighth']['additional_same_hold_stage_observables']={k:dict(absolute_difference=abs(aux['history_quarter'][k]-aux['history_eighth'][k]),relative_difference=abs(aux['history_quarter'][k]-aux['history_eighth'][k])/abs(aux['history_eighth'][k]) if aux['history_eighth'][k] else(0 if aux['history_quarter'][k]==0 else None))for k in aux['history_quarter']if k in aux['history_eighth']}
    loss_checks={}
    for name in ('history_half','history_quarter','history_eighth'):
        diff=checks.get(name,{}).get('additional_same_hold_stage_observables',{}).get('friction_dissipation')
        if diff is not None:loss_checks[name]=dict(status='PASS' if diff['relative_difference']is not None and diff['relative_difference']<=.01 else'FAIL',limit=.01,**diff)
    summary=dict(status='FAIL' if any(r['status']=='FAIL' for r in list(checks.values())+list(loss_checks.values())) else 'EXPERIMENTAL',comparisons=checks,history_dissipation_convergence=loss_checks,event_commit_audit=events,hold_stage_observables=aux,additional_observables_scope='means over identical13.9<=t<14 hold interval; no epsilon denominator; null relative difference means nonzero versus zero; historical motion gate is not blanket dissipation convergence',grasp_optimization='BLOCKED',full_grasp_certified=False,cases={n:{k:r.get(k) for k in ('status','hold_displacement_mm','hold_rotation_increment_rad','global_force_residual','global_moment_residual','recovery_pass','friction_dissipation','failure_reason','process')} for n,r in records.items()})
    write_json(OUT/'convergence.json',summary);target=ROOT/'reports/birth_evidence';target.mkdir(exist_ok=True);write_json(target/'convergence.json',summary)
    with (target/'convergence.csv').open('w',newline='')as f:
        w=csv.writer(f);w.writerow(['comparison','status','translation_relative_error','rotation_relative_error','limit'])
        for n,r in checks.items():w.writerow([n,r['status'],r.get('relative_difference',{}).get('hold_displacement_mm'),r.get('relative_difference',{}).get('hold_rotation_increment_rad'),r.get('limit')])
    print({k:v['status'] for k,v in checks.items()})
if __name__=='__main__':main()
