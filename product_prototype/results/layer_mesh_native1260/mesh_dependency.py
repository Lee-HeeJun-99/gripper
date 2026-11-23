"""One-axis mesh contrast of the coupon's independent CST reference."""
import argparse,json,subprocess,sys
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from layer_bending_reference import reference
def mesh(nx):
 q=np.array([[x,y,z] for x in np.linspace(0,.04,nx) for y in (-.005,.005) for z in (0,.0002)]);idx=lambda i,j,k:4*i+2*j+k;tet=[]
 for i in range(nx-1):
  ids=[idx(i+a,b,c) for a,b,c in ((0,0,0),(1,0,0),(0,1,0),(1,1,0),(0,0,1),(1,0,1),(0,1,1),(1,1,1))]
  for pat in ((0,1,3,7),(0,3,2,7),(0,2,6,7),(0,6,4,7),(0,4,5,7),(0,5,1,7)):
   t=[ids[j] for j in pat]
   if np.linalg.det((q[t[1:]]-q[t[0]]).T)<0:t[1],t[2]=t[2],t[1]
   tet.append(t)
 faces={}
 for a,b,c,d in tet:
  for f in ((b,c,d),(a,d,c),(a,b,d),(a,c,b)):faces.setdefault(tuple(sorted(f)),[]).append(f)
 return q,np.array(tet),[v[0] for v in faces.values() if len(v)==1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag
 if not a.worker:
  out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'reference_dependency.py').write_bytes((BASE/'sofa/layer_bending_reference.py').read_bytes());print(json.dumps(guarded([sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker'],out/'process',60)));return
 records=[]
 for nx in (9,17,33,65,129,257):
  q,tet,tri=mesh(nx);F=np.zeros_like(q);F[q[:,0]==.04,2]=-1e-4/8;r=reference(q,tet,F);records.append(dict(nx=nx,dx_m=.04/(nx-1),nodes=len(q),elements=len(tet),tip_m=r['reference_tip_m'],tip_shear_fraction=r['reference_tip_shear_energy_fraction'],pure_bending_interpolant_energy_ratio=r['pure_bending_interpolant_energy_ratio'],volume_m3=r['volume_m3'],free_residual_N=r['reference_free_residual_N'],root_reaction_N=r['reference_root_reaction_N']));np.savetxt(out/f'reference_u_nx{nx}.csv',r['u'],delimiter=',')
 pairs=[dict(nx=[a['nx'],b['nx']],relative_tip=abs(a['tip_m']-b['tip_m'])/max(abs(a['tip_m']),abs(b['tip_m']))) for a,b in zip(records,records[1:])];d=dict(status='FAIL_CST_MESH_GATE' if any(r['relative_tip']>.01 for r in pairs) else 'PASS_REFERENCE_ADJACENT_MESH_ONLY',records=records,pairs=pairs,mesh_gate=.01,physical_validation='NOT QUALIFIED',scope='Math reference only,not Native execution. One-axis refinement preserves geometry,volume,material,root and SAME four end nodal forces. No new material fit;other section resolutions not yet converged.',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
