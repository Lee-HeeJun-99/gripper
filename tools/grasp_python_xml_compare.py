"""Compare all600 original Python recorder outputs to XML/C++ adapters."""
import json,csv
from grasp_common import OUT,write_json
from run_trial import run_trial
from baseline_regression import metrics,states
def main():
    out=OUT/'python_xml_compare';out.mkdir(exist_ok=False);results={}
    for original,k in [('V109_FREE',None),('V110_FREE',0),('V110_SHEAR',.1)]:
        directory=out/original;r=run_trial(directory,k=k,duration=.3,timeout=60)
        if not r.get('execution_completed'):results[original]=dict(status='FAIL',reason=r['failure_reason']);continue
        rows=metrics(states(directory/'rigid.txt'),states(directory/'interface.txt'));sources=list((OUT/'python_recovery'/original).glob('result_*.csv'));gold=list(csv.DictReader(sources[0].open(encoding='utf-8-sig')));checks={};errors={}
        # The V110 slip recorder is a linear quaternion proxy; do NOT compare it
        # as if it were the adapter's exact mapped interface displacement.
        keys=['time_s','tip_deflection_mm','tip_velocity_z_mm_s']
        if original=='V109_FREE':keys+=['max_x_slip_mm','max_y_rel_mm','max_z_rel_mm']
        for key in keys:
            pairs=[(float(a[key]),float(b[key])) for a,b in zip(rows,gold)];errors[key]=max(abs(a-b) for a,b in pairs);checks[key]=len(rows)==len(gold)==600 and all(abs(a-b)<=1e-10+1e-6*abs(b) for a,b in pairs)
        results[original]=dict(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,max_abs_errors=errors,adapter_physics_status=r['status'],scope='transient model equivalence, NOT static equilibrium; V110 slip definitions intentionally not conflated')
    write_json(out/'summary.json',results);print(results)
if __name__=='__main__':main()
