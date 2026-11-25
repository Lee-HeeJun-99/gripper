"""Separate actual impulse work, geometric constant-tension work and BE loss."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from cable_phase_coupon import matrix

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/cable_phase1825';d=json.loads((src/'summary.json').read_text());mass=d['assumptions']['mass_per_point_kg'];T=d['assumptions']['tension_N'];dt=d['assumptions']['dt_s'];rows=list(csv.DictReader((src/'observed/phases.csv').open()));records=[]
 def length(q):return float(np.linalg.norm(np.diff(np.vstack([np.zeros(3),q]),axis=0),axis=1).sum())
 for k in range(5):
  phase={r['phase']:r for r in rows if int(r['step'])==k};b=phase['build_end'];e=phase['accepted_end'];s=phase['solve_end'];q=np.fromstring(b['q'],sep=' ').reshape(-1,3);qn=np.fromstring(e['q'],sep=' ').reshape(-1,3);v=np.fromstring(b['v'],sep=' ').reshape(-1,3);vn=np.fromstring(e['v'],sep=' ').reshape(-1,3);J=matrix(b['J'],3);lam=float(s['lambda_Ns'])
  actual_work=float((lam*J*vn).sum());geometric_work=-T*(length(qn)-length(q));loss=.5*mass*float(((vn-v)**2).sum());kinetic=.5*mass*float((vn**2-v**2).sum());gap=actual_work-geometric_work
  residual=kinetic-geometric_work-(gap-loss);assert abs(residual)<=1e-12
  records.append(dict(step=k,frozen_row_accepted_work_J=actual_work,geometric_constant_tension_work_J=geometric_work,convex_length_linearization_excess_J=gap,backward_Euler_kinetic_loss_J=loss,kinetic_increment_J=kinetic,delta_kinetic_plus_constant_tension_potential_J=kinetic-geometric_work,energy_decomposition_residual_J=residual))
 result=dict(status='PASS_EXACT_COUPON_WORK_DECOMPOSITION_NOT_ENERGY_CONSERVATION',records=records,maximum_balance_residual_J=max(abs(r['energy_decomposition_residual_J']) for r in records),positive_physical_energy_increment_steps=sum(r['delta_kinetic_plus_constant_tension_potential_J']>0 for r in records),input_sha256={str(f.relative_to(BASE)):sha(f) for f in [src/'summary.json',src/'observed/phases.csv']},source_sha256=sha(Path(__file__)),scope='Fixed pullPoint, positive constant tension, no other external load: U=T*L. Actual previous-state cable row supplies frozen linear work, not exact geometric potential change. BE loss and convex length gap are separated; no global B3 energy/convergence claim or permission to alter Raw/SDK. This is independent analysis of a deliberately finite-motion coupon, not representative B3 error magnitude.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result,indent=2))
if __name__=='__main__':main()
