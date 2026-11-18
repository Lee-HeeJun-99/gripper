"""Analytic witness:valid initial tangent state need not yield valid RK stages.
No film model/acceptance gate is changed by this diagnostic.
"""
import argparse,json,math,shutil
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');rows=[];alpha=1.
 for dt in (1e-3,5e-4,2.5e-4):
  # Unit circle,q=(1,0),v=(0,1),a=(-1,alpha). Initial g=Jv=0,
  # Ja+v^T H v=0. With M=1e-6,F=(-2M,alpha*M),lambda=M>0.
  # The RK k2 TRIAL is q+=(dt/2)*v,v+=(dt/2)*a,NOT the exact
  # constrained trajectory. J(q_trial)v_trial has a nonzero O(dt^2) term.
  q=(1.,dt/2);v=(-dt/2,1+alpha*dt/2);radius=math.hypot(*q);observed=(q[0]*v[0]+q[1]*v[1])/radius;exact=alpha*dt*dt/(4*math.sqrt(1+dt*dt/4));rows.append(dict(dt_s=dt,trial_gap_mm=radius-1,trial_normal_velocity_mm_s=observed,analytic_trial_normal_velocity_mm_s=exact,absolute_formula_error=abs(observed-exact)))
 ratios=[rows[i]['trial_normal_velocity_mm_s']/rows[i+1]['trial_normal_velocity_mm_s'] for i in (0,1)];r=dict(status='PASS' if max(x['absolute_formula_error'] for x in rows)<1e-18 and all(abs(x-4)<1e-5 for x in ratios) else 'FAIL',scope='independent analytic RK internal-stage witness ONLY;NOT actual film or time-convergence PASS',physical_reference='circle radius1mm,M=1e-6Ns2/mm,F=(-2M,M)N,initial compressive lambda=M>0',initial_gap_mm=0.,initial_normal_velocity_mm_s=0.,initial_normal_acceleration_identity=0.,rows=rows,halving_error_ratios=ratios,interpretation='O(dt^2) off-manifold k2 predictor can trigger strict geometric guard without a true physical reimpact;consistent with1350/1352 factor4 but not proof of sole cause',old_trials='1350/1352 FAIL preserved',acceptance_gate_changed=False,source_sha256=sha(out/'runner.py'));write_json(out/'summary.json',r);print(json.dumps(r))
if __name__=='__main__':main()
