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
from primary_finite_body34 import wrenchmat
from primary_inplane_mesh70b import meshpart
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
phase('before_mesh');p,t,tri,V=meshpart(step,h,8,float(sys.argv[4]),out);phase('after_mesh',nodes=len(p),tetra=len(t));N=3*len(p);m=MeshTet(p.T,t.T);E=200000.;nu=.3;la,mu=lame_parameters(E,nu);K=sparse.csr_matrix((N,N));el=ElementVector(ElementTetP1())
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
qbc=np.array([[1/3,1/3,1/3],[.059715871789770,.470142064105115,.470142064105115],[.470142064105115,.059715871789770,.470142064105115],[.470142064105115,.470142064105115,.059715871789770],[.797426985353087,.101286507323456,.101286507323456],[.101286507323456,.797426985353087,.101286507323456],[.101286507323456,.101286507323456,.797426985353087]])
qw=np.array([.225]+[.132394152788506]*3+[.125939180544827]*3)
assert abs(qw.sum()-1)<1e-13
fixedupperpath=ROOT/'validation/integrated/primaryP1_upperpoints68/upper_points.json'
fixedupper=json.loads(fixedupperpath.read_text());uppermapping=[]
from scipy.spatial import cKDTree
for port in fixedupper:
 facets=tri[np.all(abs(p[tri,port['axis']]-port['value_mm'])<1e-7,axis=1)];tang=[i for i in range(3) if i!=port['axis']];local=np.zeros_like(F)
 xy=p[facets][:,:,tang];centers=xy.mean(1);radius=float(np.linalg.norm(xy-centers[:,None,:],axis=2).max())+1e-8;tree=cKDTree(centers);xyz=np.array(port['points_mm']);forces=np.array(port['integrated_force_N']);neighbors=tree.query_ball_point(xyz[:,tang],radius)
 qi=np.repeat(np.arange(len(xyz)),[len(q) for q in neighbors]);fi=np.concatenate([np.array(q,dtype=int) for q in neighbors]);assert len(qi)>0
 inverse=np.linalg.inv(np.transpose(xy[:,1:]-xy[:,0,None],(0,2,1)));bc12=np.einsum('nij,nj->ni',inverse[fi],xyz[qi][:,tang]-xy[fi,0]);bc=np.c_[1-bc12.sum(1),bc12];ok=bc.min(1)>=-1e-10;valid_q,indices=np.unique(qi[ok],return_index=True);chosen=np.flatnonzero(ok)[indices]
 if len(valid_q)!=len(xyz):
  missing=np.setdiff1d(np.arange(len(xyz)),valid_q);dump(out/'upper_coverage_failure.json',dict(label=port['label'],source=ref(fixedupperpath),missing_points_mm=xyz[missing].tolist(),missing_integrated_force_N=forces[missing].tolist(),missing_count=len(missing),total_count=len(xyz),policy='REJECT no dropping or extrapolation'));raise ValueError((port['label'],'fixed physical upperpoint outside actual target mesh',len(missing)))
 nodes=facets[fi[chosen]];bc=bc[chosen];assert abs(np.einsum('ni,nij->nj',bc,p[nodes])-xyz).max()<1e-8
 for j in range(3):np.add.at(local,nodes[:,j],bc[:,j,None]*forces)
 F+=local;W=wrenchmat(p).transpose(1,0,2).reshape(6,-1)@local.ravel();assert abs(W-port['target_N_Nmm']).max()<1e-8
 inputjournal.append(dict(label=port['label'],target_N_Nmm=port['target_N_Nmm'],applied_N_Nmm=W.tolist(),minimum_interpolation_weight=float(bc.min()),reference='Identical frozen physical7point affine load reference, exact triangle coverage and workadjoint pullback; NOT solveduppercontact'))
 np.savez_compressed(out/('upper_mapping_'+str(len(uppermapping))+'.npz'),point_mm=xyz,nodes=nodes,barycentric=bc,integrated_force_N=forces)
 uppermapping.append(dict(label=port['label'],mapping=ref(out/('upper_mapping_'+str(len(uppermapping))+'.npz'))))
