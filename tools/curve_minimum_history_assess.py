"""Preserve the late-phase FAIL despite a successful full24s physical run."""
import json
from curve_common import OUT,sha,write_json
from curve_patch_assess import normalized
from curve_phase_assess import relative
from curve_cycle_loss import sample
from curve_local_history import immutable


def main():
    target=OUT/'history1000nm_full_assessment_v1.json'
    if target.exists():raise ValueError('immutable assessment exists')
    first=OUT/'full_coarse_history1250nm';second=OUT/'history1000nm_full24_v1'
    p=first/'metrics_same_grid_v2.json';q=second/'metrics.json';a=json.loads(p.read_text());b=json.loads(q.read_text())
    if normalized(first)!=normalized(second):raise ValueError('unintended XML physics/control changes')
    for key in('curved','inherited'):
        if immutable(a['identity'][key])!=immutable(b['identity']['runtime'][key]):raise ValueError('compiled physics differs')
    times=(0,.5,2,3,4,6,7,14,15,16,16.5,18,24)
    phases={f'{lo}_{hi}':relative(sample(first,hi)['total']-sample(first,lo)['total'],sample(second,hi)['total']-sample(second,lo)['total'],.01)for lo,hi in zip(times[:-1],times[1:])}
    physical=all(r['bounded_hold_pass']and r['recovery_pass']for r in(a,b))
    motion={key:relative(a[key],b[key],.01)for key in('hold_displacement_mm','hold_rotation_increment_rad')}
    whole=relative(a['friction_dissipation'],b['friction_dissipation'],.01)
    passed=physical and whole['status']=='PASS'and all(r['status']=='PASS'for r in list(phases.values())+list(motion.values()))
    write_json(target,dict(status='PASS'if passed else'FAIL',physical_hold_and_recovery=physical,motion=motion,whole_cycle_loss=whole,phase_losses=phases,metrics_sha256={str(p):sha(p),str(q):sha(q)},scope='actual original curved component same numerical grid/physical parameters,spacing.00125->.001mm (factor1.25,NOT a factor-two history certificate). Late-phase failures retained;neither successful full run nor tiny absolute difference overrides1percent. No full-grasp/optimization approval.'))
    print('minimum-history full contrast',passed,{k:r['relative']for k,r in phases.items()if r['status']=='FAIL'})


if __name__=='__main__':main()
