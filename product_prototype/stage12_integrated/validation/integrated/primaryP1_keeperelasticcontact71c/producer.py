"""Actual Root keeper full3D elastic / two spinning rigid sockets conditional contact.
No physical fixed DOF. Host lateral/tilt socket BC are explicit references;
keeper gravity, pin/nut/cage compliance and system equilibrium remain UNSOLVED.
"""
import sys,json,time,shutil,resource
import numpy as np
from scipy import sparse
import osqp
from skfem import MeshTet,Basis,ElementVector,ElementTetP1,asm
from skfem.models.elasticity import linear_elasticity,lame_parameters
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
import gmsh
def meshpart(path,h,curv):
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);gmsh.model.add('actual_keeper_coarse_contact_not_mesh_certificate');v=gmsh.model.occ.importShapes(str(path));gmsh.model.occ.synchronize();volume=sum(gmsh.model.occ.getMass(d,t) for d,t in v)
 for name,value in [('Mesh.MeshSizeMin',h),('Mesh.MeshSizeMax',h),('Mesh.MeshSizeFromPoints',0),('Mesh.MeshSizeFromCurvature',0),('Mesh.MeshSizeExtendFromBoundary',0)]:gmsh.option.setNumber(name,value)
 gmsh.model.mesh.generate(3);nt,p,_=gmsh.model.mesh.getNodes();order=np.argsort(nt);nt=np.array(nt)[order];p=np.array(p).reshape(-1,3)[order];ty,_,el=gmsh.model.mesh.getElements(3);t=np.concatenate([np.searchsorted(nt,np.array(a).reshape(-1,4)) for k,a in zip(ty,el) if k==4]);ty,_,el=gmsh.model.mesh.getElements(2);tri=np.concatenate([np.searchsorted(nt,np.array(a).reshape(-1,3)) for k,a in zip(ty,el) if k==2]);gmsh.finalize();ids=np.unique(t);return p[ids],np.searchsorted(ids,t),np.searchsorted(ids,tri),volume
from primary_keeper_coupled71 import faces,rot
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane

