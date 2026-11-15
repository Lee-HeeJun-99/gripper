"""Extend loss analysis to the actual full contact cycle,without hiding hold gates."""
import argparse
import csv
import json
import xml.etree.ElementTree as ET
from curve_common import OUT,write_json


def sample(path,time):
    if time==0:return dict(time=0.,plastic=0.,detachment=0.,total=0.,origin='fresh component constructor cumulative counters,not an unimplemented energy term')
    with(path/'contact.csv').open()as f:row=min(csv.DictReader(f),key=lambda r:abs(float(r['time'])-time))
    if abs(float(row['time'])-time)>1e-8:raise ValueError('actual phase endpoint not recorded')
    p=float(row['friction_dissipation']);d=float(row['release_dissipation'])
    return dict(time=float(row['time']),plastic=p,detachment=d,total=p+d,origin='actual SOFA cumulative contact CSV')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--checkpoint',default='v1');a=parser.parse_args();target=OUT/('cycle_loss_'+a.checkpoint+'.json')
    if target.exists():raise ValueError('refuse overwritten cycle evidence')
    names=('base','halfdt','quarterdt','mesh11_half','mesh41_half','history_fine_half','repeat24','half_repeat24');points=(0,.5,3,6,14,15,16,18);cases={}
    aliases={'base':'base24','halfdt':'half24','quarterdt':'quarter18'}
    for name in names:
        path=OUT/'grasp'/name
        if not(path/'metrics.json').exists()and name in aliases:path=OUT/'grasp'/aliases[name]
        if not(path/'metrics.json').exists():continue
        r=json.loads((path/'metrics.json').read_text());loop=ET.parse(path/'scene.scn').getroot();tag='FixedStepClockAnimationLoop'if loop.find('FixedStepClockAnimationLoop')is not None else'DefaultAnimationLoop'
        cases[name]=dict(status=r['status'],dt=r['config']['dt'],clock=tag,points={str(t):sample(path,t)for t in points})
        if r['config']['duration']>=24:cases[name]['points']['24']=sample(path,24)
    checks={}
    for left,right,limit in(('base','halfdt',.001),('halfdt','quarterdt',.001),('base','quarterdt',.001),('mesh11_half','halfdt',.01),('halfdt','mesh41_half',.01),('halfdt','history_fine_half',.01)):
        if left not in cases or right not in cases:continue
        x,y=cases[left]['points'],cases[right]['points'];rows={}
        for start,end in zip(points[:-1],points[1:]):
            u=x[str(end)]['total']-x[str(start)]['total'];v=y[str(end)]['total']-y[str(start)]['total'];relative=abs(u-v)/abs(v)if v else(0. if u==0 else None)
            rows[str(start)+'_'+str(end)]=dict(coarse_increment=u,fine_increment=v,absolute=abs(u-v),relative=relative,status='PASS'if relative is not None and relative<=limit else'FAIL')
        u=x['18']['total'];v=y['18']['total'];relative=abs(u-v)/abs(v)if v else(0. if u==0 else None)
        checks[left+'_'+right]=dict(limit=limit,whole_cycle=dict(relative=relative,absolute=abs(u-v),status='PASS'if relative is not None and relative<=limit else'FAIL'),phases=rows)
    write_json(target,dict(status='EXPERIMENTAL',cases=cases,checks=checks,scope='Additional full-cycle/phase diagnostics preserve original13.9–14hold gates. Use the same fine-value denominator and time.1percent/space-history1percent. Tiny/zero increments remain explicit;not epsilon-regularized.',grasp_optimization='BLOCKED pending all needed qualifications'))
    print({n:r['whole_cycle']for n,r in checks.items()})


if __name__=='__main__':main()
