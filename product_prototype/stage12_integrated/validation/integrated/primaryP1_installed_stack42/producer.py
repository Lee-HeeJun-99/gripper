"""Actual P1 installed anchor stack: CAD interfaces and axial/thread work audit.
No fictitious axial tie is adopted. Smooth envelopes and conditional helical
normals are explicitly separate; neither is installed preload certification.
"""
import sys,json,shutil,math
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,common
from validate_base_anchor36 import props
from primary_motor_bearing_wrenches import faces
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common

def cylinders(shape):
 it=TopExp_Explorer(shape,TopAbs_FACE);out=[]
 while it.More():
  f=TopoDS.Face_s(it.Current());a=BRepAdaptor_Surface(f)
  if a.GetType()==GeomAbs_Cylinder:
   c=a.Cylinder();d=c.Axis().Direction();b=bounds(f)
   out.append(dict(radius_mm=c.Radius(),axis=[d.X(),d.Y(),d.Z()],bounds_mm=b,area_mm2=props(f,True)[0]))
  it.Next()
 return out

def overlap_area(a,b,z):
 return sum(props(BRepAlgoAPI_Common(f,g).Shape(),True)[0] for f in faces(a,2,z) for g in faces(b,2,z))

def lp(A,target):
 r=linprog(np.ones(A.shape[1]),A_eq=A,b_eq=target,bounds=(0,None),method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
 return dict(feasible=bool(r.success),status=int(r.status),message=r.message,residual=None if not r.success else float(abs(A@r.x-target).max()))

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists()
 cp=ROOT/'cad/exports/primaryP1_anchor36b/summary.json';cad=json.loads(cp.read_text());refs=cad['part_references']
 assert len(refs)==85 and all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values())
 source=ROOT/'models/standard_drive/primary_retention_sources2/reviewed.json';sd=json.loads(source.read_text());pitch=sd['bolt']['dimensions_mm']['pitch'];assert pitch==sd['nut']['dimensions_mm']['pitch']
 base=read(REPO/refs['TEST_BASE']['path']);rail=read(REPO/refs['BENCH_ANCHOR_RAIL']['path']);rows=[]
 for i in range(3):
  assert not(ROOT/'runtime/STOP').exists();bn=f'ANCHOR_BOLT_{i}';nn=f'ANCHOR_NUT_{i}';bolt=read(REPO/refs[bn]['path']);nut=read(REPO/refs[nn]['path']);bb=bounds(bolt);nb=bounds(nut);bc=cylinders(bolt);nc=cylinders(nut)
  shank=[c for c in bc if abs(c['radius_mm']-2.5)<1e-7 and abs(c['axis'][2])>1-1e-9];bore=[c for c in nc if abs(c['radius_mm']-2.5)<1e-7 and abs(c['axis'][2])>1-1e-9];assert len(shank)==len(bore)==1
  lo=max(shank[0]['bounds_mm'][2],bore[0]['bounds_mm'][2]);hi=min(shank[0]['bounds_mm'][5],bore[0]['bounds_mm'][5]);L=hi-lo;r=2.5
  # Exact cylinder normal has zero Z component at every angular position.
  # Use local station origin to exclude unrelated lever-arm torque.
  theta=np.arange(64)*2*math.pi/64;radial=np.array([[math.cos(t),math.sin(t),0,0,0,0] for t in theta]).T
  target=np.array([0,0,1,0,0,0.]);smooth=lp(radial,target)
  # Hypothetical helicoid, NOT the smooth CAD. Circumferential force for
  # positive axial load produces screw torque p/(2pi). Radial components
  # cancel in paired quadrature; no head friction or external torque supplied.
  lead=pitch/(2*math.pi);helix=[]
  for t in theta:
   e=np.array([-math.sin(t),math.cos(t),0.]);f=np.array([0,0,1.])+lead/r*e;pos=np.array([r*math.cos(t),r*math.sin(t),(lo+hi)/2-60]);helix.append(np.r_[f,np.cross(pos,f)])
  H=np.array(helix).T;locked=lp(H,target);with_torque=lp(H,np.array([0,0,1,0,0,lead]));work_error=max(abs(H[5]-lead*H[2]))
  # Conditional axial compliance only: uniform shank E, neglect head/nut,
  # using distributed unloading through actual installed engagement. This
  # is not finite-body elasticity or strength. End-load is old counterfactual.
  E=200000.;A=math.pi*r*r;a=lo-60;b=hi-lo;end=bb[5]-60
  rows.append(dict(station=i,bolt_ID=bn,nut_ID=nn,bolt=refs[bn],nut=refs[nn],bolt_bounds_mm=bb,nut_bounds_mm=nb,shank_cylinders=shank,nut_bore_cylinders=bore,head_base_area_mm2=overlap_area(bolt,base,60),nut_receiver_area_mm2=overlap_area(nut,rail,74),bolt_nut_common_volume_mm3=common(bolt,nut),nominal_engagement_interval_mm=[lo,hi],nominal_overlap_length_mm=L,nominal_pitch_count=L/pitch,effective_engagement_length_mm=None,tip_projection_mm=bb[5]-nb[5],cylindrical_overlap_area_mm2=2*math.pi*r*L,exact_smooth_normal_axial_capacity_N=0.,smooth_envelope_unit_axial_equilibrium=smooth,hypothetical_helical_without_reaction_torque=locked,hypothetical_helical_with_required_torque=with_torque,unit_axial_thread_torque_Nmm=lead,helical_virtual_work_error_Nmm=work_error,conditional_major_shank=dict(E_MPa=E,area_mm2=A,end_load_compliance_mm_N=end/(E*A),uniform_engagement_compliance_mm_N=(a+b/3)/(E*A),load_at_first_engaged_plane_mm_N=a/(E*A),load_at_last_engaged_plane_mm_N=(a+b)/(E*A),uniform_to_old_end_compliance_ratio=(a+b/3)/end),actual_thread_flank_geometry=False,installed_preload_N=None,minimum_material_allowable_MPa=None))
 checks=dict(actual_candidate_hashes=True,three_positive_head_seats=all(x['head_base_area_mm2']>0 for x in rows),three_positive_nut_seats=all(x['nut_receiver_area_mm2']>0 for x in rows),positive_nominal_overlap=all(x['nominal_overlap_length_mm']>0 for x in rows),smooth_axial_tie_rejected=all(not x['smooth_envelope_unit_axial_equilibrium']['feasible'] for x in rows),torque_free_helical_transfer_rejected=all(not x['hypothetical_helical_without_reaction_torque']['feasible'] for x in rows),helical_work_control=all(x['hypothetical_helical_with_required_torque']['feasible'] and x['helical_virtual_work_error_Nmm']<1e-10 for x in rows))
 dump(out/'summary.json',dict(status='ACTUAL_P1_INSTALLED_STACK_BOUNDARY_REJECTION_NOT_RELEASE',candidate=ref(cp),producer=ref(out/'producer.py'),standard_dimensions=ref(source),rows=rows,checks=checks,actual_parts=85,actual_CAD_changed_files=[],accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],physical_stack_qualified=False,whole_system_release=False,limitations=['Exact installed head/nut seat and smooth cylinder geometry audited;nominal overlap is not effective engaged thread length.','Cylindrical smooth normal contact cannot carry axial tension. A positive connector cannot be inferred from touching major-diameter envelopes.','Helicoid rays are a source-pitch mathematical contrast,not implemented thread CAD/contact. Required thread torque needs actual reaction/locking/friction.','Conditional uniform-major-shank compliance excludes threadcore/head/nut deformation,preload/seat pressure and minimum material;not an operating or mesh qualification.','External receiver attachment,100g operating sourcefield,all22system gates and same-revision3Finger release remain unresolved.']))
 print(json.dumps(dict(checks=checks,rows=rows)));assert all(checks.values())
if __name__=='__main__':main()
