"""Independent original30row/physical-work audit of actual P1 cut reaction bounds.
No import of producer assembly/LP logic; perturbations must be rejected.
"""
import sys,json,shutil
import numpy as np
from scipy.spatial.transform import Rotation
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,bounds
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE,TopAbs_REVERSED
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');reports=[]
for tag in sys.argv[2:]:
 assert not(ROOT/'runtime/STOP').exists();src=ROOT/'validation/integrated'/tag;d=json.loads((src/'summary.json').read_text());cad=json.loads((REPO/d['candidate']['path']).read_text());L=json.loads((src/'load_ledger.json').read_text());patches=json.loads((src/'patches.json').read_text());rows=json.loads((src/'rows.json').read_text());names=L['body_names'];ext=np.array(L['external_wrench_N_Nm']);mass=json.loads((REPO/L['rest_mass_source']['path']).read_text());fresh=json.loads((REPO/d['source']['path']).read_text());state=json.loads((REPO/fresh['state']['path']).read_text());dy=fresh['root_translation_mm'][1];my=fresh.get('motor_translation_mm',[0,0,0])[1];dx=fresh.get('support_translation_mm',[0,0,0])[0];normals=[]
 for patch in patches:
  n=np.array(patch['normal_on_i']);axis=patch['axis'];value=patch['value_mm'];bind=[]
  for body,sgn in [(patch['body_i'],-1),(patch['body_j'],1)]:
   shape=read(REPO/cad['part_references'][body]['path']);shape=translate(shape,dx if body!='EXTERNAL_BENCH_PLATE' else 0,dy if body=='F0_ROOT_BACK' else my if body=='F0_MICRO_MOTOR' else 0,0);it=TopExp_Explorer(shape,TopAbs_FACE);vectors=[]
   while it.More():
    face=TopoDS.Face_s(it.Current());it.Next();bb=bounds(face);ad=BRepAdaptor_Surface(face)
    if ad.GetType()!=GeomAbs_Plane or abs(bb[axis]-value)>1e-6 or abs(bb[axis+3]-value)>1e-6:continue
    q=ad.Plane().Axis().Direction();vec=np.array([q.X(),q.Y(),q.Z()])*(-1 if face.Orientation()==TopAbs_REVERSED else 1);vectors.append(vec)
   bind.append(any(np.max(abs(vec-sgn*n))<1e-8 for vec in vectors))
  normals.append(dict(label=patch['label'],both_actual_oriented_normals=all(bind)))
 residuals=[];workerr=[];coneerr=[];perturb=[];summaries=[]
 for row in rows:
  if not row['feasible']:continue
  internal=np.zeros_like(ext);reaction_work=0.;fdwork=0.;tw=np.cos(np.arange(30)*.71+.31).reshape(5,6);h=2e-5;rx=row['reactions']
  for q in rx:
   f=np.array(q['direction'])*q['coefficient_N'];p=np.array(q['point_mm'])*.001;w=np.r_[f,np.cross(p,f)];i=names.index(q['body_i']);j=names.index(q['body_j']);internal[i]+=w;internal[j]-=w;reaction_work+=w@(tw[i]-tw[j])
   def motion(k,step):return Rotation.from_rotvec(step*tw[k,3:]).apply(p)+step*tw[k,:3]
   def power(step):return f@(motion(i,step)-motion(j,step))
   fdwork+=(power(-2*h)-8*power(-h)+8*power(h)-power(2*h))/(12*h)
   if q['kind'].startswith('finite'):
    patch=next(p0 for p0 in patches if p0['label']==q['label']);n=np.array(patch['normal_on_i']);fn=f@n;ft=f-fn*n;coneerr.append(max(-fn, np.linalg.norm(ft)-row['mu_ASSUMED']*fn,0))
  host=np.zeros_like(ext);host[-1]=row['required_host_wrench_N_Nm'];balance=internal+host+ext;residuals.append([float(np.linalg.norm(balance[:,:3],axis=1).max()),float(np.linalg.norm(balance[:,3:],axis=1).max())]);workerr.append(abs(fdwork-reaction_work));perturb.append(float(np.linalg.norm((internal-host+ext)[:,:3],axis=1).max()))
  missing=internal.copy()
  for q in rx:
   if not q['label'].startswith('root_connector'):continue
   f=np.array(q['direction'])*q['coefficient_N'];p=np.array(q['point_mm'])*.001;w=np.r_[f,np.cross(p,f)];missing[names.index(q['body_i'])]-=w;missing[names.index(q['body_j'])]+=w
  rootmissing=float(np.linalg.norm((missing+host+ext)[:,:3],axis=1).max());totals={}
  for q in rx:
   if q['kind'].startswith('EXPLICIT'):totals[q['label']]=q['coefficient_N']
  summaries.append(dict(mu_ASSUMED=row['mu_ASSUMED'],required_connector_axial_ports_N=totals,missing_Root_connector_residual_N=rootmissing,maximum_balance_force_N=residuals[-1][0],maximum_balance_moment_Nm=residuals[-1][1],finite_SE3_work_error_Nm=workerr[-1]))
 # independent source mass/object reconstruction; gravity summed by actual
 # deformedcentroids cannot be replaced with undeformed moment arms.
 expected=np.array([state['normal_N'],0,-mass['total_conditional_mass_kg']*9.80665-state['object_downward_friction_N']]);forceerr=float(np.linalg.norm(ext.sum(0)[:3]-expected));
 def wpoint(p,f):return np.r_[f,np.cross(p,f)]
 direct=wpoint(np.array(state['tip_world_m']),[state['normal_N'],0,-state['object_downward_friction_N']])
 for q in state['moving_mass_points']+state['fixed_mass_points']:direct+=wpoint(np.array(q['position_m']),[0,0,-q['mass_kg']*9.80665])
 direct+=np.array(state['string']['wire_gravity_wrench_N_Nm'])+np.array(state['string']['rotor_gravity_wrench_N_Nm'])
 motor=next(q for q in mass['parts'] if q['part_ID']=='F0_MICRO_MOTOR');direct+=wpoint(np.array(motor['CAD_centroid_mm'])*.001+[dx*.001,my*.001,0],[0,0,-motor['conditional_mass_kg']*9.80665])
 for q in L['remaining_gravity']:direct+=wpoint(np.array(q['posed_centroid_m']),[0,0,-q['conditional_mass_kg']*9.80665])
 momenterr=float(np.linalg.norm(ext.sum(0)[3:]-direct[3:]));directforceerr=float(np.linalg.norm(ext.sum(0)[:3]-direct[:3]));areaerr=max(np.linalg.norm(sum((c['area_mm2']*np.array(c['point_mm']) for c in p['cells']),np.zeros(3))/p['area_mm2']-p['centroid_mm']) for p in patches)
 checks=dict(producer_local_checks=all(d['checks'].values()),all77identities=len(cad['part_references'])==77 and all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values()),actual_both_oriented_normals=all(q['both_actual_oriented_normals'] for q in normals),cell_centroid_integral=areaerr<1e-7,independent_all30force=max(q[0] for q in residuals)<1e-8,independent_all30moment=max(q[1] for q in residuals)<1e-10,physical_SE3_virtualwork=max(workerr)<1e-9,physical_Coulomb_cone=max(coneerr)<1e-10,all77mass_and_carriedobject_force=forceerr<1e-10 and directforceerr<1e-10,all77deformed_centroid_moments=momenterr<1e-10,wrong_host_sign_rejected=min(perturb)>1.,missing_required_Root_reaction_rejected=min(q['missing_Root_connector_residual_N'] for q in summaries)>1e-4,all_floatinghost_cases_rejected=all(not q['feasible'] for q in rows if not q['explicit_unknown_host_resultant_port']))
 reports.append(dict(source=ref(src/'summary.json'),candidate=d['candidate'],checks={k:bool(v) for k,v in checks.items()},actual_normal_bindings=normals,independent_mass_object_force_error_N=forceerr,independent_deformed_mass_object_moment_error_Nm=momenterr,maximum_cell_centroid_error_mm=float(areaerr),reaction_summaries=summaries,physical_equilibria_accepted=0))
dump(out/'summary.json',dict(status='ACTUAL77_INDEPENDENT_FINITE_CONTACT_WORK_AND_MASS_PORT_AUDIT_LOCAL_PASS_NOT_RELEASE' if all(all(r['checks'].values()) for r in reports) else 'ACTUAL77_CONTACT_WORK_MASS_AUDIT_FAIL',candidate=reports[0]['candidate'],producer=ref(out/'producer.py'),reports=reports,all_checks=all(all(r['checks'].values()) for r in reports),accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,scope='Independentnecessarycutloadreactionbounds,NOTactualcompliant77part equilibrium/sourcecapacity/hostcertification'));print((out/'summary.json').read_text(),flush=True);raise SystemExit(0 if all(all(r['checks'].values()) for r in reports) else 2)
