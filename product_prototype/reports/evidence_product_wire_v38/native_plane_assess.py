"""Exact decimal Native gap/dt recurrence vs separately specified impact law.
Do not mistake exact momentum/endpoint position for post-impact velocity accuracy.
"""
import argparse,itertools,json
from decimal import Decimal
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def relative(a,b):
 absolute=abs(a-b);den=max(abs(a),abs(b));return dict(absolute_error=absolute,relative_error=absolute/den if den else 0.)
def discrete(gap,velocity,dt,count,mass):
 g=Decimal(str(gap));v=Decimal(str(velocity));h=Decimal(str(dt));m=Decimal(str(mass));out=[]
 for k in range(count):
  nextv=max(v,-g/h);imp=m*(nextv-v);g+=h*nextv;out.append(dict(gap_m=float(g),vz_m_s=float(nextv),impulse_Ns=float(imp)));v=nextv
 return out
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_native_plane_policy661';meta=json.loads((src/'summary.json').read_text());records=[];checks=[];m=meta['mass_kg'];initial_v=meta['initial_velocity_m_s'];g=meta['initial_buffered_gap_m'];event=meta['analytic_reference_event_s']
 for run in meta['records']:
  exact=discrete(g,initial_v,run['dt_s'],len(run['frames']),m);error={key:max(abs(float(actual[field])-ref[key]) for actual,ref in zip(run['frames'],exact)) for key,field in (('gap_m','actual_buffered_gap_m'),('vz_m_s','actual_vz_m_s'),('impulse_Ns','actual_normal_impulse_Ns'))};checks.append(dict(mode=run['mode'],dt_s=run['dt_s'],exact_decimal_gap_over_dt_recurrence_API_error=error,strict_API_pass=max(error.values())<=1e-12,actual_final_kinetic_J=.5*m*run['frames'][-1]['actual_vz_m_s']**2,total_algorithmic_kinetic_decrease_J=.5*m*(initial_v**2-run['frames'][-1]['actual_vz_m_s']**2),instantaneous_e0_reference_energy_loss_J=.5*m*initial_v**2,maximum_velocity_reference_error_m_s=run['maximum_velocity_reference_error_m_s']))
 for mode in ('position_first','velocity_first'):
  cases=[r for r in meta['records'] if r['mode']==mode]
  for x,y in itertools.combinations(cases,2):
   ratio=round(x['dt_s']/y['dt_s']);cumul_x=0.;cumul_y=np.cumsum([r['actual_normal_impulse_Ns'] for r in y['frames']])
   for k,r in enumerate(x['frames']):
    s=y['frames'][(k+1)*ratio-1];t=r['time_s'];cumul_x+=r['actual_normal_impulse_Ns']
    if abs(t-s['time_s'])>1e-12:raise ValueError('nonmatching actual output time')
    quantities=dict(displacement_m=(r['actual_z_m']-(meta['sphere_radius_m']+meta['contact_buffer_m']+g),s['actual_z_m']-(meta['sphere_radius_m']+meta['contact_buffer_m']+g)),normal_velocity_m_s=(r['actual_vz_m_s'],s['actual_vz_m_s']),equivalent_force_N=(r['actual_normal_impulse_Ns']/x['dt_s'],s['actual_normal_impulse_Ns']/y['dt_s']),cumulative_impulse_Ns=(cumul_x,cumul_y[(k+1)*ratio-1]),kinetic_energy_J=(.5*m*r['actual_vz_m_s']**2,.5*m*s['actual_vz_m_s']**2))
    for name,(u,v) in quantities.items():records.append(dict(mode=mode,dt_pair_s=[x['dt_s'],y['dt_s']],time_s=t,quantity=name,**relative(u,v)))
 invariance=max(abs(x[field]-y[field]) for a,b in zip(meta['records'][:3],meta['records'][3:]) for x,y in zip(a['frames'],b['frames']) for field in ('actual_z_m','actual_vz_m_s','actual_normal_impulse_Ns'))
 result=dict(status='PASS_NATIVE_DISCRETE_RECURRENCE_NOT_IMPACT_OR_TIME' if all(r['strict_API_pass'] for r in checks) else 'FAIL_DISCRETE_REFERENCE',scope='Exact decimal unilateral gap/dt recurrence/reference API only. Actual Native velocity/reference and all-common-time Gate remain separately failed. No floors,interpolation,zero exclusions or algorithmic-loss-as-heat claims.',producer_sha256=sha(Path(__file__)),source_summary_sha256=sha(src/'summary.json'),analytic_inelastic_reference_event_s=event,reference_checks=checks,velocity_first_vs_position_first_max_absolute_difference=invariance,time_gate=.001,time_gate_status='PASS' if max(r['relative_error'] for r in records)<=.001 else 'FAIL',time_worst=max(records,key=lambda r:r['relative_error']),time_records=records)
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in result.items() if k!='time_records'},indent=2))
if __name__=='__main__':main()
