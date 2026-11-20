"""Conditional uniform-density geometric union moments;not a CAD BREP or hardware mass.
Annular polygonal prism decomposes into disjoint convex sectors. Each sector is
intersected with the proposed convex support using halfspaces;subtract overlap
exactly once from additive geometric volume moments. No voxel/Monte Carlo mass.
"""
import argparse,json,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from scipy.optimize import linprog
from scipy.spatial import ConvexHull,HalfspaceIntersection
from analyse import BASE,sha
from finite_guide_coupon import eyelet
from finite_mass_reference import moments
sys.path.insert(0,str(BASE/'cad'))
from finite_guide_product import support,guide_basis
from generate import width,guide_outboard,guide_normal,world
def raw(mesh):
 V,c,I=moments(mesh.vertices,mesh.faces);return V,V*c,V*(np.trace(I)/2*np.eye(3)-I+np.outer(c,c))
def convex(points):
 h=ConvexHull(points);faces=h.simplices.copy()
 for k,f in enumerate(faces):
  if np.dot(np.cross(points[f[1]]-points[f[0]],points[f[2]]-points[f[0]]),h.equations[k,:3])<0:faces[k]=f[::-1]
 return trimesh.Trimesh(points,faces,process=False)
def intersection(a,b):
 planes=np.concatenate([ConvexHull(a.vertices).equations,ConvexHull(b.vertices).equations]);lp=linprog([0,0,0,-1],A_ub=np.c_[planes[:,:3],np.ones(len(planes))],b_ub=-planes[:,3],bounds=[(None,None)]*3+[(0,None)],method='highs')
 if lp.status==2:return (0.,np.zeros(3),np.zeros((3,3)))
 if not lp.success:raise ValueError('unresolved halfspace feasibility:'+lp.message)
 scale=max(np.max(abs(a.vertices)),np.max(abs(b.vertices)),np.finfo(float).tiny)
 if lp.x[3]<=128*np.finfo(float).eps*scale:raise ValueError('degenerate/tangent intersection requires separate exact predicate;not silently zeroed')
 points=HalfspaceIntersection(planes,lp.x[:3]).intersections;return raw(convex(points))
def add(*items):return tuple(sum((x[k] for x in items)) for k in range(3))
def normalized(r):
 V,F,S=r
 if V<=0:raise ValueError('nonpositive union volume')
 c=F/V;C=S/V-np.outer(c,c);return V,c,np.trace(C)*np.eye(3)-C
def union(ring,bracket,n):
 parts=[]
 for k in range(n):
  j=(k+1)%n;indices=[k,j,n+k,n+j,2*n+k,2*n+j,3*n+k,3*n+j];parts.append(convex(ring.vertices[indices]))
 decomposition=add(*(raw(p) for p in parts));overlap=add(*(intersection(p,bracket) for p in parts));total=add(raw(ring),raw(bracket),tuple(-x for x in overlap));return normalized(total),normalized(overlap),max(float(np.max(abs(a-b))) for a,b in zip(decomposition,raw(ring)))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--segments',type=int,choices=(32,64),default=64);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);start=time.monotonic();config=BASE/'meshes/finite_eyelet_support_v11/config.json';cfg=json.loads(config.read_text());ring,_=eyelet(cfg,a.segments);records=[]
 # Twelve geometrically distinct parts on finger0;other fingers are rigid rotations.
 for cable,side in enumerate((-1,1)):
  for x in cfg['tendon']['guide_stations']:
   p=np.array([x,side*(width(cfg,x)/2+guide_outboard(cfg,x)),guide_normal(cfg,x)]);center=np.array(world(cfg,p,0));R=guide_basis(cfg,p,0);bracket=support(cfg,x,side,0);local=trimesh.Trimesh((bracket.vertices-center)@R,bracket.faces,process=False);u,o,error=union(ring,local,a.segments);V,c,I=u;Vo,co,Io=o;Vr,cr,Ir=normalized(add(raw(ring),raw(local)))
   records.append(dict(cable=cable,station_mm=x,union_volume_mm3=float(V),overlap_volume_mm3=float(Vo),naive_additive_volume_mm3=float(Vr),naive_volume_overcount_relative=float(Vo/V),conditional_uniform_density_union_COM_local_mm=c.tolist(),conditional_uniform_density_union_normalized_inertia_mm2=I.tolist(),additive_COM_bias_mm=(cr-c).tolist(),additive_normalized_inertia_bias_mm2=(Ir-I).tolist(),ring_decomposition_raw_moment_error=error,physical_mass_kg=None,physical_density_kg_m3=None))
 result=dict(status='GEOMETRIC_UNION_MOMENTS_ONLY',scope='Polygonal64/32 eyelet prism and proposed convex support,uniform common density CONDITIONAL. Not actual differing-material/joint mass,not CAD Boolean BREP/STEP,not physical inertia calibration or Native model replacement. Other fingers follow proper rotations;no simulated grasp.',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),producer_sha256=sha(Path(__file__)),source_config_sha256=sha(config),segments=a.segments,records=records,runtime_s=time.monotonic()-start,maximum_naive_mass_overcount_relative=max(r['naive_volume_overcount_relative'] for r in records),physical_mass_qualification='BLOCKED_UNSELECTED_MATERIAL_AND_JOIN')
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
if __name__=='__main__':main()
