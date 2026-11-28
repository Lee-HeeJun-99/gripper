"""Same actual P1: coupled TWO socket planar rigid contact, not elasticity/release.
Five planar DOFs free. Out-of-plane modes explicitly unqualified. Host radial
reaction ports are exposed, never presented as actual bore/head/nut constitutive laws.
"""
import sys,json,shutil,math,time
import numpy as np
from scipy.optimize import minimize,linprog
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,translate,common
from primary_clocked62 import spin
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder,GeomAbs_Plane
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.gp import gp_Pnt

def faces(s):
 e=TopExp_Explorer(s,TopAbs_FACE);r=[]
 while e.More():r.append(TopoDS.Face_s(e.Current()));e.Next()
 return r

def rot(a):
 c,s=np.cos(a),np.sin(a);return np.array([[c,-s,0],[s,c,0],[0,0,1.]])

def pointdist(s,p):
 d=BRepExtrema_DistShapeShape(s,BRepBuilderAPI_MakeVertex(gp_Pnt(*map(float,p))).Vertex());d.Perform();assert d.IsDone();return float(d.Value())

def wrench(p,f):return np.r_[f,np.cross(p,f)]

def main():
 start=time.monotonic();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py')
 cp=ROOT/'cad/exports/primaryP1_ground65a/summary.json';cad=json.loads(cp.read_text());refs=cad['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*refs.values(),cad['assembly'],cad['BOM']]);settings=[q for q in json.loads((REPO/cad['settings']['path']).read_text())['settings'] if q['keeper']=='ROOT_SOCKET_KEEPER'];assert len(settings)==2
 keeper=read(REPO/refs['ROOT_SOCKET_KEEPER']['path']);host=read(REPO/refs['F0_ROOT_BACK']['path']);pinname='ROOT_SOCKET_KEEPER_INSTALLED_SPLIT_PIN';pin=read(REPO/refs[pinname]['path']);bolts=[read(REPO/refs[q['bolt']]['path']) for q in settings];anchor=np.array([60.,0.,0.]);groups=[]
 for q,b in zip(settings,bolts):
  center=np.array([q['x'],q['y'],0.]);circles=[];walls=[]
  for f in faces(keeper):
   a=BRepAdaptor_Surface(f)
   if a.GetType()!=GeomAbs_Cylinder:continue
   c=a.Cylinder();o=c.Location();v=np.array([o.X(),o.Y(),o.Z()]);ax=c.Axis().Direction()
   if abs(c.Radius()-.15)<1e-7 and abs(ax.Z())>.999999 and np.linalg.norm((v-center)[:2])<2:circles.append(dict(face=f,c=v,r=c.Radius(),bb=bounds(f)))
  for f in faces(b):
   a=BRepAdaptor_Surface(f)
   if a.GetType()!=GeomAbs_Plane:continue
   pl=a.Plane();o=pl.Location();nv=pl.Axis().Direction();v=np.array([o.X(),o.Y(),o.Z()]);n=np.array([nv.X(),nv.Y(),nv.Z()]);bb=bounds(f)
   if abs(n[2])<1e-7 and np.linalg.norm((np.array(bb[:3])+bb[3:])[:2]/2-center[:2])<2:
    if n@(center-v)<0:n=-n
    walls.append(dict(face=f,o=v,n=n,bb=bb))
  assert len(circles)==len(walls)==6;groups.append(dict(center=center,circles=circles,walls=walls))
 source=ROOT/'validation/integrated/primaryP1_floor65c/contact_fields.json';fc=next(q for q in json.loads(source.read_text())['rows'] if q['ground_mu_ASSUMED']==.3);T=np.array([fc['connector_required_N']['root_connector_'+str(i)]*.5/(2*np.pi) for i in range(2)])
 # Same necessary frictionless screw-lead torque contrast as historical exact flank.
 # Not applied preload, measured tightening torque, gravity or operating equilibrium.
 def geometry(x):
  R=rot(x[2]);shift=np.r_[x[:2],0.];rows=[]
  for i,g in enumerate(groups):
   B=rot(x[3+i]);dz=.5*x[3+i]/(2*np.pi)
   for wi,w in enumerate(g['walls']):
    n=B@w['n'];o=B@(w['o']-g['center'])+g['center']+[0,0,dz]
    for ci,c in enumerate(g['circles']):
     cc=R@(c['c']-anchor)+anchor+shift;rows.append((float(n@(cc-o)-c['r']),i,wi,ci,n,o,cc,dz))
  return rows
 def gap(x):return np.array([r[0] for r in geometry(x)])
 rows=[]
 for signs in [(1,1),(-1,-1),(1,-1),(-1,1)]:
  assert not(ROOT/'runtime/STOP').exists();torque=T*np.array(signs);scale=max(float(abs(torque).max()),1e-12);load=np.r_[0.,0.,0.,torque/scale];journal=[]
  def cb(x):journal.append(dict(x=x.tolist(),minimum_gap_mm=float(gap(x).min()),potential_scaled=-float(load@x)))
  result=minimize(lambda x:-load@x,np.zeros(5),jac=lambda x:-load,method='SLSQP',bounds=[(-.2,.2),(-.2,.2),(-.02,.02),(-.2,.2),(-.2,.2)],constraints=[{'type':'ineq','fun':gap}],callback=cb,options={'maxiter':300,'ftol':1e-13,'disp':False})
  x=result.x;allg=geometry(x);active=[r for r in allg if abs(r[0])<1e-7];R=rot(x[2]);posedk=translate(spin(keeper,anchor[0],anchor[1],math.degrees(x[2])),*map(float,np.r_[x[:2],0.]));posedbolts=[translate(spin(b,q['x'],q['y'],math.degrees(x[3+i])),0,0,.5*x[3+i]/(2*np.pi)) for i,(q,b) in enumerate(zip(settings,bolts))];contacts=[];columns=[]
  for gval,i,wi,ci,n,o,cc,dz in active:
   g=groups[i];c=g['circles'][ci];w=g['walls'][wi];zlo=max(c['bb'][2],w['bb'][2]+dz);zhi=min(c['bb'][5],w['bb'][5]+dz);assert zhi>zlo
   wall=translate(spin(w['face'],g['center'][0],g['center'][1],math.degrees(x[3+i])),0,0,dz);rounded=translate(spin(c['face'],anchor[0],anchor[1],math.degrees(x[2])),*map(float,np.r_[x[:2],0.]))
   for fraction in [1/6,.5,5/6]:
    p=cc-c['r']*n;p[2]=zlo+fraction*(zhi-zlo);col=np.zeros((3,6));col[0]=wrench(p,n);col[1+i]=-col[0];columns.append(col.ravel());contacts.append(dict(bolt_index=i,wall=wi,rounded_corner=ci,point_mm=p.tolist(),normal_on_keeper=n.tolist(),gap_mm=gval,z_interval_mm=[zlo,zhi],rounded_FACE_distance_mm=pointdist(rounded,p),socket_FACE_distance_mm=pointdist(wall,p)))
  A=np.column_stack(columns);ext=np.zeros((3,6));ext[1:,5]=torque
  # Four exposed radial host ports. They do not constrain spin, z or keeper DOFs.
  ports=[]
  for i,g in enumerate(groups):
   for ax in [0,1]:
    c=np.zeros((3,6));f=np.eye(3)[ax];c[1+i]=wrench(g['center'],f);ports.append(c.ravel())
  P=np.column_stack(ports);AP=np.c_[A,P];eq=linprog(np.r_[np.ones(A.shape[1]),np.zeros(4)],A_eq=AP,b_eq=-ext.ravel(),bounds=[(0,None)]*A.shape[1]+[(None,None)]*4,method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
  boundmargin=min(.2-abs(x[0]),.2-abs(x[1]),.02-abs(x[2]),.2-abs(x[3]),.2-abs(x[4]));interferences=dict(keeper_host_mm3=common(posedk,host),keeper_installed_pin_mm3=common(posedk,pin),keeper_bolts_mm3=[common(posedk,b) for b in posedbolts]);row=dict(signs=list(signs),conditional_bolt_torque_Nmm=torque.tolist(),optimizer_success=bool(result.success),optimizer_message=result.message,planar_unknowns=['keeper_dx_mm','keeper_dy_mm','keeper_yaw_rad','bolt0_spin_rad','bolt1_spin_rad'],solution=x.tolist(),minimum_all72_gap_mm=float(gap(x).min()),bound_margin=boundmargin,active_finite_lines=len(active),contacts=contacts,all18body_resultant_rows=18,full18row_feasible=bool(eq.success),LP_message=eq.message,interferences=interferences,journal=journal,axial_screw_lead_mm=(.5*x[3:]/(2*np.pi)).tolist(),pin_reaction_N=None,host_reaction_is_explicit_port=True)
  if eq.success:
   lam=eq.x[:A.shape[1]];hostforce=eq.x[A.shape[1]:].reshape(2,2);res=AP@eq.x+ext.ravel();row.update(normal_forces_N=lam.tolist(),host_radial_forces_on_bolts_N=hostforce.tolist(),all18_original_residual_N_Nmm=res.reshape(3,6).tolist(),maximum_original_residual=float(abs(res).max()),keeper_contact_wrench_N_Nmm=(A@lam).reshape(3,6)[0].tolist(),host_wrench_sum_N_Nmm=(P@eq.x[A.shape[1]:]).reshape(3,6).sum(0).tolist(),minimum_normal_force_N=float(lam.min()),internal_common_twist_work_error=float(abs(A.T@np.tile(np.arange(6)/5,3)).max()))
  # No exposed radial host ports: an internal assembly cannot resist net external torque.
  free=linprog(np.ones(A.shape[1]),A_eq=A,b_eq=-ext.ravel(),bounds=(0,None),method='highs');row['no_host_ports_feasible']=bool(free.success)
  rows.append(row);dump(out/('case_'+''.join('p' if s>0 else 'm' for s in signs)+'.json'),row)
 checks=dict(candidate83hashes=True,four_independent_sign_cases=len(rows)==4,all72_inequalities_retained=all(r['minimum_all72_gap_mm']>=-1e-9 for r in rows),no_optimizer_bound_support=all(r['bound_margin']>1e-4 for r in rows),full18_original_balance=all(r['full18row_feasible'] and r['maximum_original_residual']<1e-8 and r['minimum_normal_force_N']>=-1e-9 for r in rows),finite_actual_faces=all(c['rounded_FACE_distance_mm']<1e-7 and c['socket_FACE_distance_mm']<1e-7 for r in rows for c in r['contacts']),actual_keeper_host_pin_nonpenetration=all(r['interferences']['keeper_host_mm3']<=1e-8 and r['interferences']['keeper_installed_pin_mm3']<=1e-8 and max(r['interferences']['keeper_bolts_mm3'])<=1e-8 for r in rows),common_virtualwork=all(r.get('internal_common_twist_work_error',1)<1e-10 for r in rows),same_sign_free_host_rejected=all(not r['no_host_ports_feasible'] for r in rows if r['signs'][0]==r['signs'][1]))
 dump(out/'summary.json',dict(status='ACTUAL_P1_TWO_SOCKET_COUPLED_CONTACT_CONDITIONAL_REFERENCE' if all(checks.values()) else 'ACTUAL_P1_TWO_SOCKET_COUPLED_CONTACT_FAIL',candidate=ref(cp),producer=ref(out/'producer.py'),source_conditional_cut=ref(source),checks={k:bool(v) for k,v in checks.items()},rows=rows,elapsed_s=time.monotonic()-start,actual_changed_CAD=[],accepted83body_physical_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Five planar unknowns are free; keeper z/roll/pitch and bolt lateral/tilt/axial compliance NOT solved. Three-body full18 resultant check does not certify fullDOF stability.','Four unknown radial host reaction ports at bolt axes are explicit conditional BC, NOT actual head/shank/thread/nut/cage contact. No host spin fixation or fictitious tongue returntorque.','Actual finite rounded plug/socket walls and actual keeper/host/installedsplitpin solids checked at each pose; sampled active line traction is not Hertz area pressure/elasticity or strength.','No keeper gravity or preload in this pure torque contrast. Screw lead is frictionless necessary torque bound from conditional cut, not measured tightening/operating demand.','Contact normal inequalities describe interior supporting hex planes; whole CAD Boolean/finite-face checks guard this local branch. Clearance/axialescape, real pin reaction and full3D constitutive coupling remain.','All22system gates, original mesh1percent/time.1percent/globalenergy, source minima/process/fullstroke/speed/protection/mass/3Finger remain.']))
 print(json.dumps(dict(checks=checks,rows=[{k:r.get(k) for k in ['signs','solution','full18row_feasible','maximum_original_residual','interferences','host_radial_forces_on_bolts_N']} for r in rows])));return 0 if all(checks.values()) else 2
if __name__=='__main__':sys.exit(main())
