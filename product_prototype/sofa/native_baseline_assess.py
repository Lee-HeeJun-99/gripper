"""All-pair native baseline mesh and proportional-load checks, no relative floors."""
import argparse,itertools,json,re
from pathlib import Path
from native_bending_coupon import BASE,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True)
    p.add_argument('--cases',nargs='+',required=True);args=p.parse_args()
    out=BASE/'results'/args.tag;out.mkdir(exist_ok=False);runs=[];pairs=[]
    for name in args.cases:
        path=BASE/'results'/name/'summary.json';data=json.loads(path.read_text())
        runs.append((name,data))
    for name,data in runs:
        for a,b in itertools.combinations(data['records'],2):
            if a['model']!=b['model'] or 'tip_m' not in a or 'tip_m' not in b:continue
            error=abs(a['tip_m']-b['tip_m'])/max(abs(a['tip_m']),abs(b['tip_m']))
            pairs.append(dict(case=name,model=a['model'],nx=[a['nx'],b['nx']],relative=error,
                              gate=.01,status='PASS_PAIR_ONLY' if error<=.01 else 'FAIL_MESH_GATE'))
    linear=[]
    for (an,a),(bn,b) in itertools.combinations(runs,2):
        if a['force_N']==b['force_N'] or a.get('cross_nodes',3)!=b.get('cross_nodes',3) or a.get('tip_load','uniform-node')!=b.get('tip_load','uniform-node'):continue
        for x in a['records']:
            for y in b['records']:
                if (x['model'],x['nx'])!=(y['model'],y['nx']) or 'tip_m' not in x or 'tip_m' not in y:continue
                u=x['tip_m']/a['force_N'];v=y['tip_m']/b['force_N']
                error=abs(u-v)/max(abs(u),abs(v))
                linear.append(dict(cases=[an,bn],model=x['model'],nx=x['nx'],relative=error,
                                   gate=1e-12,status='PASS_LINEARITY_ONLY' if error<=1e-12 else 'FAIL'))
    cross=[]
    for (an,a),(bn,b) in itertools.combinations(runs,2):
        if a['force_N']!=b['force_N'] or a.get('tip_load','uniform-node')!=b.get('tip_load','uniform-node') or a.get('cross_nodes',3)==b.get('cross_nodes',3):continue
        for x in a['records']:
            for y in b['records']:
                if (x['model'],x['nx'])!=(y['model'],y['nx']) or 'tip_m' not in x or 'tip_m' not in y:continue
                error=abs(x['tip_m']-y['tip_m'])/max(abs(x['tip_m']),abs(y['tip_m']))
                cross.append(dict(cases=[an,bn],model=x['model'],nx=x['nx'],relative=error,
                                  status='PASS_PAIR_ONLY' if error<=.01 else 'FAIL_MESH_GATE'))
    result=dict(scope='Static diagnostic only; no energy/reaction/time/B3 certification',mesh_pairs=pairs,cross_pairs=cross,
                linearity=linear,inputs={n:sha(BASE/'results'/n/'summary.json') for n,_ in runs})
    (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
