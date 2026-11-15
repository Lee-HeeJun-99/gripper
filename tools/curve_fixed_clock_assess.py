"""Keep motion,hold-loss and full-cycle loss qualification separate."""
import json
from curve_common import OUT,write_json
from history_assess import comparison
from birth_assess import observables,same_physics


def main():
    target=OUT/'qualification_v1.json'
    if target.exists():raise ValueError('refuse overwritten evidence')
    names=('base24','half24','quarter18');records={n:json.loads((OUT/'grasp'/n/'metrics.json').read_text())for n in names};checks={}
    for left,right in(('base24','half24'),('half24','quarter18'),('base24','quarter18')):
        u,v=records[left],records[right];same_physics(u,v)
        for field in('curved','structural_compensation','fixed_clock'):
            if u['identity'][field]!=v['identity'][field]:raise ValueError('compiled model differs')
        r=comparison(u,v,.001);r['motion_status']=r['status'];x,y=observables(OUT/'grasp'/left),observables(OUT/'grasp'/right)
        r['observables']={k:dict(absolute=abs(x[k]-y[k]),relative=abs(x[k]-y[k])/abs(y[k])if y[k]else(0 if x[k]==0 else None))for k in x}
        loss=r['observables']['friction_dissipation']['relative'];r['hold_loss_status']='PASS'if loss is not None and loss<=.001 else'FAIL';r['physical_hold_pass']=bool(u['bounded_hold_pass']and v['bounded_hold_pass']);r['status']='PASS'if r['motion_status']=='PASS'and r['hold_loss_status']=='PASS'and r['physical_hold_pass']else'FAIL';checks[left+'_'+right]=r
    cycle=json.loads((OUT/'cycle_loss_fixed_clock_v1.json').read_text())
    write_json(target,dict(status='EXPERIMENTAL',checks=checks,cycle_loss={k:r['whole_cycle']for k,r in cycle['checks'].items()},recovery={n:('PASS'if records[n]['recovery_pass']else'FAIL')for n in('base24','half24')},quarter24_recovery='NOT RUN',global_energy='BLOCKED',full_grasp_optimization='BLOCKED',scope='fixed-clock contrast;all three actual physical hold gates pass,full-cycle loss still separate. No inherited spatial or all-wrench certification.'))
    print({n:(r['status'],r['relative_difference'],r['hold_loss_status'])for n,r in checks.items()})


if __name__=='__main__':main()
