"""Actual rounded-plug/finite socketwall firstcontact and frictionless wrench cone.
Full12bolt/keeper resultant rows, no fixedspin/axialtie. Pure torque necessary
cut contrast only: real keeper/pin/nut/support equilibrium remains unsolved.
"""
import sys,json,math,shutil,numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,bounds
from primary_clocked62 import spin
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder,GeomAbs_Plane
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.gp import gp_Pnt
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_ground65a/summary.json';cad=json.loads(cp.read_text());refs=cad['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());settings=json.loads((REPO/cad['settings']['path']).read_text())['settings'];fields=json.loads((ROOT/'validation/integrated/primaryP1_floor65c/contact_fields.json').read_text());case=next(q for q in fields['rows'] if q['ground_mu_ASSUMED']==.3);rows=[]
def facelist(s):
 e=TopExp_Explorer(s,TopAbs_FACE);r=[]
 while e.More():r.append(TopoDS.Face_s(e.Current()));e.Next()
 return r
def distpoint(face,p):
 d=BRepExtrema_DistShapeShape(face,BRepBuilderAPI_MakeVertex(gp_Pnt(*map(float,p))).Vertex());d.Perform();assert d.IsDone();return d.Value()
def wrench(p,f):return np.r_[f,np.cross(p,f)]
for qi,q in enumerate(settings):
 assert not(ROOT/'runtime/STOP').exists();center=np.array([q['x'],q['y'],0.]);bolt=read(REPO/refs[q['bolt']]['path']);keeper=read(REPO/refs[q['keeper']]['path']);cyl=[];planes=[]
 for f in facelist(keeper):
  a=BRepAdaptor_Surface(f)
  if a.GetType()!=GeomAbs_Cylinder:continue
  c=a.Cylinder();o=c.Location();axis=c.Axis().Direction();v=np.array([o.X(),o.Y(),o.Z()])
  if abs(c.Radius()-.15)<1e-7 and abs(axis.Z())>.999999 and np.linalg.norm((v-center)[:2])<2:cyl.append(dict(face=f,c=v,r=c.Radius(),bb=bounds(f)))
 for f in facelist(bolt):
  a=BRepAdaptor_Surface(f)
  if a.GetType()!=GeomAbs_Plane:continue
  p=a.Plane();o=p.Location();n=p.Axis().Direction();v=np.array([o.X(),o.Y(),o.Z()]);nv=np.array([n.X(),n.Y(),n.Z()]);b=bounds(f)
  if abs(nv[2])<1e-7 and np.linalg.norm((np.array(b[:3])+np.array(b[3:]))[:2]/2-center[:2])<2:
   if nv@(center-v)<0:nv=-nv
   planes.append(dict(face=f,o=v,n=nv,bb=b))
 assert len(cyl)==len(planes)==6,(q['bolt'],len(cyl),len(planes))
 def rotated(a,sign):
  ang=math.radians(sign*a);R=np.array([[math.cos(ang),-math.sin(ang),0],[math.sin(ang),math.cos(ang),0],[0,0,1.]])
  return [dict(o=R@(f['o']-center)+center+np.array([0,0,sign*.5*a/360]),n=R@f['n'],original=f) for f in planes]
 def gap(a,sign):return min(float(f['n']@(c['c']-f['o'])-c['r']) for f in rotated(a,sign) for c in cyl)
 for sign in [-1,1]:
  lo=0.;hi=10.;assert gap(lo,sign)>0 and gap(hi,sign)<0
  for _ in range(42):
   mid=(lo+hi)/2
   if gap(mid,sign)>=0:lo=mid
   else:hi=mid
  a=(lo+hi)/2;contacts=[]
  for f in rotated(a,sign):
   vals=[float(f['n']@(c['c']-f['o'])-c['r']) for c in cyl];i=int(np.argmin(vals));c=cyl[i];face=translate(spin(f['original']['face'],q['x'],q['y'],sign*a),0,0,sign*.5*a/360);bb=bounds(face);zlo=max(bb[2],c['bb'][2]);zhi=min(bb[5],c['bb'][5]);assert zhi-zlo>1.;p=c['c']-c['r']*f['n'];p[2]=(zlo+zhi)/2;onplug=distpoint(c['face'],p);onwall=distpoint(face,p);normal=f['n'];contacts.append(dict(point_mm=p.tolist(),normal_on_keeper=normal.tolist(),finite_axial_contact_interval_mm=[zlo,zhi],gap_mm=vals[i],actual_rounded_face_distance_mm=onplug,actual_finite_socket_face_distance_mm=onwall))
  label='root_connector_'+str(qi) if qi<2 else 'cap_connector_'+str(q['x'])+'_'+str(q['y']);required=case['connector_required_N'][label];T=sign*required*.5/(2*math.pi);target=np.array([0.,0,0,0,0,T]);A=np.column_stack([np.r_[wrench(np.array(c['point_mm']),-np.array(c['normal_on_keeper'])),wrench(np.array(c['point_mm']),np.array(c['normal_on_keeper']))] for c in contacts]);external=np.r_[target,-target];res=linprog(np.ones(6),A_eq=A,b_eq=-external,bounds=(0,None),method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9});row=dict(bolt=q['bolt'],keeper=q['keeper'],direction=sign,angle_deg=[lo,hi],actual_screw_axial_motion_mm=sign*.5*a/360,contacts=contacts,conditional_required_axial_port_N=required,reference_torque_Nmm=T,source_lead_mm=.5,lead_torque_is_frictionless_necessary_bound_not_preload=True,full12_resultant_rows=12,physical_fixed_DOF=0,fixedspin=False,scalar_axial_tie=False,feasible=bool(res.success),solver_status=int(res.status),solver_message=res.message)
  if res.success:
   residual=A@res.x+external;twist=np.arange(12)/11.;row.update(contact_normal_forces_N=res.x.tolist(),all12_resultant_residual_N_Nmm=residual.tolist(),max_original12row_error=float(abs(residual).max()),physical_virtualwork_residual=float(twist@(A@res.x+external)),contact_friction_coefficient=0.,contact_transmits_axial_force=False)
  # A sign-reversed torque at same contact state must not be called a locked spin.
  wrong=linprog(np.ones(6),A_eq=A,b_eq=external,bounds=(0,None),method='highs');row['zero_actual_torque_case']=abs(T)<1e-14
  unit=np.array([0.,0,0,0,0,float(sign)]);unit12=np.r_[unit,-unit];wrong_unit=linprog(np.ones(6),A_eq=A,b_eq=unit12,bounds=(0,None),method='highs');right_unit=linprog(np.ones(6),A_eq=A,b_eq=-unit12,bounds=(0,None),method='highs');row['wrong_torque_at_same_contact_rejected']=not bool(wrong_unit.success);row['unit_torque_at_matching_contact_admitted']=bool(right_unit.success);row['control_unit_torque_Nmm']=1.;row['control_is_not_operating_load']=True;row['finite_contact_wrench_rank']=int(np.linalg.matrix_rank(A));row['relative_contact_DOF_unconstrained_at_least']=6-int(np.linalg.matrix_rank(A));rows.append(row)
