"""First offaxis contact is an actual nut crest edge against bolt flank.
Analytical stationary point independently bound to both actual trimmed BReps.
"""
import json,sys,math,os,time,shutil
import numpy as np
from scipy.optimize import minimize_scalar,nnls
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,translate
from validate_nutseat46c import rotate
from validate_thread49f import classification
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE,TopAbs_REVERSED
from OCP.TopoDS import TopoDS
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepLProp import BRepLProp_SLProps
from OCP.BRep import BRep_Tool
from OCP.GeomAPI import GeomAPI_ProjectPointOnSurf
from OCP.gp import gp_Pnt
K=.8/(2*math.pi);CLEAR=(4.605-4.456)/2/math.sqrt(3);RN=4.334/2

def stop_for_angle(a,delta,beta,nu,rn=RN):
 xy=rn*np.array([np.cos(a),np.sin(a)]);v=xy-delta;rb=np.linalg.norm(v);ab=a+math.atan2(np.cross(xy,v),np.dot(xy,v));return CLEAR+K*(beta-nu+a-ab)+(rb-rn)/math.sqrt(3)
def first_edge(delta,beta,nu):
 delta=np.array(delta);angle=math.atan2(delta[1],delta[0]);s=minimize_scalar(lambda a:stop_for_angle(a,delta,beta,nu),bounds=(angle-.5,angle+.5),method='bounded',options=dict(xatol=1e-14));return s.x,float(s.fun)
def main():
 out=ROOT/'validation/integrated/primaryP1_edge54';out.mkdir();shutil.copyfile(__file__,out/'producer.py');sp=ROOT/'validation/integrated/primaryP1_offaxis54/summary.json';d=json.loads(sp.read_text());cp=REPO/d['candidate']['path'];assert sha(cp)==d['candidate']['SHA256'];src=d['rows'][0];delta=np.array(src['relative_transverse_offset_mm']);beta=src['bolt_yaw_rad'];nu=src['nut_yaw_rad'];a,op=first_edge(delta,beta,nu);a+=2*math.pi*4;O=np.array([-59.,-58.,54.]);point=O+np.r_[RN*np.array([math.cos(a),math.sin(a)]),K*(a-nu)-(.2+(RN-4.605/2)/math.sqrt(3))];bolt0=rotate(read(REPO/src['bolt_reference']['path']),*O[:2],beta);nut=rotate(read(REPO/src['nut_reference']['path']),*O[:2],nu);bolt=translate(bolt0,*delta,op)
 def journal(r):
  with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(r)+'\n');f.flush();os.fsync(f.fileno())
 def bind(shape,name,p):
  assert not(ROOT/'runtime/STOP').exists();journal(dict(state='START',part=name,point_mm=p.tolist(),operation='incident_trimmed_face_distance_and_outward_normals'));v=BRepBuilderAPI_MakeVertex(gp_Pnt(*p)).Vertex();ex=TopExp_Explorer(shape,TopAbs_FACE);i=0;rows=[]
  while ex.More():
   f=TopoDS.Face_s(ex.Current());b=np.array(bounds(f));ex.Next();i+=1
   if np.linalg.norm(np.maximum(np.maximum(b[:3]-p,p-b[3:]),0))>1e-6:continue
   t=time.monotonic();dd=BRepExtrema_DistShapeShape(v,f);dd.Perform()
   if dd.Value()>1e-6:continue
   pr=GeomAPI_ProjectPointOnSurf(gp_Pnt(*p),BRep_Tool.Surface_s(f));u,w=pr.LowerDistanceParameters();sl=BRepLProp_SLProps(BRepAdaptor_Surface(f),u,w,1,1e-9);nd=sl.Normal();normal=np.array([nd.X(),nd.Y(),nd.Z()])*(-1 if f.Orientation()==TopAbs_REVERSED else 1);rows.append(dict(face_index=i-1,distance_mm=dd.Value(),normal=normal.tolist(),kind=str(BRepAdaptor_Surface(f).GetType()),elapsed_s=time.monotonic()-t))
  journal(dict(state='COMPLETE',part=name,point_mm=p.tolist(),incident_faces=rows));return rows
 bf=bind(bolt,'BENCH_MOUNT_BOLT_0',point);nf=bind(nut,'BENCH_MOUNT_NUT_0',point);assert len(bf)==1 and len(nf)>=2
 nb=np.array(bf[0]['normal']);N=np.array([r['normal'] for r in nf]).T;mult,err=nnls(N,-nb);stationary=(stop_for_angle(a+1e-5,delta,beta,nu)-stop_for_angle(a-1e-5,delta,beta,nu))/2e-5
 # Independent finite actual material probes near new first event;no globalBoolean.
 probes=[]
 for dz in [-1e-4,1e-4]:
  b=translate(bolt0,*delta,op+dz);test=point+nb*2e-5;probes.append(dict(opening_offset_mm=dz,point_mm=test.tolist(),nut=classification(nut,test),bolt=classification(b,test)))
 # Unit normalized contact wrench on each of the two REAL bodies. Both bodies
 # retain full sixDOFs;unloaded bodies do not acquire fictitious restraints.
 wr=np.r_[nb,np.cross(point-O,nb)];screw=np.array([0.,0.,K,0.,0.,1.]);screwwork=float(wr@screw);axial_multiplier=1/nb[2];unit_wrench=wr*axial_multiplier
 bracket=json.loads((ROOT/'validation/integrated/primaryP1_partial54/summary.json').read_text())['local_touch_bracket_mm'];checks=dict(actual_single_bolt_flank=len(bf)==1,actual_nut_crest_edge=len(nf)>=2,bound_to_actual_BRep=max(r['distance_mm'] for r in bf+nf)<1e-7,stationary_angle=abs(stationary)<1e-8,nut_normal_cone=err<1e-6 and min(mult)>=0,local_bracket_agreement=abs(op-sum(bracket)/2)<1e-6,before_open_after_material_overlap=probes[0]['bolt']=='OUT' and probes[1]['bolt']=='IN' and all(r['nut']=='IN' for r in probes))
 dump(out/'summary.json',dict(status='ACTUAL_P1_OFFAXIS_CREST_EDGE_NORMAL_CONE_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_OFFAXIS_CREST_EDGE_BINDING_OR_CONE_FAIL',candidate=ref(cp),source=ref(sp),producer=ref(out/'producer.py'),journal=ref(out/'journal.jsonl'),checks={k:bool(v) for k,v in checks.items()},opening_mm=op,relative_transverse_offset_mm=delta.tolist(),angle_rad=a,contact_point_mm=point.tolist(),bolt_incident_faces=bf,nut_incident_faces=nf,nut_outward_cone_coefficients=mult.tolist(),normal_cone_error=err,angular_gap_derivative_mm_per_rad=stationary,actual_material_probes=probes,unit_contact_normal_on_nut=nb.tolist(),unit_contact_wrench_about_bolt_nominal_tip=wr.tolist(),conditional_one_N_axial_wrench=unit_wrench.tolist(),screw_work_about_nominal_axis=screwwork,accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Finite exact singlelocal nutcrest/boltflank event;not completeallthread/bore/cage/pin/guidecontactsequence','1Naxial wrench is conditional pairtransfer,not installed equilibrium/preload/operating tension/capacity','Edge normalcone admits kinematic contact but finite elasticpressure/notch/root/materialminima unqualified','Offaxis relativepose is not full128partassembly orcontinuousCCD qualification;all22gatesunchanged']))
 print(json.dumps(dict(checks={k:bool(v) for k,v in checks.items()},opening=op,normal_cone_error=err,probes=probes,unit_wrench=unit_wrench.tolist())));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
