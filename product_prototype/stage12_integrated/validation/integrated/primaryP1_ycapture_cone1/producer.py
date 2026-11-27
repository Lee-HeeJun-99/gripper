"""Actual finite contact support cone, no pressure capacity or sixDOF closure claim."""
import sys,json,shutil
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,bounds
from primary_motor_bearing_wrenches import faces,gravity
from primary_contact_transfer_v3 import wrench
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_VERTEX
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool

def vertices(a,b,axis,value):
 pts=[]
 for f in faces(a,axis,value):
  for g in faces(b,axis,value):
   shape=BRepAlgoAPI_Common(f,g).Shape();it=TopExp_Explorer(shape,TopAbs_VERTEX)
   while it.More():
    p=BRep_Tool.Pnt_s(TopoDS.Vertex_s(it.Current()));q=[p.X(),p.Y(),p.Z()]
    if not any(np.linalg.norm(np.array(q)-x)<1e-8 for x in pts):pts.append(q)
    it.Next()
 return pts

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');src=ROOT/'cad/exports/primaryP1_ycapture24/summary.json';cad=json.loads(src.read_text());refs=cad['part_references'];r=read(REPO/refs['F0_ROOT_BACK']['path']);f=read(REPO/refs['OPEN_FRAME']['path']);load=ROOT/'validation/transmission/primaryP1_gravity_cat_demand_ports2/summary.json';l=json.loads(load.read_text())['rows'][0];tests=[]
 for sign in [-1,1]:
  shift=sign*.1;root=translate(r,0,shift,0);meta=[]
  for ax,value,d,label in [(2,-7,[0,0,1],'seat'),(0,68,[-1,0,0],'wall'),(1,sign*20.1,[0,-sign,0],'shoulder')]:
   meta += [dict(point_mm=p,direction=d,label=label) for p in vertices(root,f,ax,value)]
  meta += [dict(point_mm=[64,y,-3],direction=[0,0,-1],label='axial_RF') for y in [-16,16]]
  refpoint=np.array(l['Root_reference_m'])+[0,shift*.001,0];W=np.array(l['Root_force_couple_XYZ_N_Nm']);W[3:]+=np.cross(refpoint,W[:3]);W+=gravity(root,7900);A=np.array([wrench(m['point_mm'],m['direction']) for m in meta]).T;direction=np.r_[0,sign,0,np.cross(refpoint,[0,sign,0])];S=np.array([1,1,1,100,100,100]);AA=np.column_stack([A,direction]);obj=np.r_[np.zeros(A.shape[1]),-1.];res=linprog(obj,A_eq=S[:,None]*AA,b_eq=-S*W,bounds=(0,None),method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9});assert res.success,res.message
  iy=[m['point_mm'][1] for m in meta if m['label']=='wall'];xs=[m['point_mm'][0] for m in meta if m['label']=='shoulder'];yv=max(iy) if sign>0 else min(iy);analytic=sign*(W[5]*1000+W[0]*yv)/(min(xs)-refpoint[0]*1000);balance=AA@res.x+W
  no=[i for i,m in enumerate(meta) if m['label']!='shoulder'];control=linprog(np.r_[np.zeros(len(no)),-1.],A_eq=S[:,None]*np.column_stack([A[:,no],direction]),b_eq=-S*W,bounds=(0,None),method='highs');rays=[dict(m,force_N=float(v)) for m,v in zip(meta,res.x[:-1]) if v>1e-10];tests.append(dict(sign=sign,closed_gap_shift_mm=shift,maximum_lateral_cone_parameter_N=float(res.x[-1]),independent_yaw_upper_N=float(analytic),yaw_upper_error_N=float(abs(analytic-res.x[-1])),force_residual_N=float(np.linalg.norm(balance[:3])),moment_residual_Nm=float(np.linalg.norm(balance[3:])),without_shoulder_maximum_N=float(control.x[-1]) if control.success else None,limit_rays=rays,external_original_wrench_N_Nm=W.tolist(),lateral_wrench_per_N=direction.tolist(),vertices=meta))
 checks=dict(both_sourcehashes=all(sha(REPO/refs[n]['path'])==refs[n]['SHA256'] for n in ['F0_ROOT_BACK','OPEN_FRAME']),both_finite_bounds=all(.1<t['maximum_lateral_cone_parameter_N']<1 for t in tests),independent_yaw_bound=all(t['yaw_upper_error_N']<1e-8 for t in tests),physical_resultants=all(t['force_residual_N']<1e-8 and t['moment_residual_Nm']<1e-10 for t in tests),missing_shoulders_reject_Y=all(t['without_shoulder_maximum_N'] is not None and t['without_shoulder_maximum_N']<1e-8 for t in tests))
 dump(out/'summary.json',dict(status='ACTUAL_P1_FINITE_Y_SUPPORT_CONE_BOUND_MEASURED' if all(checks.values()) else 'ACTUAL_P1_FINITE_Y_SUPPORT_CONE_BOUND_FAIL',candidate=ref(src),loads=ref(load),checks=checks,cases=tests,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Maximum extraY parameter at fixed original conditional Root wrench. Geometric force/moment cone upper bound, NOT material/safety capacity, load requirement or measured hardware response.','Vertex rays are limits of concentrated nonnegative traction, not finite pressure patches or unique elastic reactions. Actual admissible pressure/material can only reduce this bound.','Positive wallnormal only fixes totalwallFx, and shoulderx>=60 produces yaw mismatch against Rootportx50.4. Independent yaw inequality verifies about0.489N necessary upper bound.','Open0.1mmgap has no shoulderreaction until closure; coupled gap/elastic motion unresolved. No6DOF wrenchclosure/3Finger/physicalanchor/globalenergy certification.']))
 print(json.dumps(dict(checks=checks,bounds=[(t['maximum_lateral_cone_parameter_N'],t['independent_yaw_upper_N']) for t in tests])));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
