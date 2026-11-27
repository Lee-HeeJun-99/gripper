"""Actual P1 continuous P2 cylinder-boundary polynomial enclosure and BRep witnesses.
Convex hull arithmetic is floating point, not rigorous interval arithmetic.
"""
import sys,json,shutil,math
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump,S1
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.gp import gp_Pnt

def triN(b):return np.stack([b[...,0]*(2*b[...,0]-1),b[...,1]*(2*b[...,1]-1),b[...,2]*(2*b[...,2]-1),4*b[...,0]*b[...,1],4*b[...,1]*b[...,2],4*b[...,2]*b[...,0]],axis=-1)
indices=[(i,j,4-i-j) for i in range(5) for j in range(5-i)];lattice=np.array(indices)/4
B=np.array([[math.factorial(4)/math.prod(math.factorial(k) for k in ijk)*np.prod(b**ijk) for ijk in indices] for b in lattice]);Binv=np.linalg.inv(B)
children=np.array([[[1,0,0],[.5,.5,0],[.5,0,.5]],[[.5,.5,0],[0,1,0],[0,.5,.5]],[[.5,0,.5],[0,.5,.5],[0,0,1]],[[.5,.5,0],[0,.5,.5],[.5,0,.5]]])

def main():
 tag,*names=sys.argv[1:];out=ROOT/'validation/integrated'/tag;out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');gp=ROOT/'validation/integrated/primaryP1_gamma_attachment29/pin_hole_geometry.json';geo=json.loads(gp.read_text());results=[]
 for name in names:
  s=json.loads((ROOT/'validation/integrated'/name/'summary.json').read_text())
  for row in s['results']:
   assert not(ROOT/'runtime/STOP').exists();a=np.load(REPO/row['fields']['path']);p=a['points_mm'].T;t=a['tetra'].T;ed=a['element_dofs'].T;edges={}
   for i,j,k in [(0,1,4),(1,2,5),(0,2,6),(0,3,7),(1,3,8),(2,3,9)]:
    for tt,ee in zip(t,ed):edges[tuple(sorted((tt[i],tt[j])))]=ee[k]
   allfaces=np.concatenate([t[:,ix] for ix in [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]]);faces,count=np.unique(np.sort(allfaces,axis=1),axis=0,return_counts=True);faces=faces[count==1];part=row['part'];ports=range(4) if part=='F0_ROOT_BACK' else [i for i,g in enumerate(geo) if g['part']==part];shape=read(REPO/row['part_reference']['path']);portresults=[]
   for port in ports:
    yc,zc=geo[port]['pin']['axis_point_mm'][1:];R=1. if part=='F0_ROOT_BACK' else 1.05;rr=np.linalg.norm(p[faces,1:]-[yc,zc],axis=2);sel=faces[np.all(abs(rr-R)<1e-7,axis=1)&(np.ptp(p[faces,0],axis=1)>1e-8)];nodes=np.array([[*tr,edges[tuple(sorted((tr[0],tr[1])))],edges[tuple(sorted((tr[1],tr[2])))],edges[tuple(sorted((tr[2],tr[0])))]] for tr in sel]);assert len(nodes)>0;xyz=p[nodes];sub=np.eye(3)[None]
    # 3 uniform subdivisions; each quartic polynomial has Bernstein convex hull.
    for depth in range(3):sub=np.einsum('cij,sjk->scik',children,sub).reshape(-1,3,3)
    lo=0.;hi=0.;maxsample=0.;witness=None
    for first in range(0,len(nodes),20):
     coords=xyz[first:first+20];bc=np.einsum('qi,sij->sqj',lattice,sub);q=np.einsum('sqa,fai->fsqi',triN(bc),coords);rad2=np.sum((q[...,1:]-[yc,zc])**2,axis=-1);val=rad2-R*R;coeff=np.einsum('ij,fsj->fsi',Binv,val);roundoff=1e-11*max(1,R*R);lo=min(lo,float(coeff.min())-roundoff);hi=max(hi,float(coeff.max())+roundoff);err=abs(np.sqrt(rad2)-R);idx=np.unravel_index(np.argmax(err),err.shape)
     if err[idx]>maxsample:maxsample=float(err[idx]);witness=q[idx]
    bound=max(abs(np.sqrt(max(0,R*R+lo))-R),abs(np.sqrt(R*R+hi)-R));d=BRepExtrema_DistShapeShape(shape,BRepBuilderAPI_MakeVertex(gp_Pnt(*witness)).Vertex());d.Perform();portresults.append(dict(global_port=port,actual_cylinder_radius_mm=R,quadratic_faces=len(nodes),subtriangles_per_face=len(sub),continuous_polynomial_radial_error_enclosure_mm=bound,largest_sampled_radial_error_mm=maxsample,largest_sample_point_mm=witness.tolist(),actual_BRep_distance_at_witness_mm=d.Value(),floating_roundoff_inflation_radial_squared_mm2=roundoff,exact_rational_cylinder=False))
   results.append(dict(run=name,part=part,part_reference=row['part_reference'],ports=portresults));print(json.dumps(results[-1]),flush=True)
 cp=ROOT/'cad/exports/primaryP1_ycapture24/summary.json';dump(out/'summary.json',dict(status='ACTUAL_P1_CONTINUOUS_QUADRATIC_CYLINDER_GEOMETRY_AUDIT',candidate=ref(cp),verifier=ref(out/'verifier.py'),geometry=ref(gp),results=results,accepted_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Polynomial Bernstein convex hull enclosure uses floating point with explicit conservative numerical inflation; not formal interval arithmetic.','This encloses radial error of ALL selected P2 cylinder triangles, not just quadrature samples. No exact rational cylinder or contact-gap closure is claimed.','Geometry enclosure does not qualify element stiffness, contact pressure, unloaded boundary traction, clamp/material, physical operating demand or system strength.']))
if __name__=='__main__':main()
