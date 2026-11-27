"""Conditional AO rail dead-load beam-column: actual archived STEP-derived sections.
Not assembly dynamics: no terminal/drive/PET mass, connector or follower load.
"""
import json, shutil, math
from pathlib import Path
import numpy as np
from scipy.linalg import eigh
from baseline_registry import ROOT, REPO, ref, sha, dump

def main():
 assert not (ROOT/'runtime/STOP').exists()
 out=ROOT/'validation/integrated/batch6_chain_stability2';out.mkdir(exist_ok=False)
 shutil.copyfile(__file__,out/'producer.py')
 src=ROOT/'validation/finger/batch6_actual_specimen3/summary.json';d=json.loads(src.read_text());ip=REPO/d['inputs']['path'];assert sha(ip)==d['inputs']['SHA256'];inputs=json.loads(ip.read_text())
 for r in [inputs['candidate'],*inputs['parts'].values(),d['producer']]:assert sha(REPO/r['path'])==r['SHA256']
 dump(out/'inputs.json',dict(reference=ref(src),reference_inputs=ref(ip),parts=inputs['parts'],candidate=inputs['candidate'],producer=ref(out/'producer.py'),numpy=np.__version__,thresholds=dict(buckling_relative=1e-5,frequency_relative=1e-5,beamcolumn_relative=1e-4,residual_N=1e-8),contract='Fixed-root, free-tip straight projected AO rail pair, uniform section from archived actual STEP cuts. Prescribed spatial DEAD compressive force; Euler Bernoulli initial-stress tangent. Typical E193GPa and density7930kg/m3 conditional. No terminal eccentric-force variation/follower, PET, connector, motor, damping or full-system certification.'))
 L=d['L_mm'];A=d['combined_A_mm2'];EI=d['E_N_mm2']*d['combined_Iyy_mm4'];rho=7.93e-6/1000
 F,M,N=d['equivalent_tip_wrench_N_Nmm'];P=-N;assert P>0
 euler=math.pi**2*EI/(4*L*L);beta=1.875104068711961;omega=beta**2*math.sqrt(EI/(rho*A*L**4))
 k=math.sqrt(P/EI);sec=1/math.cos(k*L)
 exact=[F/P*(math.tan(k*L)/k-L)+M/P*(sec-1), F/P*(sec-1)+M/math.sqrt(P*EI)*math.tan(k*L)]
 states=[]
 for n in (8,16,32,64):
  assert not (ROOT/'runtime/STOP').exists()
  h=L/n;K=np.zeros((2*n+2,2*n+2));G=K.copy();mass=K.copy()
  ke=EI/h**3*np.array([[12,6*h,-12,6*h],[6*h,4*h*h,-6*h,2*h*h],[-12,-6*h,12,-6*h],[6*h,2*h*h,-6*h,4*h*h]])
  ge=1/(30*h)*np.array([[36,3*h,-36,3*h],[3*h,4*h*h,-3*h,-h*h],[-36,-3*h,36,-3*h],[3*h,-h*h,-3*h,4*h*h]])
  me=rho*A*h/420*np.array([[156,22*h,54,-13*h],[22*h,4*h*h,13*h,-3*h*h],[54,13*h,156,-22*h],[-13*h,-3*h*h,-22*h,4*h*h]])
  for j in range(n):
   ix=np.ix_(range(2*j,2*j+4),range(2*j,2*j+4));K[ix]+=ke;G[ix]+=ge;mass[ix]+=me
  K=K[2:,2:];G=G[2:,2:];mass=mass[2:,2:];f=np.zeros(2*n);f[-2:]=[F,M];T=K-P*G;u=np.linalg.solve(T,f)
  cr=float(eigh(K,G,subset_by_index=[0,0])[0][0]);w0=float(np.sqrt(eigh(K,mass,subset_by_index=[0,0])[0][0]));w=float(np.sqrt(eigh(T,mass,subset_by_index=[0,0])[0][0]));above=float(eigh(K-1.01*euler*G,mass,subset_by_index=[0,0])[0][0])
  states.append(dict(n=n,buckling_N=cr,omega0_rad_s=w0,omega_loaded_rad_s=w,above_euler_omega_squared=above,tip=u[-2:].tolist(),u=u.tolist(),residual_N=float(max(abs(T@u-f))),bending_energy_Nmm=float(.5*u@K@u),geometric_potential_Nmm=float(-.5*P*u@G@u),external_potential_Nmm=float(-f@u),stationary_energy_residual_Nmm=float(u@T@u-f@u)))
 finest=states[-1];checks=dict(buckling=abs(finest['buckling_N']/euler-1)<1e-5,frequency=abs(finest['omega0_rad_s']/omega-1)<1e-5,static_beamcolumn=max(abs(np.array(finest['tip'])/exact-1))<1e-4,residual=max(s['residual_N'] for s in states)<1e-8,unstable_control=all(s['above_euler_omega_squared']<0 for s in states),compression_softens=all(s['omega_loaded_rad_s']<s['omega0_rad_s'] for s in states))
 dump(out/'summary.json',dict(status='CONDITIONAL_AO_DEAD_LOAD_STABILITY_REFERENCE_VERIFIED' if all(checks.values()) else 'REFERENCE_FAIL',inputs=ref(out/'inputs.json'),checks={k:bool(v) for k,v in checks.items()},L_mm=L,A_mm2=A,EI_Nmm2=EI,density_kg_m3=7930,diagnostic_tension_N=.001,compression_N=P,euler_compression_N=euler,conditional_euler_tension_N=euler/(P/.001),unloaded_omega_rad_s=omega,analytic_tip=exact,linear_tip=[d['exact']['tip_x_mm'],d['exact']['tip_rotation_rad']],states=states,whole_system_release=False,actual_capacity_qualified=False,actual_demand_N=None,warning='Euler bifurcation of this ideal dead-load reference is NOT installed buckling capacity, demand or force cap. Geometric potential is external-load potential, not stored material energy. Frequencies omit all non-Rail mass and are not product resonance predictions.'))
 print(json.dumps(checks,default=bool));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
