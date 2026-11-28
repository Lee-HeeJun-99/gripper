"""Full actual footed P1 plate frictional incremental local reference.
Actual finite upper faces carry explicitly affine Neumann wrench references
from required cut reactions. This is NOT actual83body/upperthread equilibrium.
Floor normal contact active set; tangential stick admitted ONLY if reactions
satisfy measured-or-assumed friction cone. A failed cone stays FAIL.
"""
import sys,json,time,shutil,resource
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import cg, splu
import pyamg
import osqp
from skfem import MeshTet,Basis,ElementVector,ElementTetP1,asm
from skfem.models.elasticity import linear_elasticity,lame_parameters
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
from primary_finite_body34 import meshpart,wrenchmat
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate
from primary_anchor_contact38 import common_faces,surface_moment
started=time.monotonic();h=float(sys.argv[1]);nd=int(sys.argv[3]);angles=np.arange(nd)*2*np.pi/nd;directions=np.c_[np.cos(angles),np.sin(angles)];friction_facets=np.c_[np.cos(angles+np.pi/nd),np.sin(angles+np.pi/nd)]/np.cos(np.pi/nd);out=ROOT/'validation/integrated'/sys.argv[2];out.mkdir();shutil.copyfile(__file__,out/'producer.py')
def phase(n,**kw):print(json.dumps(dict(phase=n,elapsed_s=time.monotonic()-started,RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,**kw)),flush=True)
cp=ROOT/'cad/exports/primaryP1_ground65a/summary.json';cad=json.loads(cp.read_text());step=REPO/cad['part_references']['EXTERNAL_BENCH_PLATE']['path'];assert sha(step)==cad['part_references']['EXTERNAL_BENCH_PLATE']['SHA256'];src=ROOT/'validation/integrated/primaryP1_floor65c';sd=json.loads((src/'summary.json').read_text());assert all(sd['checks'].values());ld=json.loads((src/'load_ledger.json').read_text());fields=json.loads((src/'contact_fields.json').read_text());case=next(q for q in fields['rows'] if q['ground_mu_ASSUMED']==.3);ray=np.array(case['full_ray_coefficients']);patches=json.loads((REPO/ld['source_upper_patches']['path']).read_text());ports=json.loads((REPO/ld['source_ports']['path']).read_text())['ports'];sourceports=[];j=0
# Reconstruct actual prescribed wrench on each plate interface, without changing partDOFs.
for q in patches:
 target=np.zeros(6);tang=[i for i in range(3) if i!=q['axis']]
 for c in q['cells']:
  for a,sign in [(tang[0],1),(tang[0],-1),(tang[1],1),(tang[1],-1)]:
   f=np.array(q['normal_on_i'],float);f[a]+=.3*sign
   if q['body_i']=='EXTERNAL_BENCH_PLATE':target+=ray[j]*wrenchmat(np.array(c['point_mm'])[None])[0]@f
   if q['body_j']=='EXTERNAL_BENCH_PLATE':target-=ray[j]*wrenchmat(np.array(c['point_mm'])[None])[0]@f
   j+=1
 if 'EXTERNAL_BENCH_PLATE' in [q['body_i'],q['body_j']]:sourceports.append(dict(label=q['label'],axis=q['axis'],value=q['value_mm'],target_N_Nmm=target,other='BENCH_SUPPORT'))
for q in ports:
 if q['body_j']=='EXTERNAL_BENCH_PLATE':
  target=-ray[j]*wrenchmat(np.array(q['point_mm'])[None])[0]@np.array(q['direction']);sourceports.append(dict(label=q['label'],axis=2,value=-138.,target_N_Nmm=target,other=q['part_IDs'][1]))
 j+=1
phase('before_mesh');p,t,tri,V=meshpart(step,h,8);phase('after_mesh',nodes=len(p),tetra=len(t));N=3*len(p);m=MeshTet(p.T,t.T);E=200000.;nu=.3;la,mu=lame_parameters(E,nu);K=sparse.csr_matrix((N,N));el=ElementVector(ElementTetP1())
for first in range(0,len(t),8000):
 assert not(ROOT/'runtime/STOP').exists();K+=asm(linear_elasticity(la,mu),Basis(m,el,intorder=2,elements=np.arange(first,min(first+8000,len(t)))))
