"""Exact-field interpolation diagnostic only; not a new physical solver."""
import argparse,json,subprocess
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from layer_bending_reference import element,elastic

def mesh(nx,ny,nz):
 q=np.array([[x,y,z] for x in np.linspace(0,.04,nx) for y in np.linspace(-.005,.005,ny) for z in np.linspace(0,.0002,nz)])
 idx=lambda i,j,k:(i*ny+j)*nz+k
 tet=[]
 for i in range(nx-1):
  for j in range(ny-1):
   for k in range(nz-1):
    ids=[idx(i+a,j+b,k+c) for a,b,c in ((0,0,0),(1,0,0),(0,1,0),(1,1,0),(0,0,1),(1,0,1),(0,1,1),(1,1,1))]
    for pat in ((0,1,3,7),(0,3,2,7),(0,2,6,7),(0,6,4,7),(0,4,5,7),(0,5,1,7)):
     t=[ids[v] for v in pat]
     if np.linalg.det((q[t[1:]]-q[t[0]]).T)<0:t[1],t[2]=t[2],t[1]
     tet.append(t)
 return q,np.array(tet)

def assess(nx,ny,nz):
 q,tet=mesh(nx,ny,nz);D=elastic(2.5e9,.3)
 u=np.zeros_like(q);u[:,0]=-q[:,0]*(q[:,2]-.0001);u[:,2]=.5*q[:,0]**2
 normal=shear=volume=0.
 for t in tet:
  V,B,_=element(q[t],D);e=B@u[t].ravel();normal+=.5*V*(e[:3]@D[:3,:3]@e[:3]);shear+=.5*V*(e[3:]@D[3:,3:]@e[3:]);volume+=V
 exact=.5*D[0,0]*.01*.04*.0002**3/12
 return dict(resolution=[nx,ny,nz],elements=len(tet),volume_m3=volume,normal_energy_ratio=normal/exact,shear_energy_ratio=shear/exact,total_energy_ratio=(normal+shear)/exact,
             analytic_normal_ratio=1+2/(nz-1)**2)

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 records=[assess(*v) for v in ((9,2,2),(33,2,2),(33,5,2),(33,2,3),(33,2,5),(65,2,5),(129,2,5))]
 d=dict(status='PASS_EXACT_FIELD_DIAGNOSTIC_ONLY',records=records,physical_validation='NOT QUALIFIED',scope='Prescribed polynomial interpolation only; no Native execution, load response, Poisson-relaxed bending, contact or jamming qualification.',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)))
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