dump(out/'upper_pullback.json',dict(source=ref(fixedupperpath),ports=uppermapping))
phase('after_loads',floor_nodes=len(floornodes));center=np.average(p,weights=lump,axis=0);R=np.zeros((N,6))
for a,e in enumerate(np.eye(3)):R[:,a]=np.tile(e,len(p));R[:,a+3]=np.cross(e,p-center).ravel()
# Use existing OSQP. Tangential dissipation is support of inscribed diamond:
# mu*N*support_polygon(du). Frozen normal fixedpoint is Coulomb,
# NOT associated cone/dilatancy. Check original law after every accepted step.
# Exact static condensation: retain ALL actual floor displacement DOFs,
# eliminate only unconstrained linear elastic interior. No physical clamp.
scaleu=1e-4;nf=len(floornodes);bd=(3*floornodes[:,None]+np.arange(3)).ravel();inside=np.setdiff1d(np.arange(N),bd);nb=len(bd)
phase('before_interior_factor',interior=len(inside),contact_DOF=nb)
Kii=K[inside][:,inside].tocsc();Kib=K[inside][:,bd].tocsc();Kbi=K[bd][:,inside].tocsr();lu=splu(Kii,permc_spec='MMD_AT_PLUS_A',diag_pivot_thresh=0.,options={'SymmetricMode':True});phase('after_SPD_no_pivot_factor_without_factor_copies')
base=lu.solve(F.ravel()[inside]);S=K[bd][:,bd].toarray();X=np.empty((len(inside),nb))
for first in range(0,nb,24):
 assert not(ROOT/'runtime/STOP').exists()
 X[:,first:first+24]=lu.solve(Kib[:,first:first+24].toarray())
S-=Kbi@X;skew=float(abs(S-S.T).max());S=(S+S.T)/2;fcond=F.ravel()[bd]-Kbi@base
phase('after_condensation',max_asymmetry_N_mm=skew,rigid_mode_error=float(abs(S@R[bd]).max()))
np.savez_compressed(out/'condensation.npz',boundary_DOF=bd,interior_DOF=inside,Schur_N_mm=S,condensed_load_N=fcond)
# Frozen common material Voronoi quadrature on both declared meshes.
# Integrated q are physical forces: q = weight * traction, virtual work B^T q.
from scipy.linalg import cho_factor,cho_solve
ng=0
frozen_path=ROOT/'validation/integrated/primaryP1_unionquad68/material_quadrature.npz'
frozen=np.load(frozen_path);qpoints=frozen['points_mm'];weights=frozen['weights_mm2'];B=[];localindex={int(n):i for i,n in enumerate(floornodes)}
for xx3 in qpoints:
 xx=xx3[:2];found=False
 for ns in floortri:
  xy=p[ns,:2];bc12=np.linalg.solve((xy[1:]-xy[0]).T,xx-xy[0]);bc=np.r_[1-bc12.sum(),bc12]
  if bc.min()>=-1e-8:
   row=np.zeros(nf)
   for n,b in zip(ns,bc):row[localindex[int(n)]]+=b
   B.append(row);found=True;break
 assert found,xx
