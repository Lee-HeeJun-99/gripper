"""Same P1 finite Root/Frame/Cap elasticity and conditional rigid motor contact.
N,mm. Frozen upstream gravity ports; finite external Frame/Ground traction port.
No hidden shared M5 fixation, friction, case stiffness, or strength assertion.
"""
import argparse,json,shutil,time
import numpy as np
import gmsh,skfem,scipy,osqp
from scipy import sparse
from skfem import MeshTet,Basis,ElementTetP1,ElementVector,asm
from skfem.models.elasticity import linear_elasticity,lame_parameters
from baseline_registry import ROOT,REPO,ref,sha,dump

def skew(r):
 x,y,z=r;return np.array([[0,-z,y],[z,0,-x],[-y,x,0]])

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--tag',required=True);ap.add_argument('--h',type=float,default=5);ap.add_argument('--gap',type=float,default=0);ap.add_argument('--preload',type=float,default=0);a=ap.parse_args()
 out=ROOT/'validation/integrated'/a.tag;out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');start=time.monotonic();assert not(ROOT/'runtime/STOP').exists()
 src=ROOT/'cad/exports/primaryP1_interfaces18/summary.json';cad=json.loads(src.read_text());refs=cad['part_references'];load=ROOT/'validation/transmission/primaryP1_gravity_cat_demand_ports2/summary.json';loads=json.loads(load.read_text())['rows'][0]
 elastic=['OPEN_FRAME','F0_ROOT_BACK','MOTOR_CAP'];motor='F0_MICRO_MOTOR';body=elastic+[motor]
 rb=[f'F0_RF{i}_{kind}' for i in range(2) for kind in ('BOLT','NUT')];mb=[f'MOTOR_CAP_{kind}_{x}_{y}' for x in (-7,7) for y in (-29.5,-13.5) for kind in ('BOLT','NUT')];hardware=rb+mb;names=body+['GROUND_PLATE','F0_ROOT_FRONT']+hardware
 assert all(sha(REPO/refs[n]['path'])==refs[n]['SHA256'] for n in names)
 # ISO basic profile minor-core geometric compliance sensitivity; no flank capacity.
 dc=3-1.226869*.5;Ac=np.pi*dc**2/4;kroot=200000*Ac/(9+2.4/2);kcap=200000*Ac/(18+2.4/2)
 dump(out/'inputs.json',dict(candidate=ref(src),loads=ref(load),producer=ref(out/'producer.py'),parts={n:refs[n] for n in names},dependencies=[ref(ROOT/'scripts/primary_joint_compliance_v2.py'),ref(ROOT/'scripts/primary_motor_bearing_wrenches.py')],h_mm=a.h,lateral_contact_gap_mm=a.gap,preload_each_N=a.preload,connectors=dict(dcore_mm=dc,area_mm2=Ac,root_k_N_mm=kroot,cap_k_N_mm=kcap,E_MPa=200000,root_compliance_length_mm=10.2,cap_compliance_length_mm=19.2,interpretation='Conditional minor-core axial compliance plus half nominal nut thickness; no local thread/bearing/engagement or capacity certificate'),criteria=dict(force_N=1e-8,moment_Nm=1e-10,residual=1e-8,energy_relative=1e-8,complementarity_Nmm=1e-8,mesh_fraction=.01),boundary='Balanced finite traction on actual Frame/Ground z40. This is an explicit mathematical port,NOT an actual friction/shank/key or physical anchor. Six Frame gauges carry negligible wrench.'))
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);gmsh.model.add('P1_upper_separate_DOF')
 objs=[]
 for n in names:
  v=gmsh.model.occ.importShapes(str(REPO/refs[n]['path']));assert len(v)==1;objs+=v
 frag,mapping=gmsh.model.occ.fragment(objs,[]);gmsh.model.occ.synchronize();vols={n:[t for d,t in mapping[i] if d==3] for i,n in enumerate(names)}
 def surfaces(vs):return set(abs(t) for d,t in gmsh.model.getBoundary([(3,t) for t in vs],combined=True,oriented=False) if d==2)
 ss={n:surfaces(v) for n,v in vols.items()}
 def plane(t,axis,val):
  b=gmsh.model.getBoundingBox(2,t);return abs(b[axis]-val)<1e-5 and abs(b[axis+3]-val)<1e-5
 def shared(n,m,axis,val):
  s={t for t in ss[n]&ss[m] if plane(t,axis,val)};assert s,(n,m,axis,val);return s
 contact=[]
 for n,m,ax,val,normal,label in [('F0_ROOT_BACK','OPEN_FRAME',2,-7,[0,0,1],'root_seat'),('F0_ROOT_BACK','OPEN_FRAME',0,68,[-1,0,0],'root_wall'),(motor,'OPEN_FRAME',2,14,[0,0,1],'motor_bottom'),(motor,'OPEN_FRAME',0,-5,[1,0,0],'motor_xmin'),(motor,'OPEN_FRAME',0,5,[-1,0,0],'motor_xmax'),(motor,'MOTOR_CAP',2,26,[0,0,-1],'motor_top')]:
  for t in shared(n,m,ax,val):contact.append(dict(face=t,first=n,second=m,normal=normal,label=label,gap=a.gap if ax==0 else 0))
 portfaces=shared('OPEN_FRAME','GROUND_PLATE',2,40)
 # Aggregate upstream port on actual RootBack x50.5 face; local Rail/pin traction unresolved.
 rootfaces={t for t in ss['F0_ROOT_BACK'] if plane(t,0,50.5)};assert rootfaces
 connectors=[]
 for i in range(2):connectors.append(dict(name=f'RF{i}',first='F0_ROOT_BACK',second='OPEN_FRAME',a=shared('F0_ROOT_BACK',f'F0_RF{i}_BOLT',2,-3),b=shared('OPEN_FRAME',f'F0_RF{i}_NUT',2,-12),k=kroot,center=[64,(-16,16)[i]]))
 for x in (-7,7):
  for y in (-29.5,-13.5):connectors.append(dict(name=f'CAP{x}_{y}',first='MOTOR_CAP',second='OPEN_FRAME',a=shared('MOTOR_CAP',f'MOTOR_CAP_BOLT_{x}_{y}',2,29),b=shared('OPEN_FRAME',f'MOTOR_CAP_NUT_{x}_{y}',2,11),k=kcap,center=[x,y]))
 # Motor only supplies contact geometry and six rigid DOFs; never assigned fake E.
 keep=set(sum([vols[n] for n in elastic],[]));gmsh.model.occ.remove([v for v in frag if v[0]==3 and v[1] not in keep],recursive=True);gmsh.model.occ.synchronize()
 gmsh.option.setNumber('Mesh.MeshSizeMax',a.h);gmsh.option.setNumber('Mesh.MeshSizeMin',a.h*.4);gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',32);gmsh.option.setNumber('Mesh.Algorithm3D',1);gmsh.model.mesh.generate(3)
 nt,xyz,_=gmsh.model.mesh.getNodes();order=np.argsort(nt);nt=np.asarray(nt)[order];xyz=np.asarray(xyz).reshape(-1,3)[order]
 def tri(faces):
  rows=[]
  for t in faces:
   types,_,es=gmsh.model.mesh.getElements(2,t);rows.extend(np.searchsorted(nt,np.asarray(e).reshape(-1,3)) for typ,e in zip(types,es) if typ==2)
  return np.concatenate(rows)
 for c in contact:c['tri']=tri([c['face']])
 for c in connectors:c['at']=tri(c['a']);c['bt']=tri(c['b'])
 porttri=tri(portfaces);roottri=tri(rootfaces);data={};offset=0;Ks=[];meshes=[]
 for n in elastic:
  ts=[]
  for v in vols[n]:
   types,_,es=gmsh.model.mesh.getElements(3,v);ts.extend(np.searchsorted(nt,np.asarray(e).reshape(-1,4)) for typ,e in zip(types,es) if typ==4)
  t=np.concatenate(ts);used=np.unique(t);p=xyz[used];t=np.searchsorted(used,t);m=MeshTet(p.T,t.T);el=ElementVector(ElementTetP1());basis=Basis(m,el,intorder=2);E,nu,rho=(200000,.3,7900) if n=='F0_ROOT_BACK' else (68900,.33,2700);lam,mu=lame_parameters(E,nu);K=sparse.csr_matrix((basis.N,basis.N))
  for first in range(0,len(t),8000):K+=asm(linear_elasticity(lam,mu),Basis(m,el,intorder=2,elements=np.arange(first,min(first+8000,len(t)))))
  assert np.array_equal(basis.nodal_dofs,np.arange(basis.N).reshape(-1,3).T)
  dx=p[t[:,1:]]-p[t[:,0,None]];vv=abs(np.linalg.det(dx))/6;lump=np.zeros(len(p))
  for j in range(4):np.add.at(lump,t[:,j],vv/4)
  ndof=basis.N;d=dict(name=n,used=used,p=p,t=t,K=K,lump=lump,offset=offset,ndof=ndof,E=E,nu=nu,rho=rho);data[n]=d;Ks.append(K);offset+=ndof
  meshes.append(dict(part=n,nodes=len(p),tetra=len(t),volume_mm3=float(vv.sum()),CAD_volume_mm3=sum(gmsh.model.occ.getMass(3,v) for v in vols[n])))
 gmsh.finalize();mo=int(offset);N=mo+6;data[motor]=dict(name=motor,offset=mo,ndof=6,origin=np.array([0,0,20.]))
 K=sparse.block_diag(Ks+[sparse.csr_matrix((6,6))],format='csc');f=np.zeros(N)
 for n in elastic:
  d=data[n];f[d['offset']+2:d['offset']+d['ndof']:3]=-d['lump']*d['rho']*1e-9*9.80665
 def nodemap(n,node):
  d=data[n];M=sparse.lil_matrix((3,N))
  if n==motor:
   M[:,mo:mo+3]=np.eye(3);M[:,mo+3:mo+6]=-skew(xyz[node]-d['origin']) # rotations dimensionless
  else:
   j=np.searchsorted(d['used'],node);assert d['used'][j]==node;M[:,d['offset']+3*j:d['offset']+3*j+3]=np.eye(3)
  return M.tocsr()
 def patch(n,tr,axis):
  d=data[n];loc=np.searchsorted(d['used'],tr);assert np.array_equal(d['used'][loc],tr);p=d['p'];areas=np.linalg.norm(np.cross(p[loc[:,1]]-p[loc[:,0]],p[loc[:,2]]-p[loc[:,0]]),axis=1)/2;w=np.zeros(len(p))
  for j in range(3):np.add.at(w,loc[:,j],areas/3)
  v=np.zeros(N);v[d['offset']+3*np.arange(len(p))+axis]=w;return v,float(areas.sum())
 def distribute(n,tr,W):
  d=data[n];v,area=patch(n,tr,0);nodes=np.flatnonzero(v);loc=(nodes-d['offset'])//3;wt=v[nodes];p=d['p'][loc]*.001;H=np.hstack([np.vstack([np.eye(3),skew(r)])*w for r,w in zip(p,wt)]);inv=np.repeat(1/wt,3);coef=inv*(H.T@np.linalg.solve((H*inv)@H.T,W));forces=(np.repeat(wt,3)*coef).reshape(-1,3)
  for j,node in enumerate(loc):f[d['offset']+3*node:d['offset']+3*node+3]+=forces[j]
  return dict(part=n,wrench_N_Nm=W.tolist(),actual_N_Nm=(H@coef).tolist(),area_mm2=area,max_reference_traction_MPa=float(np.linalg.norm(coef.reshape(-1,3),axis=1).max()))
 RW=np.array(loads['Root_force_couple_XYZ_N_Nm']);RW[3:]+=np.cross(loads['Root_reference_m'],RW[:3]);rootport=distribute('F0_ROOT_BACK',roottri,RW)
 MW=np.array(loads['Motor_force_couple_XYZ_N_Nm']);MW[3:]+=np.cross(loads['Motor_reference_m'],MW[:3]);f[mo:mo+3]=MW[:3];f[mo+3:]=1000*(MW[3:]-np.cross(data[motor]['origin']*.001,MW[:3]))
 # Connector selfweights, finite actual envelope volumes/centroids from prior mass evidence.
 masssrc=ROOT/'validation/integrated/primaryP1_gravity_cat_massload1/summary.json';mass=json.loads(masssrc.read_text());massparts={p['part_ID']:p for p in mass['parts']};hardwareW=np.zeros(6)
 for n in hardware:hardwareW+=np.array(massparts[n]['gravity_wrench_N_Nm'])
 # Explicitly transport hardware gravity to finite Frame/Ground port; do not call this local bearing stress.
 hardwareport=distribute('OPEN_FRAME',porttri,hardwareW)
 def body_wrench(n,fv):
  d=data[n]
  if n==motor:return np.r_[fv[mo:mo+3],fv[mo+3:]*.001+np.cross(d['origin']*.001,fv[mo:mo+3])]
  ff=fv[d['offset']:d['offset']+d['ndof']].reshape(-1,3);return np.r_[ff.sum(axis=0),np.cross(d['p']*.001,ff).sum(axis=0)]
 def resultant(fv):return sum((body_wrench(n,fv) for n in body),np.zeros(6))
 external=distribute('OPEN_FRAME',porttri,-resultant(f));assert np.linalg.norm(resultant(f))<1e-10
 rows=[];labels=[];gaps=[];cpoints=[]
 for c in contact:
  norm=np.array(c['normal'])
  for node in np.unique(c['tri']):
   rows.append(sparse.csr_matrix(norm.reshape(1,3))@(nodemap(c['first'],node)-nodemap(c['second'],node)));labels.append(c['label']);gaps.append(c['gap']);cpoints.append(xyz[node])
 C=sparse.vstack(rows,format='csr');nc=len(rows);gaps=np.array(gaps);bolts=[];bareas=[];ks=[]
 for c in connectors:
  va,aa=patch(c['first'],c['at'],2);vb,ab=patch(c['second'],c['bt'],2)
  # Enforce exact common bolt-axis centroid on separately triangulated bearing patches.
  # A polygonal annulus quadrature offset must not manufacture an internal couple.
  def centered(n,v,area):
   ids=np.flatnonzero(v);loc=(ids-data[n]['offset'])//3;w=v[ids]/area;H=np.vstack([np.ones(len(ids)),data[n]['p'][loc,:2].T]);target=np.r_[1.,c['center']];w+=w*(H.T@np.linalg.solve((H*w)@H.T,target-H@w));assert w.min()>0;z=np.zeros(N);z[ids]=w;return z
  bolts.append(centered(c['first'],va,aa)-centered(c['second'],vb,ab));bareas.append([aa,ab]);ks.append(c['k'])
 D=sparse.csr_matrix(bolts);ks=np.array(ks);nb=len(ks);gauges=[];glabels=[]
 def meanrow(n,axis):
  d=data[n];v=np.zeros(N);v[d['offset']+3*np.arange(len(d['p']))+axis]=d['lump']/d['lump'].sum();return v
 def rotationrow(n,axis):
  d=data[n];q=d['p']-np.average(d['p'],weights=d['lump'],axis=0);v=np.zeros(N);v[d['offset']:d['offset']+d['ndof']]=(np.cross(axis,q)*d['lump'][:,None]/d['lump'].sum()).ravel()/100;return v
 for j in range(3):gauges.append(meanrow('OPEN_FRAME',j));glabels.append('Frame_global_translation'+str(j))
 for ax in np.eye(3):gauges.append(rotationrow('OPEN_FRAME',ax));glabels.append('Frame_global_rotation'+str(ax))
 # Physical frictionless Y sliding modes are left unloaded, fixed only as coordinate gauges.
 gauges.append(meanrow('F0_ROOT_BACK',1)-meanrow('OPEN_FRAME',1));glabels.append('Root_free_Y')
 v=np.zeros(N);v[mo+1]=1;gauges.append(v-meanrow('OPEN_FRAME',1));glabels.append('Motor_free_Y')
 for j in (0,1):gauges.append(meanrow('MOTOR_CAP',j)-meanrow('OPEN_FRAME',j));glabels.append('Cap_free_translation'+str(j))
 gauges.append(rotationrow('MOTOR_CAP',np.array([0,0,1]))-rotationrow('OPEN_FRAME',np.array([0,0,1])));glabels.append('Cap_free_yaw')
 Q=sparse.csr_matrix(gauges);nq=len(gauges);scale=.001;P=sparse.block_diag([K*scale,sparse.diags(ks*scale)],format='csc');A=sparse.vstack([sparse.hstack([C,sparse.csr_matrix((nc,nb))]),sparse.hstack([Q,sparse.csr_matrix((nq,nb))]),sparse.hstack([-D,sparse.eye(nb)]),sparse.hstack([sparse.csr_matrix((nb,N)),sparse.eye(nb)])],format='csc');lower=np.r_[-gaps/scale,np.zeros(nq),a.preload/ks/scale,np.zeros(nb)];upper=np.r_[np.full(nc,np.inf),np.zeros(nq),np.full(2*nb,np.inf)]
 solver=osqp.OSQP();solver.setup(P=sparse.triu(P,format='csc'),q=np.r_[-f,np.zeros(nb)],A=A,l=lower,u=upper,eps_abs=1e-12,eps_rel=1e-12,max_iter=100000,polishing=True,verbose=False,check_termination=25);r=solver.solve();u=r.x[:N]*scale;y=r.y;bf=ks*r.x[N:]*scale;g=C@u+gaps;p=-y[:nc];gd=y[nc:nc+nq];by=y[nc+nq:nc+nq+nb];res=K@u-f+C.T@y[:nc]+Q.T@gd-D.T@by
 energy=.5*float(u@K@u);spring=.5*float(np.sum(bf**2/ks));work=float(f@u);identity=2*(energy+spring)-work-float(np.sum(a.preload/ks*bf))+float(p@gaps)
 stresses=[];saved=dict(u_mm=u,applied_force_N=f,stationarity_N=res,contact_C_data=C.data,contact_C_indices=C.indices,contact_C_indptr=C.indptr,contact_C_shape=C.shape,contact_label=np.array(labels),contact_points_mm=np.array(cpoints),initial_gaps_mm=gaps,contact_gaps_mm=g,contact_force_N=p,bolt_D=D.toarray(),bolt_k_N_mm=ks,bolt_force_N=bf,bolt_dual_N=by,gauge_Q=Q.toarray(),gauge_dual=gd,motor_offset=mo)
 for n in elastic:
  d=data[n];p0,t=d['p'],d['t'];uu=u[d['offset']:d['offset']+d['ndof']].reshape(-1,3);dx=p0[t[:,1:]]-p0[t[:,0,None]];du=uu[t[:,1:]]-uu[t[:,0,None]];grad=np.linalg.solve(dx,du).transpose(0,2,1);eps=(grad+grad.transpose(0,2,1))/2;lam,mu=lame_parameters(d['E'],d['nu']);stress=2*mu*eps+lam*np.trace(eps,axis1=1,axis2=2)[:,None,None]*np.eye(3);dev=stress-np.trace(stress,axis1=1,axis2=2)[:,None,None]*np.eye(3)/3;vm=np.sqrt(1.5*np.sum(dev*dev,axis=(1,2)));det=np.linalg.det(dx);ratio=np.linalg.det(dx+du)/det
  stresses.append(dict(part=n,peak_unsmoothed_vm_MPa=float(vm.max()),max_motion_mm=float(np.linalg.norm(uu,axis=1).max()),minimum_signed_volume_ratio=float(ratio.min())))
  for key,val in dict(points_mm=p0,tetra=t,offset=d['offset'],ndof=d['ndof'],E_MPa=d['E'],nu=d['nu'],rho_kg_m3=d['rho'],vm_MPa=vm).items():saved[n+'_'+key]=val
 balance={n:body_wrench(n,res).tolist() for n in body};relative=float(np.linalg.norm(res)/max(np.linalg.norm(f),1));er=abs(identity)/max(energy+spring,1e-20);comp=float(np.max(abs(g*saved['contact_force_N'])));gaugeforce=Q.T@gd;gb=resultant(gaugeforce)
 checks=dict(solver_solved=r.info.status=='solved',stationarity=relative<1e-8,body_forces=all(np.linalg.norm(w[:3])<1e-8 for w in balance.values()),body_moments=all(np.linalg.norm(w[3:])<1e-10 for w in balance.values()),gauge_negligible=float(np.linalg.norm(gd))<1e-8,gaps=float(g.min())>-1e-8,compression_only=float(saved['contact_force_N'].min())>-1e-8,complementarity=comp<1e-8,bolt_law=float(np.max(abs(by-bf)))<1e-8,energy=er<1e-8,mesh_volume=all(abs(m['volume_mm3']/m['CAD_volume_mm3']-1)<.01 for m in meshes),no_inversion=all(s['minimum_signed_volume_ratio']>0 for s in stresses))
 np.savez_compressed(out/'field.npz',**saved)
 result=dict(status='ACTUAL_P1_UPPER_COMPLIANT_CONTACT_PASS' if all(checks.values()) else 'ACTUAL_P1_UPPER_COMPLIANT_CONTACT_FAIL',candidate=ref(src),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),field=ref(out/'field.npz'),checks=checks,h_mm=a.h,gap_mm=a.gap,preload_each_N=a.preload,DOF=N,meshes=meshes,solver=dict(status=r.info.status,iterations=r.info.iter,primal=r.info.prim_res,dual=r.info.dual_res),stresses=stresses,contact_groups={label:dict(nodes=labels.count(label),active=int(np.sum(saved['contact_force_N'][np.array(labels)==label]>1e-8)),force_N=float(saved['contact_force_N'][np.array(labels)==label].sum()),min_gap_mm=float(g[np.array(labels)==label].min()),max_gap_mm=float(g[np.array(labels)==label].max())) for label in set(labels)},bolt_names=[c['name'] for c in connectors],bolt_force_N=bf.tolist(),bearing_areas_head_nut_mm2=bareas,root_port=rootport,hardware_gravity_port=hardwareport,external_FrameGround_port=external,motor_external_wrench_N_Nm=MW.tolist(),body_residual_N_Nm=balance,relative_stationarity=relative,elastic_energy_Nmm=energy,bolt_energy_Nmm=spring,static_energy_relative=er,static_energy_identity_Nmm=identity,complementarity_Nmm=comp,gauge_labels=glabels,gauge_dual=gd.tolist(),gauge_wrench_N_Nm=gb.tolist(),motor_rigid_translation_mm=u[mo:mo+3].tolist(),motor_rigid_rotation_rad=u[mo+3:].tolist(),elapsed_s=time.monotonic()-start,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Actual separate elastic RootBack/Frame/Cap with rigid motor proxy. Source motorcase stiffness/contactland validity unknown; no case strength.','Frozen upstream gravity Finger/string/rotor resultant applied on actual RootBack x50.5 face,not solved local Rail/pin/clamp traction or re-solved Finger against deformed supports.','Explicit balanced finite Frame/Ground traction includes shear. Actual frictionless planar Frame/Ground and axial M5 alone cannot supply Fx; friction/bolt shank/positive key interface not solved. No hidden M5 fixation.','Root/Motor freeY and Cap freeXY/yaw gauges must carry negligible loads. They identify unrestrained frictionless modes,not physical retention or reverse/Yload qualification.','Lateral gap is a contact-law offset at same nominalCAD; not a new machined part/finitegap CCD. Small displacement/rotation contact only.','Conditional minorcore axial compliance and mean realhead/nut footprints,not threadflank/bearing/engagement/preload or capacity. Hardwaregravity transported through Frameport; local bearing weight unresolved.','Typical conditional elastic constants/densities only; no source materialminima,1%mesh/time/globalenergy/strength/full3Finger/Stage1/Stage3 certificate.'])
 dump(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','checks','DOF','solver','stresses','bolt_force_N','relative_stationarity','static_energy_relative','gauge_dual','contact_groups')}));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
