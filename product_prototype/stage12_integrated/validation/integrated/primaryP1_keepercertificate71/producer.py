"""Independent original24-row virtual-work separation on actual Root line contacts.
Certificates apply to declared finite lines at recorded poses, not all futurecontact.
"""
import sys,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,sha,dump
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');sp=ROOT/'validation/integrated/primaryP1_keeperhost71d/summary.json';d=json.loads(sp.read_text());assert sha(REPO/d['candidate']['path'])==d['candidate']['SHA256'];rows=[]
for r in d['rows']:
 cert=r['original24_Farkas_certificate'];y=np.array(cert['body_twists']);ext=np.zeros((4,6));ext[1:3,5]=r['torque_Nmm'];values=[];groups={}
 for c in r['contacts']:
  i,j=c['body_i'],c['body_j'];p=np.array(c['point_mm']);n=np.array(c['normal_on_i']);vi=y[i,:3]+np.cross(y[i,3:],p);vj=y[j,:3]+np.cross(y[j,3:],p);values.append(float(n@(vi-vj)));key=(c['label'],i,j,tuple(np.round(p[:2],10)),tuple(np.round(n,10)));groups.setdefault(key,[]).append(p)
 continuum=[]
 for key,ps in groups.items():
  ps=sorted(ps,key=lambda p:p[2]);lo,hi=ps[0],ps[-1];label,i,j,_,normal=key;n=np.array(normal);wv=[]
  for fraction in np.linspace(0,1,17):
   p=lo+fraction*(hi-lo);vi=y[i,:3]+np.cross(y[i,3:],p);vj=y[j,:3]+np.cross(y[j,3:],p);wv.append(float(n@(vi-vj)))
  continuum.append(dict(label=label,body_i=i,body_j=j,axial_interval_mm=[float(lo[2]),float(hi[2])],constant_XY_error=float(np.max(abs(np.array(ps)[:,:2]-lo[:2]))),minimum_separating_work=float(min(wv)),affine_extrema_at_endpoints=True))
 required=-float(np.sum(ext*y));hosterr=float(abs(y[-1]).max());bad=y.copy();bad[-1,0]+=.01;badhost=float(abs(bad[-1]).max());remain=np.array(r['planar_solution_original24_residual']);outofplane=remain[:,[2,3,4]];hit=r['interferences'];clear=max([hit['keeper_host_mm3'],hit['keeper_pin_mm3'],*hit['keeper_bolts_mm3'],*hit['bolts_host_mm3']])<=1e-8
 checks=dict(original24_necessary_work_negative=required<-1e-8,all_compressive_contact_work_nonnegative=min(values)>=-1e-9,full_host_port_zero_work=hosterr<1e-12,all_declared_line_continuum_nonnegative=all(c['minimum_separating_work']>=-1e-9 and c['constant_XY_error']<1e-9 for c in continuum),finite_BRep_line_witnesses=all(max(c['actual_body_i_distance_mm'],c['actual_body_j_distance_mm'])<1e-7 for c in r['contacts']),planar_discarded_row_failure=float(abs(outofplane).max())>1e-8,altered_host_twist_rejected=badhost>.009)
 rows.append(dict(signs=r['signs'],checks={k:bool(v) for k,v in checks.items()},required_contact_virtualwork=required,minimum_actual_contact_work=min(values),host_port_work_error=hosterr,entire_declared_line_checks=continuum,discarded_outofplane_original_row_maximum_N_Nmm=float(abs(outofplane).max()),actual_subassembly_pose_collision_free=clear,pose_collision_and_static_infeasibility_are_separate=True))
passed=all(all(r['checks'].values()) for r in rows);dump(out/'summary.json',dict(status='ACTUAL_ROOT_FINITE_LINE_24ROW_INFEASIBILITY_INDEPENDENTLY_CERTIFIED' if passed else 'ACTUAL_ROOT_FINITE_LINE_CERTIFICATE_AUDIT_FAIL',source=ref(sp),candidate=d['candidate'],producer=ref(out/'producer.py'),rows=rows,accepted83body_physical_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Nonnegativeworkonallgeneratingcontactlines andnegative requiredwork proveinfeasibility ofTHISdeclared unilateralstaticcone withfull24rows. They doNOTprove no feasible real3D tilted/deformed/preloaded/othercontactconfiguration exists.','Finiteaxial endpoints fromexacttopologicalvertexcoordinates avoid inflatedboundingbox endpoints. No physical/numerical tolerance relaxed.','Some directionstates also failactualhead/hostnonpenetration; only +,+ is collisionfree in declaredsubassembly, yet still full24infeasible. Entire83body nut/support/ground compatibility remainsunsolved.']));print(json.dumps(dict(checks=passed,rows=[{k:r[k] for k in ['signs','required_contact_virtualwork','discarded_outofplane_original_row_maximum_N_Nmm','actual_subassembly_pose_collision_free']} for r in rows])));raise SystemExit(0 if passed else 2)
