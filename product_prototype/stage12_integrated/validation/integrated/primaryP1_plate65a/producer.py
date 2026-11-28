"""Full actual footed P1 plate elastic unilateral floor/stick candidate.
Actual finite upper faces carry explicitly affine Neumann wrench references
from required cut reactions. This is NOT actual83body/upperthread equilibrium.
Floor normal contact active set; tangential stick admitted ONLY if reactions
satisfy measured-or-assumed friction cone. A failed cone stays FAIL.
"""
import sys,json,time,shutil,resource
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import cg
import pyamg
from skfem import MeshTet,Basis,ElementVector,ElementTetP1,asm
from skfem.models.elasticity import linear_elasticity,lame_parameters
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
from primary_finite_body34 import meshpart,wrenchmat
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate
from primary_anchor_contact38 import common_faces,surface_moment
started=time.monotonic();h=float(sys.argv[1]);out=ROOT/'validation/integrated'/sys.argv[2];out.mkdir();shutil.copyfile(__file__,out/'producer.py')
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
from OCP.TopAbs import TopAbs_IN,TopAbs_ON
for port in sourceports:
 other=support if port['other']=='BENCH_SUPPORT' else read(REPO/cad['part_references'][port['other']]['path']);fs=common_faces(plate,other,port['axis'],port['value']);assert fs,(port['label'],'noactualCADsource');facets=tri[np.all(abs(p[tri,port['axis']]-port['value'])<1e-7,axis=1)];qs=[];M=np.zeros((6,6))
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
active=set(floornodes.tolist());history=[];u=np.zeros(N);success=False
for iteration in range(35):
 assert not(ROOT/'runtime/STOP').exists();an=np.array(sorted(active),int);fixed=(3*an[:,None]+np.arange(3)).ravel();free=np.setdiff1d(np.arange(N),fixed);A=K[free][:,free].tocsr();phase('before_AMG',iteration=iteration,contact_nodes=len(an));ml=pyamg.smoothed_aggregation_solver(A,B=R[free],symmetry='symmetric',max_coarse=100);its=[0]
 def callback(x):
  its[0]+=1
  assert not(ROOT/'runtime/STOP').exists()
 u[:]=0;u[free],info=cg(A,F.ravel()[free],M=ml.aspreconditioner(),rtol=1e-11,atol=1e-12,maxiter=1200,callback=callback);assert info==0;del ml,A;reaction=(K@u-F.ravel()).reshape(-1,3);u3=u.reshape(-1,3);remove={int(n) for n in an if reaction[n,2]<-1e-9};add={int(n) for n in floornodes if n not in active and u3[n,2]<-1e-9};history.append(dict(iteration=iteration,active_nodes=len(active),release=len(remove),close=len(add),CG_iterations=its[0],min_normal_N=float(reaction[an,2].min()),min_floor_gap_mm=float(u3[floornodes,2].min())))
 if not remove and not add:success=True;break
 active=(active-remove)|add
