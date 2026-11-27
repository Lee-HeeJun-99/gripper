"""Actual P1 objective support contrast on saved field, all original rows.
No equilibrium solve unless independent current geometry checks justify one.
"""
import sys,json,shutil,time
import numpy as np
from scipy.spatial.transform import Rotation
from scipy.sparse import csr_matrix
from skfem import MeshTet
from baseline_registry import ROOT,REPO,ref,sha,dump
from primary_finite_port import ObjectiveRootPort,motor_pullback
from primary_corotated_support import CONTACTS
from primary_local_surface_support import LocalSurfaceSupport as Support

# Alias assigned below so saved implementation has a direct simple class name.
def main():
 start=time.monotonic();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');shutil.copyfile(ROOT/'scripts/primary_corotated_support.py',out/'implementation.py');shutil.copyfile(ROOT/'scripts/primary_local_surface_support.py',out/'local_surface.py');assert not(ROOT/'runtime/STOP').exists()
 src=ROOT/'validation/integrated/primaryP1_reclosure3/summary.json';s=json.loads(src.read_text());assert sha(REPO/s['field']['path'])==s['field']['SHA256'];a=dict(np.load(REPO/s['field']['path']));model=Support(a,s['elastic_bodies']);u=a['u_mm'];pressure=a['contact_force_N'];bf=a['bolt_force_N'];mo=model.mo
 # Verify exact pre-existing linear operator using independent element assembly.
 El,gl,linearrows=model.elastic(u,False);C=csr_matrix((a['contact_C_data'],a['contact_C_indices'],a['contact_C_indptr']),shape=tuple(a['contact_C_shape']));D=a['bolt_D'];Q=a['gauge_Q'];reconstructed=gl-a['applied_force_N']-C.T@pressure+D.T@bf+Q.T@a['gauge_dual'];linear_error=float(np.linalg.norm(reconstructed-a['stationarity_N']))
 E,ge,erows=model.elastic(u);gaps,gc,groups=model.contacts(u,pressure);ext,gb=model.connectors(u,bf);L=E-float(pressure@gaps)+float(bf@ext);g=ge-gc+gb
 def scalar(v):
  ee,_,_=model.elastic(v);gg,_,_=model.contacts(v,pressure);ex,_=model.connectors(v,bf);return ee-float(pressure@gg)+float(bf@ex)
 rng=np.random.default_rng(1417);directions=[]
 # Include all nodal coordinates and all Motor DOFs, plus concentrated owner
 # normal perturbations which specifically test the polar normal differential.
 for j in range(8):
  d=np.zeros(len(u))
  for nn,bb in model.bodies.items():
   pp=bb['X'];oo=bb['offset'];vv=np.sin(pp@rng.normal(size=(3,3))*.03+rng.normal(size=3));d[oo:oo+3*len(pp)]=vv.ravel()
  d[mo:mo+3]=rng.normal(size=3);d[mo+3:]=rng.normal(size=3)*.001;directions.append(d)
 for n in model.names:
  d=np.zeros(len(u));b=model.bodies[n];o=b['offset'];d[o:o+3*len(b['X'])]=np.sin(b['X']@rng.normal(size=(3,3))*.03).ravel();directions.append(d)
 fd=[]
 for d in directions:
  d/=max(np.max(abs(d)),1);h=1e-3;d1=(scalar(u+h*d)-scalar(u-h*d))/(2*h);d2=(scalar(u+h*.5*d)-scalar(u-h*.5*d))/h;estimate=(4*d2-d1)/3;analytic=float(g@d);fd.append(dict(analytic_N=analytic,Richardson_N=float(estimate),absolute_error_N=abs(analytic-estimate),central_h_error_N=abs(analytic-d1)))
 rigid=[]
 for theta,t in [([.0003,-.0002,.0004],[0,0,0]),([.3,-.2,.4],[1.2,-.4,3.1])]:
  R=Rotation.from_rotvec(theta).as_matrix();un=model.rigid(u,R,np.array(t));en,gn,_=model.elastic(un);gapn,gcn,_=model.contacts(un,pressure);exn,gbn=model.connectors(un,bf)
  rigid.append(dict(theta_rad=theta,translation_mm=t,elastic_energy_relative=abs(en-E)/max(E,1e-20),contact_gap_max_error_mm=float(np.max(abs(gapn-gaps))),bolt_extension_max_error_mm=float(np.max(abs(exn-ext))),elastic_wrench_N_Nm=model.wrench(un,gn).tolist(),contact_wrench_N_Nm=model.wrench(un,gcn).tolist(),bolt_wrench_N_Nm=model.wrench(un,gbn).tolist()))
 # Existing owner reference faces, actual current tetra-node triangles. A single
 # body polar normal is NOT silently accepted as the local deformed surface.
 facet_rows=[];normal_error_work=np.zeros(len(pressure));poses=model.poses(u)
 for row in model.groups:
  label=row['label'];owner=row['second'];b=model.bodies[owner];p=b['X'];m=MeshTet(p.T,b['t'].T);tri=m.facets[:,m.boundary_facets()].T;normal=np.array(row['n']);ax=int(np.argmax(abs(normal)));value=row['q'][0,ax];tri=tri[np.all(abs(p[tri,ax]-value)<1e-6,axis=1)];assert len(tri)
  x=p+model.body_u(u,owner);cross=np.cross(x[tri[:,1]]-x[tri[:,0]],x[tri[:,2]]-x[tri[:,0]]);sign=np.sign(cross@normal);cross*=sign[:,None];nw=np.zeros_like(p)
  for j in range(3):np.add.at(nw,tri[:,j],cross)
  nf=nw[row['b']];assert np.min(np.linalg.norm(nf,axis=1))>0;nf/=np.linalg.norm(nf,axis=1)[:,None];nr=poses[owner][0]@normal;xa=model.point(u,row['first'],row['q'],row.get('a'));xb=model.point(u,owner,row['q'],row['b']);dd=xa-xb;defect=np.einsum('ij,ij->i',dd,nf-nr);ids=row['ids'];normal_error_work[ids]=defect;angles=np.arctan2(np.linalg.norm(np.cross(nf,nr),axis=1),nf@nr)
  facet_rows.append(dict(label=label,owner=owner,rows=len(ids),max_normal_angle_rad=float(angles.max()),max_gap_change_mm=float(np.max(abs(defect))),pressure_weighted_gap_change_Nmm=float(pressure[ids]@defect),max_local_normal_force_change_N=float(np.max(pressure[ids]*np.linalg.norm(nf-nr,axis=1)))))
 # Recover source hardware and exact Base top-face port area, avoiding changed
 # load distribution/unknown hardware attachment being hidden as local stress.
 oldsrc=ROOT/'validation/integrated/primaryP1_front_h5_2/summary.json';old=json.loads(oldsrc.read_text());b=model.bodies['TEST_BASE'];p=b['X'];m=MeshTet(p.T,b['t'].T);tri=m.facets[:,m.boundary_facets()].T;tri=tri[np.all(abs(p[tri,2]-66)<1e-5,axis=1)];xy=p[tri].mean(1)[:,:2];centers=np.array([[-44,-30],[-44,10],[86,-30],[86,10]]);tri=tri[np.min(np.linalg.norm(xy[:,None,:]-centers[None,:,:],axis=2),axis=1)>4.7];area=np.linalg.norm(np.cross(p[tri[:,1]]-p[tri[:,0]],p[tri[:,2]]-p[tri[:,0]]),axis=1)/2;w=np.zeros(len(p))
 for j in range(3):np.add.at(w,tri[:,j],area/3)
 ids=np.flatnonzero(w);base=ObjectiveRootPort(p[ids],w[ids]);bu=model.body_u(u,'TEST_BASE')[ids];R,c,_=base.pose(bu);hardware=[];HW=np.zeros(6)
 for n,hp in old['hardware_actual_mass_geometry'].items():
  mass=hp['volume_mm3']*7900e-9;q=base.positions(bu,np.array(hp['centroid_mm'])[None,:]*.001)[0];ff=np.array([0,0,-mass*9.80665]);HW+=np.r_[ff,np.cross(q,ff)];hardware.append(dict(part=n,mass_kg=mass,position_m=q.tolist()))
 f=np.zeros(len(u));gravity=[]
 for n,b in model.bodies.items():
  vol=b['V'];mass=np.zeros(len(b['X']))
  for j in range(4):np.add.at(mass,b['t'][:,j],vol/4)
  mass*=float(a[n+'_rho_kg_m3'])*1e-9;ff=np.zeros_like(b['X']);ff[:,2]=-mass*9.80665;model.scatter(f,n,ff);q=(b['X']+model.body_u(u,n))*.001;gravity.append(dict(part=n,mass_kg=float(mass.sum()),current_wrench_N_Nm=np.r_[ff.sum(0),np.cross(q,ff).sum(0)].tolist()))
 stsrc=ROOT/'validation/integrated/primaryP1_objective_port1/summary.json';st=json.loads(stsrc.read_text());state=json.loads((REPO/st['state']['path']).read_text());port=np.load(REPO/st['port']['path']);b=model.bodies['F0_ROOT_BACK'];ff=np.zeros_like(b['X']);ff[port['root_nodes']]=port['root_force_N'];model.scatter(f,'F0_ROOT_BACK',ff);f[mo:mo+6]=motor_pullback(u[mo:mo+6],np.array(state['Motor_origin_wrench_N_Nm']));ff=np.zeros_like(p);ff[ids]=base.pullback(bu,HW);model.scatter(f,'TEST_BASE',ff)
 physical_before_Base=model.wrench(u,f);BaseW=-physical_before_Base;ff=np.zeros_like(p);ff[ids]=base.pullback(bu,BaseW);model.scatter(f,'TEST_BASE',ff);res=g-f;force_norm=float(np.linalg.norm(res)/max(np.linalg.norm(f),1));W=model.wrench(u,res)
 wrenches=dict(elastic=model.wrench(u,ge).tolist(),contact=model.wrench(u,gc).tolist(),connector=model.wrench(u,gb).tolist(),external=model.wrench(u,f).tolist(),residual=W.tolist())
 checks=dict(original_operator_reproduced=linear_error<1e-8,all2169rows=len(gaps)==2169,all14branches=len(ext)==14,virtual_work=max(r['absolute_error_N'] for r in fd)<1e-8,current_internal_force=max(np.linalg.norm(wrenches[k][:3]) for k in ('elastic','contact','connector'))<1e-8,current_internal_moment=max(np.linalg.norm(wrenches[k][3:]) for k in ('elastic','contact','connector'))<1e-10,current_external_force=np.linalg.norm(wrenches['external'][:3])<1e-8,current_external_moment=np.linalg.norm(wrenches['external'][3:])<1e-10,finite_rigid_contact=max(r['contact_gap_max_error_mm'] for r in rigid)<1e-8,finite_rigid_bolt=max(r['bolt_extension_max_error_mm'] for r in rigid)<1e-8,finite_rigid_elastic_energy=max(r['elastic_energy_relative'] for r in rigid)<1e-8,Base_area_unchanged=abs(area.sum()/old['external_FrameGround_port']['area_mm2']-1)<1e-12)
 # Geometry eligibility uses existing force/residual tolerance, not a new relaxed
 # angle criterion. Changing local owner normals must not alter row traction by
 # >1e-8N. Otherwise do NOT launch a support contact update.
 max_normal_force=max(r['max_local_normal_force_change_N'] for r in facet_rows);coverage=model.finite_coverage(u,pressure);unsupported=sum(len(r['outside_active_rows']) for r in coverage);eligibility=all(checks.values()) and unsupported==0
 np.savez_compressed(out/'objective_field.npz',u_mm=u,elastic_force_N=ge,contact_force_pullback_N=gc,bolt_force_pullback_N=gb,applied_force_N=f,unsolved_residual_N=res,objective_gaps_mm=gaps,objective_extensions_mm=ext,local_facet_gap_change_mm=normal_error_work)
 result=dict(status='ACTUAL_P1_LOCAL_SURFACE_COROTATED_CONTRAST_VALIDATED_NOT_EQUILIBRIUM' if all(checks.values()) else 'ACTUAL_P1_OBJECTIVE_SUPPORT_CONTRAST_CHECK_FAIL',candidate=s['candidate'],source=ref(src),source_field=s['field'],upstream=ref(stsrc),hardware_source=ref(oldsrc),producer=ref(out/'producer.py'),implementation=ref(out/'implementation.py'),output=ref(out/'objective_field.npz'),checks={k:bool(v) for k,v in checks.items()},DOF=len(u),contact_rows=len(gaps),connectors=len(ext),elastic_bodies=model.names,linear_operator_reconstruction_error_N=linear_error,linear_elastic_energy_Nmm=El,corotated_elastic_energy_Nmm=E,elastic_force_change_norm_N=float(np.linalg.norm(ge-gl)),linear_vs_corotated_elastic_energy_relative=abs(E-El)/El,virtual_work=fd,rigid_motion=rigid,current_wrenches_N_Nm=wrenches,per_body=erows,contact_groups=groups,local_facet_normal_comparison=facet_rows,maximum_wholebody_vs_local_normal_force_change_N=max_normal_force,finite_surface_coverage=coverage,unsupported_active_rows=unsupported,local_surface_implementation=ref(out/'local_surface.py'),differentiation='Wholefield smooth13directions, Richardson4thorder h=.001mm with unchanged1e-8N; local1 h=.0001mm roundingFAIL preserved; original highfrequency-sliver-perturbation truncation FAIL preserved in contrast1.',force_criterion_N=1e-8,moment_criterion_Nm=1e-10,original_to_objective_gap_max_mm=float(np.max(abs(gaps-a['contact_gaps_mm']))),original_to_objective_extension_max_mm=float(np.max(abs(ext-D@u))),objective_min_gap_mm=float(gaps.min()),objective_complementarity_Nmm=float(np.max(abs(gaps*pressure))),old_force_branch_constitutive_error_N=float(np.max(abs(bf-np.maximum(a['bolt_k_N_mm']*ext,0)))),unsolved_stationarity_relative=force_norm,elastic_gravity=gravity,hardware_positions=hardware,hardware_wrench_N_Nm=HW.tolist(),physical_wrench_before_Base_N_Nm=physical_before_Base.tolist(),physical_current_Base_wrench_N_Nm=BaseW.tolist(),Base_port_area_mm2=float(area.sum()),Base_rule='Reaction from independently enumerated current physical upstream/elastic/hardware loads; transpose differential of actual Base area-weighted polar pose. No subtraction of reference-null imbalance or unsolved residual.',contact_update_eligible=bool(eligibility),contact_update_attempted=False,new_equilibrium_solved=False,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Same original78part CAD and tetra/2169rows/14branches. Biot isotropic corotation is an objective constitutive contrast with original conditional moduli, not source material validation.','Current contact area normals use actual original owner triangles; axial directions still wholebody polar approximations. Wholebody normal approximation rejected, replaced by actual owner area-normal/differential. Finite original surface projection required before support solve; no geometry or mesh criterion relaxed.','Hardware gravity remains transported to Base port as in original model, now with objective current positions and couples. It is NOT local hardware attachment/bearing stress. Base reaction is mathematical, not an actual bench anchor.','Saved field under new operators is NOT equilibrium. No updated stress, convergence, time, global stored energy, finite wire, physical retention, source bearing/thread/protector or full3Finger qualification.'])
 dump(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('virtual_work','hardware_positions','limitations','contact_groups','local_facet_normal_comparison')}));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