phase('after_assembly',nnz=K.nnz);det=np.linalg.det(np.transpose(p[t[:,1:]]-p[t[:,0,None]],(0,2,1)));vol=abs(det)/6;lump=np.zeros(len(p))
for a in range(4):np.add.at(lump,t[:,a],vol/4)
F=np.zeros((len(p),3));F[:,2]=-lump*7900e-9*9.80665;inputjournal=[];floortri=tri[np.all(abs(p[tri,2]+170)<1e-7,axis=1)];floornodes=np.unique(floortri);nodearea=np.zeros(len(p))
for ns in floortri:
 ar=np.linalg.norm(np.cross(p[ns[1]]-p[ns[0]],p[ns[2]]-p[ns[0]]))/2;nodearea[ns]+=ar/3
plate=read(step);support=translate(read(REPO/cad['part_references']['BENCH_SUPPORT']['path']),.1,0,0)
# Finite face source quadrature; actualCADcommonfaces select genuine contact footprint.
# Analytic point classification limits triangles. Source is affine reference, not
# the nonunique constant-cell LP pressure and never claimed as solved uppercontact.
from OCP.BRepClass import BRepClass_FaceClassifier
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_IN,TopAbs_ON,TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
def flatten_faces(shapes):
 result=[]
 for shape in shapes:
  ex=TopExp_Explorer(shape,TopAbs_FACE)
  while ex.More():result.append(TopoDS.Face_s(ex.Current()));ex.Next()
 return result
for port in sourceports:
 other=support if port['other']=='BENCH_SUPPORT' else read(REPO/cad['part_references'][port['other']]['path']);fs=flatten_faces(common_faces(plate,other,port['axis'],port['value']));assert fs,(port['label'],'noactualCADsource');facets=tri[np.all(abs(p[tri,port['axis']]-port['value'])<1e-7,axis=1)];qs=[];M=np.zeros((6,6))
 for ns in facets:
  pts=p[ns];ar=np.linalg.norm(np.cross(pts[1]-pts[0],pts[2]-pts[0]))/2
  for bc in np.array([[2/3,1/6,1/6],[1/6,2/3,1/6],[1/6,1/6,2/3]]):
   x=bc@pts
   if not any(BRepClass_FaceClassifier(face,gp_Pnt(*map(float,x)),1e-7).State() in [TopAbs_IN,TopAbs_ON] for face in fs):continue
   H=wrenchmat(x[None])[0];M+=ar/3*(H@H.T);qs.append((ns,bc,ar/3,H,x))
 target=port['target_N_Nmm'];coeff=np.linalg.solve(M,target);local=np.zeros_like(F)
 for ns,bc,weight,H,x in qs:
  f=H.T@coeff
  for node,b in zip(ns,bc):local[node]+=weight*b*f
 F+=local;W=wrenchmat(p).transpose(1,0,2).reshape(6,-1)@local.ravel();inputjournal.append(dict(label=port['label'],actual_finite_CAD_face_area_mm2=sum(surface_moment(f)[0] for f in fs),FE_quadrature_area_mm2=sum(q[2] for q in qs),target_N_Nmm=target.tolist(),applied_N_Nmm=W.tolist(),reference='Affine traction with exact6wrench; sourcepressurefield/uppercontact NOT certified'))
phase('after_loads',floor_nodes=len(floornodes));center=np.average(p,weights=lump,axis=0);R=np.zeros((N,6))
for a,e in enumerate(np.eye(3)):R[:,a]=np.tile(e,len(p));R[:,a+3]=np.cross(e,p-center).ravel()
# Use existing OSQP. Tangential dissipation is support of inscribed diamond:
# mu*N*support_polygon(du). Frozen normal fixedpoint is Coulomb,
# NOT associated cone/dilatancy. Check original law after every accepted step.
# Exact static condensation: retain ALL actual floor displacement DOFs,
# eliminate only unconstrained linear elastic interior. No physical clamp.
scaleu=1e-4;nf=len(floornodes);bd=(3*floornodes[:,None]+np.arange(3)).ravel();inside=np.setdiff1d(np.arange(N),bd);nb=len(bd)
phase('before_interior_factor',interior=len(inside),contact_DOF=nb)
Kii=K[inside][:,inside].tocsc();Kib=K[inside][:,bd].tocsc();Kbi=K[bd][:,inside].tocsr();lu=splu(Kii,permc_spec='MMD_AT_PLUS_A')
base=lu.solve(F.ravel()[inside]);S=K[bd][:,bd].toarray();X=np.empty((len(inside),nb))
for first in range(0,nb,24):
 assert not(ROOT/'runtime/STOP').exists()
 X[:,first:first+24]=lu.solve(Kib[:,first:first+24].toarray())
