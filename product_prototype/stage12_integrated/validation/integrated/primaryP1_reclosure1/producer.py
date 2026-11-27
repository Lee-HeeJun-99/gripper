"""Re-use actual seated22 mesh, all unilateral rows and axial connectors.
Outer support/spatial-string/planar-Finger closure, conditional small-displacement
elasticity only. No remesh, altered contact, physical retention or strength claim.
"""
import sys,json,shutil,time
import numpy as np
from scipy import sparse
from scipy.spatial.transform import Rotation
from skfem import MeshTet,Basis,ElementTetP1,ElementVector,asm
from skfem.models.elasticity import linear_elasticity,lame_parameters
from baseline_registry import ROOT,REPO,ref,sha,dump
from primary_support_feedback import fit
from primary_seated_string import SeatedString
from primary_seated_finger_v2 import solve
from primary_contact_polish_spatial import polish

def skew(r):
 x,y,z=r;return np.array([[0,-z,y],[z,0,-x],[-y,x,0]])

def main():
 start=time.monotonic();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 assert not(ROOT/'runtime/STOP').exists()
 source=ROOT/'validation/integrated/primaryP1_front_h5_2/summary.json';s=json.loads(source.read_text());assert all(s['checks'].values())
 assert sha(REPO/s['field']['path'])==s['field']['SHA256'];a=dict(np.load(REPO/s['field']['path']));N=len(a['u_mm']);mo=int(a['motor_offset']);names=s['elastic_bodies'];Ks=[];data={}
 for n in names:
  p=a[n+'_points_mm'];t=a[n+'_tetra'];m=MeshTet(p.T,t.T);el=ElementVector(ElementTetP1());basis=Basis(m,el,intorder=2);E=float(a[n+'_E_MPa']);nu=float(a[n+'_nu']);lam,mu=lame_parameters(E,nu);K=sparse.csr_matrix((basis.N,basis.N))
  for first in range(0,len(t),8000):K+=asm(linear_elasticity(lam,mu),Basis(m,el,intorder=2,elements=np.arange(first,min(first+8000,len(t)))))
  Ks.append(K);data[n]=dict(p=p,t=t,offset=int(a[n+'_offset']),mesh=m,E=E,nu=nu)
 K=sparse.block_diag(Ks+[sparse.csr_matrix((6,6))],format='csc');C=sparse.csr_matrix((a['contact_C_data'],a['contact_C_indices'],a['contact_C_indptr']),shape=tuple(a['contact_C_shape']));Q=sparse.csr_matrix(a['gauge_Q']);D=sparse.csr_matrix(a['bolt_D']);ks=a['bolt_k_N_mm'];gaps=a['initial_gaps_mm'];q=a['gauge_targets_mm'].copy()
 def port(n,axis,value):
  d=data[n];p=d['p'];tri=d['mesh'].facets[:,d['mesh'].boundary_facets()].T;tri=tri[np.all(abs(p[tri,axis]-value)<1e-5,axis=1)];assert len(tri)
  # Base port excludes nut bearing faces, exactly as original CAD surface port.
  if n=='TEST_BASE':
   centers=np.array([[-44,-30],[-44,10],[86,-30],[86,10]])
   xy=p[tri].mean(axis=1)[:,:2];tri=tri[np.min(np.linalg.norm(xy[:,None,:]-centers[None,:,:],axis=2),axis=1)>4.7]
  area=np.linalg.norm(np.cross(p[tri[:,1]]-p[tri[:,0]],p[tri[:,2]]-p[tri[:,0]]),axis=1)/2;wt=np.zeros(len(p))
  for j in range(3):np.add.at(wt,tri[:,j],area/3)
  ids=np.flatnonzero(wt);w=wt[ids];H=np.hstack([np.vstack([np.eye(3),skew(r*.001)])*z for r,z in zip(p[ids],w)]);inv=np.repeat(1/w,3);B=(np.repeat(w,3)*inv)[:,None]*(H.T@np.linalg.inv((H*inv)@H.T));rows=d['offset']+3*ids[:,None]+np.arange(3);M=sparse.csr_matrix((B.ravel(),(np.repeat(rows.ravel(),6),np.tile(np.arange(6),len(rows.ravel())))),shape=(N,6))
  return M,float(area.sum())
 R,ra=port('F0_ROOT_BACK',0,50.5);B,ba=port('TEST_BASE',2,66)
 assert abs(ra/s['root_port']['area_mm2']-1)<1e-12,(ra,s['root_port']['area_mm2'])
 assert abs(ba/s['external_FrameGround_port']['area_mm2']-1)<1e-12,(ba,s['external_FrameGround_port']['area_mm2'])
 M=sparse.lil_matrix((N,6));M[mo:mo+3,:3]=np.eye(3);M[mo+3:mo+6,:3]=-1000*skew([0,0,.020]);M[mo+3:mo+6,3:]=1000*np.eye(3);M=M.tocsr()
 def wrench(f):
  w=np.r_[f[mo:mo+3],f[mo+3:mo+6]*.001+np.cross([0,0,.020],f[mo:mo+3])]
  for d in data.values():
   off=d['offset'];ff=f[off:off+3*len(d['p'])].reshape(-1,3);w+=np.r_[ff.sum(0),np.cross(d['p']*.001,ff).sum(0)]
  return w
 # Independently recovered port operators must reproduce original recorded loads.
 oldload=ROOT/'validation/integrated/primaryP1_seated_finger2/summary.json';old=json.loads(oldload.read_text());RW0=np.array(old['Root_origin_wrench_N_Nm']);MW0=np.array(old['Motor_origin_wrench_N_Nm']);f0=a['applied_force_N'];u=a['u_mm'];p=a['contact_force_N'];gd=a['gauge_dual'];bf=a['bolt_force_N'];res0=K@u-f0-C.T@p+Q.T@gd+D.T@bf
 operator_checks=dict(original_stationarity=np.linalg.norm(res0)/max(np.linalg.norm(f0),1)<1e-8,root_port_area=abs(ra/s['root_port']['area_mm2']-1)<1e-12,base_port_area=abs(ba/s['external_FrameGround_port']['area_mm2']-1)<1e-12,root_unit_wrenches=max(np.max(abs(wrench(R[:,j].toarray().ravel())-np.eye(6)[j])) for j in range(6))<1e-12,base_unit_wrenches=max(np.max(abs(wrench(B[:,j].toarray().ravel())-np.eye(6)[j])) for j in range(6))<1e-12)
 assert all(operator_checks.values()),operator_checks
 masssrc=ROOT/'validation/integrated/primaryP1_seated_string1/mass_points.json';points=json.loads(masssrc.read_text());seedpath=ROOT/'validation/finger/primaryP1_gravity_cat_demand32_2/cases.json';seed=json.loads(seedpath.read_text())[0]
 def feedback(u):
  d=data['F0_ROOT_BACK'];pp=d['p'];uu=u[d['offset']:d['offset']+3*len(pp)].reshape(-1,3);sel=abs(pp[:,0]-50.5)<1e-5;row,z,center=fit(pp[sel],uu[sel]);anchor=np.array([50.4,0,-7.]);ur=z[:3]+np.cross(z[3:],anchor-center);Rr=Rotation.from_rotvec(z[3:]).as_matrix();tr=(anchor+ur)*.001-Rr@(anchor*.001);Rm=Rotation.from_rotvec(u[mo+3:mo+6]).as_matrix();mc=np.array([0,0,.020])+u[mo:mo+3]*.001;E=Rr@np.array([seed['cable_end_m'][0],0,seed['cable_end_m'][1]])+tr;initial=SeatedString(points,Rm,mc,E,.01125).solve(seed);parent=dict(root_R=Rr.tolist(),root_translation_m=tr.tolist(),motor_R=Rm.tolist(),motor_C_m=mc.tolist(),actual_wire_center_radius_m=.01125,actual=initial);actual=solve(parent,seed,points);return actual,dict(root_fit=row,**{k:v for k,v in parent.items() if k!='actual'})
 dump(out/'inputs.json',dict(candidate=s['candidate'],field_source=ref(source),field=s['field'],loads=ref(oldload),mass=ref(masssrc),seed=ref(seedpath),producer=ref(out/'producer.py'),dependencies=[ref(ROOT/'scripts'/n) for n in ['primary_seated_finger_v2.py','primary_seated_string.py','primary_spatial_string.py','primary_support_feedback.py','primary_contact_polish_spatial.py']],criteria=dict(force_N=1e-8,moment_Nm=1e-10),operator_checks={k:bool(v) for k,v in operator_checks.items()},port_area_mm2=dict(Root=ra,Base=ba),boundary='Original small-displacement reference geometry/gauges and linear selfweights; updated upstream pose-dependent fixed/moving weights and couples; finite Base traction is mathematical, NOT physical anchorage.'))
 history=[];closed=False
 for iteration in range(6):
  assert not(ROOT/'runtime/STOP').exists();assert time.monotonic()-start<360,'Reserve child saving time'
  actual,pose=feedback(u);RW=np.array(actual['Root_origin_wrench_N_Nm']);MW=np.array(actual['Motor_origin_wrench_N_Nm']);f=f0+R@(RW-RW0)+M@(MW-MW0);f-=B@wrench(f);q[s['gauge_labels'].index('Root_free_Y')]=-.01+actual['string']['root_free_Y_shift_mm'];u,p,gd,bf,ph=polish(K,f,C,Q,D,ks,gaps,0,u,p,q)
  returned,pose2=feedback(u);dr=np.array(returned['Root_origin_wrench_N_Nm'])-RW;dm=np.array(returned['Motor_origin_wrench_N_Nm'])-MW;fe=float(max(np.linalg.norm(dr[:3]),np.linalg.norm(dm[:3])));me=float(max(np.linalg.norm(dr[3:]),np.linalg.norm(dm[3:])));freeY=abs(returned['string']['root_free_Y_shift_mm']-actual['string']['root_free_Y_shift_mm']);g=C@u+gaps;res=K@u-f-C.T@p+Q.T@gd+D.T@bf;elastic=.5*float(u@K@u);spring=.5*float(np.sum(bf*bf/ks));energy=abs(2*(elastic+spring)-f@u+p@gaps)/max(elastic+spring,1e-20)
  checks=dict(local=all(returned['checks'].values()),stationarity=np.linalg.norm(res)/max(np.linalg.norm(f),1)<1e-8,gap=g.min()>-1e-8,pressure=p.min()>-1e-8,complementarity=np.max(abs(g*p))<1e-8,gauge=np.linalg.norm(gd)<1e-8,energy=energy<1e-8,force_fixed_point=fe<1e-8,moment_fixed_point=me<1e-10,freeY_fixed_point=freeY<1e-8)
  row=dict(iteration=iteration,force_difference_N=fe,moment_difference_Nm=me,freeY_difference_mm=freeY,normal_N=returned['normal_N'],gauge_norm_N=float(np.linalg.norm(gd)),stationarity=float(np.linalg.norm(res)/max(np.linalg.norm(f),1)),energy_relative=float(energy),polish_steps=len(ph),checks={k:bool(v) for k,v in checks.items()},elapsed_s=time.monotonic()-start);history.append(row);dump(out/f'iteration{iteration}.json',dict(**row,applied_Root_wrench_N_Nm=RW.tolist(),applied_Motor_wrench_N_Nm=MW.tolist(),returned_Root_wrench_N_Nm=returned['Root_origin_wrench_N_Nm'],returned_Motor_wrench_N_Nm=returned['Motor_origin_wrench_N_Nm'],pose=pose2,polish_history=ph));print(json.dumps(row),flush=True)
  if all(checks.values()):closed=True;break
 a.update(u_mm=u,applied_force_N=f,stationarity_N=res,contact_gaps_mm=g,contact_force_N=p,bolt_force_N=bf,bolt_dual_N=-bf,gauge_targets_mm=q,gauge_dual=gd)
 stresses=[]
 for n,d in data.items():
  pp=d['p'];t=d['t'];off=d['offset'];uu=u[off:off+3*len(pp)].reshape(-1,3);dx=pp[t[:,1:]]-pp[t[:,0,None]];du=uu[t[:,1:]]-uu[t[:,0,None]];grad=np.linalg.solve(dx,du).transpose(0,2,1);eps=(grad+grad.transpose(0,2,1))/2;lam,mu=lame_parameters(d['E'],d['nu']);st=2*mu*eps+lam*np.trace(eps,axis1=1,axis2=2)[:,None,None]*np.eye(3);dev=st-np.trace(st,axis1=1,axis2=2)[:,None,None]*np.eye(3)/3;vm=np.sqrt(1.5*np.sum(dev*dev,axis=(1,2)));a[n+'_vm_MPa']=vm;stresses.append(dict(part=n,conditional_peak_MPa=float(vm.max()),minimum_volume_ratio=float(np.min(np.linalg.det(dx+du)/np.linalg.det(dx)))))
 np.savez_compressed(out/'field.npz',**a);dump(out/'curves.json',{k:returned['string'].pop(k) for k in ('curve_m','wrap_curve_m','lead_curve_m','free_curve_m')});dump(out/'state.json',returned)
 result=dict(status='ACTUAL_P1_SEATED22_CONDITIONAL_OUTER_CLOSURE_PASS' if closed else 'ACTUAL_P1_SEATED22_CONDITIONAL_OUTER_CLOSURE_FAIL',candidate=s['candidate'],producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),source=ref(source),field=ref(out/'field.npz'),state=ref(out/'state.json'),curves=ref(out/'curves.json'),pose=pose2,history=history,checks=history[-1]['checks'],operator_checks={k:bool(v) for k,v in operator_checks.items()},elastic_bodies=names,preload_each_N=0,elastic_energy_Nmm=elastic,bolt_energy_Nmm=spring,DOF=N,contact_rows=C.shape[0],connectors=len(ks),normal_N=returned['normal_N'],stresses=stresses,elapsed_s=time.monotonic()-start,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=s['limitations']+['Outer closure ONLY on original saved coarse linear operator/all original contact rows; planar rod constitutive law. No spatial mesh convergence, exact nonlinear geometry, physical retention/anchorage, global energy or strength certification. Reference elastic/hardware gravity remains original small-displacement load; upstream fixed/moving gravity positions and couples re-evaluated each iteration.'])
 dump(out/'summary.json',result);print(result['status']);raise SystemExit(0 if closed else 2)
if __name__=='__main__':main()
