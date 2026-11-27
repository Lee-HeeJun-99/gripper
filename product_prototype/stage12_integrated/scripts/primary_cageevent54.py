"""Finite actual inactive nutcage event along one component of spatial witness.
Not a wholeproduct trajectory;old contact tractions are never transferred.
"""
import json,sys,math,shutil,os,time
import numpy as np
from scipy.optimize import brentq
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,bounds,common
from validate_nutseat46c import rotate
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE,TopAbs_REVERSED
from OCP.TopoDS import TopoDS
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepLProp import BRepLProp_SLProps
from OCP.gp import gp_Pnt
out=ROOT/'validation/integrated/primaryP1_cageevent54';out.mkdir();shutil.copyfile(__file__,out/'producer.py');ap=ROOT/'validation/integrated/primaryP1_audit54b/summary.json';audit=json.loads(ap.read_text());assert all(audit['checks'].values());sp=ROOT/'validation/integrated/primaryP1_independent54f/summary.json';st=json.loads(sp.read_text());cp=REPO/st['candidate']['path'];assert sha(cp)==st['candidate']['SHA256'];cad=json.loads(cp.read_text());bn='BENCH_MOUNT_NUT_1';w=np.array(next(r['twist'] for r in audit['Farkas_certificate']['body_twists'] if r['body']==bn));assert np.linalg.norm(w[3:])<1e-10;pose=st['poses'][bn];nut=translate(rotate(read(REPO/cad['part_references'][bn]['path']),*pose['rotation_about_mm'][:2],pose['yaw_rad']),*pose['translation_after_rotation_mm']);support=read(REPO/cad['part_references']['BENCH_SUPPORT']['path']);events=[]
for row in st['all_constraints']:
 if row['kind']!='nutcage' or row['i']!=1:continue
 n=np.r_[row['inward_xy'],0.];dg=n@w[:3]
 if dg< -1e-10 and row['gap_mm']>1e-7:events.append(dict(row=row,gdot=float(dg),scale=float(row['gap_mm']/-dg)))
event=min(events,key=lambda r:r['scale']);scale=event['scale'];rr=event['row'];point=np.r_[rr['point_xy'],57.4]+scale*w[:3];normal=np.r_[rr['inward_xy'],0.];results=[]
def journal(r):
 with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(r)+'\n');f.flush();os.fsync(f.fileno())
def bind(shape,name,point,expected=None):
 journal(dict(state='START',part=name,operation='ONE_local_trimmed_face_distance_normal',point_mm=point.tolist()));v=BRepBuilderAPI_MakeVertex(gp_Pnt(*point)).Vertex();ex=TopExp_Explorer(shape,TopAbs_FACE);best=None;i=0
 while ex.More():
  f=TopoDS.Face_s(ex.Current());ex.Next();b=np.array(bounds(f));i+=1
  if np.linalg.norm(np.maximum(np.maximum(b[:3]-point,point-b[3:]),0))>1e-6:continue
  d=BRepExtrema_DistShapeShape(v,f);d.Perform();err=None
  if expected is not None and d.Value()<1e-7:
   try:
    u,w0=d.ParOnFaceS2(1);pr=BRepLProp_SLProps(BRepAdaptor_Surface(f),u,w0,1,1e-9);nn=pr.Normal();nv=np.array([nn.X(),nn.Y(),nn.Z()])*(-1 if f.Orientation()==TopAbs_REVERSED else 1);err=float(max(abs(nv-expected)))
   except Exception:pass
  score=d.Value()+(0 if expected is None else (err if err is not None else 100))
  if best is None or score<best['score']:best=dict(score=score,face_index=i-1,distance_mm=d.Value(),normal_error=err)
 journal(dict(state='COMPLETE',part=name,**best));return best
newnut=translate(nut,*(scale*w[:3]));nb=bind(newnut,bn,point);sb=bind(support,'BENCH_SUPPORT',point,normal)
for delta in [-1e-5,0.,1e-5]:
 assert not(ROOT/'runtime/STOP').exists();journal(dict(state='START',operation='ONE_nut_cage_nonthread_BRep_intersection',scale=scale+delta));t=time.monotonic();volume=common(translate(nut,*((scale+delta)*w[:3])),support);r=dict(state='COMPLETE',scale=scale+delta,intersection_mm3=volume,elapsed_s=time.monotonic()-t);results.append(r);journal(r)
checks=dict(actual_nut_boundary=nb['distance_mm']<1e-7,actual_cage_wall=sb['distance_mm']<1e-7 and sb['normal_error']<1e-7,before_clear_after_intersection=results[0]['intersection_mm3']<1e-8 and results[-1]['intersection_mm3']>1e-8,nominal_initial_reaction_zero=rr['gap_mm']>1e-7,finite_translation=scale>0)
dump(out/'summary.json',dict(status='ACTUAL_P1_FINITE_INACTIVE_NUTCAGE_TAKEUP_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_FINITE_INACTIVE_NUTCAGE_EVENT_FAIL',candidate=ref(cp),producer=ref(out/'producer.py'),journal=ref(out/'journal.jsonl'),pose_source=ref(sp),witness_source=ref(ap),checks={k:bool(v) for k,v in checks.items()},body=bn,initial_cage_gap_mm=rr['gap_mm'],separating_twist=w.tolist(),local_event_scale=scale,finite_nut_translation_mm=(scale*w[:3]).tolist(),contact_point_mm=point.tolist(),cage_inward_normal=normal.tolist(),nut_binding=nb,support_binding=sb,probes=results,accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Onlynut1translationcomponentof108DOFwitness isadvanced;NOT wholeproduct path/firstevent ornew_equilibrium','Other body contacts and threads mayclose earlier;do NOT mix thisnewcontact withold endpointtractions','Finite edge/flat contact is not elasticpressure/bearing/notch/materialcapacity;all22gatesremainunqualified']))
print(json.dumps(dict(checks={k:bool(v) for k,v in checks.items()},gap=rr['gap_mm'],scale=scale,translation=(scale*w[:3]).tolist(),probes=results)));raise SystemExit(0 if all(checks.values()) else 2)
