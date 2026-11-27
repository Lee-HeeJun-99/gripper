"""Same P1 actual BRep free-tip membership and converged boundary residual.
Corrects only a coordinate label in the first audit, preserved separately.
"""
import sys,json,time,shutil,hashlib
import numpy as np
from numpy.polynomial.legendre import leggauss
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
from verify_primary_variational33 import bgstress
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,bounds
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.gp import gp_Pnt

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();src=ROOT/'validation/integrated/primaryP1_variational_contact33/summary.json';s=json.loads(src.read_text());cad=json.loads((REPO/s['candidate']['path']).read_text());assert all(sha(REPO/v['path'])==v['SHA256'] for v in cad['part_references'].values());a=np.load(REPO/s['fields']['path']);root=translate(read(REPO/cad['part_references']['F0_ROOT_BACK']['path']),0,.05,0)
 faces=[];it=TopExp_Explorer(root,TopAbs_FACE)
 while it.More():
  f=TopoDS.Face_s(it.Current());bb=bounds(f);sf=BRepAdaptor_Surface(f)
  if sf.GetType()==GeomAbs_Plane and abs(bb[0]-48.5)<1e-7 and abs(bb[3]-48.5)<1e-7:faces.append(f)
  it.Next()
 assert len(faces)>0;rows=[]
 for row in s['results']:
  if row['target_gauss_order']!=48 or row['nx']!=16 or row['ny']!=24:continue
  key=row['key'];x,t=a[key+'_x_t_mm'].T;force=a[key+'_force_N'];dx=row['dx_mm'];dt=row['dt_mm'];yc,zc=row['axis_yz_mm'];R=row['R_mm']
  for depth in [.02,.1,.5]:
   point=[48.5,yc+R-depth,zc];vertex=BRepBuilderAPI_MakeVertex(gp_Pnt(*point)).Vertex();ds=[]
   for face in faces:
    d=BRepExtrema_DistShapeShape(face,vertex);d.Perform();assert d.IsDone();ds.append(d.Value())
   tr=[]
   for order in [24,48]:
    z,w=leggauss(order);traction=np.zeros(3)
    for u,wu in zip(z,w):
     for v,wv in zip(z,w):
      rr=np.c_[48.5-x-u*dx/2,-t-v*dt/2,np.full(len(x),depth)];traction-=wu*wv/4*np.einsum('nij,n->ij',bgstress(rr,.3),force)[:,0]
    tr.append(traction)
   rel=float(np.linalg.norm(tr[1]-tr[0])/np.linalg.norm(tr[1]));rows.append(dict(port=row['port'],actual_seated_Root_pin_tip_point_mm=point,Root_y_translation_mm=.05,equivalent_hole_translation_mm=-.05,actual_tip_face_distance_mm=min(ds),depth_from_actual_seated_crown_mm=depth,quadrature_orders=[24,48],local_halfspace_traction_MPa=[q.tolist() for q in tr],traction_norm_MPa=float(np.linalg.norm(tr[1])),relative_integration_change=rel,required_actual_free_surface_traction_MPa=[0,0,0],free_tip_boundary_satisfied=False))
 checks=dict(actual_BRep_free_tip_membership=all(r['actual_tip_face_distance_mm']<1e-8 for r in rows),nonzero_boundary_residual=all(r['traction_norm_MPa']>1e-8 for r in rows),boundary_residual_integration_1percent=all(r['relative_integration_change']<.01 for r in rows))
 dump(out/'summary.json',dict(status='ACTUAL_P1_BREP_FREE_TIP_BOUNDARY_REJECTS_LOCAL_HALFSPACE',candidate=s['candidate'],part=cad['part_references']['F0_ROOT_BACK'],source=ref(src),producer=ref(out/'producer.py'),stress_source=ref(ROOT/'scripts/verify_primary_variational33.py'),checks=checks,results=rows,actual_tip_planar_faces=len(faces),newly_qualified_system_gate_ids=[],whole_system_release=False,accepted_product_equilibria=0,elapsed_s=time.monotonic()-start,correction='Original33audit free-tip coordinate LABEL used yc+1-depth. The stress calculation used correct crown depth; corrected label is yc+R-depth. Initial audit preserved; actual BRep membership and24/48integration added here.',limitations=['Actual finite78part P1 CAD is unchanged. This rejects local halfspace as actual finite-pin free-boundary solution; it does not solve finite-body contact or actual product stress.','Same conditional selfweight/gamma load contrast and material assumptions; no actual operating demand/pressure/strength/loadsplit/globalenergy certification.']))
 print(json.dumps(dict(checks=checks,results=rows)))
if __name__=='__main__':main()