B=np.array(B);C=np.kron(B,np.eye(3));nq=len(B)
assert abs(weights.sum()-1600)<1e-8 and abs(B.sum(1)-1).max()<1e-10
assert abs(B@p[floornodes]-qpoints).max()<1e-8
rng=np.random.default_rng(68);vu=rng.normal(size=nb);vf=rng.normal(size=3*nq)
adjoint_error=abs((C@vu)@vf-vu@(C.T@vf))
np.savez_compressed(out/'quadrature.npz',points_mm=qpoints,weights_mm2=weights,B=B,C=C,floor_triangles=floortri,floor_nodes=floornodes)
phase('fixed_floor_quadrature',grid_subdivisions=ng,points=nq,area_mm2=float(weights.sum()),adjoint_error=float(adjoint_error))
P=scaleu*S;rho=1.;factor=cho_factor(P+rho*(C.T@C));u=np.zeros(N);hist=[];saved=[];allsteps=True;lastfrac=0.;forcefraction=0.;qforce=np.zeros((nq,3));normalguess=weights/weights.sum()*(-F[:,2].sum())*.1
lastdualforce=None
fractions=[.1,.25,.5,1.]
for fraction in fractions:
 previous=u.copy();converged=False
 if lastfrac>0:
  ratio=fraction/lastfrac;u*=ratio;normalguess*=ratio
  if lastdualforce is not None:lastdualforce*=ratio
 for outer in range(80):
  assert not(ROOT/'runtime/STOP').exists()
  prev=(C@previous[bd]/scaleu).reshape(-1,3);x=u[bd]/scaleu;z=C@x;dual=np.zeros(3*nq) if lastdualforce is None else lastdualforce/rho;innerok=False
  for inner in range(100000):
   x=cho_solve(factor,fraction*fcond+rho*C.T@(z-dual),check_finite=False)
   oldz=z.copy();w=(C@x+dual).reshape(-1,3);zz=w.copy();slip=w[:,:2]-prev[:,:2];length=np.linalg.norm(slip,axis=1)
   zz[:,:2]=prev[:,:2]+slip*np.maximum(0,1-.3*normalguess/(rho*np.maximum(length,1e-300)))[:,None];zz[:,2]=np.maximum(w[:,2],0);z=zz.ravel();dual+=C@x-z
   primal=float(abs(C@x-z).max());dualres=float(abs(rho*C.T@(z-oldz)).max())
   if primal<1e-11 and dualres<1e-11:innerok=True;break
   if inner%200==199:
    assert not(ROOT/'runtime/STOP').exists()
    newrho=rho*2 if primal>10*dualres else rho/2 if dualres>10*primal else rho
    if newrho!=rho:dual*=rho/newrho;rho=newrho;factor=cho_factor(P+rho*(C.T@C))
  lastdualforce=rho*dual.copy()
  u[bd]=x*scaleu;u[inside]=fraction*base-X@u[bd];reaction=(K@u-fraction*F.ravel()).reshape(-1,3)
  # Lagrange sign: S u-f = -C^T rho*dual.
  qforce=(-rho*dual).reshape(-1,3);normal=np.maximum(qforce[:,2],0);uq=(C@u[bd]).reshape(-1,3);delta=uq[:,:2]-prev[:,:2]*scaleu;gap=uq[:,2];T=qforce[:,:2];slack=.3*normal-np.linalg.norm(T,axis=1);diss=-np.einsum('ij,ij->i',T,delta);support=.3*normal*np.linalg.norm(delta,axis=1)
  normalerr=float(abs(normal-normalguess).max());lawerr=float(abs(diss-support).max());off=np.setdiff1d(np.arange(len(p)),floornodes);freeerr=float(abs(reaction[off]).max());pullerr=float(abs(reaction.ravel()[bd]-C.T@qforce.ravel()).max());vertexgap=float(u.reshape(-1,3)[floornodes,2].min())
  row=dict(fraction=fraction,outer=outer,inner_iterations=inner+1,inner_converged=innerok,primal_residual=primal,dual_residual=dualres,rho=rho,normal_fixedpoint_error_N=normalerr,min_quadrature_gap_mm=float(gap.min()),min_whole_triangle_gap_mm=vertexgap,minimum_cone_slack_N=float(slack.min()),max_dissipation_error_Nmm=lawerr,off_floor_equilibrium_error_N=freeerr,adjoint_pullback_error_N=pullerr,normal_complementarity_Nmm=float(abs(gap*qforce[:,2]).max()),min_normal_reaction_N=float(qforce[:,2].min()),min_dissipation_Nmm=float(diss.min()))
  hist.append(row);phase('fixed_floor_contact',**row)
  np.savez_compressed(out/f'trial_{fraction:g}_{outer:02d}.npz',points_mm=p,tetra=t,displacement_mm=u.reshape(-1,3),load_N=fraction*F,reaction_N=reaction,floor_nodes=floornodes,previous_displacement_mm=previous.reshape(-1,3),frozen_normal_N=normalguess,quadrature_force_N=qforce)
  dump(out/'iteration_journal.json',dict(history=hist,accepted_steps=saved,accepted_fraction=lastfrac))
  forcefraction=fraction
  if innerok and row['min_normal_reaction_N']>=-1e-7 and row['normal_complementarity_Nmm']<1e-8 and row['min_dissipation_Nmm']>=-1e-9 and normalerr<1e-7 and gap.min()>=-1e-9 and slack.min()>=-1e-7 and lawerr<1e-9 and freeerr<1e-7 and pullerr<1e-7:
   converged=True;normalguess=normal;break
  normalguess=normal.copy() # direct Picard update; original physical acceptance unchanged
 if not converged:allsteps=False;break
 lastfrac=fraction;saved.append(dict(fraction=fraction,outer_iterations=outer+1,elastic_energy_Nmm=.5*float(u@K@u),step_friction_dissipation_Nmm=float(diss.sum()),maximum_slip_mm=float(np.linalg.norm(delta,axis=1).max()),law=row))
