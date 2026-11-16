"""Assess actual film trajectories, not merely their final tip coordinate."""
import argparse,csv,json
from pathlib import Path
import numpy as np

def read(case):
    rows=list(csv.DictReader((case/'journal.csv').open()))
    return {key:np.array([float(r[key]) for r in rows]) for key in ('time','tip_z','U','free_force','contact_area','normal_force','max_speed')}

def compare(coarse,fine,threshold):
    metrics={}
    for key in ('tip_z','U','contact_area','normal_force'):
        a=coarse[key];b=np.interp(coarse['time'],fine['time'],fine[key]);absolute=float(np.max(np.abs(a-b)));scale=float(np.max(np.abs(b)))
        relative=absolute/scale if scale else (0 if absolute==0 else None)
        final=abs(float(a[-1]-b[-1]));final_scale=abs(float(b[-1]))
        metrics[key]=dict(max_absolute=absolute,trajectory_relative=relative,final_absolute=final,
                          final_relative=final/final_scale if final_scale else None,
                          trajectory_status='PASS' if relative is not None and relative<=threshold else 'FAIL')
    return metrics

def main():
    p=argparse.ArgumentParser();p.add_argument('campaign',type=Path);a=p.parse_args()
    cases={i:read(a.campaign/str(i)) for i in (1,2,4) if (a.campaign/str(i)/'journal.csv').exists()}
    pairs={f'{i}:{j}':compare(cases[i],cases[j],.001) for i,j in ((1,2),(1,4),(2,4)) if i in cases and j in cases}
    warnings={str(i):(a.campaign/str(i)/'process/stdout.log').read_text().count('Newton-Raphson method failed to converge') for i in cases}
    print(json.dumps(dict(source='Actual SOFA journals',time_threshold=.001,pairs=pairs,newton_failed_steps=warnings,
                         full_grasp='NOT RUN',energy_closure='BLOCKED'),indent=2))

if __name__=='__main__':main()
