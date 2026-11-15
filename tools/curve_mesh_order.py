"""Actual adjacent mesh gates plus labelled Richardson estimate,not a new gate."""
import json
import math
from curve_common import OUT,write_json,sha


def main():
    target=OUT/'mesh_order_v1.json'
    if target.exists():raise ValueError('refuse overwritten mesh evidence')
    names=('mesh11_half','halfdt','mesh41_half');records=[json.loads((OUT/'grasp'/n/'metrics.json').read_text())for n in names]
    if not all(r['bounded_hold_pass']for r in records):raise ValueError('underlying actual physical gate failure')
    if [r['config']['nodes']for r in records]!=[11,21,41]or any(r['config']['dt']!=.00025 for r in records):raise ValueError('controlled mesh/dt mismatch')
    values={};checks={}
    for metric in('hold_displacement_mm','hold_rotation_increment_rad'):
        a,b,c=[r[metric]for r in records];d0=a-b;d1=b-c
        order=math.log2(abs(d0/d1))if d0*d1>0 else None
        values[metric]=dict(actual_SOFA=[a,b,c],observed_order=order,Richardson_O_h2_estimate=c+(c-b)/3,estimate_origin='mathematical extrapolation from actual SOFA values,not a measured/reference solution')
        checks[metric]=[dict(pair=[11,21],relative=abs(a-b)/abs(b),status='PASS'if abs(a-b)/abs(b)<=.01 else'FAIL'),dict(pair=[21,41],relative=abs(b-c)/abs(c),status='PASS'if abs(b-c)/abs(c)<=.01 else'FAIL')]
    write_json(target,dict(status='EXPERIMENTAL',values=values,unchanged_one_percent_gates=checks,actual_metrics_hashes={n:sha(OUT/'grasp'/n/'metrics.json')for n in names},scope='near-second-order trend does NOT relabel coarse11FAIL. Same half-dt,fixed hardware,tributary mass,compensated structural arithmetic;not inherited by a different time grid.'))
    print(values)


if __name__=='__main__':main()