u3=u.reshape(-1,3);energy=.5*float(u@K@u);iv=np.linalg.inv(p[t[:,1:]]-p[t[:,0,None]]);grad=np.concatenate([-iv.sum(2)[:,None,:],iv.transpose(0,2,1)],axis=1);G=np.einsum('tai,taj->tij',u3[t],grad);eps=(G+G.transpose(0,2,1))/2;sig=2*mu*eps+la*np.trace(eps,axis1=1,axis2=2)[:,None,None]*np.eye(3);ee=float(np.sum(.5*np.einsum('tij,tij->t',eps,sig)*vol));W=np.r_[(forcefraction*F+reaction).sum(0),np.cross(p,forcefraction*F+reaction).sum(0)]
checks=dict(actual_plate_hash=True,full_load_quadrature_law=allsteps and lastfrac==1.,whole_surface_nonpenetration=all(q['min_whole_triangle_gap_mm']>=-1e-9 for q in hist if any(q['fraction']==s['fraction'] and q['outer']==s['outer_iterations']-1 for s in saved)),adjoint_virtual_work=adjoint_error<1e-10,adjoint_force_pullback=pullerr<1e-7,all6physical_force_moment_balance=float(abs(W).max())<1e-6,volume1percent=abs(vol.sum()/V-1)<.01,finite=bool(np.isfinite(u).all()),element_energy=abs(ee/energy-1)<1e-8)
np.savez_compressed(out/'field.npz',points_mm=p,tetra=t,displacement_mm=u3,load_N=forcefraction*F,reaction_N=reaction,floor_nodes=floornodes,quadrature_force_N=qforce,lumped_volume_mm3=lump)
dump(out/'summary.json',dict(status='ACTUAL_FIXED_FLOOR_LOCAL_REFERENCE' if all(checks.values()) else 'ACTUAL_FIXED_FLOOR_FAIL',candidate=ref(cp),STEP=ref(step),source=ref(src/'summary.json'),producer=ref(out/'producer.py'),field=ref(out/'field.npz'),quadrature=ref(out/'quadrature.npz'),checks={k:bool(v) for k,v in checks.items()},h_mm=h,nested_inplane_levels=int(sys.argv[4]),mesh_geometry_journal=ref(out/"mesh_geometry.json"),grid_subdivisions=ng,quadrature_points=nq,quadrature_area_mm2=float(weights.sum()),frozen_upper_points=ref(fixedupperpath),upper_pullback=ref(out/'upper_pullback.json'),frozen_physical_quadrature=ref(frozen_path),warm_start_only=True,condensation_solver="SuperLU symmetric ordering zero diagonal pivot threshold for SPD interior block, all original residuals checked",normal_fixedpoint_update="direct Picard without relaxation; no physical criterion change",upper_quadrature='7point affine prescribed CADface wrench reference, not solved uppercontact',E_ASSUMED_MPa=E,nu_ASSUMED=nu,mu_ASSUMED=.3,rho_ASSUMED_kg_m3=7900,physical_fixed_DOF=0,accepted_load_fraction=lastfrac,current_attempt_fraction=forcefraction,accepted_steps=saved,fixedpoint_history=hist,static_energy_Nmm=energy,volume_RMS_mm=float(np.sqrt(np.sum(lump*np.sum(u3*u3,axis=1))/lump.sum())),maximum_displacement_mm=float(np.linalg.norm(u3,axis=1).max()),minimum_whole_triangle_gap_mm=float(u3[floornodes,2].min()),total_force_moment_residual_N_Nmm=W.tolist(),source_ports=inputjournal,mesh_volume_mm3=float(vol.sum()),CAD_volume_mm3=V,peak_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,elapsed_s=time.monotonic()-started,newly_qualified_system_gate_ids=[],accepted83body_physical_equilibria=0,whole_system_release=False,limitations=['Frozen common physical Voronoi quadrature is identical on both declared meshes; constructed from their geometric vertex union, not universal futuremesh independence. Integrated forces use Btranspose; whole linear floor triangle minimum is exactly a vertex minimum. Quadrature contact alone cannot certify this inequality.','All failed fields preserved. A wholetriangle penetration rejects physical contact even when quadrature law converges.','Material/floor friction assumptions, affine upper references, no strength/time/globalenergy/full83body certification. Four quasistatic subdivisions are notdt. All22UNQUALIFIED NoStage3.']))
print(json.dumps(dict(checks={k:bool(v) for k,v in checks.items()},accepted_fraction=lastfrac)));raise SystemExit(0 if all(checks.values()) else 2)
