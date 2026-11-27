"""Actual full RootBack four finite pin ports: free-body elastic compliance.
Prescribed pressure-shape sensitivity only. No contact law or upstream fixation.
"""
import sys,json,time,shutil,itertools
import numpy as np
import gmsh
from scipy import sparse
from scipy.sparse.linalg import splu
from skfem import MeshTet,Basis,ElementTetP1,ElementVector,asm
from skfem.models.elasticity import linear_elasticity,lame_parameters
from baseline_registry import ROOT,REPO,ref,sha,dump

def clip(poly,axis,value,above):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=(a[axis]-value)*(1 if above else -1);db=(b[axis]-value)*(1 if above else -1)
  if da>=-1e-13:out.append(a)
  if (da>0 and db<0) or (da<0 and db>0):out.append(a+(b-a)*da/(da-db))
 return out

def balance_port(p,ids,weights,W):
 # Minimum area-weighted traction with specified SIX resultants, no fixed node.
 q=p[ids];H=np.zeros((6,3*len(ids)))
 for i,r in enumerate(q):
  H[:3,3*i:3*i+3]=np.eye(3);H[3:,3*i:3*i+3]=[[0,-r[2],r[1]],[r[2],0,-r[0]],[-r[1],r[0],0]]
 w=np.repeat(weights,3);f=w*(H.T@np.linalg.solve((H*w)@H.T,W));return f.reshape(-1,3)
def resultants(p,f):return np.r_[f.sum(0),np.cross(p,f).sum(0)]
def allocation(C,total):
 best=None
 for mask in itertools.product([False,True],repeat=4):
  ids=np.flatnonzero(mask)
  if not len(ids):continue
  ci=C[np.ix_(ids,ids)];v=np.linalg.solve(ci,np.ones(len(ids)));r=np.zeros(4);r[ids]=total*v/v.sum();mu=(C@r)[ids].mean()
  if min(r)>=-1e-12 and np.all((C@r)[~np.array(mask)]>=mu-1e-12):
   e=float(r@C@r/2)
   if best is None or e<best[0]:best=(e,r,mu)
 assert best is not None
 return best

