"""Existing P1 tetrahedral elasticity on entire new monolithic product support.
Self-equilibrated normal Neumann100g vertical test plus own-weight reference.
No physical fixed nodes or host constraints; six rigid gauges restored after solve.
"""
import json,sys,shutil,time,gc
import numpy as np
from scipy import sparse
from scipy.linalg import qr
from scipy.sparse.linalg import splu
from skfem import MeshTet,Basis,ElementVector,ElementTetP1,asm
from skfem.models.elasticity import linear_elasticity,lame_parameters
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
from primary_finite_body34 import meshpart
from primary_anchor_contact38 import common_faces,planar_triangles,tri_shape,surface_moment,bary
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common

def main():
 h=float(sys.argv[1]);tag=sys.argv[2];out=ROOT/'validation/integrated'/tag;out.mkdir();shutil.copyfile(__file__,out/'producer.py');start=time.monotonic();cp=ROOT/'cad/exports/primaryP1_integral55b/summary.json';cad=json.loads(cp.read_text());step=REPO/cad['part_references']['BENCH_SUPPORT']['path'];assert sha(step)==cad['part_references']['BENCH_SUPPORT']['SHA256'];assert not(ROOT/'runtime/STOP').exists()
 dump(out/'inputs.json',dict(candidate=ref(cp),STEP=ref(step),producer=ref(out/'producer.py'),dependencies=[ref(ROOT/'scripts'/n) for n in ['primary_finite_body34.py','primary_anchor_contact38.py']],h_mm=h,curvature_points=12,conditional_material=dict(E_MPa=68900,nu=.33,rho_kg_m3=2700,source=ref(ROOT/'models/materials/primary_joint_sources1/reviewed.json'),strength_minimum_MPa=None),load='Prescribed physical downward100g vertical test on3actual ANCHOR_NUT seat footprints plus distributedsupportownweight;NOT actual100ggrasp/tendon demand',BC='Bottom actual foot normal-affine pressure balances specified Neumann test;positivepressure verified,NOT solved platecontact/hostreaction. Nophysicalfixation; all displacement DOFs retained.',criteria=dict(force_N=1e-8,moment_Nm=1e-10,free_residual_N=1e-8,energy_relative=1e-8,volume_fraction=.01,response_mesh_fraction=.01)))
 p,t,tri,cadV=meshpart(step,h,12);N=3*len(p);print(json.dumps(dict(stage='mesh',nodes=len(p),tetra=len(t))),flush=True);det=np.linalg.det(np.transpose(p[t[:,1:]]-p[t[:,0,None]],(0,2,1)));vol=abs(det)/6;lump=np.zeros(len(p))
 for j in range(4):np.add.at(lump,t[:,j],vol/4)
 center=np.average(p,weights=lump,axis=0);m=MeshTet(p.T,t.T);el=ElementVector(ElementTetP1());la,mu=lame_parameters(68900,.33);K=sparse.csr_matrix((N,N))
 for first in range(0,len(t),8000):
  assert not(ROOT/'runtime/STOP').exists();K+=asm(linear_elasticity(la,mu),Basis(m,el,intorder=2,elements=np.arange(first,min(first+8000,len(t)))))
 body=dict(p=p,t=t,tri=tri);support=read(step);shapes={n:read(REPO/cad['part_references'][n]['path']) for n in ['ANCHOR_NUT_0','ANCHOR_NUT_1','ANCHOR_NUT_2','EXTERNAL_BENCH_PLATE']};ports=[];journal=[]
 def integrate_trace(face,z,label):
  qs=[];bb=np.array(bounds(face));candidate=planar_triangles(body,2,z)
  for nodes,pts in candidate:
   if any(pts[:,k].max()<bb[k]-1e-8 or pts[:,k].min()>bb[k+3]+1e-8 for k in [0,1]):continue
   cs=BRepAlgoAPI_Common(face,tri_shape(pts)).Shape();ar,q,cov=surface_moment(cs)
   if ar<1e-10:continue
   bc=bary(pts,q);pinv=np.linalg.pinv((pts[1:]-pts[0]).T);grad=np.vstack([-pinv.sum(0),pinv]);assert bc.min()>-1e-7
   qs.append(dict(nodes=nodes.tolist(),bc=bc.tolist(),point=q.tolist(),area=ar,cov=cov.tolist(),grad=grad.tolist()))
  assert qs,(label,'empty trace');area=sum(q['area'] for q in qs);ca,cq,cc=surface_moment(face);r=dict(label=label,quadrature=qs,integrated_area_mm2=area,actual_CAD_area_mm2=ca,area_relative_error=abs(area/ca-1));ports.append(r);return qs
 F=np.zeros((len(p),3));F[:,2]=-lump*2700e-9*9.80665;ownF=F.copy();loadqs=[]
 for i in range(3):
  ff=common_faces(support,shapes[f'ANCHOR_NUT_{i}'],2,74);assert len(ff)==1;qs=integrate_trace(ff[0],74,f'upper_nut{i}');area=sum(q['area'] for q in qs)
  for q in qs:
   force=-.980665/3*q['area']/area;loadqs.append(q)
   for node,bc in zip(q['nodes'],q['bc']):F[node,2]+=bc*force
 before=F.copy();moment=np.cross(p-center,F).sum(0);target=np.array([-F[:,2].sum(),-(p[:,0]*F[:,2]).sum(),-(p[:,1]*F[:,2]).sum()]);ff=common_faces(support,shapes['EXTERNAL_BENCH_PLATE'],2,-130);assert len(ff)==1;qs=integrate_trace(ff[0],-130,'actual_lower_foot');M=np.zeros((3,3))
 for q in qs:
  r=np.r_[1,np.array(q['point'])[:2]];M+=q['area']*np.outer(r,r);M[1:,1:]+=np.array(q['cov'])[:2,:2]
 coeff=np.linalg.solve(M,target)
 for q in qs:
  r=np.r_[1,np.array(q['point'])[:2]];pressure=coeff@r;cov=np.array(q['cov']);grad=np.array(q['grad'])
  for a,node in enumerate(q['nodes']):F[node,2]+=q['area']*q['bc'][a]*pressure+grad[a,:2]@cov[:2,:2]@coeff[1:]
 bb=np.array(bounds(ff[0]));pmin=min(coeff@np.array([1,x,y]) for x in [bb[0],bb[3]] for y in [bb[1],bb[4]])
 force_balance=F.sum(0);moment_balance=np.cross(p-center,F).sum(0)*.001;R=np.zeros((N,6))
 for j,e in enumerate(np.eye(3)):R[:,j]=np.broadcast_to(e,p.shape).ravel();R[:,j+3]=(np.cross(e,p-center)/100).ravel()
 wt=lump/lump.sum();Q=np.zeros((6,N))
 for j in range(6):Q[j]=(R[:,j].reshape(-1,3)*wt[:,None]).ravel()
 # Algebraic quotient only; all originalDOFs restored and ORIGINAL residual checked.
 _,_,pivot=qr(R.T,mode='economic',pivoting=True);anchor=np.sort(pivot[:6]);free=np.setdiff1d(np.arange(N),anchor);fac=splu((K[free][:,free]/68900).tocsc(),permc_spec='MMD_AT_PLUS_A');f=F.ravel();u=np.zeros(N);u[free]=fac.solve(f[free]/68900);u-=R@np.linalg.solve(Q@R,Q@u);residual=K@u-f;energy=.5*float(u@K@u);work=.5*float(f@u);u3=u.reshape(-1,3);portwork=float((before-ownF).ravel()@u);C=(f@u)/float(-before[:,2].sum())**2
 # Independent element gradient/stress; full actual continuum, rawsharp peaks unqualified.
 dx=p[t[:,1:]]-p[t[:,0,None]];iv=np.linalg.inv(dx);grad=np.concatenate([-iv.sum(2)[:,None,:],iv.transpose(0,2,1)],axis=1);G=np.einsum('tai,taj->tij',u3[t],grad);eps=(G+G.transpose(0,2,1))/2;sig=2*mu*eps+la*np.trace(eps,axis1=1,axis2=2)[:,None,None]*np.eye(3);dev=sig-np.trace(sig,axis1=1,axis2=2)[:,None,None]*np.eye(3)/3;vm=np.sqrt(1.5*np.sum(dev*dev,axis=(1,2)));newdet=np.linalg.det(np.transpose((p+u3)[t[:,1:]]-(p+u3)[t[:,0,None]],(0,2,1)));ratio=newdet/det;edge2=sum(np.sum((p[t[:,i]]-p[t[:,j]])**2,axis=1) for i in range(4) for j in range(i));quality=12*(3*vol)**(2/3)/edge2
 element_energy=float(np.sum(.5*np.einsum('tij,tij->t',eps,sig)*vol));checks=dict(alloriginalDOFs_restored=True,one_actual_CAD_solid=True,no_physical_fixed_nodes=True,positive_bottom_pressure=pmin>0,force=float(np.linalg.norm(force_balance))<1e-8,moment=float(np.linalg.norm(moment_balance))<1e-10,original_all_DOF_residual=float(abs(residual).max())<1e-8,static_energy=abs(energy-work)/energy<1e-8,independent_element_energy=abs(element_energy/energy-1)<1e-8,volume=abs(vol.sum()/cadV-1)<.01,finite_positive_tetra=bool(np.isfinite(u).all() and ratio.min()>0),actual_trace_area=max(r['area_relative_error'] for r in ports)<.01,quality=float(quality.min())>.01)
 np.savez_compressed(out/'field.npz',points_mm=p,tetra=t,displacement_mm=u3,load_N=F,ownweight_N=ownF,residual_N=residual,vm_MPa=vm,signed_volume_ratio=ratio);dump(out/'port_journal.json',ports)
 result=dict(status='ACTUAL_P1_FULL_INTEGRAL_SUPPORT_NORMAL_NEUMANN_REFERENCE_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_FULL_INTEGRAL_SUPPORT_NORMAL_NEUMANN_REFERENCE_FAIL',candidate=ref(cp),STEP=ref(step),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),field=ref(out/'field.npz'),port_journal=ref(out/'port_journal.json'),checks={k:bool(v) for k,v in checks.items()},nodes=len(p),tetra=len(t),DOF=N,physical_fixed_DOF=0,algebraic_gauge_DOF=6,all_displacement_DOF_restored=True,h_mm=h,material_E_MPa=68900,material_density_kg_m3=2700,material_minimum_MPa=None,mesh_volume_mm3=float(vol.sum()),CAD_volume_mm3=cadV,volume_relative_error=abs(vol.sum()/cadV-1),conditional_CAD_mass_kg=cadV*2700e-9,conditional_mesh_mass_kg=float(vol.sum()*2700e-9),conditional_mesh_COM_mm=center.tolist(),test_payload_downward_N=.980665,total_downward_including_ownweight_N=float(-before[:,2].sum()),bottom_affine_pressure_coefficients_MPa=coeff.tolist(),minimum_bottom_pressure_bound_MPa=pmin,force_balance_N=force_balance.tolist(),moment_balance_Nm=moment_balance.tolist(),original_all_DOF_residual_N=float(abs(residual).max()),static_strain_energy_Nmm=energy,independent_element_energy_Nmm=element_energy,external_halfwork_Nmm=work,normal_load_compliance_mm_N=C,maximum_displacement_mm=float(np.linalg.norm(u3,axis=1).max()),maximum_raw_vm_MPa=float(vm.max()),min_quality=float(quality.min()),minimum_signed_volume_ratio=float(ratio.min()),elapsed_s=time.monotonic()-start,accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],actual_100g_grasp_operating_field=None,whole_system_release=False,limitations=['Prescribed vertical100g testpayload is NOT100ggrasp/tendontension/normalforce;other retained111part selfweights not applied','Actualfullsupportcontinuum and positivegivenbottomnormalpressure;NOT coupledplatecontact/complementarity/benchmarkhostfixation. No physicalrotation/translationfixed','69000historicalvs68900here source typical elasticreference;not materialstrength/processcertificate','Sharpnotches/rawstress andmesh convergence notstrengthcertification;time/globalenergy/final3Finger/all22stillunqualified'])
 dump(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ['limitations','checks']}),flush=True);print(json.dumps(checks),flush=True);raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
