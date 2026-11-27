"""Actual thread-crest/receiver-bore active contacts;no smooth-envelope reactions.
Extends fresh same-product finiteendpoint with locally bound cylindricalpatchpoints.
"""
import sys,json,math,shutil,os,time
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
from primary_takeup53d import XY,C,rot
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

def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated/primaryP1_bore53';out.mkdir();shutil.copyfile(__file__,out/'producer.py');oldp=ROOT/'validation/integrated/primaryP1_contact53b/summary.json';old=json.loads(oldp.read_text());sp=ROOT/'validation/integrated/primaryP1_takeup53d/summary.json';state=json.loads(sp.read_text());cp=REPO[state['candidate']['path']][0] if False else REPO/state['candidate']['path'];assert sha(cp)==state['candidate']['SHA256'];cad=json.loads(cp.read_text());names=state['body_names'];origin=np.array(old['origin_mm']);contacts=list(old['contacts']);rows=[];poses={};ff={};active=[r for r in state['active_constraints'] if r['kind']=='conservative_crest_envelope'];op=state['opening_mm']
 def journal(row):
  with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(row)+'\n');f.flush();os.fsync(f.fileno())
 def prepare(n):
  if n in ff:return
  r=cad['part_references'][n];assert sha(REPO/r['path'])==r['SHA256'];p=state['poses'][n];s=translate(rotate(read(REPO/r['path']),*p['rotation_about_mm'][:2],p['yaw_rad']),*p['translation_after_rotation_mm']);poses[n]=s;ex=TopExp_Explorer(s,TopAbs_FACE);ff[n]=[]
  while ex.More():
   f=TopoDS.Face_s(ex.Current());ff[n].append((f,np.array(bounds(f))));ex.Next()
 def bind(n,p,expected):
  assert not(ROOT/'runtime/STOP').exists();prepare(n);p=np.array(p);t=time.monotonic();journal(dict(state='START',part=n,point_mm=p.tolist(),operation='local_trimmed_face_pointdistance_normal'));vertex=BRepBuilderAPI_MakeVertex(gp_Pnt(*p)).Vertex();found=[]
  for k,(f,b) in enumerate(ff[n]):
   if np.any(p<b[:3]-1e-6) or np.any(p>b[3:]+1e-6):continue
   d=BRepExtrema_DistShapeShape(vertex,f);d.Perform();assert d.IsDone()
   if d.Value()>1e-7:continue
   try:
    u,v=d.ParOnFaceS2(1);prop=BRepLProp_SLProps(BRepAdaptor_Surface(f),u,v,1,1e-9)
    if not prop.IsNormalDefined():continue
    dr=prop.Normal();nn=np.array([dr.X(),dr.Y(),dr.Z()])*(-1 if f.Orientation()==TopAbs_REVERSED else 1);err=float(max(abs(nn-expected)));found.append(dict(face=k,distance_mm=d.Value(),normal_error=err,normal=nn.tolist()))
   except Exception:continue
  good=[r for r in found if r['normal_error']<1e-7];best=min(good,key=lambda r:r['normal_error']) if good else None;r=dict(state='COMPLETE',part=n,point_mm=p.tolist(),bound=bool(good),matches=found,elapsed_s=time.monotonic()-t);rows.append(r);journal(r);return best
 bore=[]
 for r in active:
  i=int(r['label'].rsplit('_',1)[1]);bn=f'BENCH_MOUNT_BOLT_{i}';rn='BENCH_ANCHOR_RAIL' if r['label'].startswith('bore_receiver') else 'BENCH_SUPPORT';axis=XY[i]+state['poses'][bn]['translation_after_rotation_mm'][:2];rc=rot(state['receiver_yaw_rad'])@(XY[i]-C)+C+state['receiver_translation_mm'] if rn=='BENCH_ANCHOR_RAIL' else XY[i];direction=(axis-rc)/np.linalg.norm(axis-rc);p2=axis+2.488*direction;assert np.linalg.norm(p2-rc)-2.75<1e-7;zs=np.arange(66.1+op,73.9+op,.025) if rn=='BENCH_ANCHOR_RAIL' else np.arange(60.1,65.9,.025);accepted=[]
  for z in zs:
   if accepted and z-accepted[-1]['point_mm'][2]<.6:continue
   p=np.r_[p2,z];nb=np.r_[direction,0.];b=bind(bn,p,nb)
   if b is None:continue
   w=bind(rn,p,-nb)
   if w is None:continue
   force=-nb;wi=np.r_[force,np.cross(p-origin,force)];col=np.zeros((18,6));col[names.index(bn)]+=wi;col[names.index(rn)]-=wi;co=dict(label=r['label']+'_crest_'+str(len(accepted)),body_i=bn,body_j=rn,point_mm=p.tolist(),force_on_i=force.tolist(),weight=1.,column=col.ravel().tolist(),kind='actual_cylindrical_thread_crest_bore_point',bolt_binding=b,receiver_binding=w);contacts.append(co);accepted.append(co)
   if len(accepted)==8:break
  bore.append(dict(envelope_constraint=r,actual_bound_contact_points=accepted,not_ideal_smooth_shank=True))
 A=np.array([r['column'] for r in contacts]).T;F=np.array(old['external_load']);
 def solve(ix):
  r=linprog(np.ones(len(ix)),A_eq=A[:,ix],b_eq=-F,bounds=(0,None),method='highs');return dict(feasible=bool(r.success),message=r.message,indices=ix,multipliers=None if not r.success else r.x.tolist(),residual=None if not r.success else float(max(abs(A[:,ix]@r.x+F))))
 solution=solve(list(range(len(contacts))));controls=[]
 for prefix in ['bore','guide','thread','socket','keycage','nutcage']:
  controls.append(dict(removed=prefix,**solve([i for i,r in enumerate(contacts) if not r['label'].startswith(prefix)])))
 certificate=None
 if not solution['feasible']:
  r=linprog(np.zeros(108),A_ub=-A.T,b_ub=np.zeros(A.shape[1]),A_eq=F[None,:],b_eq=[1.],bounds=[(-10000,10000)]*108,method='highs')
  if r.success:certificate=dict(twist=r.x.tolist(),external_positive_work=float(F@r.x),minimum_contact_work=float(min(A.T@r.x)))
 checks=dict(two_actual_borepaths=len(bore)==2 and all(len(r['actual_bound_contact_points'])>=2 for r in bore),fresh_parent_all1740bindings=old['checks']['all_actual_bindings'],all108DOFs_retained=A.shape[0]==108,unit_separation_equilibrium=solution['feasible'] and solution['residual']<1e-8,no_bore_envelope_force=True,no_declared_fixation=True)
 dump(out/'summary.json',dict(status='ACTUAL_P1_FRESH_GUIDE_BORE_THREAD_108DOF_UNIT_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_FRESH_GUIDE_BORE_THREAD_UNIT_EQUILIBRIUM_FAIL',candidate=ref(cp),producer=ref(out/'producer.py'),pose_source=ref(sp),parent_contact=ref(oldp),journal=ref(out/'journal.jsonl'),checks=checks,bore_contacts=bore,local_face_queries=len(rows),maximum_query_seconds=max(r['elapsed_s'] for r in rows),contact_count=len(contacts),contacts=contacts,origin_mm=origin.tolist(),body_names=names,external_load=F.tolist(),solution=solution,removed_path_controls=controls,Farkas_certificate=certificate,body_balances=None if not solution['feasible'] else (A@np.array(solution['multipliers'])+F).reshape(18,6).tolist(),accepted_physical_product_equilibria=0,normalized_conditional_equilibria=int(solution['feasible']),installed_capacity_N=None,actual_100g_operating_field=None,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Conditional actual finite108DOFunitstatics only,not operating load/dynamics/elasticpressure/strength orglobalenergy','Borebearing points bound on actual2.488mmthreadcrest cylinders and2.75mmreceiverbore,not substitute smooth shank or invented friction','Coaxial planar finitepose;actualpin clearance/full128assembly/entirethreadnonpenetration/path/convergence require independent checks','Corner/crestcontact pressure andmaterial/process/source minimum remain unqualified;nohardware/Stage3']))
 print(json.dumps(dict(checks=checks,residual=solution['residual'],contacts=len(contacts),borepoints=[len(r['actual_bound_contact_points']) for r in bore],Farkas=certificate is not None)),flush=True);raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