def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();tag,h,curv=sys.argv[1],float(sys.argv[2]),int(sys.argv[3]);out=ROOT/'validation/integrated'/tag;out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 cp=ROOT/'cad/exports/primaryP1_ycapture24/summary.json';cad=json.loads(cp.read_text());assert len(cad['part_references'])==78 and all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values());sp=ROOT/'validation/integrated/primaryP1_gamma_attachment29/summary.json';src=json.loads(sp.read_text());geo=json.loads((REPO/src['geometry']['path']).read_text());old=ROOT/'validation/integrated/primaryP1_fivebody_rebuild27/h2_fivebody_reference.npz';a=np.load(old);E=float(a['F0_ROOT_BACK_E_MPa']);nu=float(a['F0_ROOT_BACK_nu']);pinstate=json.loads((ROOT/'validation/integrated/primaryP1_pin_mode29/summary.json').read_text());total=next(r['total_necessary_pin_reaction_N'] for r in pinstate['results'] if r['case']=='tilt_minus')
 dump(out/'inputs.json',dict(candidate=ref(cp),part=cad['part_references']['F0_ROOT_BACK'],pin_holes=src['geometry'],material_geometry_only=ref(old),conditional_E_MPa=E,conditional_nu=nu,material_minimum_qualified=False,h_mm=h,curvature_elements=curv,producer=ref(out/'producer.py'),source_total_reaction=ref(ROOT/'validation/integrated/primaryP1_pin_mode29/summary.json'),scope='Full actual Root solid, finite curved pin-surface pressure ports over actual axial overlaps. Self-equilibrated SIX-resultant return through actual x50.5 clamp interface. Six volume gauges remove only rigid modes; no Root fixation. Prescribed finite pressure bands .6/.3 rad are shape sensitivities, NOT elastic contact solutions, machining changes, preload or physical acceptance criteria. Other77actual product bodies remain unsolved.'))
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);gmsh.model.add('actual_P1_RootBack');vs=gmsh.model.occ.importShapes(str(REPO/cad['part_references']['F0_ROOT_BACK']['path']));gmsh.model.occ.synchronize();cadvol=sum(gmsh.model.occ.getMass(d,t) for d,t in vs);gmsh.option.setNumber('Mesh.MeshSizeMax',h);gmsh.option.setNumber('Mesh.MeshSizeMin',min(.04,h/30));gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',curv);gmsh.model.mesh.generate(3);nt,xyz,_=gmsh.model.mesh.getNodes();order=np.argsort(nt);nt=np.array(nt)[order];p=np.array(xyz).reshape(-1,3)[order]
 types,_,es=gmsh.model.mesh.getElements(3);t=np.concatenate([np.searchsorted(nt,np.array(e).reshape(-1,4)) for typ,e in zip(types,es) if typ==4]);types,_,es=gmsh.model.mesh.getElements(2);tri=np.concatenate([np.searchsorted(nt,np.array(e).reshape(-1,3)) for typ,e in zip(types,es) if typ==2]);gmsh.finalize();used=np.unique(t);assert np.isin(tri,used).all();p=p[used];t=np.searchsorted(used,t);tri=np.searchsorted(used,tri);N=3*len(p);m=MeshTet(p.T,t.T);el=ElementVector(ElementTetP1());lam,mu=lame_parameters(E,nu);K=sparse.csr_matrix((N,N))
 for first in range(0,len(t),8000):
  assert not(ROOT/'runtime/STOP').exists();K+=asm(linear_elasticity(lam,mu),Basis(m,el,intorder=2,elements=np.arange(first,min(first+8000,len(t)))))
 vol=abs(np.linalg.det((p[t[:,1:]]-p[t[:,0,None]]).transpose(0,2,1)))/6;lump=np.zeros(len(p))
 for j in range(4):np.add.at(lump,t[:,j],vol/4)
 q=p-np.average(p,weights=lump,axis=0);wt=lump/lump.sum();Q=[]
 for axis in np.eye(3):Q.append((wt[:,None]*np.tile(axis,(len(p),1))).ravel())
 length=np.sqrt(np.average(np.sum(q*q,axis=1),weights=lump))
 for axis in np.eye(3):Q.append((wt[:,None]*np.cross(axis,q)/length).ravel())
 Q=sparse.csr_matrix(Q);A=sparse.bmat([[K,Q.T],[Q,None]],format='csc');factor=splu(A)
 clamp=tri[np.all(abs(p[tri,0]-50.5)<1e-7,axis=1)];area=np.linalg.norm(np.cross(p[clamp[:,1]]-p[clamp[:,0]],p[clamp[:,2]]-p[clamp[:,0]]),axis=1)/2;cw=np.zeros(len(p))
 for j in range(3):np.add.at(cw,clamp[:,j],area/3)
 ids=np.flatnonzero(cw);assert len(ids)>5;answers=[];fields={'points_mm':p,'tetra':t,'boundary_triangles':tri,'clamp_weight_mm2':cw};journals=[]
 for angle in [.6,.3]:
  F=[];patchinfo=[]
  for gi,g in enumerate(geo):
   yc,zc=g['pin']['axis_point_mm'][1:];lo=max(g['pin']['bounds_mm'][0],g['hole']['bounds_mm'][0]);hi=min(g['pin']['bounds_mm'][3],g['hole']['bounds_mm'][3]);f=np.zeros((len(p),3));ar=0.;ns=0;minb=1.;max_recon=0.
   for tr in tri:
    pts=p[tr];rad=pts[:,1:]-[yc,zc]
    if np.max(abs(np.linalg.norm(rad,axis=1)-1))>1e-6:continue
    normal=np.cross(pts[1]-pts[0],pts[2]-pts[0]);norm=np.linalg.norm(normal)
    if norm<1e-14 or np.ptp(pts[:,0])<1e-8:continue
    # CAD radial normal at facet centroid, not an axis-parallel facet assumption.
    normal=np.r_[0.,np.mean(rad,axis=0)];normal/=np.linalg.norm(normal)
    if normal[1]<=0:continue
    poly=[x.copy() for x in pts]
    for ax,value,above in [(0,lo,True),(0,hi,False),(1,yc+np.cos(angle),True)]:
     if poly:poly=clip(poly,ax,value,above)
    if len(poly)<3:continue
    edge=np.column_stack([pts[1]-pts[0],pts[2]-pts[0]]);pinv=np.linalg.pinv(edge)
    for j in range(1,len(poly)-1):
     sub=np.array([poly[0],poly[j],poly[j+1]]);aa=np.linalg.norm(np.cross(sub[1]-sub[0],sub[2]-sub[0]))/2
     if aa<1e-15:continue
     qp=sub.mean(0);bc=pinv@(qp-pts[0]);bary=np.r_[1-bc.sum(),bc];ff=-normal*aa
     for k,node in enumerate(tr):f[node]+=ff*bary[k]
     ar+=aa;ns+=1;minb=min(minb,float(bary.min()));err=float(np.linalg.norm(bary@pts-qp));max_recon=max(max_recon,err)
     journals.append(dict(angle_rad=angle,port=gi,nodes=tr.tolist(),q_mm=qp.tolist(),barycentric=bary.tolist(),area_mm2=float(aa),normal=normal.tolist(),axial_interval_mm=[lo,hi]))
   assert ar>0 and f[:,1].sum()<0,(gi,ar);f/= -f[:,1].sum();raw=resultants(p,f);returnf=balance_port(p,ids,cw[ids],-raw);f[ids]+=returnf;F.append(f.ravel());patchinfo.append(dict(part=g['part'],axis_y_mm=yc,axial_interval_mm=[lo,hi],faceted_band_area_mm2=ar,quadrature_samples=ns,min_barycentric=minb,reconstruction_error_mm=max_recon,unit_pin_wrench_N_Nmm=raw.tolist(),return_wrench_N_Nmm=resultants(p[ids],returnf).tolist(),total_wrench_N_Nmm=resultants(p,f).tolist(),pressure_shape_is_prescribed=True))
  B=np.array(F).T;sol=factor.solve(np.vstack([B,np.zeros((6,4))]));U=sol[:N];duals=sol[N:];res=K@U+Q.T@duals-B;C=B.T@U;energy,r,common=allocation(C,total);equal=np.ones(4)*total/4;kinematic=C@r;inactive=r<1e-14;splitres=max(abs(r.sum()-total),float(np.max(abs(kinematic[~inactive]-common))));shape_key=f'a{angle:g}';fields[shape_key+'_unit_loads_N']=B;fields[shape_key+'_unit_displacements_mm']=U;fields[shape_key+'_compliance_mm_N']=C;fields[shape_key+'_gauge_duals']=duals
  eig=np.linalg.eigvalsh((C+C.T)/2);checks=dict(force_residual=bool(np.max(abs(res))<1e-8),gauge_load_negligible=bool(np.max(abs(duals))<1e-8),gauge_kinematics=bool(np.max(abs(Q@U))<1e-10),reciprocity=bool(np.max(abs(C-C.T))/max(abs(C).max(),1e-30)<1e-8),positive_compliance=bool(eig.min()>0),self_equilibrated=all(np.max(abs(np.array(x['total_wrench_N_Nmm'])[:3]))<1e-8 and np.max(abs(np.array(x['total_wrench_N_Nmm'])[3:]))<1e-7 for x in patchinfo),finite_port_inside=all(x['min_barycentric']>-1e-10 and x['reconstruction_error_mm']<1e-9 for x in patchinfo),split_KKT=bool(splitres<1e-8 and min(r)>=0),elastic_energy=bool(abs(float(r@C@r)/2-energy)<1e-15))
  answers.append(dict(angle_rad=angle,checks=checks,compliance_mm_N=C.tolist(),compliance_eigenvalues_mm_N=eig.tolist(),unit_load_max_stationarity_N=float(abs(res).max()),gauge_load_max_N=float(abs(duals).max()),reciprocity_relative=float(abs(C-C.T).max()/abs(C).max()),conditional_total_source_reaction_N=total,conditional_Root_side_reaction_N=r.tolist(),conditional_equal_split_energy_Nmm=float(equal@C@equal/2),conditional_minimum_energy_Nmm=energy,conditional_common_port_motion_mm=common,split_is_actual_product_solution=False,port_geometry=patchinfo))
 np.savez_compressed(out/'root_compliance_fields.npz',**fields);dump(out/'finite_pin_quadrature.json',journals);checks=dict(all_numeric_checks=all(all(r['checks'].values()) for r in answers),CAD_volume_1percent=bool(abs(vol.sum()/cadvol-1)<.01),all_four_actual_ports=all(len(r['port_geometry'])==4 for r in answers));dump(out/'summary.json',dict(status='ACTUAL_P1_ROOT_FINITE_PIN_PORT_COMPLIANCE_CONDITIONAL' if all(checks.values()) else 'ACTUAL_P1_ROOT_FINITE_PIN_COMPLIANCE_FAIL',candidate=ref(cp),inputs=ref(out/'inputs.json'),fields=ref(out/'root_compliance_fields.npz'),finite_quadrature=ref(out/'finite_pin_quadrature.json'),checks=checks,results=answers,nodes=len(p),tetra=len(t),DOF=N,h_mm=h,curvature_elements=curv,CAD_volume_mm3=cadvol,mesh_volume_mm3=float(vol.sum()),elapsed_s=time.monotonic()-start,newly_qualified_system_gate_ids=[],accepted_equilibria=0,whole_system_release=False,actual_CAD_change_files=[],limitations=['Actual full RootBack conditional E200000MPa/nu.3 only. Finite facets approximate cylindrical CAD; finite axial bands clipped to actual1.5/.2mm Front/Rail intervals. No ideal coupon.','Normal dead-pressure band shapes are prescribed sensitivity ports, NOT unilateral compliant pressure/contact law or solved physical area. Exact CAD gap at the undeformed seated pose is zero only on a line; finite bands require compliant deformation not solved here.','Four-port elastic cross-compliance retains all Root elastic DOF; six gauges remove only rigid modes and carry negligible load. Return traction is an explicit conditional SIX-resultant source interface, NOT a fixation, physical clamp solution or whole-system counterload.','Conditional minimum-energy split assumes common rigid upstream port motion and those pressure shapes. Front/Rail and clamp compliance, real contact pressure, full source modes, thread shear/tilt/rest setting, finite bore and Base anchor still required. No load split/strength/gate/global energy/product release certification.']));print(json.dumps(dict(checks=checks,nodes=len(p),tetra=len(t),results=answers)));return 0 if all(checks.values()) else 2
if __name__=='__main__':sys.exit(main())
