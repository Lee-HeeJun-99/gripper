"""Preregister one load-sizing hypothesis from old measured prewithdrawal data.
Local secant is not a validated nonlinear prediction or structural-efficiency claim.
"""
import argparse,csv,json,subprocess
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[]
 for case,force in (('b3_railback_grasp1001298',1.5),('b3_railback_force_hold1306',2.)):
  src=BASE/'results'/case;objects=list(csv.DictReader((src/'object.csv').open()));t=np.array([float(r['time_s']) for r in objects]);index={x:i for i,x in enumerate(t)};skin=np.zeros((len(t),3));support=np.zeros_like(skin)
  with (src/'response_rows.csv').open() as f:
   for r in csv.DictReader(f):
    names=(r['model0'],r['model1'])
    if not any('/object/'in x for x in names):continue
    target=skin if any('/skinCollision/'in x for x in names) else support if any('/floor/'in x for x in names) else None
    if target is not None:target[index[float(r['time_s'])]]+=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ')[:3]/.0025
  win=(t>=.55-1e-12)&(t<=.65+1e-12);records.append(dict(case=case,force_N_per_cable=force,window_s=[.55,.65],samples=int(win.sum()),mean_Skin_Fz_N=float(skin[win,2].mean()),mean_Support_Fz_N=float(support[win,2].mean()),source_hashes={f:sha(src/f) for f in ('scene.scn','object.csv','response_rows.csv','summary.json')}))
 slope=(records[1]['mean_Skin_Fz_N']-records[0]['mean_Skin_Fz_N'])/.5;load=.1*9.81;reserve=.10;required=1.5+(load*(1+reserve)-records[0]['mean_Skin_Fz_N'])/slope;valid=slope>0 and 2.<required<=2.5
 d=dict(status='READY_SINGLE_LOAD_SIZING_HYPOTHESIS' if valid else 'BLOCKED_LOAD_BUDGET_RANGE',records=records,gravity_load_N=load,assumed_design_reserve_fraction=reserve,target_prewithdrawal_Skin_Fz_N=load*(1+reserve),local_secant_N_per_N=slope,proposed_force_N_per_cable=float(required),range_screen='2.5N railback no-object1129 positive savedvolumes for1s exists;NOT a monotonic stability guarantee. Actual candidate no-object Pilot still required. Not original2.5N interface model that inverted.',scope='ONE derived actuation-capacity experiment,NOT force/offset/dt sweep,not structural improvement,not motor specification. Old2NFAIL and2.5Noldinterfaceinversion preserved. Secant uses distinct actual dynamic shapes so is only a hypothesis. If rejected,no further increments in this family.',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
