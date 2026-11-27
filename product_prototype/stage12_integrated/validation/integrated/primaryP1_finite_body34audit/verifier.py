"""Independent direct-element and positive-Duffy quadrature audit of actual P1.
No import of producer, skfem assembler, solve, or Kelvin gradient.
"""
import sys,json,time,shutil
import numpy as np
from numpy.polynomial.legendre import leggauss
from baseline_registry import ROOT,REPO,ref,sha,dump,S1
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.TopAbs import TopAbs_OUT
from OCP.gp import gp_Pnt

def displacement(x,c,f,E,nu):
 r=x[...,None,:]-c;R=np.sqrt(np.sum(r*r,axis=-1));dot=np.sum(r*f,axis=-1);mu=E/(2*(1+nu));return ((3-4*nu)*f/R[...,None]+dot[...,None]*r/R[...,None]**3)/(16*np.pi*mu*(1-nu))

def independent_eps(x,c,f,E,nu):
 # Complex-step derivative of independently written analytic displacement.
 grads=[]
 for j in range(3):
  z=x.astype(complex);z[...,j]+=1e-24j;grads.append(displacement(z,c,f,E,nu).imag/1e-24)
 g=np.stack(grads,axis=-1);return (g+g.swapaxes(-1,-2))/2

def sigma(e,E,nu):
 tr=np.einsum('...ii->...',e);mu=E/(2*(1+nu));la=E*nu/((1+nu)*(1-2*nu));return 2*mu*e+la*tr[...,None,None]*np.eye(3)

def duffy(n):
 x,w=leggauss(n);x=(x+1)/2;w=w/2;bc=[];weights=[]
 for i,u in enumerate(x):
  for j,v in enumerate(x):
   for k,z in enumerate(x):bc.append([(1-u)*(1-v)*(1-z),u,(1-u)*v,(1-u)*(1-v)*z]);weights.append(w[i]*w[j]*w[k]*(1-u)**2*(1-v))
 return np.array(bc),np.array(weights)

