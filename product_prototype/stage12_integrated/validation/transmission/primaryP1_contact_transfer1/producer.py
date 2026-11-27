"""Actual P1 finite interface traction feasibility; no arbitrary support DOFs.
Rigid-body necessary equilibrium under explicit Coulomb coefficient, not FEM,
preload prescription, threaded strength, tolerance closure or system certificate.
"""
import json,sys,shutil
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,box
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.gp import gp_Pnt

def faces(s,z):
 it=TopExp_Explorer(s,TopAbs_FACE);out=[]
 while it.More():
  f=TopoDS.Face_s(it.Current());ad=BRepAdaptor_Surface(f);b=bounds(f)
  if ad.GetType()==GeomAbs_Plane and abs(b[2]-z)<1e-5 and abs(b[5]-z)<1e-5:out.append(f)
  it.Next()
 return out

def patch(a,b,z):
 pieces=[];area=0
 for f in faces(a,z):
  for g in faces(b,z):
   c=BRepAlgoAPI_Common(f,g).Shape();p=GProp_GProps();BRepGProp.SurfaceProperties_s(c,p)
   if p.Mass()>1e-8:pieces.append(c);area+=p.Mass()
 # Interior grid witnesses; each checked against actual common face, not bbox alone.
 pts=[]
 for s in pieces:
  bb=bounds(s)
  for x in np.linspace(bb[0]+.02,bb[3]-.02,9):
   for y in np.linspace(bb[1]+.02,bb[4]-.02,9):
    d=BRepExtrema_DistShapeShape(BRepBuilderAPI_MakeVertex(gp_Pnt(float(x),float(y),z)).Vertex(),s);d.Perform()
    if d.IsDone() and d.Value()<1e-7:pts.append([float(x),float(y),z])
 return dict(area_mm2=float(area),points_mm=np.unique(np.round(pts,10),axis=0).tolist() if pts else [],z_mm=z,pieces=len(pieces))

