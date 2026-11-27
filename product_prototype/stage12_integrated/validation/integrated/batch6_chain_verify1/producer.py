"""Independent Gauss weak-form reconstruction and continuous shooting check."""
import json, shutil
import numpy as np
from scipy.linalg import expm
from baseline_registry import ROOT,REPO,sha,ref,dump

def main():
 assert not (ROOT/'runtime/STOP').exists()
 out=ROOT/'validation/integrated/batch6_chain_verify1';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 p=ROOT/'validation/integrated/batch6_chain_stability1/summary.json';d=json.loads(p.read_text());r=d['inputs'];assert sha(REPO/r['path'])==r['SHA256'];inp=json.loads((REPO/r['path']).read_text())
 for r in [inp['reference'],inp['reference_inputs'],inp['candidate'],inp['producer'],*inp['parts'].values()]:assert sha(REPO/r['path'])==r['SHA256']
 old=json.loads((REPO/inp['reference']['path']).read_text());F,M,N=old['equivalent_tip_wrench_N_Nmm'];P=-N;EI=d['EI_Nmm2'];L=d['L_mm'];rho=d['density_kg_m3']*1e-12
 # State y,theta,bending moment, shear: EI*y''''+P*y''=0.
 B=np.array([[0,1,0,0],[0,0,1/EI,0],[0,0,0,1],[0,0,-P/EI,0.]])
 E=expm(B*L);bc=np.vstack([E[2,2:],E[3,2:]+P*E[1,2:]])
 init=np.linalg.solve(bc,[M,-F]);tip=E@np.r_[0.,0.,init]
 residual=[];energy=[];modal=[];negative_control=[]
 x,w=np.polynomial.legendre.leggauss(4)
 for state in d['states']:
  n=state['n'];h=L/n;size=2*n+2;K=np.zeros((size,size));G=K.copy();mass=K.copy()
  for xi,wi in zip((x+1)/2,w/2):
   shape=np.array([1-3*xi**2+2*xi**3,h*(xi-2*xi**2+xi**3),3*xi**2-2*xi**3,h*(-xi**2+xi**3)])
   slope=np.array([-6*xi+6*xi**2,h*(1-4*xi+3*xi**2),6*xi-6*xi**2,h*(-2*xi+3*xi**2)])/h
   curvature=np.array([-6+12*xi,h*(-4+6*xi),6-12*xi,h*(-2+6*xi)])/h**2
   for j in range(n):
    ix=np.ix_(range(2*j,2*j+4),range(2*j,2*j+4));K[ix]+=wi*h*EI*np.outer(curvature,curvature);G[ix]+=wi*h*np.outer(slope,slope);mass[ix]+=wi*h*rho*d['A_mm2']*np.outer(shape,shape)
  K=K[2:,2:];G=G[2:,2:];mass=mass[2:,2:];u=np.array(state['u']);f=np.zeros(len(u));f[-2:]=[F,M];T=K-P*G
  residual.append(float(max(abs(T@u-f))));energy.append(float(abs(.5*u@K@u/state['bending_energy_Nmm']-1)))
  # General eigensolver independently, avoiding producer's symmetric subset solver.
  vals=np.linalg.eigvals(np.linalg.solve(mass,T));mode=float(np.sqrt(min(vals.real)));modal.append(abs(mode/state['omega_loaded_rad_s']-1))
  bad=u.copy();bad[-2]+=.001;negative_control.append(float(max(abs(T@bad-f)))>1e-8)
 checks=dict(input_hashes=True,continuous_shooting=max(abs(tip[:2]/np.array(d['analytic_tip'])-1))<1e-8,weak_form_residual=max(residual)<1e-8,quadrature_energy=max(energy)<1e-8,independent_modal=max(modal)<1e-5,perturbed_state_rejected=all(negative_control))
 dump(out/'summary.json',dict(status='INDEPENDENT_REFERENCE_CHECK_PASS' if all(checks.values()) else 'VERIFY_FAIL',result=ref(p),producer=ref(out/'producer.py'),checks={k:bool(v) for k,v in checks.items()},continuous_tip=tip[:2].tolist(),max_residual_N=max(residual),max_energy_relative=max(energy),max_modal_relative=max(modal),whole_system_release=False))
 print(checks);raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