S-=Kbi@X;skew=float(abs(S-S.T).max());S=(S+S.T)/2;fcond=F.ravel()[bd]-Kbi@base
phase('after_condensation',max_asymmetry_N_mm=skew,rigid_mode_error=float(abs(S@R[bd]).max()))
np.savez_compressed(out/'condensation.npz',boundary_DOF=bd,interior_DOF=inside,Schur_N_mm=S,condensed_load_N=fcond)
from scipy.linalg import cho_factor,cho_solve
P=scaleu*S
u=np.zeros(N);reactions=np.zeros((len(p),3));normalguess=nodearea[floornodes]/nodearea.sum()*(-F[:,2].sum())*.1;hist=[];saved=[];allsteps=True;lastlaw={};lastfrac=0.;finaldual=None
cuts=[[d.copy() for d in directions] for _ in floornodes]
rho=1.;factor=cho_factor(P+rho*np.eye(nb));warm=None
for fraction in [.1,.25,.5,1.]:
 previous=u.copy();converged=False
 for outer in range(80):
  assert not(ROOT/'runtime/STOP').exists()
  # Exact circular Tresca proximal map with frozen normal. No friction
  # polygon and no norm regularization. ADMM consensus is algorithmic only.
  prev=previous[bd].reshape(-1,3)/scaleu
  x=u[bd]/scaleu;z=x.copy();dual=np.zeros(nb)
  innerok=False
  for inner in range(100000):
   x=cho_solve(factor,fraction*fcond+rho*(z-dual),check_finite=False)
   oldz=z.copy();w=(x+dual).reshape(-1,3);zz=w.copy();slip=w[:,:2]-prev[:,:2];length=np.linalg.norm(slip,axis=1)
   zz[:,:2]=prev[:,:2]+slip*np.maximum(0,1-.3*normalguess/(rho*np.maximum(length,1e-300)))[:,None];zz[:,2]=np.maximum(w[:,2],0);z=zz.ravel();dual+=x-z
   primal=float(abs(x-z).max());dualres=float(abs(rho*(z-oldz)).max())
   if primal<1e-9 and dualres<1e-9:innerok=True;break
   if inner%200==199:
    assert not(ROOT/'runtime/STOP').exists()
    newrho=rho*2 if primal>10*dualres else rho/2 if dualres>10*primal else rho
    if newrho!=rho:
     dual*=rho/newrho;rho=newrho;factor=cho_factor(P+rho*np.eye(nb))
  class Result:pass
  sol=Result();sol.x=x;sol.y=rho*dual
  row=dict(fraction=fraction,outer=outer,status='ADMM_consensus_converged' if innerok else 'ADMM_iteration_limit',inner_iterations=inner+1,primal_residual=primal,dual_residual=dualres,rho=rho,inner_QP_converged=innerok)
  phase('exact_circular_proximal',**row)
  if not np.isfinite(x).all():hist.append(row);break
  u[bd]=sol.x[:nb]*scaleu;u[inside]=fraction*base-X@u[bd];reaction=(K@u-fraction*F.ravel()).reshape(-1,3);normal=np.maximum(reaction[floornodes,2],0);delta=u.reshape(-1,3)[floornodes,:2]-previous.reshape(-1,3)[floornodes,:2];gap=u.reshape(-1,3)[floornodes,2];T=reaction[floornodes,:2];slack=.3*normal-np.linalg.norm(T,axis=1);diss=-np.einsum('ij,ij->i',T,delta);support=.3*normal*np.linalg.norm(delta,axis=1);normalerr=float(abs(normal-normalguess).max());lawerr=float(abs(diss-support).max());off=np.setdiff1d(np.arange(len(p)),floornodes);freeerr=float(abs(reaction[off]).max());row.update(normal_fixedpoint_error_N=normalerr,min_gap_mm=float(gap.min()),minimum_cone_slack_N=float(slack.min()),max_dissipation_error_Nmm=lawerr,off_floor_equilibrium_error_N=freeerr);hist.append(row)
  np.savez_compressed(out/f'trial_{fraction:g}_{outer:02d}.npz',points_mm=p,tetra=t,displacement_mm=u.reshape(-1,3),load_N=fraction*F,reaction_N=reaction,floor_nodes=floornodes,previous_displacement_mm=previous.reshape(-1,3),frozen_normal_N=normalguess,QP_dual=sol.y)
  dump(out/'iteration_journal.json',dict(history=hist,accepted_steps=saved,accepted_fraction=lastfrac,current_field=f'trial_{fraction:g}_{outer:02d}.npz'))
  phase('physical_law',**row)
  lastlaw=dict(min_normal_reaction_N=float(reaction[floornodes,2].min()),normal_fixedpoint_error_N=normalerr,min_gap_mm=float(gap.min()),minimum_cone_slack_N=float(slack.min()),max_dissipation_error_Nmm=lawerr,off_floor_equilibrium_error_N=freeerr,normal_complementarity_Nmm=float(abs(gap*normal).max()),min_dissipation_Nmm=float(diss.min()))
  if float(reaction[floornodes,2].min())>=-1e-7 and float(abs(gap*reaction[floornodes,2]).max())<1e-8 and float(diss.min())>=-1e-9 and normalerr<1e-7 and float(gap.min())>=-1e-9 and float(slack.min())>=-1e-7 and lawerr<1e-9 and freeerr<1e-7:
   converged=True;normalguess=normal;finaldual=sol.y.copy();break
  normalguess=.5*normalguess+.5*normal
 if not converged:allsteps=False;break
 reactions=reaction.copy();saved.append(dict(fraction=fraction,law=lastlaw,elastic_energy_Nmm=.5*float(u@K@u),step_friction_dissipation_Nmm=float(diss.sum()),maximum_slip_mm=float(np.max(np.max(delta@directions.T,axis=1))),sliding_nodes=int(np.sum(np.max(delta@directions.T,axis=1)>1e-9)),outer_iterations=outer+1));lastfrac=fraction
