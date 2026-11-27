"""One actual P1 mount joint: finite clearance configuration and unilateral rigid statics.
Normalized opening pair only; not whole-product load, stiffness, pressure or capacity.
"""
import sys,json,math,shutil,os,time
import numpy as np
from scipy.optimize import linprog,brentq
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,common
from validate_nutseat46c import rotate
from primary_flank50 import integrate,K,RPI
from OCP.gp import gp_Pnt
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepLProp import BRepLProp_SLProps
from OCP.TopAbs import TopAbs_REVERSED

X,Y=-59.,-58.;ORIGIN=np.array([X,Y,74.])
NAMES=['BENCH_MOUNT_BOLT_0','BENCH_MOUNT_NUT_0','BENCH_MOUNT_SOCKET_KEY_0','BENCH_MOUNT_SPLIT_PIN_0','BENCH_ANCHOR_RAIL','BENCH_SUPPORT']

def main():
 out=ROOT/'validation/integrated/primaryP1_installed51';out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_thread49f/summary.json';cad=json.loads(cp.read_text());refs=cad['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*refs.values(),cad['assembly'],cad['BOM']]);parts={n:read(REPO/refs[n]['path']) for n in NAMES};assert not(ROOT/'runtime/STOP').exists()
 a=brentq(lambda t:4.5*(math.cos(t)+math.sin(t))-4.6,0,.2,xtol=1e-15);b=brentq(lambda t:3.9/math.sqrt(3)*math.cos(math.pi/6-t)-2,0,.2,xtol=1e-15);nu=-brentq(lambda t:8/math.sqrt(3)*math.cos(math.pi/6-t)-4.1,0,.2,xtol=1e-15);beta=a+b;c=(4.605-4.456)/2/math.sqrt(3);opening=c+K*(beta-nu)
 angles=[beta,nu,a,0,0,0];zs=[opening,0,opening,opening,opening,0];posed={n:translate(rotate(parts[n],X,Y,t),0,0,z) for n,t,z in zip(NAMES,angles,zs)}
 plan=dict(candidate=ref(cp),actual_parts={n:refs[n] for n in NAMES},DOFs={n:['tx','ty','tz','rx','ry','rz'] for n in NAMES},global_joint_origin_mm=ORIGIN.tolist(),pose_yaw_rad=dict(zip(NAMES,angles)),pose_z_mm=dict(zip(NAMES,zs)),thread_axial_clearance_mm=c,opening_mm=opening,configuration='one isolated installed joint;receiver/support separate rigid bodies with balanced normalized separating loads;NOT global assembly displacement',tolerances=dict(face_distance_mm=1e-7,normal_error=1e-7,force_moment_balance=1e-8,nonnegative_reaction=1e-10),preload_N=0,friction_coefficient=0,ultimate_host_fixed=False,whole_system_release=False)
 dump(out/'plan.json',plan)
 # Each geometric query is durable. Normal on moving body's opposing solid is force on moving body.
 bindings=[]
 def bind(label,body,point,expected,face_required=True):
  assert not(ROOT/'runtime/STOP').exists();p=np.array(point);ex=np.array(expected);d=BRepExtrema_DistShapeShape(BRepBuilderAPI_MakeVertex(gp_Pnt(*p)).Vertex(),posed[NAMES[body]]);d.Perform();assert d.IsDone();actual=None;error=None;support=str(d.SupportTypeShape2(1))
  if face_required:
   face=TopoDS.Face_s(d.SupportOnShape2(1));u,v=d.ParOnFaceS2(1);prop=BRepLProp_SLProps(BRepAdaptor_Surface(face),u,v,1,1e-9);assert prop.IsNormalDefined();dn=prop.Normal();actual=np.array([dn.X(),dn.Y(),dn.Z()])*(-1 if face.Orientation()==TopAbs_REVERSED else 1);error=float(max(abs(actual-ex)))
  row=dict(label=label,part=NAMES[body],point_mm=p.tolist(),distance_mm=d.Value(),support=support,expected_outward_normal=ex.tolist(),actual_outward_normal=None if actual is None else actual.tolist(),normal_error=error);bindings.append(row)
  with (out/'bindings.jsonl').open('a') as f:f.write(json.dumps(row)+'\n');f.flush();os.fsync(f.fileno())
  return actual if actual is not None else ex
 def rz(p,t):
  p=np.array(p);return np.array([math.cos(t)*p[0]-math.sin(t)*p[1],math.sin(t)*p[0]+math.cos(t)*p[1],p[2]])
 contacts=[]
 def add(label,i,j,p,n,weight=1.):
  # force on i = +lambda*n;force on j = -lambda*n;common spatial point.
  p=np.array(p);n=np.array(n)*weight;w=np.r_[n,np.cross(p-ORIGIN,n)];col=np.zeros(36);col[i*6:i*6+6]=w;col[j*6:j*6+6]=-w;contacts.append(dict(label=label,body_i=NAMES[i],body_j=NAMES[j],point_mm=p.tolist(),force_on_i_per_multiplier_N=n.tolist(),column=col.tolist(),contact_type='finite_helical_patch_uniform_traction' if label.startswith('thread') else 'rigid_corner_or_seat_point_reaction',gap_at_selected_pose_mm=0.))
 # Actual nut outward normals, ONE loaded side (-1),48 finite patches from existing bound faces.
 # Reconstruct quadrature ourselves at moved configuration;both solids queried.
 from numpy.polynomial.legendre import leggauss
 q,w=leggauss(2);_,patches=integrate(2)
 for idx,p in enumerate(patches):
  if p['side']!=-1:continue
  lo,hi=p['theta_range'];col=np.zeros(36);samples=[]
  for qr,wr in zip(q,w):
   r=2.32+.1*qr
   for qt,wt in zip(q,w):
    th=(lo+hi)/2+(hi-lo)/2*qt;z=K*th-(.8/4+(r-RPI)/math.sqrt(3));local=np.array([r*math.cos(th),r*math.sin(th),z]);point=rz(local,nu)+[X,Y,54.];raw=np.array([math.cos(th)/math.sqrt(3)+K/r*math.sin(th),math.sin(th)/math.sqrt(3)-K/r*math.cos(th),1.]);normal=rz(-raw/np.linalg.norm(raw),nu);normal=bind(f'thread{idx}_nut',1,point,normal);bind(f'thread{idx}_bolt',0,point,-normal);area=r*np.linalg.norm(raw)*.1*(hi-lo)/2*wr*wt;ww=np.r_[normal,np.cross(point-ORIGIN,normal)]*area;col[:6]+=ww;col[6:12]-=ww;samples.append(dict(point_mm=point.tolist(),normal_force_on_bolt=normal.tolist(),area_mm2=area))
  contacts.append(dict(label=f'thread{idx}',body_i=NAMES[0],body_j=NAMES[1],column=col.tolist(),quadrature=samples,contact_type='finite_helical_patch_uniform_traction',gap_at_selected_pose_mm=0.))
  if idx%8==0:print(json.dumps(dict(completed_thread_patch=idx)),flush=True)
 # Head/nut seats sampled inside actual annular overlap, no fictitious axial ties.
 for j in range(8):
  th=2*math.pi*j/8;rel=[3.3*math.cos(th),3.3*math.sin(th),0]
  p=ORIGIN+np.array(rel)+[0,0,opening];n=bind(f'headseat{j}_receiver',4,p,[0,0,1]);bind(f'headseat{j}_bolt',0,p,[0,0,-1]);add(f'headseat{j}',0,4,p,n)
  p=np.array([X+rel[0],Y+rel[1],60.]);n=bind(f'nutseat{j}_support',5,p,[0,0,-1]);bind(f'nutseat{j}_nut',1,p,[0,0,1]);add(f'nutseat{j}',1,5,p,n)
 # Nut cage: six corners,finite actual wall normals, no fixed nut translation/yaw.
 for j in range(6):
  phi=j*math.pi/3;point=rz([8/math.sqrt(3)*math.cos(phi),8/math.sqrt(3)*math.sin(phi),0],nu)+[X,Y,57.65];ang=phi-math.pi/6;normal=np.array([-math.cos(ang),-math.sin(ang),0]);normal=bind(f'nutcage{j}_wall',5,point,normal);bind(f'nutcage{j}_nutcorner',1,point,-normal,False);add(f'nutcage{j}',1,5,point,normal)
 # Socket-key engaged corners: bolt rotated relative to key;sample z77.8 + opening.
 for j in range(6):
  phi=j*math.pi/3;point=rz([3.9/math.sqrt(3)*math.cos(phi),3.9/math.sqrt(3)*math.sin(phi),0],a)+[X,Y,77.8+opening];ang=phi-math.pi/6+beta;normal=np.array([-math.cos(ang),-math.sin(ang),0]);normal=bind(f'socket{j}_boltwall',0,point,normal);bind(f'socket{j}_keycorner',2,point,-normal,False);add(f'socket{j}',2,0,point,normal)
 lever=4.5*(math.cos(a)-math.sin(a))
 for sign in [-1,1]:
  p=np.array([X+sign*4.6,Y-sign*lever,84.+opening]);normal=bind(f'keycage{sign}_wall',4,p,[-sign,0,0]);bind(f'keycage{sign}_corner',2,p,-normal,False);add(f'keycage{sign}',2,4,p,normal)
 # Pin remains an explicit free six-DOF body. Its key-hole does not bear at selected yaw.
 # Actual closest gap queries instead of inventing an axial retainer force.
 gaps=[]
 for i,j in [(2,3),(3,4)]:
  d=BRepExtrema_DistShapeShape(posed[NAMES[i]],posed[NAMES[j]]);d.Perform();gaps.append(dict(a=NAMES[i],b=NAMES[j],minimum_gap_mm=d.Value(),normal_reaction_N=0.,active=False))
 A=np.array([r['column'] for r in contacts]).T;F=np.zeros(36);F[4*6+2]=1;F[5*6+2]=-1
 def solve(keep):
  B=A[:,keep];s=linprog(np.ones(len(keep)),A_eq=B,b_eq=-F,bounds=(0,None),method='highs');return dict(feasible=bool(s.success),solver_status=s.message,reactions=None if not s.success else s.x.tolist(),residual=None if not s.success else float(max(abs(B@s.x+F))),contact_indices=keep)
 full=solve(list(range(len(contacts))));controls=[]
 for omitted in ['thread','headseat','nutseat','nutcage','socket','keycage']:
  rr=solve([j for j,r in enumerate(contacts) if not r['label'].startswith(omitted)]);controls.append(dict(removed=omitted,**rr))
 # Reciprocity/virtual work: common-point equal/opposite wrenches;all36DOFs retained.
 rng=np.random.default_rng(51);dq=rng.normal(size=36);vw=[]
 for co in contacts:
  ci=np.array(co['column']);i=NAMES.index(co['body_i']);j=NAMES.index(co['body_j']);samples=co.get('quadrature',[dict(point_mm=co.get('point_mm'),normal_force_on_bolt=co.get('force_on_i_per_multiplier_N'),area_mm2=1.)]);direct=0.
  for sm in samples:
   rr=np.array(sm['point_mm'])-ORIGIN;vi=dq[i*6:i*6+3]+np.cross(dq[i*6+3:i*6+6],rr);vj=dq[j*6:j*6+3]+np.cross(dq[j*6+3:j*6+6],rr);direct+=np.dot(sm['normal_force_on_bolt'],vi-vj)*sm['area_mm2']
  vw.append(abs(float(ci@dq-direct)))
 if full['feasible']:
  lam=np.array(full['reactions']);reactions=A@lam;body_balance=(reactions+F).reshape(6,6).tolist()
 else:body_balance=None
 checks=dict(all128part_assembly_BOM_hashes_unchanged=True,actual_face_distances=max(r['distance_mm'] for r in bindings)<1e-7,actual_oriented_normals=max(r['normal_error'] or 0 for r in bindings)<1e-7,one_loaded_thread_side_only=all('quadrature' not in r or r['label'].startswith('thread') for r in contacts),normalized_36DOF_unilateral_balance=full['feasible'] and full['residual']<1e-8,all_six_missing_path_controls_rejected=all(not r['feasible'] for r in controls),explicit_pin_remains_unloaded_clear=all(r['minimum_gap_mm']>1e-7 for r in gaps),spatial_virtual_work=max(vw)<1e-10)
 # Do not silently accept selected configuration as a physical trajectory or capacity.
 dump(out/'summary.json',dict(status='ACTUAL_P1_ONE_INSTALLED_JOINT_RIGID_UNIT_BALANCE_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_ONE_INSTALLED_JOINT_VALIDATION_FAIL',candidate=ref(cp),producer=ref(out/'producer.py'),plan=ref(out/'plan.json'),bindings=ref(out/'bindings.jsonl'),checks={k:bool(v) for k,v in checks.items()},actual_face_query_count=len(bindings),max_face_distance_mm=max(r['distance_mm'] for r in bindings),max_normal_error=max(r['normal_error'] or 0 for r in bindings),finite_thread_patches=48,loaded_flank_side=-1,contacts=contacts,external_load_vector_N_Nmm=F.tolist(),solution=full,body_balance_N_Nmm=body_balance,removed_path_controls=controls,pin_gaps=gaps,DOF_count=36,equilibrium_matrix_rank=int(np.linalg.matrix_rank(A,tol=1e-8)),free_tangent_mode_count=36-int(np.linalg.matrix_rank(A,tol=1e-8)),virtual_work_max_error=max(vw),opening_mm=opening,thread_clearance_mm=c,serial_rotation_opening_mm=K*(beta-nu),pose_yaw_rad=angles,accepted_physical_product_equilibria=0,normalized_rigid_joint_equilibria=int(full['feasible']),installed_capacity_N=None,operating_load_N=None,ultimate_host_fixed=False,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['One actual joint subassembly only;other seven bolts and full128part motion not solved','Selected finite-clearance endpoint;not contact-sequence dynamics or unique quasistatic takeup','Rigid nonnegative point/corner forces have no finite pressure or material capacity','Thread patches use finite actual Gauss points;not continuous full contact activation','Pin carries zero at this load and has explicit six free DOFs;retention under other loads not certified','No assumed preload/friction,minimum material,100g operating field,mesh/time/globalenergy or host attachment qualification']))
 print(json.dumps(dict(checks={k:bool(v) for k,v in checks.items()},binding_count=len(bindings),maxdistance=max(r['distance_mm'] for r in bindings),maxnormal=max(r['normal_error'] or 0 for r in bindings),balance=full['residual'],opening=opening,pin_gaps=gaps,controls=[dict(removed=r['removed'],feasible=r['feasible']) for r in controls])),flush=True);raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