def wrench(p,f):return np.r_[f,np.cross(np.asarray(p)*.001,f)]
def solve_interface(points,bolt_xy,external,mu,normal,bolt_z):
 # Tangential diamond |fx|+|fy|<=mu*fn is an INSCRIBED Coulomb cone.
 # Each nonnegative ray is an admissible force, no tensile contact.
 cols=[];meta=[]
 for i,p in enumerate(points):
  for t in ((mu,0),(0,mu),(-mu,0),(0,-mu)):
   v=np.array([t[0],t[1],normal]);cols.append(wrench(p,v));meta.append(dict(kind='contact',point_mm=p,direction=v.tolist(),point_id=i))
 for x,y in bolt_xy:
  v=np.array([0,0,-normal]);cols.append(wrench([x,y,bolt_z],v));meta.append(dict(kind='bolt_axial',point_mm=[x,y,bolt_z],direction=v.tolist()))
 A=np.array(cols).T;scale=np.array([1,1,1,100,100,100]);obj=np.array([0 if m['kind']=='contact' else 1 for m in meta],dtype=float)
 r=linprog(obj,A_eq=scale[:,None]*A,b_eq=-scale*np.array(external),bounds=(0,None),method='highs',options={'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9})
 row=dict(mu_assumed=mu,success=bool(r.success),solver_message=r.message,solver_status=int(r.status),external_wrench_N_Nm=list(map(float,external)),normal_sign=normal,variables=len(meta),points=len(points))
 if r.success:
  f=A@r.x;res=f+external;row.update(minimum_total_bolt_axial_N=float(obj@r.x),contact_compression_N=float(sum(r.x[j] for j,m in enumerate(meta) if m['kind']=='contact')),force_error_N=float(np.linalg.norm(res[:3])),moment_error_Nm=float(np.linalg.norm(res[3:])),rays=[dict(m,coefficient_N=float(v)) for m,v in zip(meta,r.x) if v>1e-12],balance_wrench_N_Nm=f.tolist())
 return row

def main():
 tag=sys.argv[1];out=ROOT/'validation/transmission'/tag;out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists()
 src=ROOT/'cad/exports/primaryP1_clamp10/summary.json';cad=json.loads(src.read_text());refs=cad['part_references'];names=['OPEN_FRAME','GROUND_PLATE','MOTOR_CAP','F0_MICRO_MOTOR','F0_ROOT_BACK'];s={n:read(REPO/refs[n]['path']) for n in names};loads=ROOT/'validation/transmission/primaryP1_corner_demand_loads1/summary.json';l=json.loads(loads.read_text())['rows'][-1]
 dump(out/'inputs.json',dict(candidate=ref(src),parts={n:refs[n] for n in names},loads=ref(loads),producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(ROOT/'scripts/baseline_registry.py')],criteria=dict(force_N=1e-8,moment_Nm=1e-10),scope='Actual finite nominal interface necessary wrench feasibility. No finite-element/contact stiffness,selected preload or source allowables. No tied bodies or fixed DOFs.'))
 p={'root_frame':patch(s['F0_ROOT_BACK'],s['OPEN_FRAME'],-7),'motor_bottom':patch(s['F0_MICRO_MOTOR'],s['OPEN_FRAME'],14),'motor_top':patch(s['F0_MICRO_MOTOR'],s['MOTOR_CAP'],26),'frame_ground':patch(s['OPEN_FRAME'],s['GROUND_PLATE'],40)}
 dump(out/'patches.json',p)
 rootF=np.array([l['frame_root_force_XZ_N'][0],0,l['frame_root_force_XZ_N'][1]]);motorF=np.array([l['motor_cradle_force_XZ_N'][0],0,l['motor_cradle_force_XZ_N'][1]])
 R=np.array([50.4,0,-7]);C=np.array([0,0,20]);rootW=wrench(R,rootF);rootW[4]+=l['frame_root_couple_about_Y_Nm'];motorW=wrench(C,motorF);motorW[4]+=l['motor_cradle_couple_about_Y_Nm'];total=rootW+motorW
 rows=[]
 for mu in (0.,.1,.2,.4,.8):
  assert not(ROOT/'runtime/STOP').exists()
  rows.append(dict(interface='root_frame',**solve_interface(p['root_frame']['points_mm'],[(64,-16),(64,16)],rootW,mu,1,-3)))
  rows.append(dict(interface='frame_ground',**solve_interface(p['frame_ground']['points_mm'],[(-25,-28),(-25,14),(60,-28),(60,0)],total,mu,-1,34)))
  # Motor: two actual opposed 8x10 lands; minimize total normal compression.
  pts=p['motor_bottom']['points_mm']+p['motor_top']['points_mm'];cols=[];meta=[]
  for side in ('motor_bottom','motor_top'):
   nz=1 if side=='motor_bottom' else -1
   for q in p[side]['points_mm']:
    for tx,ty in ((mu,0),(0,mu),(-mu,0),(0,-mu)):
     f=[tx,ty,nz];cols.append(wrench(q,f));meta.append(dict(side=side,point_mm=q,direction=f))
  A=np.array(cols).T;sc=np.array([1,1,1,100,100,100]);r=linprog(np.ones(A.shape[1]),A_eq=sc[:,None]*A,b_eq=-sc*motorW,bounds=(0,None),method='highs',options={'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9})
  row=dict(interface='motor_lands',mu_assumed=mu,success=bool(r.success),solver_message=r.message,external_wrench_N_Nm=motorW.tolist())
  if r.success:
   residual=A@r.x+motorW;row.update(total_compression_N=float(sum(r.x)),force_error_N=float(np.linalg.norm(residual[:3])),moment_error_Nm=float(np.linalg.norm(residual[3:])),rays=[dict(m,coefficient_N=float(v)) for m,v in zip(meta,r.x) if v>1e-12],bottom_compression_N=float(sum(v for m,v in zip(meta,r.x) if m['side']=='motor_bottom')),top_compression_N=float(sum(v for m,v in zip(meta,r.x) if m['side']=='motor_top')))
  rows.append(row)
 # Free finite Ground must carry +total from Frame and needs -total externally.
 # A normal-only fixture on either single planar face cannot carry Fx or a pure My with Fz=0.
 ground_normal_only=solve_interface(p['frame_ground']['points_mm'],[],total,0.,-1,46)
 result=dict(status='ACTUAL_P1_FINITE_INTERFACE_TRACTION_BOUNDS_NOT_RELEASE',candidate=ref(src),producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),patches=ref(out/'patches.json'),rows=rows,paired_external_wrench_N_Nm=total.tolist(),finite_ground_required_external_wrench_N_Nm=(-total).tolist(),free_ground_or_single_normal_plane=ground_normal_only,actual_product_parts=69,actual_changed_CAD=['OPEN_FRAME','MOTOR_CAP'],newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Rigid equilibrium is a necessary condition,not elastic bolt/contact/load distribution or uniqueness','Minimum axial reactions are load-induced tension bounds,NOT prescribed torque/preload or strength approval; thread core,flank,engagement and bearing pressure need actual geometry/source minima','Coulomb mu is a sensitivity variable,not measured or source-guaranteed friction; frictionless cases remain failures','Motor model is source simplified body envelope,not certified gearbox contact land or case capacity','Finite Ground is not hidden-fixed. Its external wrench needs a real positive attachment or specified clamp/preload/friction. No physical bench attachment exists in69part CAD.','Finite point traction rays are not bounded pressure fields; no peak-contact-stress/mesh PASS','Frame/Rail historical mesh failures,global energy,time/full3Finger/Stage1 gates unchanged'])
 dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],areas={k:v['area_mm2'] for k,v in p.items()},rows=[{k:v for k,v in r.items() if k!='rays'} for r in rows],ground_normal_only=ground_normal_only)))
if __name__=='__main__':main()