phase('after_incremental_contact',all_steps=allsteps,accepted_fraction=lastfrac);u3=u.reshape(-1,3);actualreaction=(K@u-(hist[-1]['fraction'] if hist else 0)*F.ravel()).reshape(-1,3);forcefraction=hist[-1]['fraction'] if hist else 0.;off=np.setdiff1d(np.arange(len(p)),floornodes);WW=wrenchmat(p).transpose(1,0,2).reshape(6,-1);W=WW@((forcefraction*F).ravel()+actualreaction.ravel());energy=.5*float(u@K@u);iv=np.linalg.inv(p[t[:,1:]]-p[t[:,0,None]]);grad=np.concatenate([-iv.sum(2)[:,None,:],iv.transpose(0,2,1)],axis=1);G=np.einsum('tai,taj->tij',u3[t],grad);eps=(G+G.transpose(0,2,1))/2;sig=2*mu*eps+la*np.trace(eps,axis1=1,axis2=2)[:,None,None]*np.eye(3);ee=float(np.sum(.5*np.einsum('tij,tij->t',eps,sig)*vol));dev=sig-np.trace(sig,axis1=1,axis2=2)[:,None,None]*np.eye(3)/3;vm=np.sqrt(1.5*np.sum(dev*dev,axis=(1,2)));sourceerr=max(float(abs(np.array(q['applied_N_Nmm'])-q['target_N_Nmm']).max()) for q in inputjournal);gap=u3[floornodes,2];normal=actualreaction[floornodes,2];slack=.3*np.maximum(normal,0)-np.linalg.norm(actualreaction[floornodes,:2],axis=1)
checks=dict(actual_plate_hash=True,all_four_increments_converged=allsteps and lastfrac==1.,all_local_Coulomb_laws=allsteps and all(s['law']['min_normal_reaction_N']>=-1e-7 and s['law']['min_dissipation_Nmm']>=-1e-9 and s['law']['min_gap_mm']>=-1e-9 and s['law']['minimum_cone_slack_N']>=-1e-7 and s['law']['normal_complementarity_Nmm']<1e-8 and s['law']['max_dissipation_error_Nmm']<1e-9 for s in saved),off_floor_equilibrium=float(abs(actualreaction[off]).max())<1e-7,all6physical_force_moment_balance=float(abs(W).max())<1e-6,actual_source_wrenches=sourceerr<1e-8,volume1percent=abs(vol.sum()/V-1)<.01,finite=bool(np.isfinite(u).all()),element_energy=abs(ee/energy-1)<1e-8)
np.savez_compressed(out/'field.npz',points_mm=p,tetra=t,displacement_mm=u3,load_N=forcefraction*F,reaction_N=actualreaction,floor_nodes=floornodes,vm_MPa=vm)
dump(out/'summary.json',dict(status='ACTUAL_FULL_PLATE_INCREMENTAL_COULOMB_LOCAL_REFERENCE' if all(checks.values()) else 'ACTUAL_FULL_PLATE_INCREMENTAL_COULOMB_FAIL',candidate=ref(cp),STEP=ref(step),source=ref(src/'summary.json'),producer=ref(out/'producer.py'),field=ref(out/'field.npz'),checks={k:bool(v) for k,v in checks.items()},nonlinear_inexact_innerQP=True,inner_QP_iteration_limit=12000,physical_acceptance_unchanged=True,exact_circular_proximal_ADMM=True,initial_support_directions_UNUSED=nd,friction_polygon_vertices=nd,friction_directions=directions.tolist(),friction_facets=friction_facets.tolist(),condensation_max_asymmetry_N_mm=skew,condensation=ref(out/'condensation.npz'),h_mm=h,nodes=len(p),tetra=len(t),E_ASSUMED_MPa=E,nu_ASSUMED=nu,rho_ASSUMED_kg_m3=7900,mu_ASSUMED=.3,minimum_strength_MPa=None,physical_fixed_DOF=0,physical_floor_contact='Unilateral normal; exact circular norm proximal ADMM with original circular cone and circular maximum dissipation acceptance',peak_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,accepted_load_fraction=lastfrac,current_attempt_fraction=forcefraction,accepted_steps=saved,fixedpoint_history=hist,last_law=lastlaw,static_energy_Nmm=energy,independent_element_energy_Nmm=ee,raw_max_vm_MPa=float(vm.max()),maximum_displacement_mm=float(np.linalg.norm(u3,axis=1).max()),total_force_moment_residual_N_Nmm=W.tolist(),minimum_floor_gap_mm=float(gap.min()),minimum_normal_reaction_N=float(normal.min()),minimum_friction_slack_N=float(slack.min()),source_ports=inputjournal,mesh_volume_mm3=float(vol.sum()),CAD_volume_mm3=V,volume_error=abs(vol.sum()/V-1),newly_qualified_system_gate_ids=[],accepted83body_physical_equilibria=0,whole_system_release=False,elapsed_s=time.monotonic()-started,limitations=['Entireactualplate,physicalfinitefloor,noarbitrarybodyfixation. Upperaffinetractionsareexplicitreferencewrenches,not solvedupperthread/contactconstitutiveforces.','Fourdeclaredquasistaticloadincrementsfromzero areconditionalpath; increment/mesh/timeconvergence notcertified. StaticenergyidentityorcommittedfrictionlossisNOTglobalenergy.','Normalfixedpointmustconvergeandoriginalmaximumdissipation/gap/coneforcesmustpass. Failedpartialload isNOTfulloperatingequilibrium.','AssumedmaterialandfloormuareNOTsource-minimumorhardwaretruth. Rawstressnotcapacity; all22gatesretaincriteria,NoStage3.']))
print(json.dumps(dict(checks={k:bool(v) for k,v in checks.items()},accepted_fraction=lastfrac,current_fraction=forcefraction)));raise SystemExit(0 if all(checks.values()) else 2)
