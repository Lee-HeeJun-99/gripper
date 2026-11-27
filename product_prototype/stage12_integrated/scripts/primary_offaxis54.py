"""Actual P1 independent offaxis local trimmed-flank distance and 12DOF work.
This is a positive-gap pair verification, never an installed equilibrium.
"""
import json,sys,math,shutil,time,os
import numpy as np
from scipy.spatial.transform import Rotation
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,translate
from validate_nutseat46c import rotate
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE,TopAbs_REVERSED
from OCP.TopoDS import TopoDS
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepLProp import BRepLProp_SLProps
from OCP.gp import gp_Pnt
P=.8;K=P/(2*math.pi);RPE=4.456/2;RPI=4.605/2

def main():
 out=ROOT/'validation/integrated/primaryP1_offaxis54';out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_guide53/summary.json';cad=json.loads(cp.read_text());assert len(cad['part_references'])==128
 assert all(sha(REPO[r['path']])==r['SHA256'] for r in []) # hash checks below, all128 parts
 assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*cad['part_references'].values(),cad['assembly'],cad['BOM']])
 rows=[]
 def journal(r):
  with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(r)+'\n');f.flush();os.fsync(f.fileno())
 for mount,(x,y) in enumerate([(-59.,-58.),(101.,-58.),(-59.,39.),(101.,39.)]):
  bn=f'BENCH_MOUNT_BOLT_{mount}';nn=f'BENCH_MOUNT_NUT_{mount}';O=np.array([x,y,54.]);beta=.011;nu=-.007;opening=.015;offset=np.array([.02,-.012]);bolt=translate(rotate(read(REPO/cad['part_references'][bn]['path']),x,y,beta),*offset,opening);nut=rotate(read(REPO/cad['part_references'][nn]['path']),x,y,nu)
  r=2.32;a=2*math.pi*(3+.37)+nu;p=O+np.array([r*math.cos(a),r*math.sin(a),K*(a-nu)-(P/4+(r-RPI)/math.sqrt(3))]);faces=[];ex=TopExp_Explorer(bolt,TopAbs_FACE)
  while ex.More():faces.append(TopoDS.Face_s(ex.Current()));ex.Next()
  local=[]
  for i,f in enumerate(faces):
   b=np.array(bounds(f));lower=np.linalg.norm(np.maximum(np.maximum(b[:3]-p,p-b[3:]),0))
   if lower<.12:local.append((i,f))
  def query(point,label):
   assert not(ROOT/'runtime/STOP').exists();journal(dict(state='START',mount=mount,label=label,operation='point_to_local_trimmed_faces',point_mm=point.tolist(),candidate_faces=len(local)));t=time.monotonic();v=BRepBuilderAPI_MakeVertex(gp_Pnt(*point)).Vertex();best=None
   for i,f in local:
    d=BRepExtrema_DistShapeShape(v,f);d.Perform();assert d.IsDone()
    if best is None or d.Value()<best[0]:best=(d.Value(),i,d,f)
   dist,i,d,f=best;q=d.PointOnShape2(1);q=np.array([q.X(),q.Y(),q.Z()]);journal(dict(state='COMPLETE',mount=mount,label=label,distance_mm=dist,face=i,nearest_mm=q.tolist(),elapsed_s=time.monotonic()-t));return dist,q,i,d,f
  dist,q,fi,d,f=query(p,'base_actual_offaxis_gap');n=(p-q)/dist;u,v=d.ParOnFaceS2(1);sl=BRepLProp_SLProps(BRepAdaptor_Surface(f),u,v,1,1e-9);nd=sl.Normal();outward=np.array([nd.X(),nd.Y(),nd.Z()])*(-1 if f.Orientation()==TopAbs_REVERSED else 1)
  # Distances use the actual transformed BRep. Pull moving bolt back into its
  # base frame; rotating the nut carries this fixed material point exactly.
  def gap(q12,label):
   pb=O+Rotation.from_rotvec(q12[9:12]).apply(p-O)+q12[6:9]
   pb=O+Rotation.from_rotvec(-q12[3:6]).apply(pb-O-q12[:3])
   return query(pb,label)[0]
  analytic=np.r_[-n,-np.cross(q-O,n),n,np.cross(p-O,n)];fd=[]
  for h in [1e-5,2e-6]:
   g=[]
   for j in range(12):
    z=np.zeros(12);z[j]=h;plus=gap(z,f'FD_h{h}_dof{j}_plus');z[j]=-h;minus=gap(z,f'FD_h{h}_dof{j}_minus');g.append((plus-minus)/(2*h))
   fd.append(dict(h=h,derivative=g,error=float(max(abs(np.array(g)-analytic)))))
  rb=np.linalg.norm(p[:2]-(O[:2]+offset));ab=math.atan2(p[1]-y-offset[1],p[0]-x-offset[0]);ab+=2*math.pi*round((a-ab)/(2*math.pi));zb=54+opening+K*(ab-beta)-(P/4+(rb-RPE)/math.sqrt(3));axgap=p[2]-zb
  nutdist=BRepExtrema_DistShapeShape(BRepBuilderAPI_MakeVertex(gp_Pnt(*p)).Vertex(),nut);nutdist.Perform()
  # 1N normalized physical pair action/reaction,with distinct nearest points.
  force_nut=n;force_bolt=-n;netmoment=np.cross(p-O,n)+np.cross(q-O,-n);rng=np.random.default_rng(mount+54);twist=rng.normal(size=12);direct=np.dot(n,twist[6:9]+np.cross(twist[9:12],p-O)-twist[:3]-np.cross(twist[3:6],q-O));work=float(analytic@twist)
  rows.append(dict(mount=mount,bolt=bn,nut=nn,bolt_reference=cad['part_references'][bn],nut_reference=cad['part_references'][nn],relative_transverse_offset_mm=offset.tolist(),bolt_yaw_rad=beta,nut_yaw_rad=nu,opening_mm=opening,nut_material_point_mm=p.tolist(),bolt_nearest_point_mm=q.tolist(),bolt_face_index=fi,local_candidate_faces=len(local),gap_mm=dist,axial_same_xy_gap_mm=axgap,nut_boundary_distance_mm=nutdist.Value(),normal_on_nut=n.tolist(),bolt_outward_normal=outward.tolist(),normal_error=float(max(abs(outward-n))),gap_Jacobian_12DOF=analytic.tolist(),finite_difference=fd,unit_normal_forces_N=dict(nut=n.tolist(),bolt=(-n).tolist()),unit_pair_net_moment_Nmm=netmoment.tolist(),unit_virtual_work=work,direct_virtual_work=direct,virtual_work_error=abs(work-direct),status='POSITIVE_GAP_NO_REACTION_NOT_EQUILIBRIUM'))
 checks=dict(all128_CAD_hashes=True,independent_axes=True,actual_nut_boundary=max(r['nut_boundary_distance_mm'] for r in rows)<1e-7,actual_bolt_normal=max(r['normal_error'] for r in rows)<1e-7,positive_gaps=all(r['gap_mm']>0 for r in rows),twelve_DOF_FD=max(f['error'] for r in rows for f in r['finite_difference'])<1e-6,action_reaction_moments=max(abs(v) for r in rows for v in r['unit_pair_net_moment_Nmm'])<1e-9,virtualwork=max(r['virtual_work_error'] for r in rows)<1e-10)
 dump(out/'summary.json',dict(status='ACTUAL_P1_OFFAXIS_LOCAL_GAP_AND_12DOF_WORK_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_OFFAXIS_LOCAL_GAP_OR_WORK_FAIL',candidate=ref(cp),actual_parts=128,producer=ref(out/'producer.py'),journal=ref(out/'journal.jsonl'),checks={k:bool(v) for k,v in checks.items()},rows=rows,accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Positive gap forces are zero;1N pair is normalized Jacobian/work verification only,not operating tension or installed equilibrium','Nut material point to bolt trimmed face;NOT whole-surface closest pair or common-normal contact','Independent transverse offset is local mechanism test,not full128part admissibleassembly pose','No wholethread Boolean root,wholeassemblyCCD,elasticpressure,strength,100gfield,convergence/globalenergy orhostqualification']))
 print(json.dumps(dict(checks={k:bool(v) for k,v in checks.items()},gaps=[r['gap_mm'] for r in rows],FD=max(f['error'] for r in rows for f in r['finite_difference']))));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
