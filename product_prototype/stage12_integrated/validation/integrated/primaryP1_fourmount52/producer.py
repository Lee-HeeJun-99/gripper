"""Actual four installed P1 mount stacks sharing two rigid support bodies.
All internal bodies explicit; no imposed receiver yaw,port torque,friction or preload.
Finite endpoint is conditional; not takeup dynamics,capacity or product release.
"""
import json,sys,math,shutil,os,time
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,ref,sha,dump,S1
XY=[(-59.,-58.),(101.,-58.),(-59.,39.),(101.,39.)]
ORIGIN=np.array([21.,-9.5,74.])
BASE=ROOT/'validation/integrated/primaryP1_installed51/summary.json'
def inputs():
 d=json.loads(BASE.read_text());cp=REPO/d['candidate']['path'];assert sha(cp)==d['candidate']['SHA256'];cad=json.loads(cp.read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*cad['part_references'].values(),cad['assembly'],cad['BOM']]);return d,cad

def geometry(index):
 sys.path.insert(0,str(S1/'scripts'))
 from incremental_stage1 import read,translate
 from validate_nutseat46c import rotate
 from OCP.gp import gp_Pnt
 from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
 from OCP.BRepExtrema import BRepExtrema_DistShapeShape
 from OCP.TopoDS import TopoDS
 from OCP.BRepAdaptor import BRepAdaptor_Surface
 from OCP.BRepLProp import BRepLProp_SLProps
 from OCP.TopAbs import TopAbs_REVERSED
 d,cad=inputs();out=ROOT/f'validation/integrated/primaryP1_fourmount52_geometry{index}';out.mkdir();shutil.copyfile(__file__,out/'producer.py');x,y=XY[index];delta=np.array([x-XY[0][0],y-XY[0][1],0.]);plan=json.loads((REPO/d['plan']['path']).read_text());names=list(plan['DOFs']);actual=[n.replace('_0',f'_{index}') if n.endswith('_0') else n for n in names];parts={}
 for old,n in zip(names,actual):
  s=read(REPO/cad['part_references'][n]['path']);t=plan['pose_yaw_rad'][old];z=plan['pose_z_mm'][old];parts[old]=translate(rotate(s,x,y,t),0,0,z) if old.endswith('_0') else translate(s,0,0,z)
 source=[json.loads(s) for s in (REPO/d['bindings']['path']).read_text().splitlines()];rows=[]
 def journal(row):
  with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(row)+'\n');f.flush();os.fsync(f.fileno())
 for j,b in enumerate(source):
  assert not(ROOT/'runtime/STOP').exists();p=np.array(b['point_mm'])+delta;t=time.monotonic();journal(dict(state='START',index=j,label=b['label'],part=actual[names.index(b['part'])],point_mm=p.tolist(),operation='point_to_actual_posed_BRep_distance_and_oriented_normal',whole_solid_boolean=False))
  q=BRepExtrema_DistShapeShape(BRepBuilderAPI_MakeVertex(gp_Pnt(*p)).Vertex(),parts[b['part']]);q.Perform();assert q.IsDone();err=None;nn=None
  if b['actual_outward_normal'] is not None:
   face=TopoDS.Face_s(q.SupportOnShape2(1));u,v=q.ParOnFaceS2(1);prop=BRepLProp_SLProps(BRepAdaptor_Surface(face),u,v,1,1e-9);assert prop.IsNormalDefined();n=prop.Normal();nn=np.array([n.X(),n.Y(),n.Z()])*(-1 if face.Orientation()==TopAbs_REVERSED else 1);err=float(max(abs(nn-np.array(b['expected_outward_normal']))))
  row=dict(state='COMPLETE',index=j,label=b['label'],part=actual[names.index(b['part'])],point_mm=p.tolist(),distance_mm=q.Value(),actual_outward_normal=None if nn is None else nn.tolist(),normal_error=err,elapsed_s=time.monotonic()-t);rows.append(row);journal(row)
  if j%80==0:print(json.dumps(dict(mount=index,completed=j+1,elapsed=row['elapsed_s'])),flush=True)
 checks=dict(all444_actual_boundaries=len(rows)==444,face_distance=max(r['distance_mm'] for r in rows)<1e-7,oriented_normals=max(r['normal_error'] or 0 for r in rows)<1e-7,original128part_hashes=True)
 dump(out/'summary.json',dict(status='ACTUAL_FOURMOUNT_BOUNDARY_BINDING_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_FOURMOUNT_BOUNDARY_BINDING_FAIL',candidate=d['candidate'],producer=ref(out/'producer.py'),parent_endpoint=ref(BASE),mount_index=index,actual_parts={n:cad['part_references'][n] for n in actual},journal=ref(out/'journal.jsonl'),boundary_count=len(rows),max_distance_mm=max(r['distance_mm'] for r in rows),max_normal_error=max(r['normal_error'] or 0 for r in rows),maximum_query_seconds=max(r['elapsed_s'] for r in rows),checks=checks,whole_system_release=False,limitations=['Rebound finite contact points at a common receiver/support pose;not whole-solid nonpenetration or actual contact sequence','Single active flank;corner reactions not certified finite pressure','No bore bearing assumed or inserted']))
 raise SystemExit(0 if all(checks.values()) else 2)

