"""Actual trimmed BRep nut face normals bind finite thread quadrature; no capacity."""
import json,sys,math,shutil,os,time
import numpy as np
from scipy.optimize import linprog
from numpy.polynomial.legendre import leggauss
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read
from primary_flank50 import integrate,K,RPI,P
from OCP.gp import gp_Pnt
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepLProp import BRepLProp_SLProps
from OCP.TopAbs import TopAbs_REVERSED

def main():
 out=ROOT/'validation/integrated/primaryP1_actualface50';out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_thread49f/summary.json';cad=json.loads(cp.read_text());nr=cad['part_references']['BENCH_MOUNT_NUT_0'];assert sha(REPO/nr['path'])==nr['SHA256'];nut=read(REPO/nr['path']);math4,patch=integrate(4);math8,_=integrate(8);math16,_=integrate(16);actual=[];details=[];q,w=leggauss(4);t=time.monotonic()
 dump(out/'plan.json',dict(candidate=ref(cp),nut=nr,quadrature_order=4,patches=96,expected_point_count=1536,distance_limit_mm=1e-7,normal_limit=1e-7,integral_difference_limit=1e-7,unit_balance_limit=1e-9,whole_system_release=False))
 for index,p in enumerate(patch):
  assert not(ROOT/'runtime/STOP').exists();s=p['side'];lo,hi=p['theta_range'];col=np.zeros(6);md=0.;mn=0.;samples=[]
  for qr,wr in zip(q,w):
   r=2.32+.1*qr
   for qa,wa in zip(q,w):
    a=(lo+hi)/2+(hi-lo)/2*qa;z=K*a+s*(P/4+(r-RPI)/math.sqrt(3));pos=np.array([r*math.cos(a),r*math.sin(a),z-3.65]);point=[-59+pos[0],-58+pos[1],54+z];dist=BRepExtrema_DistShapeShape(BRepBuilderAPI_MakeVertex(gp_Pnt(*point)).Vertex(),nut);dist.Perform();assert dist.IsDone();face=TopoDS.Face_s(dist.SupportOnShape2(1));u,v=dist.ParOnFaceS2(1);props=BRepLProp_SLProps(BRepAdaptor_Surface(face),u,v,1,1e-9);assert props.IsNormalDefined();dn=props.Normal();normal=np.array([dn.X(),dn.Y(),dn.Z()]);normal*=(-1 if face.Orientation()==TopAbs_REVERSED else 1)
    er=np.array([math.cos(a),math.sin(a),0]);et=np.array([-math.sin(a),math.cos(a),0]);raw=er/math.sqrt(3)+s*K/r*et+[0,0,-s];expected=-raw/np.linalg.norm(raw);dA=r*np.linalg.norm(raw)*.1*(hi-lo)/2*wr*wa;col+=np.r_[normal,np.cross(pos,normal)]*dA;dd=dist.Value();ne=float(max(abs(normal-expected)));md=max(md,dd);mn=max(mn,ne);samples.append(dict(point_mm=point,closest_distance_mm=dd,actual_outward_normal=normal.tolist(),analytic_outward_normal=expected.tolist(),normal_error=ne))
  actual.append(col);row=dict(index=index,side=s,turn=p['turn'],theta_range=p['theta_range'],wrench_per_MPa=col.tolist(),max_distance_mm=md,max_normal_error=mn,samples=samples);details.append(row)
  with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(row)+'\n');f.flush();os.fsync(f.fileno())
  if index%16==0:print(json.dumps(dict(completed_patches=index+1,elapsed_s=time.monotonic()-t)),flush=True)
 A=np.array(actual).T;targets=[('Fx',[1,0,0,0,0,0]),('Fy',[0,1,0,0,0,0]),('Mx',[0,0,0,1,0,0]),('My',[0,0,0,0,1,0]),('Fz_free_torque',[0,0,1,0,0,0]),('Mz_free_axial',[0,0,0,0,0,1]),('Fz_with_screw_torque',[0,0,1,0,0,-K])];cases=[]
 for label,target in targets:
  sol=linprog(np.array([p['area_mm2'] for p in patch]),A_eq=A,b_eq=np.array(target),bounds=(0,None),method='highs');cases.append(dict(label=label,target=target,feasible=bool(sol.success),status=sol.message,residual=None if not sol.success else float(max(abs(A@sol.x-target))),conditional_peak_pressure_MPa=None if not sol.success else float(max(sol.x)),pressure_MPa=None if not sol.success else sol.x.tolist()))
 distance=max(r['max_distance_mm'] for r in details);normal=max(r['max_normal_error'] for r in details);delta=float(max(abs(A+math4).flat));screw=np.array([0,0,K,0,0,1]);work=float(max(abs(A.T@screw)));checks=dict(actual_face_distance=distance<1e-7,actual_outward_normals=normal<1e-7,finite_integral_binding=delta<1e-7,quadrature_4_8_16=float(max(abs(math4-math8).flat))<1e-9 and float(max(abs(math8-math16).flat))<1e-11,actual_screw_work=work<1e-7,transverse_bending_conditional=all(c['feasible'] and c['residual']<1e-9 for c in cases[:4]),free_axial_and_free_torque_rejected=not cases[4]['feasible'] and not cases[5]['feasible'],axial_with_torque_conditional=cases[6]['feasible'] and cases[6]['residual']<1e-9)
 dump(out/'summary.json',dict(status='ACTUAL_P1_TRIMMED_FACE_UNIT_TRACTION_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_TRIMMED_FACE_UNIT_TRACTION_FAIL',candidate=ref(cp),producer=ref(out/'producer.py'),plan=ref(out/'plan.json'),actual_nut=nr,checks={k:bool(v) for k,v in checks.items()},journal=ref(out/'journal.jsonl'),patch_count=96,actual_face_queries=1536,max_distance_mm=distance,max_normal_error=normal,max_integral_difference=delta,screw_work_error=work,singular_values=np.linalg.svd(A,compute_uv=False).tolist(),cases=cases,required_screw_torque_Nmm_per_N=-K,accepted_product_equilibria=0,installed_capacity_N=None,newly_qualified_system_gate_ids=[],whole_system_release=False,previous_failed_map=ref(ROOT/'validation/integrated/primaryP1_flank50/summary.json'),limitations=['Actual trimmed face bindings at Gauss points;NOT continuous fullface/contact solve','Initial analytic map used inward nut normals;this independently uses oriented actual BRep outward normals;old FAIL preserved','Two flank cone includes mutually exclusive contact sides;NOT installed active-set or elasticity solution','Free screw null mode prevents independent axial/torque support;actual cage/head/key/pin reaction needed','Unit1N/1Nmm are normalized loads,NOT100g operating/protectedpeak/materialcapacity/globalenergy qualification']))
 print(json.dumps(dict(checks={k:bool(v) for k,v in checks.items()},distance=distance,normal=normal,delta=delta,work=work)),flush=True);raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