def main():
 start=time.monotonic();h=float(sys.argv[1]);out=ROOT/'validation/integrated'/sys.argv[2];out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_ground65a/summary.json';cad=json.loads(cp.read_text());refs=cad['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*refs.values(),cad['assembly'],cad['BOM']]);step=REPO/refs['ROOT_SOCKET_KEEPER']['path'];src=ROOT/'validation/integrated/primaryP1_keepercoupled71/summary.json';d=json.loads(src.read_text());r=d['rows'][0];assert r['signs']==[1,1] and r['full18row_feasible'];T=np.array(r['conditional_bolt_torque_Nmm']);angles=np.array(r['solution'][3:]);settings=[q for q in json.loads((REPO/cad['settings']['path']).read_text())['settings'] if q['keeper']=='ROOT_SOCKET_KEEPER'];p,t,tri,Vcad=meshpart(step,h,12);N=3*len(p);E=200000.;nu=.3;la,mu=lame_parameters(E,nu);m=MeshTet(p.T,t.T);K=sparse.csr_matrix((N,N))
 print(json.dumps(dict(phase='mesh',nodes=len(p),tetra=len(t))),flush=True)
 for first in range(0,len(t),8000):
  assert not(ROOT/'runtime/STOP').exists();K+=asm(linear_elasticity(la,mu),Basis(m,ElementVector(ElementTetP1()),intorder=2,elements=np.arange(first,min(first+8000,len(t)))))
 nodeids=[];which=[];normal=[];origins=[];centers=[];wallids=[]
 for i,q in enumerate(settings):
  c=np.array([q['x'],q['y'],0.]);centers.append(c);walls=[]
  for f in faces(read(REPO/refs[q['bolt']]['path'])):
   a=BRepAdaptor_Surface(f)
   if a.GetType()!=GeomAbs_Plane:continue
   pl=a.Plane();o=pl.Location();axis=pl.Axis().Direction();o=np.array([o.X(),o.Y(),o.Z()]);n=np.array([axis.X(),axis.Y(),axis.Z()]);bb=bounds(f)
   if abs(n[2])<1e-7 and np.linalg.norm((np.array(bb[:3])+bb[3:])[:2]/2-c[:2])<2:
    if n@(c-o)<0:n=-n
    walls.append((o,n))
  assert len(walls)==6
  # All mesh boundary nodes on actual plug within finite socket axial overlap.
  ids=np.intersect1d(np.unique(tri),np.flatnonzero((p[:,2]>=-1.25-1e-7)&(p[:,2]<=-0.01)&(np.linalg.norm(p[:,:2]-c[:2],axis=1)<1.6)))
  assert len(ids)>12
  for wi,(o,n) in enumerate(walls):
   for node in ids:nodeids.append(int(node));which.append(i);normal.append(n);origins.append(o);wallids.append(wi)
 ids=np.array(nodeids);which=np.array(which);n0=np.array(normal);o0=np.array(origins);centers=np.array(centers);M=len(ids);L=.001;OBJ=.0001
 np.savez_compressed(out/'original_mesh.npz',points_mm=p,tetra=t,boundary_triangles=tri);print(json.dumps(dict(phase='assembled',nodes=len(p),tetra=len(t),contact_rows=M,nnz=K.nnz)),flush=True)
 P=sparse.block_diag([K*(L*L/OBJ),sparse.csr_matrix((2,2))],format='csc');q=np.r_[np.zeros(N),-T*L/OBJ];x=np.zeros(N+2);journal=[];final=None
 def geom(y):
  u=y[:N].reshape(-1,3)*L;beta=y[N:]*L;n=np.empty_like(n0);o=np.empty_like(o0)
  for i in range(2):
   mask=which==i;R=rot(angles[i]+beta[i]);n[mask]=n0[mask]@R.T;o[mask]=(o0[mask]-centers[i])@R.T+centers[i];o[mask,2]+=.5*(angles[i]+beta[i])/(2*np.pi)
  pp=p[ids]+u[ids];gap=np.sum(n*(pp-o),axis=1);v=pp-centers[which];cross=np.c_[-v[:,1],v[:,0],np.zeros(M)];spin=-np.sum(n*cross,axis=1)
  rr=np.repeat(np.arange(M),3);cc=(ids[:,None]*3+np.arange(3)).ravel();A=sparse.coo_matrix((n.ravel(),(rr,cc)),shape=(M,N+2)).tocsr();A+=sparse.coo_matrix((spin,(np.arange(M),N+which)),shape=(M,N+2)).tocsr();return gap,n,pp,A
 # Continue an explicitly hashed numerical initial guess, never an equilibrium claim.
 initial=ROOT/'validation/integrated/primaryP1_keeperelasticcontact71b/iterate_00.npz';meshsrc=initial.parent/'original_mesh.npz';old=np.load(meshsrc);assert np.array_equal(old['points_mm'],p) and np.array_equal(old['tetra'],t) and np.array_equal(old['boundary_triangles'],tri)
 guess=np.load(initial);x=guess['scaled_unknown'];active=set(np.flatnonzero(guess['normal_force_N']>1e-7).tolist());assert len(active)>0;dump(out/'initial_guess.json',dict(field=ref(initial),mesh=ref(meshsrc),all_mesh_arrays_exact=True,initial_is_not_accepted_equilibrium=True))
 from scipy.sparse.linalg import splu
 for iteration in range(60):
  assert not(ROOT/'runtime/STOP').exists();gap,n,pp,A=geom(x);lower=-gap/L+A@x;act=np.array(sorted(active),dtype=int);C=A[act].tocsc();gauge=sparse.coo_matrix(([1.],([0],[2])),shape=(1,N+2)).tocsc();C=sparse.vstack([C,gauge],format='csc');rhs=np.r_[lower[act],0.];system=sparse.bmat([[P,-C.T],[C,None]],format='csc');factor=splu(system,permc_spec='COLAMD');answer=factor.solve(np.r_[-q,rhs]);xnew=answer[:N+2];dual=answer[N+2:];del factor,system;gg,nn,pp,AA=geom(xnew);lam=np.zeros(M);lam[act]=dual[:-1]*OBJ/L;u=xnew[:N]*L;Bforce=AA.T@lam;res=K@u-Bforce[:N];torqueres=T+Bforce[N:];comp=lam*gg;negative=act[lam[act]<-1e-9];violated=np.flatnonzero(gg<-1e-9);entry=dict(iteration=iteration,status='SPARSE_ACTIVE_KKT_ORIGINAL_DOF_CHECK',active_rows=len(act),minimum_gap_mm=float(gg.min()),minimum_lambda_N=float(lam.min()),original_force_residual_N=float(abs(res).max()),bolt_torque_residual_Nmm=float(abs(torqueres).max()),complementarity_Nmm=float(abs(comp).max()),gauge_reaction_N=float(dual[-1]*OBJ/L),delta_scaled=float(abs(xnew-x).max()),energy_Nmm=float(u@K@u/2),negative_active_rows=len(negative),violating_rows=len(violated));journal.append(entry);print(json.dumps(entry),flush=True);np.savez_compressed(out/f'iterate_{iteration:02}.npz',scaled_unknown=xnew,normal_force_N=lam,gap_mm=gg,active_rows=act);x=xnew;final=(gg,nn,pp,AA,lam,res,torqueres)
  if len(negative):active.remove(int(negative[np.argmin(lam[negative])]))
  elif len(violated):active.update(int(j) for j in violated[np.argsort(gg[violated])[:12]])
  elif abs(res).max()<1e-8 and abs(torqueres).max()<1e-8 and abs(comp).max()<1e-8:break
 gg,nn,pp,A,lam,res,torqueres=final;u=x[:N].reshape(-1,3)*L;load=np.zeros_like(u)
 for j in range(3):np.add.at(load[:,j],ids,lam*nn[:,j])
 boltforces=np.zeros((2,3));boltmoments=np.zeros((2,3))
 for i in range(2):
  mask=which==i;ff=-lam[mask,None]*nn[mask];boltforces[i]=ff.sum(0);boltmoments[i]=np.cross(pp[mask]-centers[i],ff).sum(0)
 xyz=p[t];det=np.linalg.det(np.transpose(xyz[:,1:]-xyz[:,0,None],(0,2,1)));vol=abs(det)/6;iv=np.linalg.inv(xyz[:,1:]-xyz[:,0,None]);grad=np.concatenate([-iv.sum(2)[:,None,:],iv.transpose(0,2,1)],axis=1);G=np.einsum('tai,taj->tij',u[t],grad);eps=(G+G.transpose(0,2,1))/2;sig=2*mu*eps+la*np.trace(eps,axis1=1,axis2=2)[:,None,None]*np.eye(3);ee=float(np.sum(.5*np.einsum('tij,tij->t',eps,sig)*vol));energy=float(u.ravel()@K@u.ravel()/2);ratio=np.linalg.det(np.transpose((p+u)[t[:,1:]]-(p+u)[t[:,0,None]],(0,2,1)))/det;force=load.sum(0);moment=np.cross(p,load).sum(0);finiteoverlap=bool(np.all((pp[:,2]>-1.3+.5*(angles[which]+x[N+which]*L)/(2*np.pi))&(pp[:,2]<.5*(angles[which]+x[N+which]*L)/(2*np.pi))))
 checks=dict(actual83hashes=True,gauge_reaction_zero=abs(journal[-1]['gauge_reaction_N'])<1e-8,all_original_elastic_DOF_residual=abs(res).max()<1e-8,free_bolt_spin_torque=abs(torqueres).max()<1e-8,nonnegative_normals=lam.min()>=-1e-9,all_contact_node_gaps=gg.min()>=-1e-9,complementarity=abs(lam*gg).max()<1e-8,keeper_force=float(abs(force).max())<1e-8,keeper_moment=float(abs(moment).max())<1e-8,independent_energy=abs(ee/energy-1)<1e-8,positive_deformed_elements=ratio.min()>0,finite_original_socket_axial_overlap=finiteoverlap)
 np.savez_compressed(out/'field.npz',points_mm=p,tetra=t,boundary_triangles=tri,displacement_mm=u,load_N=load,residual_N=res,contact_node=ids,bolt_index=which,wall_index=np.array(wallids),normal=nn,normal_force_N=lam,gap_mm=gg,bolt_spin_increment_rad=x[N:]*L)
 dump(out/'summary.json',dict(status='ACTUAL_P1_KEEPER_ELASTIC_FREE_SPIN_CONDITIONAL_CONTACT_REFERENCE' if all(checks.values()) else 'ACTUAL_P1_KEEPER_ELASTIC_CONTACT_FAIL',candidate=ref(cp),STEP=ref(step),producer=ref(out/'producer.py'),source=ref(src),field=ref(out/'field.npz'),checks={k:bool(v) for k,v in checks.items()},h_mm=h,nodes=len(p),tetra=len(t),contact_rows=M,positive_contact_rows=int(np.sum(lam>1e-10)),journal=journal,E_ASSUMED_MPa=E,nu_ASSUMED=nu,material_minimum_MPa=None,static_energy_Nmm=energy,independent_element_energy_Nmm=ee,volume_RMS_displacement_mm=float(np.sqrt(np.sum(vol[:,None]*(u[t].sum(1)**2+np.sum(u[t]**2,axis=1)))/(20*vol.sum()))),CAD_volume_mm3=Vcad,mesh_volume_mm3=float(vol.sum()),bolt_reference_spin_rad=angles.tolist(),bolt_spin_increment_rad=(x[N:]*L).tolist(),conditional_bolt_torque_Nmm=T.tolist(),explicit_host_force_on_each_bolt_N=(-boltforces).tolist(),explicit_host_moment_on_each_bolt_Nmm=(-(boltmoments+np.c_[np.zeros((2,2)),T])).tolist(),keeper_load_force_N=force.tolist(),keeper_load_moment_Nmm=moment.tolist(),physical_fixed_keeper_DOF=0,free_bolt_spin_DOF=2,accepted83body_physical_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,peak_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,limitations=['Actual entire3D keeper elasticity with alloriginalDOFs and two free bolt spins. Rigid socket lateral/tiltBC exposed as unknown hostreaction, not constitutivehost/nut/thread/cage equilibrium.','Normal constraints only at finite plug mesh boundarynodes within socket axialoverlap. Linear tetra boundary approximation and wholeface/curvedCAD/nonlinear largegeometry accuracy NOT certified.','No pin/keeper/host gravity, friction, preload or materialminima in pure torque contrast. No invented pin reaction or bottomface returntorque.','Full3D contact quadrature/mesh1percent/time.1percent/globalenergy and all22systemgates unqualified. Rigid clearancemodes and sourceconditionaltorque do not certify actual100g operation.']))
 print(json.dumps(dict(checks={k:bool(v) for k,v in checks.items()},energy=energy,host_force=(-boltforces).tolist())));return 0 if all(checks.values()) else 2
if __name__=='__main__':sys.exit(main())