phase('after_contact_active_set',converged=success);an=np.array(sorted(active),int);free=np.setdiff1d(np.arange(N),(3*an[:,None]+np.arange(3)).ravel());res=K@u-F.ravel()-reaction.ravel();normal=reaction[an,2];slack=.3*normal-abs(reaction[an,0])-abs(reaction[an,1]);energy=.5*float(u@K@u);halfwork=.5*float(F.ravel()@u);iv=np.linalg.inv(p[t[:,1:]]-p[t[:,0,None]]);grad=np.concatenate([-iv.sum(2)[:,None,:],iv.transpose(0,2,1)],axis=1);G=np.einsum('tai,taj->tij',u3[t],grad);eps=(G+G.transpose(0,2,1))/2;sig=2*mu*eps+la*np.trace(eps,axis1=1,axis2=2)[:,None,None]*np.eye(3);ee=float(np.sum(.5*np.einsum('tij,tij->t',eps,sig)*vol));dev=sig-np.trace(sig,axis1=1,axis2=2)[:,None,None]*np.eye(3)/3;vm=np.sqrt(1.5*np.sum(dev*dev,axis=(1,2)));WW=wrenchmat(p).transpose(1,0,2).reshape(6,-1);W=WW@(F.ravel()+reaction.ravel());ratio=np.linalg.det(np.transpose((p+u3)[t[:,1:]]-(p+u3)[t[:,0,None]],(0,2,1)))/det;ffres=(K@u-F.ravel())[free];complementarity=float(abs(u3[floornodes,2]*reaction[floornodes,2]).max());sourceerr=max(float(abs(np.array(q['applied_N_Nmm'])-q['target_N_Nmm']).max()) for q in inputjournal)
checks=dict(actual_plate_hash=True,contact_active_set_converged=success,nonpenetration=float(u3[floornodes,2].min())>=-1e-9,compressive_normal=float(normal.min())>=-1e-9,normal_complementarity=complementarity<1e-9,stick_reaction_in_mu03_diamond=float(slack.min())>=-1e-9,all_unconstrained_equilibrium=float(abs(ffres).max())<1e-8,all6physical_force_moment_balance=float(abs(W).max())<1e-7,actual_source_wrenches=sourceerr<1e-8,volume1percent=abs(vol.sum()/V-1)<.01,positive_elements=bool(ratio.min()>0),finite=bool(np.isfinite(u).all()),element_energy=abs(ee/energy-1)<1e-8,energy_halfwork=abs(energy/halfwork-1)<1e-8)
np.savez_compressed(out/'field.npz',points_mm=p,tetra=t,displacement_mm=u3,load_N=F,reaction_N=reaction,floor_nodes=floornodes,active_contact_nodes=an,vm_MPa=vm)
dump(out/'summary.json',dict(status='ACTUAL_FULL_PLATE_UNILATERAL_STICK_LOCAL_REFERENCE' if all(checks.values()) else 'ACTUAL_FULL_PLATE_UNILATERAL_OR_STICK_REFERENCE_FAIL',candidate=ref(cp),STEP=ref(step),source=ref(src/'summary.json'),producer=ref(out/'producer.py'),field=ref(out/'field.npz'),checks={k:bool(v) for k,v in checks.items()},h_mm=h,nodes=len(p),tetra=len(t),peak_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,E_ASSUMED_MPa=E,nu_ASSUMED=nu,minimum_strength_MPa=None,rho_ASSUMED_kg_m3=7900,mu_ASSUMED=.3,physical_noncontact_fixed_DOF=0,contact_tangent_constraints='Candidate sticking at current compressive floor nodes; FAILED cone means this candidate is inadmissible,never clamp/constraint success',floor_nodes=len(floornodes),active_contact_nodes=len(an),active_set_history=history,minimum_floor_gap_mm=float(u3[floornodes,2].min()),minimum_contact_normal_N=float(normal.min()),minimum_stick_friction_slack_N=float(slack.min()),stick_friction_violating_nodes=int(np.sum(slack<-1e-9)),max_original_free_DOF_residual_N=float(abs(ffres).max()),total_force_moment_residual_N_Nmm=W.tolist(),source_wrench_error_N_Nmm=sourceerr,source_ports=inputjournal,static_energy_Nmm=energy,independent_element_energy_Nmm=ee,halfwork_Nmm=halfwork,raw_max_vm_MPa=float(vm.max()),maximum_displacement_mm=float(np.linalg.norm(u3,axis=1).max()),mesh_volume_mm3=float(vol.sum()),CAD_volume_mm3=V,volume_error=abs(vol.sum()/V-1),newly_qualified_system_gate_ids=[],accepted83body_physical_equilibria=0,whole_system_release=False,elapsed_s=time.monotonic()-started,limitations=['Entire actual footed plate with actual upperfaces,nominalfloor and sourcewrenchreference; NOT an idealcoupon. UpperNeumannaffinetractions are not actualsolved30LPcellpressure or thread/seatconstitutivelaws.','Normalactive set solved on actualfinitefloorfacets. Candidate stick must independently satisfy nonnegativepressure and friction; a violation isFAIL,notpermission tofixsliding.','Assumed steelE/rho/nu/floormu,not source-minimumstrength/materialtruth. Rawnotchstress isnotcapacity. Mesh/time/globalenergy and83bodyequilibrium notcertified.']))
print(json.dumps(dict(checks={k:bool(v) for k,v in checks.items()},nodes=len(p),energy=energy,stick_violation_nodes=int(np.sum(slack<-1e-9)))));raise SystemExit(0 if all(checks.values()) else 2)
