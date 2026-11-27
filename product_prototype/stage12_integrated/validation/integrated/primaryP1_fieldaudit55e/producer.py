"""Independent saved-field tetra force/energy audit and all-pair mesh contrasts.
No producer stiffness/matrix or copied residual is used to certify physics.
"""
import sys,json,shutil,numpy as np
from baseline_registry import ROOT,REPO,ref,sha,dump
out=ROOT/'validation/integrated/primaryP1_fieldaudit55e';out.mkdir();shutil.copyfile(__file__,out/'producer.py');rows=[];paths=[ROOT/'validation/integrated'/n/'summary.json' for n in sys.argv[1:]];cp=ROOT/'cad/exports/primaryP1_integral55e/summary.json'
def L(x):
 x,y,z=x;return np.c_[np.eye(3),-np.array([[0,-z,y],[z,0,-x],[-y,x,0]])]
for path in paths:
 assert not(ROOT/'runtime/STOP').exists();d=json.loads(path.read_text());assert d['candidate']==ref(cp);assert sha(REPO/d['field']['path'])==d['field']['SHA256'];a=np.load(REPO/d['field']['path']);p=a['points_mm'];t=a['tetra'];u=a['displacement_mm'];F=a['load_N'];dx=p[t[:,1:]]-p[t[:,0,None]];V=abs(np.linalg.det(dx))/6;iv=np.linalg.inv(dx);grad=np.concatenate([-iv.sum(2)[:,None,:],iv.transpose(0,2,1)],axis=1);E=68900;nu=.33;mu=E/(2*(1+nu));la=E*nu/((1+nu)*(1-2*nu))
 def internal(uu):
  G=np.einsum('tai,taj->tij',uu[t],grad);eps=(G+G.transpose(0,2,1))/2;sig=2*mu*eps+la*np.trace(eps,axis1=1,axis2=2)[:,None,None]*np.eye(3);ef=np.einsum('tij,taj,t->tai',sig,grad,V);r=np.zeros_like(uu)
  for j in range(4):np.add.at(r,t[:,j],ef[:,j])
  energy=float(np.sum(.5*np.einsum('tij,tij->t',eps,sig)*V));return r,energy
 fi,en=internal(u);res=float(abs(fi-F).max());bal=F.sum(0);mom=np.cross(p,F).sum(0)*.001;work=float(.5*np.sum(F*u));bad=u.copy();bad[t[0,0],2]+=1e-4;fi_bad,_=internal(bad);negative=float(abs(fi_bad-F).max());rigid=np.cross([0,0,1e-5],p)+[.002,-.003,.004];fi_rigid,en_rigid=internal(u+rigid);rigid_force_error=float(abs(fi_rigid-fi).max());rigid_energy_error=abs(en_rigid/en-1)
 ports=json.loads((REPO/d['port_journal']['path']).read_text());M=np.zeros((6,6));rhs=np.zeros(6);rootarea=0.;rootc=np.zeros(3);rootu=np.zeros(3)
 for port in ports:
  for q in port['quadrature']:
   point=np.array(q['point']);uv=np.array(q['bc'])@u[np.array(q['nodes'])];area=q['area']
   if port['label']=='actual_lower_foot':
    A=L(point);M+=area*A.T@A;rhs+=area*A.T@uv
   elif port['label'].startswith('actual_Root_seat'):
    rootarea+=area;rootc+=area*point;rootu+=area*uv
 footrigid=np.linalg.solve(M,rhs);rootc/=rootarea;rootu/=rootarea;relative=rootu-L(rootc)@footrigid
 checks=dict(independent_all_DOF_force=res<1e-8,force=float(np.linalg.norm(bal))<1e-8,moment=float(np.linalg.norm(mom))<1e-10,independent_energy=abs(en/work-1)<1e-8,producer_energy_agreement=abs(en/d['static_strain_energy_Nmm']-1)<1e-8,perturbed_displacement_rejected=negative>1e-6,wrong_load_sign_rejected=float(abs(fi+F).max())>1e-6,rigid_force_invariance=rigid_force_error<1e-8,rigid_energy_invariance=rigid_energy_error<1e-8,producer_all_local_checks=all(d['checks'].values()))
 rows.append(dict(source=ref(path),candidate=d['candidate'],h_mm=d['h_mm'],nodes=d['nodes'],tetra=d['tetra'],checks={k:bool(v) for k,v in checks.items()},independent_all_DOF_residual_N=res,independent_static_energy_Nmm=en,half_external_work_Nmm=work,force_balance_N=bal.tolist(),moment_balance_Nm=mom.tolist(),perturbed_state_residual_N=negative,rigid_force_error_N=rigid_force_error,rigid_energy_relative_error=rigid_energy_error,root_relative_to_best_fit_actual_foot_mm=relative.tolist(),normal_load_compliance_mm_N=d['normal_load_compliance_mm_N'],maximum_displacement_in_restored_gauge_mm=d['maximum_displacement_mm'],raw_peak_vm_MPa=d['maximum_raw_vm_MPa'],minimum_quality=d['min_quality']))
contrasts=[]
for i in range(len(rows)):
 for j in range(i+1,len(rows)):
  a,b=rows[i],rows[j];values=dict(energy=abs(b['independent_static_energy_Nmm']/a['independent_static_energy_Nmm']-1),compliance=abs(b['normal_load_compliance_mm_N']/a['normal_load_compliance_mm_N']-1),root_objective_relative_displacement=float(np.linalg.norm(np.array(b['root_relative_to_best_fit_actual_foot_mm'])-a['root_relative_to_best_fit_actual_foot_mm'])/np.linalg.norm(a['root_relative_to_best_fit_actual_foot_mm'])));contrasts.append(dict(h_mm=[a['h_mm'],b['h_mm']],relative_changes=values,original1percent=all(v<.01 for v in values.values()),raw_peak_stress_relative_change=abs(b['raw_peak_vm_MPa']/a['raw_peak_vm_MPa']-1)))
checks=dict(actual_same_candidate_all_levels=all(r['candidate']==ref(cp) for r in rows),independent_each_actual_field=all(all(r['checks'].values()) for r in rows),atleast_two_spatial_levels=len(rows)>=2,all_pairs_original1percent=all(c['original1percent'] for c in contrasts));dump(out/'summary.json',dict(status='ACTUAL_P1_FULL_INTEGRAL_FIELD_AUDITS_PASS_SPATIAL_MESH_FAIL_NOT_RELEASE' if checks['independent_each_actual_field'] and not checks['all_pairs_original1percent'] else 'ACTUAL_P1_FULL_INTEGRAL_FIELD_AND_LOCAL_MESH_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_FULL_INTEGRAL_FIELD_AUDIT_FAIL',candidate=ref(cp),producer=ref(out/'producer.py'),checks={k:bool(v) for k,v in checks.items()},rows=rows,mesh_contrasts=contrasts,accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,time_convergence=None,global_energy_closure=None,limitations=['Independentlinearstaticcontinuum audit ofactualnewentirepiece,prescribed100gverticaltest+ownweight/positivegivenfoottraction;NOT installedplatecontact orrealgrasp','1percentcheckedallpairs includingcoarsefinest;noadjacentonlyclaim/rawpeakstresscertification','Staticstrainenergy identity isNOTglobalenergy/dynamics;dt.1percent/realPETfriction/operating/protection/materialminimum/host/final3Fingerremain']))
print(json.dumps(dict(checks={k:bool(v) for k,v in checks.items()},contrasts=contrasts,field_audit_checks=[r['checks'] for r in rows])));raise SystemExit(0 if checks['independent_each_actual_field'] else 2)
