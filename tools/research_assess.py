"""Separate kinematic, loss, and physical-equilibrium diagnostics."""
import json,csv
from research_common import ROOT,OUT,write_json
from history_assess import comparison
from birth_assess import same_physics,observables
PAIRS=[('history_01_005','base','h_half',.01),('history_005_0025','h_half','h_quarter',.01),('history_0025_00125','h_quarter','h_eighth',.01),('fine_mesh11_21','h_quarter','fine_n21',.01),('fine_mesh21_41','fine_n21','fine_n41',.01),('fine_time_half','h_quarter','fine_halfdt',.001),('fine_repeat','h_quarter','fine_repeat',1e-6)]
PAIRS.append(('fine_time_quarter','fine_halfdt','fine_quarterdt',.001))
def main():
    records={};observed={};checks={};transactions={}
    for p in sorted((OUT/'grasp').glob('*/metrics.json')):
        r=json.loads(p.read_text())
        if r['config']['profile_only']:continue
        records[p.parent.name]=r
        if not r.get('bounded_hold_pass'):continue
        observed[p.parent.name]=observables(p.parent)
        lines=[json.loads(t[len('BIRTH_EVENT_STATS '):])for t in(p.parent/'stdout.log').read_text().splitlines()if t.startswith('BIRTH_EVENT_STATS ')]
        if lines:
            s=lines[-1];transactions[p.parent.name]=dict(status='PASS'if s['point_commit_plastic']==s['observer_plastic']and s['commits']==round(r['config']['duration']/r['config']['dt'])else'FAIL',stats=s,scope='exact equality of accumulated observation and actual committed material-point plastic; legacy nodes key denotes material points')
    for name,a,b,limit in PAIRS:
        if a not in records or b not in records:checks[name]=dict(status='NOT RUN');continue
        ra,rb=records[a],records[b];same_physics(ra,rb)
        if ra['identity']['material_point']!=rb['identity']['material_point']:raise ValueError('different compiled contact model')
        if not ra.get('bounded_hold_pass')or not rb.get('bounded_hold_pass'):checks[name]=dict(status='FAIL',reason='underlying physics/engine gate');continue
        r=dict(comparison(ra,rb,limit),coarse=a,fine=b);r['motion_status']=r['status'];r['same_hold_observables']={}
        for key in observed[a]:
            x,y=observed[a][key],observed[b][key];difference=abs(x-y)/abs(y)if y else(0 if x==0 else None)
            r['same_hold_observables'][key]=dict(absolute_difference=abs(x-y),relative_difference=difference)
        d=r['same_hold_observables']['friction_dissipation']['relative_difference'];r['friction_loss_status']='PASS'if d is not None and d<=limit else'FAIL'
        if r['friction_loss_status']=='FAIL':r['status']='FAIL'
        checks[name]=r
    summary=dict(status='FAIL'if any(r['status']=='FAIL'for r in checks.values())else'EXPERIMENTAL',comparisons=checks,transactions=transactions,cases={name:{k:r.get(k)for k in('status','bounded_hold_pass','hold_displacement_mm','hold_rotation_increment_rad','global_force_residual','global_moment_residual','recovery_pass','process','failure_reason')}for name,r in records.items()},grasp_optimization='BLOCKED',global_energy='BLOCKED',scope='same13.9<=t<14 cumulative loss mean as legacy diagnostic; not full integration/contact-distribution/force-closure certificate')
    write_json(OUT/'assessment.json',summary);target=ROOT/'reports/autonomous_evidence';target.mkdir(exist_ok=True);write_json(target/'assessment.json',summary)
    with(target/'comparisons.csv').open('w',newline='')as f:
        writer=csv.writer(f);writer.writerow(['comparison','combined_status','motion_status','translation_relative','rotation_relative','friction_loss_relative','limit'])
        for name,r in checks.items():writer.writerow([name,r['status'],r.get('motion_status'),r.get('relative_difference',{}).get('hold_displacement_mm'),r.get('relative_difference',{}).get('hold_rotation_increment_rad'),r.get('same_hold_observables',{}).get('friction_dissipation',{}).get('relative_difference'),r.get('limit')])
    print({n:(r['status'],r.get('friction_loss_status'))for n,r in checks.items()})
if __name__=='__main__':main()
