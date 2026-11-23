"""Interpret actual exploration without attributing numerical failure to design."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 meta=json.loads((src/'summary.json').read_text());rows=list(csv.DictReader((src/'object.csv').open()));t=np.array([float(r['time_s']) for r in rows]);err=np.array([float(r['solver_error']) for r in rows]);it=np.array([int(r['solver_iterations']) for r in rows]);hold=(t>=1.6-1e-12)&(t<=2+1e-12)
 records=[]
 for f in range(3):
  rs=list(csv.DictReader((src/f'finger{f}.csv').open()));cmd=np.array([float(r['command_N']) for r in rs]);force=np.array([[float(r['cable0_force_raw']),float(r['cable1_force_raw'])] for r in rs]);short=np.array([[float(r['cable0_displacement_m']),float(r['cable1_displacement_m'])] for r in rs]);records.append(dict(finger=f,hold_command_N=[float(cmd[hold].min()),float(cmd[hold].max())],hold_reported_impulse_over_dt_N_range=[float((force[hold]/meta['dt_s']).min()),float((force[hold]/meta['dt_s']).max())],hold_internal_cable_shortening_mm_range=[float(short[hold].min()*1000),float(short[hold].max()*1000)],geometric_shortening='NOT RECOMPUTED_BY_THIS_AUDIT'))
 d=dict(status='EXPLORATORY_SOLVER_LIMIT_REVIEW' if np.any(it>=1000) else 'EXPLORATORY_DIAGNOSTIC_ONLY',case=a.case,all_output_solver_max_error=float(err.max()),hold_solver_max_error=float(err[hold].max()),all_outputs_at_or_above_iteration_limit=int(np.sum(it>=1000)),hold_outputs_at_or_above_iteration_limit=int(np.sum(it[hold]>=1000)),hold_outputs=int(hold.sum()),first_limit_time_s=float(t[it>=1000][0]) if np.any(it>=1000) else None,cables=records,interpretation='Native solver iteration-limit evidence prevents attributing lost holding solely to friction, stiffness or normal direction. No tolerance change or force increase adopted. Need a bounded actual failing-state contact/cable coupling diagnostic; not a repeat dt/alarm sweep.',physical_validation='NOT QUALIFIED',numerical_convergence='EXISTING_FAIL_NOT_RETESTED',input_hashes={f.name:sha(f) for f in [src/'summary.json',src/'object.csv',*[src/f'finger{f}.csv' for f in range(3)]]},producer_sha256=sha(Path(__file__)))
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
