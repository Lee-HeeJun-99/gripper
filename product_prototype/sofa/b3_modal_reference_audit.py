"""Independent proportional-damping modal closed form vs affine exponential.
Reference conditioning audit only; no actual Native trajectory is generated.
"""
import argparse,csv,json,sys
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from scipy.linalg import eigh,expm
from analyse import BASE,sha
from native_bending_coupon import guarded

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag
    if not a.worker:
        out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(guarded([sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker'],out/'process',120)));return
    src=BASE/'results/b3_linear_gravity_ode1166';root=ET.parse(src/'scene.scn').getroot();node=root.find('Node');q=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ');N=len(q);free=np.ones(N,bool)
    for i in np.fromstring(node.find('FixedProjectiveConstraint').get('indices'),sep=' ',dtype=int):free[3*i:3*i+3]=False
    raw=np.zeros((N,N))
    for r in csv.DictReader((src/'rest.matrix.csv').open()):raw[int(r['i']),int(r['j'])]=float(r['K_N_per_m'])
    K=raw[np.ix_(free,free)];n=len(K);m=float(node.find('UniformMass').get('totalMass'))/(N//3);M=m*np.eye(n);f=np.tile(m*np.fromstring(root.get('gravity'),sep=' '),N//3)[free];asym=float(np.linalg.norm(K-K.T)/np.linalg.norm(K));lam,V=eigh((K+K.T)/2,M)
    if np.any(lam<=0):raise ValueError('Nonpositive eigenvalues: cannot silently clip reference modes')
    c=1+1e-4*lam;s=np.sqrt((c*c/4-lam).astype(complex));r2=-c/2-s;r1=-lam/(c/2+s);modal_force=V.T@f;B=np.zeros((2*n+1,2*n+1));B[:n,n:2*n]=np.eye(n);B[n:2*n,:n]=-K/m;B[n:2*n,n:2*n]=-(M+1e-4*K)/m;B[n:2*n,-1]=f/m;initial=np.zeros(2*n+1);initial[-1]=1;results=[]
    for t in (.0025,.1):
        modal=modal_force/lam*(1+(r2*np.exp(r1*t)-r1*np.exp(r2*t))/(r1-r2));x=(V@modal).real;reference=(expm(t*B)@initial)[:n];absolute=float(np.linalg.norm(x-reference));den=max(np.linalg.norm(x),np.linalg.norm(reference));results.append(dict(time_s=t,absolute_L2_m=absolute,relative=absolute/den,imaginary_norm=float(np.linalg.norm((V@modal).imag))))
    eigen_residual=np.linalg.norm(K@V-M@V*lam,axis=0)/(np.linalg.norm(K@V,axis=0)+np.linalg.norm(M@V*lam,axis=0));d=dict(status='PASS_LINEAR_REFERENCE_CROSSCHECK_ONLY' if max(r['relative'] for r in results)<=.001 else 'FAIL_LINEAR_REFERENCE_CROSSCHECK',comparisons=results,relative_gate=.001,K_antisymmetry_relative=asym,minimum_eigenvalue_s_minus2=float(lam.min()),maximum_eigenvalue_s_minus2=float(lam.max()),spectral_condition_ratio=float(lam.max()/lam.min()),maximum_modal_eigen_residual=float(eigen_residual.max()),physical_validation='NOT QUALIFIED',B3_time_convergence='FAIL_PRESERVED',scope='Symmetric-part modal closed form vs unsymmetrized affine exponential; no fitted modes, no clipped eigenvalues, not actual nonlinear dominant modes.',input_hashes={str(f.relative_to(BASE)):sha(f) for f in (src/'scene.scn',src/'rest.matrix.csv',Path(__file__))});(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))

if __name__=='__main__':main()
