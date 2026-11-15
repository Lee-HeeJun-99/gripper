"""One-factor controls; sequential so combined long-process cap stays four."""
import json
from curve_common import OUT,write_json
from curve_trial import run
def main():
    profile=json.loads((OUT/'grasp/profile_n21/metrics.json').read_text());prediction=profile['process']['runtime_s']*4.5
    if profile['status']!='EXPERIMENTAL'or prediction*1.1>480:raise RuntimeError('existing full-network profile cannot justify480s control')
    write_json(OUT/'ablation_plan.json',dict(predicted_upper_cost=prediction,reason='same21nodes and contact;remove rather than add connections/cable segments;previous full-network profile bounds cost',wall=480,parallel=1,controls=['fixed_connectors_only','fixed_cable_guides_only']))
    for name,kw in [('connectors_only_n21',dict(fixed_connectors=True)),('cables_only_n21',dict(fixed_cables=True))]:run(name,nodes=21,**kw)
if __name__=='__main__':main()
