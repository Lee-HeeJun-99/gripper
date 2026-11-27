"""Actual P1 Ground/Base conforming-interface, separate-DOF elastic contact contrast.
Reuses existing Gmsh/skfem tetra elasticity. No nominal-major-cylinder thread tie.
Units N,mm. Conditional averaged bolt core connector and external grip port.
"""
import argparse,json,shutil,time
from pathlib import Path
import numpy as np
import gmsh,skfem,scipy,osqp
from scipy import sparse
from skfem import MeshTet,Basis,ElementTetP1,ElementVector,asm
from skfem.models.elasticity import linear_elasticity,lame_parameters
from baseline_registry import ROOT,REPO,ref,sha,dump

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--tag',required=True);ap.add_argument('--h',type=float,default=5);ap.add_argument('--preload',type=float,default=0);ap.add_argument('--gap',type=float,default=0);a=ap.parse_args()
 out=ROOT/'validation/integrated'/a.tag;out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists();start=time.monotonic()
 src=ROOT/'cad/exports/primaryP1_fixture13/summary.json';cad=json.loads(src.read_text());masssrc=ROOT/'validation/integrated/primaryP1_full_mass1/summary.json';mass=json.loads(masssrc.read_text());refs=cad['part_references'];names=['GROUND_PLATE','TEST_BASE','OPEN_FRAME']+[f'FIXTURE_{kind}_{i}' for kind in ('BOLT','NUT') for i in range(4)]
 assert all(sha(REPO/refs[n]['path'])==refs[n]['SHA256'] for n in names)
 # Conservative minor-core axial area, not nominal major-cylinder stiffness.
 # Unthreaded grip13mm, threaded grip13mm; explicit half-nut4.4/2mm added
 # compliance sensitivity. This does not prove flank/core engagement capacity.
 dcore=5-1.226869*.8;Acore=np.pi*dcore*dcore/4;Ashank=np.pi*25/4;kbolt=200000/(13/Ashank+(13+2.2)/Acore)
 dump(out/'inputs.json',dict(candidate=ref(src),mass=ref(masssrc),producer=ref(out/'producer.py'),dependencies=[ref(ROOT/'scripts/primary_frame_reference.py')],parts={n:refs[n] for n in names},h_mm=a.h,preload_each_N=a.preload,key_lateral_gap_mm=a.gap,bolt_connector=dict(core_diameter_mm=dcore,core_area_mm2=Acore,k_N_mm=kbolt,formula='200000/(13/Amajor+(13+2.2)/Aminor). ISO metric basic profile geometry; half-minimum-nut length is explicit compliance sensitivity,not actual flank solution.',class_capacity=None),criteria=dict(force_N=1e-8,moment_Nm=1e-10,relative_residual=1e-8,energy_relative=1e-8,mesh_fraction=.01)))
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);gmsh.model.add('actual_P1_joint')
 objects=[];owners=[]
 for n in names:
  v=gmsh.model.occ.importShapes(str(REPO/refs[n]['path']));assert len(v)==1;objects+=v;owners.append(n)
 fragments,mapping=gmsh.model.occ.fragment(objects,[]);gmsh.model.occ.synchronize();vols={n:[t for dim,t in mapping[i] if dim==3] for i,n in enumerate(owners)}
 def surfaces(vs):return set(abs(t) for dim,t in gmsh.model.getBoundary([(3,t) for t in vs],combined=True,oriented=False) if dim==2)
 boundaries={n:surfaces(v) for n,v in vols.items()};gb=boundaries['GROUND_PLATE']&boundaries['TEST_BASE'];loadfaces=boundaries['GROUND_PLATE']&boundaries['OPEN_FRAME'];heads=[boundaries['GROUND_PLATE']&boundaries[f'FIXTURE_BOLT_{i}'] for i in range(4)];nuts=[boundaries['TEST_BASE']&boundaries[f'FIXTURE_NUT_{i}'] for i in range(4)]
 assert gb and loadfaces and all(heads) and all(nuts),(gb,loadfaces,heads,nuts)
 contact={}
 for t in gb:
  bb=np.array(gmsh.model.getBoundingBox(2,t));span=bb[3:]-bb[:3];axis=int(np.argmin(span));assert span[axis]<1e-5;value=(bb[axis]+bb[axis+3])/2
  if axis==2:assert abs(value-46)<1e-5;normal=np.array([0,0,-1.]);label='seat'
  else:
   # Ground key inside Base pocket; G=(uGround-uBase).n>=-gap
   normal=np.zeros(3);normal[axis]=1 if (axis==0 and value<-44) or (axis==1 and value<0) else -1;label='key'
  contact[t]=(normal,label)
 grip=[t for t in boundaries['TEST_BASE'] if abs(gmsh.model.getBoundingBox(2,t)[2]-66)<1e-5 and abs(gmsh.model.getBoundingBox(2,t)[5]-66)<1e-5 and not any(t in ss for ss in nuts)]
 assert grip
 keep=set(vols['GROUND_PLATE']+vols['TEST_BASE']);extras=[v for v in fragments if v[0]==3 and v[1] not in keep];gmsh.model.occ.remove(extras,recursive=True);gmsh.model.occ.synchronize()
 gmsh.option.setNumber('Mesh.MeshSizeMax',a.h);gmsh.option.setNumber('Mesh.MeshSizeMin',a.h*.4);gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',16);gmsh.option.setNumber('Mesh.Algorithm3D',1);gmsh.model.mesh.generate(3)
 nt,xyz,_=gmsh.model.mesh.getNodes();order=np.argsort(nt);nt=np.asarray(nt)[order];xyz=np.asarray(xyz).reshape(-1,3)[order]
 def tri(ss):
  rows=[]
  for t in ss:
   types,_,es=gmsh.model.mesh.getElements(2,t);rows.extend(np.searchsorted(nt,np.asarray(e).reshape(-1,3)) for typ,e in zip(types,es) if typ==2)
  return np.concatenate(rows)
 tris={t:tri([t]) for t in gb};loadtri=tri(loadfaces);headtri=[tri(ss) for ss in heads];nuttri=[tri(ss) for ss in nuts];griptri=tri(grip)
 data=[];offset=0;Ks=[];meshinfo=[]
 for n in ('GROUND_PLATE','TEST_BASE'):
  ts=[]
  for v in vols[n]:
   types,_,es=gmsh.model.mesh.getElements(3,v);ts.extend(np.searchsorted(nt,np.asarray(e).reshape(-1,4)) for typ,e in zip(types,es) if typ==4)
  t=np.concatenate(ts);used=np.unique(t);p=xyz[used];t=np.searchsorted(used,t);m=MeshTet((p*.001).T,t.T);el=ElementVector(ElementTetP1());basis=Basis(m,el,intorder=2);E=200000 if n=='GROUND_PLATE' else 68900;nu=.3 if n=='GROUND_PLATE' else .33;lam,mu=lame_parameters(E,nu)
  # Assemble in mm coordinates to use MPa=N/mm2.
  m=MeshTet(p.T,t.T);basis=Basis(m,el,intorder=2);K=sparse.csr_matrix((basis.N,basis.N))
  for first in range(0,len(t),8000):K+=asm(linear_elasticity(lam,mu),Basis(m,el,intorder=2,elements=np.arange(first,min(first+8000,len(t)))))
  assert np.array_equal(basis.nodal_dofs,np.arange(basis.N).reshape(-1,3).T)
  det=np.linalg.det(np.transpose(p[t[:,1:]]-p[t[:,0,None]],(0,2,1)));vv=abs(det)/6;rho=7900 if n=='GROUND_PLATE' else 2700;f=np.zeros(basis.N)
  for j in range(4):np.add.at(f,np.array([3*t[:,j]+2]),-vv*rho*1e-9*9.80665/4)
  lump=np.zeros(len(p))
  for j in range(4):np.add.at(lump,t[:,j],vv/4)
  info=dict(name=n,used=used,p=p,t=t,K=K,f=f,lump=lump,offset=offset,ndof=basis.N,volume_mm3=float(vv.sum()),E=E,nu=nu);data.append(info);Ks.append(K);offset+=basis.N
  meshinfo.append(dict(part=n,nodes=int(len(p)),elements=int(len(t)),volume_mm3=float(vv.sum()),CAD_volume_mm3=sum(gmsh.model.occ.getMass(3,v) for v in vols[n])))
 gmsh.finalize();N=offset;K=sparse.block_diag(Ks,format='csc');f=np.concatenate([d['f'] for d in data]);G,B=data
 def patch_vector(d,tr,axis):
  tr=np.searchsorted(d['used'],tr);p=d['p'];area=np.linalg.norm(np.cross(p[tr[:,1]]-p[tr[:,0]],p[tr[:,2]]-p[tr[:,0]]),axis=1)/2;v=np.zeros(N)
  for j in range(3):np.add.at(v,d['offset']+3*tr[:,j]+axis,area/3)
  return v,float(area.sum())
 def distribute(d,tr,W):
  # Exact linear nodal traction space with six resultant constraints;
  # minimum area-weighted field. Explicit port; no fixed surface nodes.
  v,_=patch_vector(d,tr,0);nodes=np.flatnonzero(v);nodeids=(nodes-d['offset'])//3;wt=v[nodes];p=d['p'][nodeids]*.001;H=np.zeros((6,3*len(nodes)))
  for j,(r,w) in enumerate(zip(p,wt)):
   H[:3,3*j:3*j+3]=np.eye(3)*w;H[3:,3*j:3*j+3]=np.array([[0,-r[2],r[1]],[r[2],0,-r[0]],[-r[1],r[0],0]])*w
  inv=np.repeat(1/wt,3);coef=inv*(H.T@np.linalg.solve((H*inv)@H.T,W));forces=(np.repeat(wt,3)*coef).reshape(-1,3)
  for j,node in enumerate(nodeids):f[d['offset']+3*node:d['offset']+3*node+3]+=forces[j]
  return dict(resultant=(H@coef).tolist(),max_traction_MPa=float(np.max(np.linalg.norm(coef.reshape(-1,3),axis=1))),area_mm2=float(wt.sum()),nodes=len(nodes))
 # All non-Ground/nonBase masses transported in frozen-state upstream port.
 own={r['part_ID']:np.array(r['gravity_wrench_N_Nm']) for r in mass['parts']};up=np.array(mass['nonBase_gravity_wrench_N_Nm'])-own['GROUND_PLATE'];port=np.array(mass['operating_external_port_N_Nm'])+up
 loadport=distribute(G,loadtri,port)
 # Use mesh-integrated own gravity for exact free-body force/moment closure.
 def resultants(fv):
  W=np.zeros(6)
  for d in data:
   forces=fv[d['offset']:d['offset']+d['ndof']].reshape(-1,3);W[:3]+=forces.sum(axis=0);W[3:]+=np.cross(d['p']*.001,forces).sum(axis=0)
  return W
 external_before=resultants(f);gripport=distribute(B,griptri,-external_before)
 # Contact rows at coincident conforming nodes; separate Ground/Base DOFs.
 rows=[];labels=[];gaps=[]
 for face,(normal,label) in contact.items():
  for node in np.unique(tris[face]):
   ig=np.searchsorted(G['used'],node);ib=np.searchsorted(B['used'],node);assert G['used'][ig]==node and B['used'][ib]==node
   row=sparse.lil_matrix((1,N))
   for j in range(3):row[0,G['offset']+3*ig+j]=normal[j];row[0,B['offset']+3*ib+j]=-normal[j]
   rows.append(row.tocsr());labels.append(label);gaps.append(a.gap if label=='key' else 0)
 C=sparse.vstack(rows,format='csr');C,idx=np.unique(C.toarray(),axis=0,return_index=True) if N<0 else (C,np.arange(len(rows)))
 # Four averaged real head/nut bearing footprints; axial spring only.
 bolts=[];areas=[]
 for i in range(4):
  vg,ag=patch_vector(G,headtri[i],2);vb,ab=patch_vector(B,nuttri[i],2);bolts.append(vb/ab-vg/ag);areas.append([ag,ab])
 D=sparse.csr_matrix(np.array(bolts));gauge=[]
 # Six volume-weighted rigid-motion gauges on Base; no deformation clamp.
 q=B['p']-np.average(B['p'],weights=B['lump'],axis=0);weight=B['lump']/B['lump'].sum()
 for j in range(3):
  v=np.zeros(N);v[B['offset']+3*np.arange(len(q))+j]=weight;gauge.append(v)
 for axis in np.eye(3):
  v=np.zeros(N);v[B['offset']:] = (np.cross(axis,q)*weight[:,None]).ravel()/100;gauge.append(v)
 Q=sparse.csr_matrix(gauge);ncontact=C.shape[0]
 # x=u/.001mm; auxiliary t=bolt elongation/.001mm; objective/.001Nmm.
 scale=.001;P=sparse.block_diag([K*scale,sparse.eye(4)*kbolt*scale],format='csc');obj=np.r_[-f,np.zeros(4)];Z=sparse.csr_matrix((ncontact,4));constraints=sparse.vstack([sparse.hstack([C,Z]),sparse.hstack([Q,sparse.csr_matrix((6,4))]),sparse.hstack([-D,sparse.eye(4)]),sparse.hstack([sparse.csr_matrix((4,N)),sparse.eye(4)])],format='csc');lower=np.r_[-np.array(gaps)/scale,np.zeros(6),np.ones(4)*a.preload/kbolt/scale,np.zeros(4)];upper=np.r_[np.full(ncontact,np.inf),np.zeros(6),np.full(8,np.inf)]
 solver=osqp.OSQP();solver.setup(P=sparse.triu(P,format='csc'),q=obj,A=constraints,l=lower,u=upper,eps_abs=1e-10,eps_rel=1e-10,max_iter=100000,polishing=True,verbose=False,check_termination=25);r=solver.solve();x=r.x;y=r.y;u=x[:N]*scale;forces=kbolt*x[N:]*scale;cu=C@u+np.array(gaps);res=K@u-f+C.T@y[:ncontact]+Q.T@y[ncontact:ncontact+6]-D.T@y[ncontact+6:ncontact+10];force_balance=resultants(res);energy=.5*float(u@K@u);spring=.5*float(np.sum(forces**2/kbolt));stored=energy+spring;work=float(f@u);initial_work=float(np.sum(a.preload/kbolt*forces));gapwork=float(np.dot(-y[:ncontact],np.array(gaps)));identity=2*stored-work-initial_work+gapwork
 stresses=[]
 for d in data:
  p,t=d['p'],d['t'];uu=u[d['offset']:d['offset']+d['ndof']].reshape(-1,3);dx=p[t[:,1:]]-p[t[:,0,None]];du=uu[t[:,1:]]-uu[t[:,0,None]];grad=np.linalg.solve(dx,du).transpose(0,2,1);eps=(grad+grad.transpose(0,2,1))/2;lam,mu=lame_parameters(d['E'],d['nu']);stress=2*mu*eps+lam*np.trace(eps,axis1=1,axis2=2)[:,None,None]*np.eye(3);dev=stress-np.trace(stress,axis1=1,axis2=2)[:,None,None]*np.eye(3)/3;stresses.append(dict(part=d['name'],peak_unsmoothed_vm_MPa=float(np.sqrt(1.5*np.sum(dev*dev,axis=(1,2))).max()),max_motion_mm=float(np.linalg.norm(uu,axis=1).max())))
 checks=dict(solver_solved=r.info.status=='solved',normal_gaps=bool(cu.min()>-1e-8),compression_only=bool(y[:ncontact].max()<1e-8),stationarity=bool(np.linalg.norm(res)/max(np.linalg.norm(f),1)<1e-8),global_force=bool(np.linalg.norm(force_balance[:3])<1e-8),global_moment=bool(np.linalg.norm(force_balance[3:])<1e-10),gauge_force_negligible=bool(np.linalg.norm(y[ncontact:ncontact+6])<1e-8),static_energy=bool(abs(identity)/max(abs(stored),1e-20)<1e-8),positive_bolt_force=bool(forces.min()>=-1e-10),mesh_volume=all(abs(m['volume_mm3']/m['CAD_volume_mm3']-1)<.01 for m in meshinfo))
 np.savez_compressed(out/'field.npz',u_mm=u,bolt_force_N=forces,contact_gaps_mm=cu,contact_dual_N=-y[:ncontact],applied_force_N=f,stationarity_N=res,gauge_dual=y[ncontact:ncontact+6],G_points_mm=G['p'],G_tetra=G['t'],B_points_mm=B['p'],B_tetra=B['t'],G_ndof=G['ndof'],contact_C_data=C.data,contact_C_indices=C.indices,contact_C_indptr=C.indptr,contact_C_shape=C.shape,bolt_D=D.toarray(),initial_gaps_mm=np.array(gaps))
 result=dict(status='ACTUAL_P1_CONDITIONAL_COMPLIANT_JOINT_PASS' if all(checks.values()) else 'ACTUAL_P1_CONDITIONAL_COMPLIANT_JOINT_FAIL',candidate=ref(src),producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),field=ref(out/'field.npz'),checks=checks,h_mm=a.h,preload_each_N=a.preload,key_lateral_gap_mm=a.gap,meshes=meshinfo,DOF=int(N),solver=dict(status=r.info.status,iterations=r.info.iter,primal_residual=r.info.prim_res,dual_residual=r.info.dual_res),bolt_force_N=forces.tolist(),bolt_k_N_mm=kbolt,bearing_areas_head_nut_mm2=areas,contact_nodes=ncontact,active_contact_nodes=int(np.sum(-y[:ncontact]>1e-8)),min_gap_mm=float(cu.min()),max_key_gap_mm=float(np.max(cu[np.array(labels)=='key'])),relative_stationarity=float(np.linalg.norm(res)/max(np.linalg.norm(f),1)),global_residual_N_Nm=force_balance.tolist(),gauge_dual_N=y[ncontact:ncontact+6].tolist(),elastic_energy_Nmm=energy,bolt_energy_Nmm=spring,static_energy_identity_Nmm=identity,static_energy_relative=abs(identity)/max(abs(stored),1e-20),stresses=stresses,upstream_port=loadport,external_grip_port=gripport,elapsed_s=time.monotonic()-start,software=dict(gmsh=gmsh.__version__,skfem=skfem.__version__,scipy=scipy.__version__,osqp=osqp.__version__),limitations=['Linear small-displacement actual full Ground/Base only; upstream module gravity transported frozen,not re-solved Finger','Uniform mean axial head/nut connector is a compliance sensitivity,not local solved bearing/thread flank/core/engagement or capacity','Frictionless linearized key/seat contacts. Gap offset is a contact-law contrast,not new machined pocket CAD; no large-slip/finite CCD','Finite Base top distributed external traction is explicit mathematical grip port,not source-qualified physical laboratory anchor; six volume gauges must carry negligible load','304/6061design intent with typical elastic constants,nominal conditional full mass; no source minima/physical mass/preload guarantee','No full assembly strength,1%mesh convergence,time/global-energy,protector or Stage3 qualification'],newly_qualified_system_gate_ids=[],whole_system_release=False)
 dump(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','checks','DOF','solver','bolt_force_N','stresses','static_energy_relative','gauge_dual_N')}));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