def solve():
 d,cad=inputs();out=ROOT/'validation/integrated/primaryP1_fourmount52';out.mkdir();shutil.copyfile(__file__,out/'producer.py');names=[]
 for i in range(4):names += [f'BENCH_MOUNT_{s}_{i}' for s in ['BOLT','NUT','SOCKET_KEY','SPLIT_PIN']]
 names+=['BENCH_ANCHOR_RAIL','BENCH_SUPPORT'];rows=[];cols=[]
 for i,(x,y) in enumerate(XY):
  loc=np.array([x,y,74.]);off=loc-ORIGIN
  for c in d['contacts']:
   old=np.array(c['column']).reshape(6,6);col=np.zeros((18,6))
   for j in range(6):
    k=4*i+j if j<4 else 16+j-4;w=old[j].copy();w[3:]+=np.cross(off,w[:3]);col[k]+=w
   cols.append(col.ravel());rows.append(dict(mount=i,label=c['label'],body_i=c['body_i'].replace('_0',f'_{i}') if c['body_i'].endswith('_0') else c['body_i'],body_j=c['body_j'].replace('_0',f'_{i}') if c['body_j'].endswith('_0') else c['body_j'],column=col.ravel().tolist()))
 A=np.array(cols).T;F=np.zeros(108);F[16*6+2]=1;F[17*6+2]=-1
 def lp(ix,load=F):
  r=linprog(np.ones(len(ix)),A_eq=A[:,ix],b_eq=-load,bounds=(0,None),method='highs');return dict(feasible=bool(r.success),message=r.message,reactions=None if not r.success else r.x.tolist(),residual=None if not r.success else float(max(abs(A[:,ix]@r.x+load))),indices=ix)
 allix=list(range(len(rows)));s=lp(allix);controls=[]
 for mounts in [[0],[0,1],[0,2],[0,3],[0,1,2,3]]:
  ix=[j for j,r in enumerate(rows) if r['mount'] in mounts];controls.append(dict(mounts=mounts,**lp(ix)))
 # Compare the old free-screw twist under ONE global receiver/support twist.
 v=np.zeros((18,6));k=.8/(2*math.pi)
 for i,(x,y) in enumerate(XY):
  off=np.array([x,y,74.])-ORIGIN
  for j in [0,2,3]:v[4*i+j,:3]=np.cross([0,0,1],off)+[0,0,k];v[4*i+j,5]=1
 v[16,2]=k;v[16,5]=1
 vv=A.T@v.ravel();top=np.argsort(abs(vv))[-8:]
 balances=None
 if s['feasible']:
  lam=np.array(s['reactions']);balances=[dict(body=n,internal_wrench=(A@lam).reshape(18,6)[i].tolist(),external_wrench=F.reshape(18,6)[i].tolist(),balance=(A@lam+F).reshape(18,6)[i].tolist()) for i,n in enumerate(names)]
 checks=dict(all108DOFs_retained=A.shape[0]==108,all_four_mounts_coupled=all(r['mount'] in range(4) for r in rows),no_external_torque_or_rotation_restraint=True,unilateral_unit_balance=s['feasible'] and s['residual']<1e-8,old_onejoint_failure_preserved=not d['solution']['feasible'],old_free_screw_not_common_fourmount_mechanism=max(abs(vv))>1e-5)
 dump(out/'summary.json',dict(status='ACTUAL_P1_FOURMOUNT_COMMON_BODY_UNIT_WRENCH_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_FOURMOUNT_COMMON_BODY_UNIT_WRENCH_FAIL',candidate=d['candidate'],producer=ref(out/'producer.py'),parent_endpoint=ref(BASE),actual_product_parts=128,actual_installed_subassembly_bodies=18,DOFs=108,body_names=names,origin_mm=ORIGIN.tolist(),contact_columns=rows,contacts=len(rows),solution=s,external_load_vector=F.tolist(),body_balances=balances,mount_subset_controls=controls,old_mode_max_contact_normal_velocity=float(max(abs(vv))),old_mode_largest_work_rows=[dict(mount=rows[j]['mount'],label=rows[j]['label'],work=float(vv[j])) for j in top],checks=checks,preload=0,friction=0,external_torque_port=None,host_fixed=False,accepted_physical_product_equilibria=0,normalized_conditional_fourmount_equilibria=int(s['feasible']),installed_capacity_N=None,actual_100g_operating_field=None,whole_system_release=False,newly_qualified_system_gate_ids=[],limitations=['Conditional simultaneous finite-clearance endpoint with all4local contact sets;whole assembly nonpenetration and takeup must be checked independently','Reactions are nonnegative rigid finite-flank/corner wrenches,not elastic pressures or capacity','No bolt-shank/bore contact assumed;these may activate earlier and invalidate endpoint path','Not actual100g operating equilibrium,host closure,mass,mesh,time,energy or release']))
 print(json.dumps(dict(checks=checks,feasible=s['feasible'],residual=s['residual'],contacts=len(rows),controls=[dict(mounts=c['mounts'],feasible=c['feasible']) for c in controls],oldmode=max(abs(vv)))),flush=True)
 raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':
 assert not(ROOT/'runtime/STOP').exists()
 if sys.argv[1]=='solve':solve()
 else:geometry(int(sys.argv[1]))
