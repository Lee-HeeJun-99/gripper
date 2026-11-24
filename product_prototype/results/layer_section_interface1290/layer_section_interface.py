"""Existing linear CST reference:ideal normal-only vs XYZ interface limits.
Not a pressure/friction constitutive law or Native solver implementation.
"""
import argparse,json,subprocess,sys
from pathlib import Path
import numpy as np
from scipy.sparse import block_diag,coo_matrix
from scipy.sparse.linalg import spsolve
from analyse import BASE,sha
from native_bending_coupon import guarded
from layer_section_reference import mesh
from layer_face_load import tip_load
from layer_bending_reference import reference

def solve(nx,nz,axes):
 q,t=mesh(nx,2,nz);n=len(q);F,_,_=tip_load(q,t,[0,0,-5e-5]);r=reference(q,t,F);parent=np.arange(6*n)
 lower=np.flatnonzero((q[:,2]==.0002)&(q[:,0]>0));upper=lower-(nz-1)
 for lo,up in zip(lower,upper):
  for axis in axes:parent[3*(n+up)+axis]=3*lo+axis
 _,labels=np.unique(parent,return_inverse=True);R=coo_matrix((np.ones(6*n),(np.arange(6*n),labels)),shape=(6*n,int(labels.max())+1)).tocsc();K=block_diag([r['K'],r['K']],format='csc');Kr=R.T@K@R;load=np.tile(F.ravel(),2);Fr=R.T@load;roots=np.flatnonzero(q[:,0]==0);ids=(3*np.r_[roots,n+roots][:,None]+np.arange(3)).ravel();fixed=np.unique(labels[ids]);free=np.setdiff1d(np.arange(Kr.shape[0]),fixed);ur=np.zeros(Kr.shape[0]);ur[free]=spsolve(Kr[free][:,free],Fr[free]);u=(R@ur).reshape(2,n,3);tip=float(u[:,q[:,0]==.04,2].mean());res=Kr@ur-Fr
 return dict(nx=nx,nz=nz,tied_axes=list(axes),free_tip_m=r['reference_tip_m'],tied_tip_m=tip,free_to_tied_displacement_ratio=abs(r['reference_tip_m']/tip),interface_constrained_displacement_error_m=float(abs((u[1,upper]-u[0,lower])[:,axes]).max()),reduced_free_residual_N=float(abs(res[free]).max()),scope='Linear displacement constraints across fixed world gap;normal-only permits tangential slip but forbids separation;XYZ is ideal infinite stick,neither is calibrated jamming')

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag
 if not a.worker:
  out.mkdir(exist_ok=False)
  for name in ('layer_section_interface.py','layer_section_reference.py','layer_face_load.py','layer_bending_reference.py'):(out/name).write_bytes((BASE/'sofa'/name).read_bytes())
  print(json.dumps(guarded([sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker'],out/'process',60)));return
 records=[solve(nx,nz,axes) for nx,nz in ((9,3),(33,3)) for axes in ((2,),(0,1,2))]
 d=dict(status='IDEAL_INTERFACE_LIMITS_ONLY',records=records,physical_validation='NOT QUALIFIED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),pressure_Pa=None,friction_coefficient=None,actual_hardware='NOT MEASURED');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