checks=dict(actual83hashes=True,twelve_signed_actual_pair_cases=len(rows)==12,finite_rounded_and_socket_witnesses=all(c['actual_rounded_face_distance_mm']<1e-7 and c['actual_finite_socket_face_distance_mm']<1e-7 and c['finite_axial_contact_interval_mm'][1]-c['finite_axial_contact_interval_mm'][0]>1 for r in rows for c in r['contacts']),all12row_equilibria=all(r['feasible'] and r['max_original12row_error']<1e-8 and abs(r['physical_virtualwork_residual'])<1e-8 and min(r['contact_normal_forces_N'])>=-1e-9 for r in rows),positive_real_angular_and_axial_clearance=all(r['angle_deg'][0]>5 and abs(r['actual_screw_axial_motion_mm'])>.007 for r in rows),reverse_torque_controls_reject=all(r['wrong_torque_at_same_contact_rejected'] and r['unit_torque_at_matching_contact_admitted'] for r in rows))
dump(out/'summary.json',dict(status='ACTUAL_FINITE_ROUNDED_HEX_FRICTIONLESS12ROW_TORQUE_CONE_NOT_ASSEMBLY_EQUILIBRIUM' if all(checks.values()) else 'ACTUAL_FINITE_ROUNDED_HEX_CONTACT_AUDIT_FAIL',candidate=ref(cp),producer=ref(out/'producer.py'),source_cut_result=ref(ROOT/'validation/integrated/primaryP1_floor65c/summary.json'),settings=cad['settings'],checks=checks,rows=rows,physical_fixed_DOF=0,full_bolt_keeper_DOF_retained=True,accepted83body_physical_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['ActualBRepfiniteaxialflanks/roundedcylindricalfacesverifiedatcontactpoints. Rigidpointcone isnotelasticline/areaHertzstressorsourcedcapacity.','PureopposedtorqueNeumanncontrast satisfiesbothbody12resultantswithoutfixedspin. It doesNOTsolvekeeper/tongue/pin/nut/cage/contactpreloador83bodyoperatingequilibrium.','M3leadtorquefromrequiredcutaxialport isfrictionlessnecessaryboundonly,notactualthreadtighteningtorque/preload. Syntheticsettingandunknownmanufacturingremain.','No axialforce transmittedbyfrictionlessverticalhexflanks; existinghelicalclearance andheight/play remainfree. No globalenergy/mesh/time/strength orStage3.']))
print(json.dumps(dict(checks=checks,rows=len(rows))));raise SystemExit(0 if all(checks.values()) else 2)
