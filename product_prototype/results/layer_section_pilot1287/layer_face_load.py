"""Consistent linear-tetrahedron face traction; no state or material correction."""
import argparse,json,subprocess
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from layer_section_reference import mesh

def tip_load(q,tet,total_force):
 faces={}
 for a,b,c,d in tet:
  for f in ((b,c,d),(a,d,c),(a,b,d),(a,c,b)):
   faces.setdefault(tuple(sorted(f)),[]).append(f)
 end=[v[0] for v in faces.values() if len(v)==1 and np.all(q[list(v[0]),0]==.04)]
 areas=np.array([np.linalg.norm(np.cross(q[b]-q[a],q[c]-q[a]))/2 for a,b,c in end])
 F=np.zeros_like(q)
 for f,A in zip(end,areas):
  F[list(f)]+=np.asarray(total_force)*A/(3*areas.sum())
 return F,float(areas.sum()),end

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[]
 for dims in ((9,2,2),(33,2,2),(33,5,2),(33,2,5),(33,5,5)):
  q,t=mesh(*dims);F,A,end=tip_load(q,t,[0,0,-5e-5]);equal=np.zeros_like(q);equal[q[:,0]==.04,2]=-5e-5/np.count_nonzero(q[:,0]==.04)
  records.append(dict(resolution=dims,area_m2=A,force_N=F.sum(axis=0).tolist(),moment_about_root_Nm=np.cross(q,F).sum(axis=0).tolist(),max_difference_from_equal_nodal_N=float(abs(F-equal).max()),end_triangles=len(end)))
 d=dict(status='PASS_FACE_QUADRATURE_ONLY',records=records,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),scope='Uniform end-face traction gives A/3 nodal integral per triangle. Changes original equal-four-point load distribution; not a mesh-only Native contrast or actual new execution.',physical_validation='NOT QUALIFIED')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
