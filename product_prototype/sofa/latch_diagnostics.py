"""Read-only initial/default purity, actual input switch and curved cable errors."""
import argparse,csv,json,subprocess
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='latch_single1450');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.case;latch=read(src/'latch0.csv');first=next(i for i,r in enumerate(latch) if int(r['latched']));maximum=0.;peak=0.
 for i in range(1 if json.loads((src/'summary.json').read_text())['single'] else 3):
  for r in read(src/f'latch{i}.csv'):
   if int(r['latched']):maximum=max(maximum,*[abs(float(r[f'target{j}_m'])-float(r[f'geometric{j}_m'])) for j in range(2)]);peak=max(peak,*[abs(float(r[f'force{j}_Ns']))/.0025 for j in range(2)])
 pure={};single=json.loads((src/'summary.json').read_text())['single'];base=BASE/'results'/('opposed_control_mid1393' if single else 'b3_railback_grasp1001298')
 for name in ('finger0.csv','guide_frames0.csv','skin_points0.csv','rail_points0.csv'):
  before=read(base/name);after=read(src/name);n=min(first,len(before),len(after));pure[name]=dict(rows=n,exact=before[:n]==after[:n])
 old=read(BASE/'results/cable_latch_control1443/states.csv');new=read(BASE/'results/cable_latch_initialized1449/states.csv');n=sum(float(r['time_s'])<.1 for r in old);coupon_prefix=old[:n]==new[:n];result=dict(status='LATCH_INPUT_AND_PURITY_INVENTORY_ONLY',case=a.case,first_active_accepted_time_s=float(latch[first]['time_s']),first_previous_accepted_time_s=float(latch[first-1]['time_s']) if first else 0,first_targets_m=[float(latch[first][f'target{j}_m']) for j in range(2)],maximum_geometric_hold_error_m=maximum,geometric_hold_error_le_1e12_m=bool(maximum<=1e-12),maximum_emergent_cable_force_N=peak,prefix= pure,straight_coupon_prefix_rows=n,straight_coupon_prefix_exact=coupon_prefix,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),input_hashes={f:sha(src/f) for f in ('scene.scn','preflight.json','summary.json','latch0.csv','finger0.csv')},scope='Target read frompreviousaccepted actualpath;publicNativeinput only. Strict1e−12 geometricaccuracy inventory is not relaxed or equated to functional grasp. Emergent CableλNs/dt,not commandedforce afterlatch. Pre-override originalcommand fields must not be used as actual input. Default-prefix equality is reproducibility,not timeconvergence. No grasp or physicalqualification from this inventory.');(out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result,indent=2))
if __name__=='__main__':main()
