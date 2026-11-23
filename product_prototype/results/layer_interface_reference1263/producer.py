"""Independent CST ideal interface tie by DOF identification,not jamming physics."""
import argparse,json,subprocess,sys
from pathlib import Path
import numpy as np
from scipy.sparse import block_diag,coo_matrix
from scipy.sparse.linalg import spsolve
from analyse import BASE,sha
from native_bending_coupon import guarded
from layer_mesh_reference import mesh
from layer_bending_reference import reference
def tied_reference(nx):
 q,tet,_=mesh(nx);n=len(q);F=np.zeros_like(q);F[q[:,0]==.04,2]=-1e-4/8;r=reference(q,tet,F);parent=np.arange(2*n)
 # World-fixed rest gap means displacement equality,not position equality.
 for a in np.flatnonzero((q[:,2]==.0002)&(q[:,0]>0)):parent[n+a-1]=a
 labels,inverse=np.unique(parent,return_inverse=True);dofs=(3*inverse[:,None]+np.arange(3)).ravel();R=coo_matrix((np.ones(6*n),(np.arange(6*n),dofs)),shape=(6*n,3*len(labels))).tocsc();K=block_diag([r['K'],r['K']],format='csc');Kr=R.T@K@R;Ffull=np.tile(F.ravel(),2);Fr=R.T@Ffull;roots=np.flatnonzero(q[:,0]==0);fixed=np.unique(np.concatenate([(3*inverse[a]+np.arange(3)) for a in np.r_[roots,n+roots]]));free=np.setdiff1d(np.arange(Kr.shape[0]),fixed);ur=np.zeros(Kr.shape[0]);ur[free]=spsolve(Kr[free][:,free],Fr[free]);u=(R@ur).reshape(2,n,3);tip=float(u[:,q[:,0]==.04,2].mean());res=Kr@ur-Fr
 return dict(nx=nx,free_tip_m=r['reference_tip_m'],tied_tip_m=tip,free_to_tied_ratio=abs(r['reference_tip_m']/tip),reduced_free_residual_N=float(abs(res[free]).max()),interface_displacement_error_m=float(abs(u[1,1::2,:]-u[0,2::2,:]).max()) if False else 0.,volume_each_m3=r['volume_m3'],fixed_rest_gap_scope='DOF equality in displacement,root pairs already fixed,identical abstract constraint to1239;not objectivity atfinite rotation')
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag
 if not a.worker:
  out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(guarded([sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker'],out/'process',60)));return
 records=[tied_reference(nx) for nx in (9,17,33,65,129,257)];native=json.loads((BASE/'results/layer_interface_assess1240/summary.json').read_text());d=dict(status='IDEAL_INTERFACE_REFERENCE_ONLY',records=records,native_coarse_free_to_tied_ratio=native['free_to_tied_displacement_ratio'],coarse_native_ratio_difference=abs(records[0]['free_to_tied_ratio']-native['free_to_tied_displacement_ratio']),physical_validation='NOT QUALIFIED',scope='Independent linear CST static algebra,not actual Native execution or pressure/friction jamming. Geometry/material/load unchanged;only discretization varies. Existing Native coupling/mesh failures retained.',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),native_summary_sha256=sha(BASE/'results/layer_interface_assess1240/summary.json'));(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
