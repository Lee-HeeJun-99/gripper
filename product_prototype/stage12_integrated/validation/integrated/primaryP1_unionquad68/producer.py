"""Freeze ONE common physical surface quadrature from two declared actual meshes.
Voronoi areas integrate exactly each20x20foot. This is geometry-derived common
integration, NOT a fitted material change or a universal future-mesh guarantee.
"""
import sys,json,shutil,numpy as np
from baseline_registry import ROOT,REPO,ref,dump
V=ROOT/'validation/integrated';out=V/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');paths=[REPO/p for p in sys.argv[2:]];xy=[]
for p in paths:
 a=np.load(p);xy.extend(a['points_mm'][a['floor_nodes'],:2])
# Near duplicates from shared CAD corners consolidated only at1e-9mm geometry roundoff.
xy=np.unique(np.round(np.array(xy),9),axis=0);points=[];weights=[];areas=[]
def clip(poly,n,c):
 out=[]
 for a,b in zip(poly,np.roll(poly,-1,axis=0)):
  da=a@n-c;db=b@n-c
  if da<=1e-12:out.append(a)
  if (da<0 and db>0) or (da>0 and db<0):out.append(a+(b-a)*da/(da-db))
 return np.array(out)
for x0 in [-115.,137.]:
 for y0 in [-90.,60.]:
  pts=xy[(xy[:,0]>=x0-1e-8)&(xy[:,0]<=x0+20+1e-8)&(xy[:,1]>=y0-1e-8)&(xy[:,1]<=y0+20+1e-8)];area=0
  for k,p in enumerate(pts):
   poly=np.array([[x0,y0],[x0+20,y0],[x0+20,y0+20],[x0,y0+20]],float)
   for j,q in enumerate(pts):
    if j!=k:poly=clip(poly,q-p,(q@q-p@p)/2)
    assert len(poly)>=3,(p,q)
   ar=abs(np.cross(poly,np.roll(poly,-1,axis=0)).sum()/2);assert ar>0
   points.append([*p,-170.]);weights.append(ar);area+=ar
  areas.append(area)
assert len(points)==len(xy) and max(abs(np.array(areas)-400))<1e-6
np.savez_compressed(out/'material_quadrature.npz',points_mm=np.array(points),weights_mm2=np.array(weights))
dump(out/'summary.json',dict(status='ACTUAL_P1_FROZEN_COMMON_FLOOR_GEOMETRY_QUADRATURE',candidate=ref(ROOT/'cad/exports/primaryP1_ground65a/summary.json'),producer=ref(out/'producer.py'),geometry_fields=[ref(p) for p in paths],quadrature=ref(out/'material_quadrature.npz'),points=len(points),foot_areas_mm2=areas,minimum_weight_mm2=min(weights),geometry_merge_mm=1e-9,physical_tolerance_unchanged=True,scope='One frozen common physical point/area set includes both declared meshfloor vertices. New mesh needs renewed wholetriangle audit. Dual integrated forces may be nonunique; no inferredpressure convergence.',newly_qualified_system_gate_ids=[],whole_system_release=False))
print(json.dumps(dict(points=len(points),areas=areas,minimum_weight=min(weights))))
