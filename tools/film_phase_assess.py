"""Complete-campaign phase diagnosis; never overrides the full-time FAIL."""
import argparse,json
import numpy as np
from curve_common import ROOT,write_json
from film_nonlinear_assess import read,compare

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    if not a.tag.replace('_','').isalnum():raise ValueError('tag')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
    campaign=ROOT/'results/autonomous_film_20261116_hard_transient25';summary=json.loads((campaign/'summary.json').read_text());data={i:read(campaign/str(i)) for i in (1,2,4)}
    for i,d in data.items():
        if len(d['time'])!=summary['rows'][str(i)]['steps']:raise RuntimeError('incomplete trajectory')
    result={}
    for lo,hi in ((0,1),(1,1.3),(1.3,1.5),(1.5,2)):
        # Only compensate timestamp accumulation roundoff when selecting a
        # reporting window. No physical value or convergence tolerance changes.
        selected={i:{k:v[(d['time']>=lo-1e-12)&(d['time']<=hi+1e-12)] for k,v in d.items()} for i,d in data.items()}
        result[f'{lo}:{hi}']={f'{i}:{j}':compare(selected[i],selected[j],.001) for i,j in ((1,2),(1,4),(2,4))}
    first={str(i):next((float(t) for t,q in zip(d['time'],d['contact_area']) if q>0),None) for i,d in data.items()}
    penalty=read(ROOT/'results/autonomous_film_20261116_bdf2_transient18/4')
    boundary=compare(data[4],penalty,.001)
    report=dict(source='Actual completed SOFA journals',full_time_status=summary['time_status'],phase_comparisons=result,first_sampled_contact_time=first,hard_vs_penalty_fine=boundary,
        interpretation='Large error concentrates after sampled contact. Hard slope did not qualify time convergence. The penalty comparison also tightens Newton tolerance, so is evidence against dominance, not an exact one-factor proof. No friction is enabled in either coupon.')
    write_json(out/'summary.json',report);print(json.dumps(dict(first_contact=first,full_time_status=report['full_time_status'],hard_vs_penalty=boundary),indent=2))

if __name__=='__main__':main()
