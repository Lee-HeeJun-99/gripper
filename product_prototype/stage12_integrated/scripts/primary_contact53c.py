"""Fresh finite actual-boundary and108DOF unilateral statics at guide-engaged pose.
No wholethread Boolean and no previous endpoint traction transfer.
"""
import sys,json,math,shutil,time,os
import numpy as np
from scipy.optimize import linprog
from numpy.polynomial.legendre import leggauss
from baseline_registry import ROOT,REPO,S1,ref,dump,sha
from primary_takeup53e import rot,XY,C,K,CLEAR
from primary_flank50 import integrate,RPI
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,bounds
from validate_nutseat46c import rotate
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE,TopAbs_REVERSED
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepLProp import BRepLProp_SLProps
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.gp import gp_Pnt
ORIGIN=np.array([21.,-9.5,74.])
def main():
 out=ROOT/'validation/integrated/primaryP1_contact53c';out.mkdir();shutil.copyfile(__file__,out/'producer.py');sp=ROOT/'validation/integrated/primaryP1_takeup53e/summary.json';state=json.loads(sp.read_text());cp=REPO/state['candidate']['path'];assert sha(cp)==state['candidate']['SHA256'];cad=json.loads(cp.read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*cad['part_references'].values(),cad['assembly'],cad['BOM']]);names=state['body_names'];posed={};faces={};bindings=[];contacts=[];op=state['opening_mm']
 def journal(row):
  with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(row)+'\n');f.flush();os.fsync(f.fileno())
 for n in names:
  p=state['poses'][n];s=read(REPO/cad['part_references'][n]['path']);s=translate(rotate(s,*p['rotation_about_mm'][:2],p['yaw_rad']),*p['translation_after_rotation_mm']);posed[n]=s;ff=[];ex=TopExp_Explorer(s,TopAbs_FACE)
  while ex.More():
   f=TopoDS.Face_s(ex.Current());ff.append((f,np.array(bounds(f))));ex.Next()
  faces[n]=ff
 def bind(label,body,p,normal=None):
  assert not(ROOT/'runtime/STOP').exists();t=time.monotonic();p=np.array(p);journal(dict(state='START',label=label,part=body,point_mm=p.tolist(),operation='trimmed_local_face_distance_and_normal',whole_BRep_sequence=False));v=BRepBuilderAPI_MakeVertex(gp_Pnt(*p)).Vertex();candidates=[]
  for k,(face,b) in enumerate(faces[body]):
   lower=float(np.linalg.norm(np.maximum(np.maximum(b[:3]-p,p-b[3:]),0)))
   if lower<1e-6:candidates.append((k,face))
  best=None
  for k,f in candidates:
   d=BRepExtrema_DistShapeShape(v,f);d.Perform();assert d.IsDone();nn=None;err=None
   if normal is not None and d.Value()<1e-6:
    # Wall point is inside actual trimmed wall;distance may choose an edge only on corner body.
    try:
     u,w=d.ParOnFaceS2(1);prop=BRepLProp_SLProps(BRepAdaptor_Surface(f),u,w,1,1e-9)
     if prop.IsNormalDefined():
      n=prop.Normal();nn=np.array([n.X(),n.Y(),n.Z()])*(-1 if f.Orientation()==TopAbs_REVERSED else 1);err=float(max(abs(nn-normal)))
    except Exception:pass
   score=(d.Value(),err if err is not None else (0 if normal is None else 100))
   if best is None or (score[0]<1e-7 and best[0][0]<1e-7 and score[1]<best[0][1]) or (score[0]<best[0][0] and not(score[0]<1e-7 and best[0][0]<1e-7)):best=(score,k,nn)
  ok=best is not None and best[0][0]<1e-7 and (normal is None or best[0][1]<1e-7)
  r=dict(state='COMPLETE',label=label,part=body,point_mm=p.tolist(),expected_normal=None if normal is None else list(normal),distance_mm=None if best is None else best[0][0],normal_error=None if normal is None or best is None else best[0][1],face_index=None if best is None else best[1],candidate_faces=len(candidates),bound=bool(ok),elapsed_s=time.monotonic()-t);bindings.append(r);journal(r);return bool(ok)
 def add(label,ni,nj,p,n,weight=1,kind='rigid_finite_boundary_point'):
  p=np.array(p);n=np.array(n);wi=np.r_[n,np.cross(p-ORIGIN,n)]*weight;col=np.zeros((18,6));col[names.index(ni)]+=wi;col[names.index(nj)]-=wi;contacts.append(dict(label=label,body_i=ni,body_j=nj,point_mm=p.tolist(),force_on_i=n.tolist(),weight=weight,column=col.ravel().tolist(),kind=kind))
 # Fresh actual active corner/wall contacts at TWO safe interior axial heights.
 for r in state['active_constraints']:
  kind=r['kind'];i=r.get('i');xy=r.get('point_xy');normal=np.r_[r.get('inward_xy',[0,0]),0.]
  if kind=='nutcage':ni=f'BENCH_MOUNT_NUT_{i}';nj='BENCH_SUPPORT';zs=[55.5,59.8]
  elif kind=='socket':ni=f'BENCH_MOUNT_SOCKET_KEY_{i}';nj=f'BENCH_MOUNT_BOLT_{i}';zs=[76.8+op,78.8+op]
  elif kind=='keycage':ni=f'BENCH_MOUNT_SOCKET_KEY_{i}';nj='BENCH_ANCHOR_RAIL';zs=[79.4+op,85.+op]
  elif kind=='guide':ni='BENCH_ANCHOR_RAIL';nj='BENCH_SUPPORT';zs=[60.2+op,65.8]
  else:continue
  for z in zs:
   point=np.r_[xy,z];a=bind(r['label']+'_wall_'+str(z),nj,point,normal);b=bind(r['label']+'_corner_'+str(z),ni,point)
   if a and b:add(r['label']+'_'+str(z),ni,nj,point,normal)
 # Actual annular seat interiors around each current common bolt/nutaxis.
 for i in range(4):
  axis=XY[i]+np.array(state['poses'][f'BENCH_MOUNT_BOLT_{i}']['translation_after_rotation_mm'][:2])
  for j in range(8):
   th=j*math.pi/4;xy=axis+3.3*np.array([math.cos(th),math.sin(th)])
   for typ,z,ni,nj,n in [('head',74+op,f'BENCH_MOUNT_BOLT_{i}','BENCH_ANCHOR_RAIL',np.array([0.,0.,1.])),('nut',60.,f'BENCH_MOUNT_NUT_{i}','BENCH_SUPPORT',np.array([0.,0.,-1.]))]:
    p=np.r_[xy,z];a=bind(f'{typ}{i}_{j}_wall',nj,p,n);b=bind(f'{typ}{i}_{j}_face',ni,p,-n)
    if a and b:add(f'{typ}seat_{i}_{j}',ni,nj,p,n)
 # One loaded helical flank;fresh axis/phase/normal quadrature at each actual posed bolt/nut.
 q,w=leggauss(2);_,patches=integrate(2)
 for i in range(4):
  bn=f'BENCH_MOUNT_BOLT_{i}';nn=f'BENCH_MOUNT_NUT_{i}';nu=state['poses'][nn]['yaw_rad'];axis=XY[i]+np.array(state['poses'][bn]['translation_after_rotation_mm'][:2]);R=rot(nu)
  for idx,patch in enumerate(patches):
   if patch['side']!=-1:continue
   lo,hi=patch['theta_range'];col=np.zeros(108);samples=[];valid=True
   for qr,wr in zip(q,w):
    r=2.32+.1*qr
    for qt,wt in zip(q,w):
     th=(lo+hi)/2+(hi-lo)/2*qt;z=K*th-(.8/4+(r-RPI)/math.sqrt(3));point=np.r_[axis+R@np.array([r*math.cos(th),r*math.sin(th)]),54+z];raw=np.array([math.cos(th)/math.sqrt(3)+K/r*math.sin(th),math.sin(th)/math.sqrt(3)-K/r*math.cos(th),1.]);normal=-raw/np.linalg.norm(raw);normal[:2]=R@normal[:2];area=r*np.linalg.norm(raw)*.1*(hi-lo)/2*wr*wt
     good=bind(f'thread_{i}_{idx}_nut_{qr}_{qt}',nn,point,normal) and bind(f'thread_{i}_{idx}_bolt_{qr}_{qt}',bn,point,-normal);valid=valid and good;wi=np.r_[normal,np.cross(point-ORIGIN,normal)]*area;col[names.index(bn)*6:names.index(bn)*6+6]+=wi;col[names.index(nn)*6:names.index(nn)*6+6]-=wi;samples.append(dict(point_mm=point.tolist(),normal=normal.tolist(),area_mm2=area))
   if valid:contacts.append(dict(label=f'thread_{i}_{idx}',body_i=bn,body_j=nn,column=col.tolist(),quadrature=samples,kind='finite_helical_patch_uniform_traction'))
  print(json.dumps(dict(mount=i,bindings=len(bindings),failed=sum(not b['bound'] for b in bindings))),flush=True)
 A=np.array([r['column'] for r in contacts]).T;F=np.zeros(108);F[16*6+2]=1;F[17*6+2]=-1
 def solve(ix,force=F):
  s=linprog(np.ones(len(ix)),A_eq=A[:,ix],b_eq=-force,bounds=(0,None),method='highs');return dict(feasible=bool(s.success),message=s.message,indices=ix,residual=None if not s.success else float(max(abs(A[:,ix]@s.x+force))),multipliers=None if not s.success else s.x.tolist())
 solution=solve(list(range(len(contacts))));controls=[]
 for omitted in ['guide','thread','nutcage','socket','keycage']:
  ix=[i for i,r in enumerate(contacts) if not r['label'].startswith(omitted)];controls.append(dict(removed=omitted,**solve(ix)))
 # Independent randomvirtualwork uses saved pointquadrature,not copiedcolumn dotproducts.
 rng=np.random.default_rng(53);dq=rng.normal(size=(18,6));errors=[]
 for r in contacts:
  bi=names.index(r['body_i']);bj=names.index(r['body_j']);direct=0
  for sm in r.get('quadrature',[dict(point_mm=r.get('point_mm'),normal=r.get('force_on_i'),area_mm2=r.get('weight'))]):
   rr=np.array(sm['point_mm'])-ORIGIN;dv=dq[bi,:3]-dq[bj,:3]+np.cross(dq[bi,3:]-dq[bj,3:],rr);direct+=np.dot(sm['normal'],dv)*sm['area_mm2']
  errors.append(abs(float(np.array(r['column'])@dq.ravel()-direct)))
 checks=dict(all_actual_bindings=all(r['bound'] for r in bindings),finite108DOFs=A.shape[0]==108,no_external_torque_or_declared_rotation_fixation=True,unit_separation_equilibrium=solution['feasible'] and solution['residual']<1e-8,virtualwork=max(errors)<1e-10)
 dump(out/'summary.json',dict(status='ACTUAL_P1_GUIDE_ENGAGED_108DOF_UNIT_CONTACT_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_GUIDE_ENGAGED_BOUNDARY_OR_UNIT_EQUILIBRIUM_FAIL',candidate=ref(cp),pose_source=ref(sp),producer=ref(out/'producer.py'),journal=ref(out/'journal.jsonl'),checks=checks,DOFs=108,body_names=names,origin_mm=ORIGIN.tolist(),actual_parts=128,boundary_count=len(bindings),failed_bindings=[b for b in bindings if not b['bound']],max_distance_mm=max(b['distance_mm'] or 0 for b in bindings),contacts=contacts,contact_count=len(contacts),external_load=F.tolist(),solution=solution,removed_path_controls=controls,virtualwork_error=max(errors),maximum_query_seconds=max(b['elapsed_s'] for b in bindings),all_body_balances=None if not solution['feasible'] else (A@np.array(solution['multipliers'])+F).reshape(18,6).tolist(),accepted_physical_product_equilibria=0,normalized_conditional_unit_equilibria=int(solution['feasible']),newly_qualified_system_gate_ids=[],whole_system_release=False,operating_load_N=None,capacity_N=None,limitations=['Conditional rigid18body endpoint with active actualpoint/corner/finiteflank contacts only;not elasticpressures/capacity or100gproductequilibrium','Coaxial planar candidate search is not108DOFcontacttakeup dynamics;full108DOFs retained only in statics','Pin sixDOFs retained but pinpath clearances/retention/loads still need separate checks','Freshgeometry binding is not full128partassemblysweep,wholethreadCCD,convergence/globalenergy orhostcertification']))
 print(json.dumps(dict(checks=checks,contacts=len(contacts),failed_bindings=sum(not b['bound'] for b in bindings),residual=solution['residual'])),flush=True)
 raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
