"""BVP-seeded discrete equilibrium: initialization contrast, not guide identification."""
import shutil
from pathlib import Path
import numpy as np
from scipy.integrate import solve_bvp
from scipy.optimize import root
from baseline_registry import ROOT, REPO, dump, ref, sha
from extensible_rod_reference import section
import json

def main():
 if (ROOT/'runtime/STOP').exists(): raise SystemExit('STOP')
 out=ROOT/'validation/finger/axial_seed1';out.mkdir(parents=True,exist_ok=False)
 shutil.copyfile(__file__,out/'producer.py')
 inputs=[ref(Path(__file__)),ref(ROOT/'scripts/extensible_rod_reference.py'),ref(ROOT.parent/'stage2_load_transfer/scripts/finger_structure.py'),ref(ROOT/'validation/finger/axial_boundary1/summary.json')]
 criteria=dict(tip_relative_max=.001,reaction_relative_max=.001,residual_Nm_max=1e-10,axial_gap_m_max=1e-10)
 dump(out/'inputs.json',dict(inputs=inputs,criteria=criteria,contract='Same x_tip=L counterfactual, root fixed, dead Fy, zero tip moment. Only initializer changes from zero to independent continuous BVP.',predeclared='One BVP and one root solve per body/load/mesh; no retry, no tolerance change. Finest comparison and ALL equilibrium checks required.'))
 old=json.loads((ROOT/'validation/finger/axial_boundary1/summary.json').read_text());rows=[]
 for previous in old['rows']:
  if (ROOT/'runtime/STOP').exists():raise SystemExit('STOP')
  body=previous['body'];L=previous['L_m'];F=previous['force_N']
  def ode(s,z,p):
   EA,EI=section(body,s);t=z[2];e=(p[0]*np.cos(t)+F*np.sin(t))/EA
   return np.array([(1+e)*np.cos(t),(1+e)*np.sin(t),z[3]/EI,(1+e)*(p[0]*np.sin(t)-F*np.cos(t))])
  def bc(a,b,p):return np.array([a[0],a[1],a[2],b[3],b[0]-L])
  s=np.linspace(0,L,101);z=np.zeros((4,len(s)));z[0]=s
  b=solve_bvp(ode,bc,s,z,p=[0.],tol=1e-10,max_nodes=10000)
  ds=[]
  for n in (16,32,64):
   h=L/n;EA,EI=section(body,(np.arange(n)+.5)*h)
   def fields(z):
    th=np.r_[0,z[:-1]];a=(th[:-1]+th[1:])/2;N=z[-1];e=(N*np.cos(a)+F*np.sin(a))/EA
    g=np.zeros(n+1);bend=EI*np.diff(th)/h;c=-h*(-N*np.sin(a)+F*np.cos(a))*(1+e)/2
    g[:-1]+=-bend+c;g[1:]+=bend+c
    r=np.cumsum(h*(1+e)[:,None]*np.column_stack((np.cos(a),np.sin(a))),axis=0)
    return th,e,g[1:],r
   def fun(z):
    th,e,g,r=fields(z);return np.r_[g/(abs(F)*L),(r[-1,0]-L)/L]
   seed=np.r_[b.sol(np.linspace(0,L,n+1))[2,1:],b.p[0]]
   sol=root(fun,seed,tol=1e-9);th,e,g,r=fields(sol.x)
   U=float(np.sum(h*(EA*e**2+EI*(np.diff(th)/h)**2)/2))
   ok=bool(sol.success and max(abs(g))<=1e-10 and abs(r[-1,0]-L)<=1e-10)
   ds.append(dict(n=n,success=bool(sol.success),message=str(sol.message),nfev=int(sol.nfev),accepted=ok,axial_reaction_N=float(sol.x[-1]),tip_m=r[-1].tolist(),theta_rad=th.tolist(),strain=e.tolist(),r_m=r.tolist(),stored_energy_J=U,residual_Nm=float(max(abs(g))),axial_gap_m=float(r[-1,0]-L),seed_residual_max=float(max(abs(fun(seed))))))
  tip=abs(ds[-1]['tip_m'][1]/b.y[1,-1]-1);reaction=abs(ds[-1]['axial_reaction_N']/b.p[0]-1)
  ok=b.success and all(d['accepted'] for d in ds) and tip<=.001 and reaction<=.001
  rows.append(dict(body=body,L_m=L,force_N=F,reference=dict(success=bool(b.success),tip_m=b.y[:2,-1].tolist(),axial_reaction_N=float(b.p[0]),max_rms_residual=float(max(b.rms_residuals))),refinements=ds,tip_relative_error=tip,reaction_relative_error=reaction,status='PASS' if ok else 'FAIL',original_zero_seed_success_count=sum(d['success'] for d in previous['refinements'])))
 hashes=all(sha(REPO/i['path'])==i['SHA256'] for i in inputs);passed=hashes and all(r['status']=='PASS' for r in rows)
 dump(out/'summary.json',dict(status='SEEDED_BOUNDARY_REFERENCE_PASS' if passed else 'FAIL',scope='INITIALIZATION CONTRAST ONLY; SAME COUNTERFACTUAL BOUNDARY',rows=rows,inputs=ref(out/'inputs.json'),input_hashes_verified=hashes,criteria=criteria,whole_system_release=False,limitations=['No proof of branch uniqueness or stability','No actual guide/contact/strength/global energy qualification','Original zero-seed failures remain unchanged; RevAA adopted']))
 print([(r['body'],r['force_N'],r['status'],r['tip_relative_error'],r['reaction_relative_error']) for r in rows]);raise SystemExit(0 if passed else 2)
if __name__=='__main__':main()
