"""Preserve incomplete force-sensitivity data without fabricating Holding verdict."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results/b3_mass100_force25_1101';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);rows=list(csv.DictReader((src/'object.csv').open()));q=np.array([np.fromstring(r['rigid_q'],sep=' ') for r in rows]);v=np.array([np.fromstring(r['rigid_v'],sep=' ') for r in rows]);iters=np.array([int(r['solver_iterations']) for r in rows]);records=[]
 for f in range(3):
  rs=list(csv.DictReader((src/f'finger{f}.csv').open()));records.append(dict(finger=f,outputs=len(rs),last_time_s=float(rs[-1]['time_s']),maximum_actual_command_N=max(float(r['command_N']) for r in rs),last_actual_command_N=float(rs[-1]['command_N'])))
 d=dict(status='PARTIAL_FORCE_DIAGNOSTIC_HOLDING_NOT_RUN',object_outputs=len(rows),last_time_s=float(rows[-1]['time_s']),maximum_object_upward_from_initial_mm=float((q[:,2]+.065).max()*1000),maximum_object_speed_mm_s=float(np.linalg.norm(v[:,:3],axis=1).max()*1000),iteration_limited_outputs=int(sum(iters>=1000)),maximum_reported_solver_error=max(float(r['solver_error']) for r in rows),records=records,physical_validation='NOT QUALIFIED',scope='NoRoot/Palm motion was commanded;upward object motion is NOT a Lift result. Partial data cannot establish eventual Holding,escape or reliable force-capacity. Cost cancellation is not physical FAIL or OS exhaustion.',input_hashes={str(f.relative_to(BASE)):sha(f) for f in [src/'summary.json',src/'object.csv',src/'force_protocol.json',src/'preflight.json',Path(__file__)]})
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
