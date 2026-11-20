"""Actual Native compliant contact vs exact unilateral elastic oscillator.
Spring energy/force below are independent analytical evaluations,NOT native
getPotentialEnergy (unimplemented) or sampled addForce callback measurements.
"""
import argparse,csv,itertools,json,math
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def vec(s):return np.fromstring(s,sep=' ')
def reference(t,g0,u,m,k):
 birth=g0/u;w=math.sqrt(k/m);release=birth+math.pi/w
 if t<=birth:return g0-u*t,-u
 if t<release:return -u/w*math.sin(w*(t-birth)),-u*math.cos(w*(t-birth))
 return u*(t-release),u
def rel(x,y):
 a=abs(x-y);d=max(abs(x),abs(y));return dict(absolute_error=a,relative_error=a/d if d else 0.)
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='b3_native_penalty_snapshot665');p.add_argument('--purity-case',default='b3_native_penalty_plain666');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.case;meta=json.loads((src/'summary.json').read_text());data=[];cases=[];comparisons=[];purity=0.;m=meta['mass_kg'];k=meta['assumed_stiffness_N_per_m'];g0=meta['initial_buffered_gap_m'];u=-meta['initial_vz_m_s'];E0=m*u*u/2
 if meta['status']!='RUN_COMPLETED_NOT_PHYSICALLY_QUALIFIED':
  result=dict(status='BLOCKED_INCOMPLETE_OR_FAILED_NATIVE_INPUT',source_summary_sha256=sha(src/'summary.json'),producer_sha256=sha(Path(__file__)),scope='No physical/reference/time verdict computed from failed/partial Native run',actual_measurements=None);(out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result,indent=2));return
 for run in meta['records']:
  dt=run['dt_s'];name=format(dt,'.7f');rows=read(src/name/'rigid.csv');probe=read(src/name/'penalty.csv');control=read(BASE/'results'/a.purity_case/name/'rigid.csv');oldv=-u;entries=[]
  if len(rows)!=round(.02/dt) or len(control)!=len(rows) or len(probe)!=len(rows):raise ValueError('incomplete actual trajectory or field snapshot')
  first_t=float(rows[0]['time_s']);first_g=float(vec(rows[0]['rigid_q'])[2]-.0012)
  if first_t<g0/u and abs(first_g-(g0-u*first_t))>1e-12:
   result=dict(status='FAIL_PRECONTACT_KINEMATICS_NOT_TIME_QUALIFIED',source_summary_sha256=sha(src/'summary.json'),producer_sha256=sha(Path(__file__)),time_s=first_t,actual_gap_m=first_g,reference_force_free_gap_m=g0-u*first_t,scope='Native solver/animation-loop combination fails known free motion before contact. Identical frozen trajectories are not a physical time PASS.',common_time_gate_status='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result,indent=2));return
  actualks={float(r['ks_N_per_m']) for r in probe}
  if any(abs(x-k)/k>1e-12 for x in actualks):raise ValueError('actual Native penalty stiffness differs from analytical reference')
  for r,c,s in zip(rows,control,probe):
   for key in ('rigid_q','rigid_v','object_impulse_Ns_Nms'):purity=max(purity,float(np.max(abs(vec(r[key])-vec(c[key])))))
   t=float(r['time_s']);g=float(vec(r['rigid_q'])[2]-.0012);v=float(vec(r['rigid_v'])[2]);rg,rv=reference(t,g0,u,m,k);F=m*(v-oldv)/dt;oldv=v;E=.5*m*v*v+.5*k*min(g,0.)**2;entries.append(dict(time_s=t,actual_buffered_gap_m=g,actual_vz_m_s=v,analytical_gap_reference_m=rg,analytical_velocity_reference_m_s=rv,effective_force_INFERRED_from_momentum_N=F,analytical_accepted_spring_law_N=k*max(-g,0.),analytical_spring_energy_plus_actual_kinetic_J=E,stored_penetration_snapshot_m=float(s.get('stored_penetration_snapshot_m',s.get('last_evaluated_penetration_m'))),normal_force_callback_measurement=None))
  data.append(entries);cases.append(dict(dt_s=dt,maximum_gap_reference_error_m=max(abs(r['actual_buffered_gap_m']-r['analytical_gap_reference_m']) for r in entries),maximum_velocity_reference_error_m_s=max(abs(r['actual_vz_m_s']-r['analytical_velocity_reference_m_s']) for r in entries),maximum_reconstructed_energy_relative_defect=max(abs(r['analytical_spring_energy_plus_actual_kinetic_J']-E0)/E0 for r in entries),minimum_inferred_effective_force_N=min(r['effective_force_INFERRED_from_momentum_N'] for r in entries),stored_penetration_snapshot_nonzero_count=sum(r['stored_penetration_snapshot_m']!=0 for r in entries),actual_frames=entries))
 for i,j in itertools.combinations(range(3),2):
  ratio=round(meta['records'][i]['dt_s']/meta['records'][j]['dt_s'])
  for n,x in enumerate(data[i]):
   y=data[j][(n+1)*ratio-1]
   if abs(x['time_s']-y['time_s'])>1e-12:raise ValueError('nonmatching clocks')
   for quantity in ('actual_buffered_gap_m','actual_vz_m_s','analytical_spring_energy_plus_actual_kinetic_J','effective_force_INFERRED_from_momentum_N'):
    comparisons.append(dict(dt_pair_s=[meta['records'][i]['dt_s'],meta['records'][j]['dt_s']],time_s=x['time_s'],quantity=quantity,**rel(x[quantity],y[quantity])))
 result=dict(status='NATIVE_PENALTY_REFERENCE_DIAGNOSTIC_ONLY',scope='Verified actual ks=100N/m and pure read-only observer. Exact conservative unilateral spring reference,NOT same model as661 e=0. End-of-step contact snapshots are reset by addContact and are NOT last force evaluations. Momentum-inferred effective force is explicitly not measured addForce. Native potential energy API is unimplemented;reconstructed inventory is NOT global energy certification.',producer_sha256=sha(Path(__file__)),source_summary_sha256=sha(src/'summary.json'),strict_observer_state_error=purity,strict_observer_state_pass=purity<=1e-12,reference_contact_birth_s=g0/u,reference_release_s=g0/u+math.pi/math.sqrt(k/m),reference_initial_kinetic_J=E0,cases=cases,common_time_gate=.001,common_time_gate_status='PASS' if max(r['relative_error'] for r in comparisons)<=.001 else 'FAIL',worst=max(comparisons,key=lambda r:r['relative_error']),comparisons=comparisons)
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({**{k:v for k,v in result.items() if k not in ('cases','comparisons')},'cases':[{k:v for k,v in r.items() if k!='actual_frames'} for r in cases]},indent=2))
if __name__=='__main__':main()
