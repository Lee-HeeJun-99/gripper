"""Exact axisymmetric torque-free reference vs saved actual Native finite rings.
Reference is mathematical,not another SOFA solver or a replacement trajectory.
"""
import argparse,csv,json,subprocess
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha,rotation

def read(p):return list(csv.DictReader(p.open()))
def vec(s):return np.fromstring(s,sep=' ')
def axisymmetric_state(t,L,n0,axial,transverse):
 if axial<=0 or transverse<=0 or abs(np.linalg.norm(n0)-1)>1e-12:raise ValueError('invalid physical reference inertia/axis')
 norm=np.linalg.norm(L)
 if norm==0:return n0.copy(),np.zeros(3),transverse*np.eye(3)+(axial-transverse)*np.outer(n0,n0)
 n=Rotation.from_rotvec(L/norm*(norm/transverse*t)).apply(n0);w=L/transverse+(1/axial-1/transverse)*(L@n0)*n;I=transverse*np.eye(3)+(axial-transverse)*np.outer(n,n);return n,w,I
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',default=['b3_finite_com_mapped_free572','b3_finite_com_mapped_half577','b3_finite_com_mapped_quarter578']);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[];summaries=[];references=[]
 for case in a.cases:
  src=BASE/'results'/case;meta=json.loads((src/'summary.json').read_text());case_records=[]
  for i in (0,1):
   initial=meta['initial'][i];R0=rotation(np.array(initial['q'])[3:]);w0=np.array(initial['v'])[3:];I0=np.array(initial['world_inertia_kg_m2']);B=R0.T@I0@R0;axial=B[0,0];transverse=(B[1,1]+B[2,2])/2
   if np.max(abs(B-np.diag([axial,transverse,transverse])))/np.linalg.norm(B)>1e-12:raise ValueError('reference requires an axisymmetric ring')
   n0=R0[:,0];L=I0@w0;Lnorm=np.linalg.norm(L);projection=L@n0;energy0=.5*w0@L
   def exact(t):
    return axisymmetric_state(t,L,n0,axial,transverse)
   max_L=0.;max_E=0.;max_FD=0.
   for t in np.linspace(0,.01,11):
    n,w,I=exact(t);max_L=max(max_L,float(np.linalg.norm(I@w-L)/Lnorm));max_E=max(max_E,float(abs(.5*w@I@w-energy0)/energy0));h=1e-7;derivative=(exact(t+h)[1]-exact(t-h)[1])/(2*h);expected=-np.linalg.solve(I,np.cross(w,I@w));max_FD=max(max_FD,float(np.linalg.norm(derivative-expected)))
   references.append(dict(case=case,body=i,reference='Exact torque-free axisymmetric rigid ring:axis rotates about conserved world L at |L|/Itransverse',momentum_relative_defect=max_L,energy_relative_defect=max_E,Euler_equation_FD_error_rad_s2=max_FD))
   for row in read(src/f'0/guide{i}.csv'):
    t=float(row['time_s']);q=vec(row['rigid_q']);w=vec(row['rigid_v'])[3:];nref,wref,Iref=exact(t);n=rotation(q[3:])[:,0];actualI=transverse*np.eye(3)+(axial-transverse)*np.outer(n,n);item=dict(case=case,body=i,time_s=t,actual_omega_world_rad_s=w.tolist(),exact_reference_omega_world_rad_s=wref.tolist(),omega_error_rad_s=float(np.linalg.norm(w-wref)),actual_axis_error=float(np.linalg.norm(n-nref)),actual_relative_angular_momentum_error=float(np.linalg.norm(actualI@w-L)/Lnorm),actual_rotational_energy_relative_error=float(abs(.5*w@actualI@w-energy0)/energy0));records.append(item);case_records.append(item)
  summaries.append(dict(case=case,dt_s=meta['dt_s'],maximum_omega_error_rad_s=max(r['omega_error_rad_s'] for r in case_records),maximum_relative_angular_error=max(r['actual_relative_angular_momentum_error'] for r in case_records),source_summary_sha256=sha(src/'summary.json')))
 result=dict(status='PASS_NATIVE_FREE_SPIN_ANGULAR_GATE_ONLY' if max(r['actual_relative_angular_momentum_error'] for r in records)<=.001 else 'FAIL_NATIVE_FREE_SPIN_VS_EXACT_REFERENCE',scope='Exact axisymmetric torque-free analytical reference compared with ACTUAL saved Native states. No replacement of simulation output,no new physics solver,no B3 qualification.',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),source_sha256=sha(Path(__file__)),references=references,cases=summaries,records=records)
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes())
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,axes=plt.subplots(1,2,figsize=(10,4))
 for case in summaries:
  rows=[r for r in records if r['case']==case['case'] and r['body']==0];t=[r['time_s']*1000 for r in rows];axes[0].plot(t,[r['omega_error_rad_s'] for r in rows],label=f"dt={case['dt_s']*1000:g}ms");axes[1].plot(t,[r['actual_relative_angular_momentum_error']*100 for r in rows])
 axes[0].set(xlabel='Time (ms)',ylabel='Actual Native omega - exact reference (rad/s)');axes[0].legend();axes[1].set(xlabel='Time (ms)',ylabel='Actual Native angular momentum error (%)');fig.suptitle('Actual Native finite ring / mass mapping vs analytical free-spin reference\n10mg assumed;no contact,cable,gravity;SDK26.06;source '+result['source_commit'][:12]);fig.tight_layout();fig.savefig(out/'actual_native_free_spin.png',dpi=160);plt.close(fig)
 print(json.dumps({k:v for k,v in result.items() if k not in ('records','references')},indent=2))
if __name__=='__main__':main()
