"""Independent elastic reference AND discrete equation tests of actual Native q/v.
No interpolation/floors or accepting solver convergence messages as physics proof.
"""
import argparse,csv,itertools,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_penalty_assess import reference,rel
def read(p):return list(csv.DictReader(p.open()))
def vec(s):return np.fromstring(s,sep=' ')
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);cases=[];comparisons=[];data={};m=.001;k=100.;g0=.000015;u=.01;E0=m*u*u/2
 for case in ('b3_native_plane_force682','b3_native_plane_newmark683'):
  src=BASE/'results'/case;meta=json.loads((src/'summary.json').read_text())
  if meta['status']!='NATIVE_SURROGATE_RUN_COMPLETED_NOT_PHYSICALLY_QUALIFIED':raise ValueError('partial/failed Native case is not a reference')
  for run in meta['records']:
   mode=run['mode'];h=run['dt_s'];rows=read(src/(mode+'_'+format(h,'.7f'))/'probe.csv.point.csv');qold=.001215;vold=-u;qolder=None;volder=None;records=[]
   for r in rows:
    t=float(r['time_s']);q=float(vec(r['q'])[2]);v=float(vec(r['v'])[2]);g=q-.0012;F=k*max(-g,0.);rg,rv=reference(t,g0,u,m,k)
    if mode=='bdf2' and qolder is not None:qr=(1.5*q-2*qold+.5*qolder)/h-v;fr=m*(1.5*v-2*vold+.5*volder)/h-F;formula='standard BDF2 first-order q/v system'
    elif mode=='newmark':an=k*max(.0012-qold,0.)/m;anew=2*(v-vold)/h-an;qr=(q-qold-h*vold-h*h/4*(an+anew))/h;fr=m*anew-F;formula='nonlinear Newmark gamma=.5,beta=.25 using physical previous acceleration'
    else:qr=(q-qold)/h-v;fr=m*(v-vold)/h-F;formula='nonlinear backward Euler'
    E=m*v*v/2+k*min(g,0.)**2/2;records.append(dict(time_s=t,gap_m=g,velocity_m_s=v,Native_force_slot_N=float(vec(r['force_slot'])[2]),independent_accepted_spring_law_N=F,reference_gap_m=rg,reference_velocity_m_s=rv,independent_energy_inventory_J=E,discrete_reference_formula=formula,position_equation_residual_m_s=qr,dynamic_equation_residual_N=fr,Native_Newton_status=r['Newton_status']));qolder,qold=qold,q;volder,vold=vold,v
   data.setdefault(mode,[]).append((h,records));cases.append(dict(case=case,mode=mode,dt_s=h,source_summary_sha256=sha(src/'summary.json'),maximum_gap_reference_error_m=max(abs(r['gap_m']-r['reference_gap_m']) for r in records),maximum_velocity_reference_error_m_s=max(abs(r['velocity_m_s']-r['reference_velocity_m_s']) for r in records),maximum_independent_energy_relative_defect=max(abs(r['independent_energy_inventory_J']-E0)/E0 for r in records),maximum_position_equation_residual_m_s=max(abs(r['position_equation_residual_m_s']) for r in records),maximum_dynamic_equation_residual_N=max(abs(r['dynamic_equation_residual_N']) for r in records),actual_records=records))
 for mode,streams in data.items():
  for (h,x),(dt,y) in itertools.combinations(streams,2):
   ratio=round(h/dt)
   for n,r in enumerate(x):
    s=y[(n+1)*ratio-1]
    if abs(r['time_s']-s['time_s'])>1e-12:raise ValueError('common Native output clock mismatch')
    for quantity in ('gap_m','velocity_m_s','independent_energy_inventory_J'):
     comparisons.append(dict(mode=mode,dt_pair_s=[h,dt],time_s=r['time_s'],quantity=quantity,**rel(r[quantity],s[quantity])))
 result=dict(status='ACTUAL_NATIVE_ODE_REFERENCE_DIAGNOSTIC',scope='Same unilateral PlaneForceField research surrogate,NOT collision/rigid/cable/B3 qualification. Native force SLOT is a snapshot,not assumed an addForce evaluation at accepted q. Analytical spring inventory is separately reconstructed;Native potential API unimplemented. Algebraic equations tested separately in m/s and N,no mixed-unit norms.',producer_sha256=sha(Path(__file__)),cases=cases,time_gate=.001,time_worst_by_mode={mode:max((r for r in comparisons if r['mode']==mode),key=lambda r:r['relative_error']) for mode in data},time_gate_by_mode={mode:all(r['relative_error']<=.001 for r in comparisons if r['mode']==mode) for mode in data},comparisons=comparisons)
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes())
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,axes=plt.subplots(1,3,figsize=(13,3.8))
 for mode,streams in data.items():
  h,records=streams[-1];times=np.array([r['time_s'] for r in records]);axes[0].plot(times*1000,[r['gap_m']*1e6 for r in records],label=mode);axes[1].plot(times*1000,[r['velocity_m_s']*1000 for r in records]);axes[2].plot(times*1000,[(r['independent_energy_inventory_J']/E0-1)*100 for r in records])
 t=np.linspace(0,.02,1000);ref=np.array([reference(x,g0,u,m,k) for x in t]);axes[0].plot(t*1000,ref[:,0]*1e6,'k--',label='analytical elastic reference');axes[1].plot(t*1000,ref[:,1]*1000,'k--');axes[0].legend(fontsize=7);axes[0].set(ylabel='Buffered gap (um)');axes[1].set(ylabel='Normal velocity (mm/s)');axes[2].set(ylabel='Reconstructed energy defect (%)')
 for ax in axes:ax.set(xlabel='Actual Native time (ms)')
 fig.suptitle('Actual Native PlaneForceField / 1g / 100N/m assumed / dt62.5us\nSDK26.06;not B3/contact certification;source '+json.loads((BASE/'results/b3_native_plane_force682/summary.json').read_text())['source_commit'][:12]);fig.tight_layout();fig.savefig(out/'actual_native_ode_comparison.png',dpi=160);plt.close(fig)
 print(json.dumps({**{k:v for k,v in result.items() if k not in ('cases','comparisons')},'cases':[{k:v for k,v in r.items() if k!='actual_records'} for r in cases]},indent=2))
if __name__=='__main__':main()