def integrate(a,bc,w,E,nu,alpha=None):
 p=a['points_mm'];t=a['tetra'];dx=p[t[:,1:]]-p[t[:,0,None]];inv=np.linalg.inv(dx);V=abs(np.linalg.det(dx))/6;gr=np.concatenate([-inv.sum(2)[:,None,:],inv.transpose(0,2,1)],axis=1);M=len(a['centers_mm']);G=np.zeros_like(a['G']);H=np.zeros((M,M))
 for first in range(0,len(t),160):
  assert not(ROOT/'runtime/STOP').exists();sl=slice(first,min(first+160,len(t)));tt=t[sl];pos=np.einsum('qa,tai->tqi',bc,p[tt]);eps=independent_eps(pos,a['centers_mm'],a['directions'],E,nu);s=sigma(eps,E,nu);weights=V[sl,None]*6*w;H+=np.einsum('tqkij,tqlij,tq->kl',eps,s,weights);intstress=np.einsum('tqmij,tq->tmij',s,weights);force=np.einsum('tmij,taj->taim',intstress,gr[sl])
  for j in range(4):
   for axis in range(3):np.add.at(G,3*tt[:,j]+axis,force[:,j,axis,:])
 return G,H

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');start=time.monotonic();docs=[json.loads((ROOT/'validation/integrated'/n/'summary.json').read_text()) for n in sys.argv[2:]];sources=[ref(ROOT/'validation/integrated'/n/'summary.json') for n in sys.argv[2:]];cp=docs[0]['candidate'];cad=json.loads((REPO/cp['path']).read_text());assert all(sha(REPO[v['path']])==v['SHA256'] for v in [])
 for v in cad['part_references'].values():assert sha(REPO/v['path'])==v['SHA256']
 dump(out/'inputs.json',dict(candidate=cp,sources=sources,verifier=ref(out/'verifier.py'),methods='Direct constant-strain element forces/energy; analytic displacement complex-step derivative, positive Duffy tensor quadrature independent of Keast producer; direct boundary-load reconstruction; actual BRep exterior classification.'))
 results=[];comparisons=[]
 # Audit saved fine body field with same Keast nodes (gradient/assembly independent), then separate Duffy3/5 integration.
 fine=docs[-1]
 from skfem.quadrature import get_quadrature_tet
 for row in fine['results']:
  a=np.load(REPO/row['fields']['path']);p=a['points_mm'];t=a['tetra'];E=row['conditional_E_MPa'];nu=row['conditional_nu'];M=a['F'].shape[1];u=a['VFE'].reshape(len(p),3,M);dx=p[t[:,1:]]-p[t[:,0,None]];inv=np.linalg.inv(dx);V=abs(np.linalg.det(dx))/6;grad=np.concatenate([-inv.sum(2)[:,None,:],inv.transpose(0,2,1)],axis=1);du=u[t[:,1:]]-u[t[:,0,None]];g=np.einsum('tij,tjkm->tkim',inv,du).transpose(0,3,1,2);eps=(g+g.swapaxes(2,3))/2;st=sigma(eps,E,nu);internal=np.zeros_like(a['F']);ef=V[:,None,None,None]*np.einsum('tmij,taj->taim',st,grad)
  for j in range(4):
   for axis in range(3):np.add.at(internal,3*t[:,j]+axis,ef[:,j,axis,:])
  journals=json.loads((REPO/row['quadrature']['path']).read_text());F=np.zeros_like(a['F']);L=np.zeros_like(a['L']);W=np.zeros((6,M));baryerr=0.;minb=1.
  for q in journals:
   ids=q['nodes'];bc=np.array(q['barycentric']);pt=np.array(q['point_mm']);f=np.array(q['force_N']);j=q['port'];baryerr=max(baryerr,float(abs(bc@p[ids]-pt).max()));minb=min(minb,float(bc.min()));W[:3,j]+=f;W[3:,j]+=np.cross(pt,f)
   for k,node in enumerate(ids):F[3*node:3*node+3,j]+=bc[k]*f
   rr=pt-np.average(p,weights=np.bincount(t.ravel(),weights=np.repeat(V/4,4),minlength=len(p)),axis=0)
   wt=np.zeros(len(p))
   # Rigid field interpolation is exactly affine; use nodal R at existing barycentric point.
   rb=sum(bc[k]*a['R'][3*node:3*node+3] for k,node in enumerate(ids));uh=displacement(pt[None],a['centers_mm'],a['directions'],E,nu)[0].T-rb@a['gauge'];L[:,j]+=uh.T@f
  x,w=get_quadrature_tet(row['quadrature_order']);G,H=integrate(a,np.vstack([1-x.sum(0),x]).T,w,E,nu);alpha=a['alpha'];C=a['compliance'];v=a['VFE'];same_force=float(abs(internal+G@alpha-F).max());same_enrichment=float(abs(G.T@v+H@alpha-L).max());fe_energy=np.einsum('tmij,tnij,t->mn',eps,st,V);energy=fe_energy+v.T@G@alpha+alpha.T@G.T@v+alpha.T@H@alpha;Lwork=F.T@v+L.T@alpha
  shape=read(REPO/row['part_reference']['path']);outside=[]
  for pt in a['centers_mm']:outside.append(BRepClass3d_SolidClassifier(shape,gp_Pnt(*pt),1e-9).State()==TopAbs_OUT)
  indep=[]
  for n in [3,5]:
   bc,w=duffy(n);Gd,Hd=integrate(a,bc,w,E,nu);res=max(abs(internal+Gd@alpha-F).max(),abs(Gd.T@v+Hd@alpha-L).max());en=fe_energy+v.T@Gd@alpha+alpha.T@Gd.T@v+alpha.T@Hd@alpha;indep.append(dict(positive_Duffy_order=n,points_per_tetra=n**3,weak_equation_max_residual_N=float(res),strain_work_relative_change=float(np.linalg.norm(en-C)/np.linalg.norm(C)),analytic_G_relative_change=float(np.linalg.norm(Gd-G)/np.linalg.norm(G)),analytic_H_relative_change=float(np.linalg.norm(Hd-H)/np.linalg.norm(H)),original1percent_work_pass=bool(np.linalg.norm(en-C)/np.linalg.norm(C)<.01)))
  results.append(dict(part=row['part'],same_rule_independent_internal_force_error_N=same_force,same_rule_independent_enrichment_force_error_N=same_enrichment,boundary_load_reconstruction_error_N=float(abs(F-a['F']).max()),boundary_analytic_load_reconstruction_error=float(abs(L-a['L']).max()),barycentric_position_error_mm=baryerr,min_barycentric=minb,source_wrench_error_N_Nmm=float(abs(W).max()),independent_work_identity_relative=float(np.linalg.norm(energy-Lwork)/np.linalg.norm(C)),independent_stored_C_relative=float(np.linalg.norm(energy-C)/np.linalg.norm(C)),all_analytic_sources_actual_BRep_OUT=all(outside),independent_quadrature=indep,free_end_raw_traction_MPa_per_unit_N=row['free_end_raw_traction_max_MPa_per_unit_N'],free_surface_pointwise_qualified=False))
  print(json.dumps(results[-1]),flush=True)
 for i in range(len(docs)-1):
  d,e=docs[i:i+2]
  for a,b in zip(d['results'],e['results']):
   A=np.array(a['compliance_enriched_mm_N']);B=np.array(b['compliance_enriched_mm_N']);rel=float(np.linalg.norm(A-B)/np.linalg.norm(B));same=a['nodes']==b['nodes'] and a['tetra']==b['tetra'];comparisons.append(dict(part=a['part'],sources=sources[i:i+2],variable='integration' if same else 'mixed_bulk_surface_mesh',relative_compliance_change=rel,original_1percent_pass=rel<.01,full_contact_convergence=False))
 checks=dict(independent_element_equations=all(max(r['same_rule_independent_internal_force_error_N'],r['same_rule_independent_enrichment_force_error_N'])<1e-8 for r in results),independent_energy=all(max(r['independent_work_identity_relative'],r['independent_stored_C_relative'])<1e-8 for r in results),independent_finite_traction_load=all(r['boundary_load_reconstruction_error_N']<1e-10 and r['boundary_analytic_load_reconstruction_error']<1e-10 and r['barycentric_position_error_mm']<1e-9 and r['min_barycentric']>-1e-10 and r['source_wrench_error_N_Nmm']<1e-8 for r in results),analytic_enrichment_singularities_OUT_actual_BRep=all(r['all_analytic_sources_actual_BRep_OUT'] for r in results))
 dump(out/'summary.json',dict(status='ACTUAL_P1_FINITE_BODY_INDEPENDENT_AUDIT' if all(checks.values()) else 'ACTUAL_P1_FINITE_BODY_INDEPENDENT_AUDIT_FAIL',candidate=cp,inputs=ref(out/'inputs.json'),checks=checks,results=results,comparisons=comparisons,newly_qualified_system_gate_ids=[],accepted_product_equilibria=0,whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Shared-rule element/gradient audit verifies implementation; independent Duffy quadrature and mixed mesh changes remain separate physical numerical blockers.','Finite-body weak natural boundary treatment is NOT pointwise traction satisfaction; raw finite-end stress remains nonzero. No contact or product equilibrium, full clamp/source coupling, 100g operating demand, material minimum, strength or global energy approval.']))
if __name__=='__main__':main()
