"""Actual P1 finite bore seating and shifted bearing geometry.
LP with free internal thread wrench is ONLY a necessary static relaxation.
No thread constitutive law, preload, pressure or support equilibrium is claimed.
"""
import sys,json,time,shutil
import numpy as np
from scipy.optimize import linprog
from scipy.spatial.transform import Rotation
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
from primary_gamma_attachment29 import cylinders
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,bounds
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

def area_centroid(s):
 p=GProp_GProps();BRepGProp.SurfaceProperties_s(s,p);q=p.CentreOfMass();return p.Mass(),np.array([q.X(),q.Y(),q.Z()])
def planar(s,z):
 it=TopExp_Explorer(s,TopAbs_FACE);out=[]
 while it.More():
  f=TopoDS.Face_s(it.Current());bb=bounds(f)
  if BRepAdaptor_Surface(f).GetType()==GeomAbs_Plane and abs(bb[2]-z)<1e-7 and abs(bb[5]-z)<1e-7:out.append(f)
  it.Next()
 return out

def W(q,f):return np.r_[f,np.cross(np.array(q)*.001,f)]
def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 cp=ROOT/'cad/exports/primaryP1_ycapture24/summary.json';cad=json.loads(cp.read_text());assert len(cad['part_references'])==78 and all(sha(REPO/cad['part_references'][n]['path'])==cad['part_references'][n]['SHA256'] for n in cad['part_references'])
 src=ROOT/'validation/integrated/primaryP1_hardware_audit29/summary.json';audit=json.loads(src.read_text());geos=json.loads((REPO/audit['actual_geometry']['path']).read_text());inp=json.loads((REPO/audit['inputs']['path']).read_text());hw={a['part_ID']:a for a in json.loads((REPO/inp['hardware']['path']).read_text())};branches=json.loads((REPO/inp['branches']['path']).read_text());patches=json.loads((REPO/inp['patches']['path']).read_text());shapes={n:read(REPO/r['path']) for n,r in cad['part_references'].items() if n in hw or n in {g['body'] for g in geos}}
 dump(out/'inputs.json',dict(candidate=ref(cp),prior=ref(src),geometries=audit['actual_geometry'],hardware=inp['hardware'],branches=inp['branches'],patches=inp['patches'],producer=ref(out/'producer.py'),dependencies=[ref(ROOT/'scripts/primary_gamma_attachment29.py')],scope='Same actual CAD; prescribed common bolt/nut parallel seating is a geometry family, not solved 6DOF configuration. Fixed world gravity in +/- .003rad sensitivity. Free six-component thread wrench LP is a necessary relaxation, not a glue, constitutive connector or strength certificate.'))
 rows=[];cases=[];work=[]
 for b in branches:
  assert not(ROOT/'runtime/STOP').exists();gg=[g for g in geos if g['branch']==b['branch']];clear=min(g['actual_radial_clearance_mm'] for g in gg);bolt=gg[0]['bolt'];shaft=min(cylinders(shapes[bolt]),key=lambda fd:fd[1]['radius_mm'])[0]
  for sign in [-1,1]:
   shift=np.array([0.,sign*clear,0.]);foot=[];contacts=[]
   for side,hn,body in [('a',b['hardware_a'],b['body_a']),('b',b['hardware_b'],b['body_b'])]:
    p=next(p for p in patches if p['branch']==b['branch'] and p['side']==side);pairs=[]
    for hf in planar(shapes[hn],p['z']):
     for sf in planar(shapes[body],p['z']):
      op=BRepAlgoAPI_Common(translate(hf,*shift),sf);op.Build();assert op.IsDone();a,c=area_centroid(op.Shape())
      if a>1e-10:pairs.append((a,c))
    ar=sum(a for a,c in pairs);assert ar>0;cen=sum((a*c for a,c in pairs),np.zeros(3))/ar
    foot.append(dict(side=side,hardware=hn,body=body,shift_mm=shift.tolist(),actual_shifted_overlap_area_mm2=ar,nominal_overlap_area_mm2=p['CAD_area_mm2'],actual_shifted_overlap_centroid_mm=cen.tolist(),old_center_error_mm=float(np.linalg.norm(cen-np.r_[p['center'],p['z']])),centroid_relative_to_shifted_hardware_axis_mm=(cen-np.r_[p['center'],p['z']]-shift).tolist(),pressure_assigned=False))
   for g in gg:
    hole=next(f for f,d in cylinders(shapes[g['body']]) if abs(d['radius_mm']-g['bore']['radius_mm'])<1e-9 and np.linalg.norm(np.array(d['axis_point_mm'][:2])-b['thread_action_point_mm'][:2])<1e-8)
    ds=BRepExtrema_DistShapeShape(translate(shaft,*shift),hole);ds.Perform();gap=g['actual_radial_clearance_mm']-clear;assert ds.IsDone();active=abs(gap)<1e-10;lo=max(g['shaft']['bounds_mm'][2],g['bore']['bounds_mm'][2]);hi=min(g['shaft']['bounds_mm'][5],g['bore']['bounds_mm'][5]);qs=[np.r_[b['thread_action_point_mm'][:2],z]+shift+np.array([0,sign*g['shaft']['radius_mm'],0]) for z in [lo,hi]]
    contacts.append(dict(body=g['body'],radial_gap_mm=gap,finite_surface_distance_mm=ds.Value(),active=active,finite_z_interval_mm=[lo,hi],line_endpoints_mm=[q.tolist() for q in qs],force_on_bolt_normal=[0,-sign,0],ideal_contact_area_mm2=0.,finite_pressure_available=False))
    if active:
     for q in qs:
      center=np.array(g['bore']['axis_point_mm']);normal=np.array([0.,-sign,0]);v=np.array([.001,-.002,.003]);omega=np.array([.0003,-.0002,.0001]);eps=1e-3
      def gapfun(e):
       qp=Rotation.from_rotvec(e*omega).apply(q)+e*v;return g['bore']['radius_mm']-np.linalg.norm((qp-center)[:2])
      fd=(gapfun(eps)-gapfun(-eps))/(2*eps);an=normal@(v+np.cross(omega,q));work.append(dict(branch=b['branch'],sign=sign,body=g['body'],point_mm=q.tolist(),numerical_gap_rate_mm=fd,analytical_gap_rate_mm=an,error_mm=abs(fd-an),scope='Material generator point to exact finite-bore interior; nearby tilted shaft envelope/edge ownership not certified.'))
   rows.append(dict(branch=b['branch'],sign=sign,parallel_seating_translation_mm=shift.tolist(),bearing_footprints=foot,bore_contacts=contacts,thread_own_relative_pose_unchanged=True,configuration_is_solved=False))
   for angle in [-sign*.003,sign*.003]:
    R=Rotation.from_rotvec([angle,0,0]).as_matrix();axis=R[:,2];qt=R@b['thread_action_point_mm'];a=hw[b['hardware_a']];bb=hw[b['hardware_b']];gravity=np.r_[W(R@(np.array(a['centroid_mm'])+shift),[0,0,-a['conditional_mass_kg']*9.80665]),W(R@(np.array(bb['centroid_mm'])+shift),[0,0,-bb['conditional_mass_kg']*9.80665])];cols=[];labels=[]
    for f in foot:
     col=np.zeros(12);off=0 if f['side']=='a' else 6;col[off:off+6]=W(R@f['actual_shifted_overlap_centroid_mm'],axis*(1 if off==0 else -1));cols.append(col);labels.append('bearing_'+f['side'])
    boff=0 if b['hardware_a']==bolt else 6
    for ct in contacts:
     if ct['active']:
      for q in ct['line_endpoints_mm']:
       col=np.zeros(12);col[boff:boff+6]=W(R@q,R@ct['force_on_bolt_normal']);cols.append(col);labels.append('bore_'+ct['body'])
    A=np.array(cols).T;tw=np.zeros((12,6));tw[:6]=-np.eye(6);tw[6:]=np.eye(6)
    # Thread wrench is about world origin; equal/opposite and unrestricted ONLY for a necessary relaxation.
    for kind in ['AXIAL_THREAD_ONLY','FREE_THREAD_WRENCH_NECESSARY_RELAXATION']:
     C=np.column_stack([A,np.r_[-W(qt,axis),W(qt,axis)]] if kind=='AXIAL_THREAD_ONLY' else [A,tw]);boundsLP=[(0,None)]*A.shape[1]+([(0,None)] if kind=='AXIAL_THREAD_ONLY' else [(None,None)]*6);obj=np.r_[np.ones(A.shape[1]),np.zeros(C.shape[1]-A.shape[1])];sol=linprog(obj,A_eq=C,b_eq=-gravity,bounds=boundsLP,method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9});res=float(np.max(abs(C@sol.x+gravity))) if sol.success else None
     record=dict(branch=b['branch'],sign=sign,common_X_rotation_rad=angle,model=kind,LP_success=bool(sol.success),LP_status=int(sol.status),message=sol.message,max12row_residual_N_Nm=res,unknown_labels=labels,solution=sol.x.tolist() if sol.success else None,physical_equilibrium_qualified=False)
     if sol.success:
      record['pair_support_wrench_N_Nm']=(-A@sol.x[:A.shape[1]]).reshape(2,6).sum(0).tolist();record['pair_gravity_wrench_N_Nm']=gravity.reshape(2,6).sum(0).tolist();record['action_reaction_error_N_Nm']=float(np.max(abs(np.array(record['pair_support_wrench_N_Nm'])-np.array(record['pair_gravity_wrench_N_Nm']))))
     cases.append(record)
 dump(out/'finite_seating_and_shifted_footprints.json',rows);dump(out/'own_body_12row_cases.json',cases);dump(out/'bore_generator_virtual_work.json',work)
 checks=dict(all28_shifted_states=len(rows)==28,all56_positive_shifted_bearing_areas=all(f['actual_shifted_overlap_area_mm2']>0 for r in rows for f in r['bearing_footprints']),all_finite_bore_distances=all(abs(c['finite_surface_distance_mm']-c['radial_gap_mm'])<1e-7 for r in rows for c in r['bore_contacts']),no_open_gap_reactions=all(c['radial_gap_mm']>=-1e-10 for r in rows for c in r['bore_contacts']),finite_generator_work=max(w['error_mm'] for w in work)<1e-8,all_feasible_LP_residuals=all(c['max12row_residual_N_Nm']<1e-8 and c['action_reaction_error_N_Nm']<1e-8 for c in cases if c['LP_success']))
 dump(out/'summary.json',dict(status='ACTUAL_P1_FINITE_BORE_SEATING_AND_SHIFTED_BEARING_NECESSARY_LOAD_AUDIT' if all(checks.values()) else 'ACTUAL_P1_BORE_SEATING_AUDIT_FAIL',candidate=ref(cp),inputs=ref(out/'inputs.json'),geometry=ref(out/'finite_seating_and_shifted_footprints.json'),numerical_cases=ref(out/'own_body_12row_cases.json'),virtual_work=ref(out/'bore_generator_virtual_work.json'),checks=checks,case_counts={kind:dict(feasible=sum(c['LP_success'] for c in cases if c['model']==kind),infeasible=sum(not c['LP_success'] for c in cases if c['model']==kind)) for kind in sorted(set(c['model'] for c in cases))},max_work_error_mm=max(w['error_mm'] for w in work),max_shifted_center_error_mm=max(f['old_center_error_mm'] for r in rows for f in r['bearing_footprints']),elapsed_s=time.monotonic()-start,accepted_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['No changed product CAD. Same actual78part product, not an ideal coupon. Shifted finite BRep bearing intersections are geometry; centroid force columns are a necessary relaxed positive pressure distribution, not solved pressure or elastic work.','Co-translated parallel bolt/nut family retains physical clearance; no full6DOF nonlinear equilibrium or actual preload/thread shear/tilt constitutive law. Free internal wrench LP is ONLY necessary feasibility, no glue/support constraint or stiffness is implemented.','Finite line-contact endpoints bound nonnegative normal line reaction resultant; ideal line has zero area. Finite compliant pressure, edge contact, tilted envelope ownership, thread rest setting, material minima, pin load split and global support/anchor/source/strength/mesh/time/energy/3Finger remain blocked.','Sensitivity tilt is not certified operating duty. No Base counterload, no hardware measurement, no gate criteria change.']))
 print(json.dumps(dict(checks=checks,case_counts=json.loads((out/'summary.json').read_text())['case_counts'])));return 0 if all(checks.values()) else 2
if __name__=='__main__':sys.exit(main())
