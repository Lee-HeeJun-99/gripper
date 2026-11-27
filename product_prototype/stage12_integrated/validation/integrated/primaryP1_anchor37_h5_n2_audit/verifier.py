"""Independent constant-strain force/work and actual boundary-trace audit.
Imports no producer, FEM assembler/solver, optimizer or projected gauge operator.
"""
import sys,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,sha,dump

def wrench(p,f):return np.r_[f,np.cross(p,f)]
def h(p):
 mat=np.zeros((6,3));mat[:3]=np.eye(3)
 for i,e in enumerate(np.eye(3)):mat[3:,i]=np.cross(p,e)
 return mat

def internal(points,tetra,U,E,nu):
 # Independent affine-polynomial inverse gives physical basis gradients.
 force=np.zeros_like(U);energy=np.zeros(U.shape[1]);mu=E/(2*(1+nu));la=E*nu/((1+nu)*(1-2*nu))
 for first in range(0,len(tetra),2000):
  assert not(ROOT/'runtime/STOP').exists();tt=tetra[first:first+2000];x=points[tt];M=np.concatenate([np.ones((len(tt),4,1)),x],axis=2);iv=np.linalg.inv(M);grad=iv[:,1:,:].transpose(0,2,1);V=np.abs(np.linalg.det(x[:,1:]-x[:,0,None]))/6;u=U.reshape(len(points),3,-1)[tt];du=np.einsum('taim,taj->tmij',u,grad);eps=(du+du.swapaxes(-1,-2))/2;tr=np.trace(eps,axis1=-2,axis2=-1);stress=2*mu*eps+la*tr[...,None,None]*np.eye(3);ef=np.einsum('tmij,taj,t->taim',stress,grad,V)
  for a in range(4):
   for k in range(3):np.add.at(force,3*tt[:,a]+k,ef[:,a,k,:])
  energy+=np.einsum('tmij,tmij,t->m',eps,stress,V)
 return force,energy

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');src=ROOT/'validation/integrated'/sys.argv[2];doc=json.loads((src/'summary.json').read_text());geo=json.loads((REPO/doc['geometry']['path']).read_text());inp=json.loads((REPO/doc['inputs']['path']).read_text());cad=json.loads((REPO/doc['candidate']['path']).read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values());nc=doc['contact_variables'];ops=np.load(REPO/doc['operators']['path']);rows=[];newU=[];newF=[];fullenergy=[];maxworldforce=0.;maxworldmoment=0.;loadsverified=[]
 for k,body in enumerate(doc['body_results']):
  a=np.load(REPO/body['fields']['path']);points=a['points_mm'];F=np.zeros_like(a['F']);reconstruction=0.;minimum=1.;patchW=[]
  for j,p in enumerate(geo['body_quadrature'][k]):
   area=sum(q['area_mm2'] for q in p['quadrature']);assert abs(area-p['integrated_area_mm2'])<1e-8;w=np.zeros(6)
   for q in p['quadrature']:
    nodes=q['nodes'];bc=np.array(q['barycentric']);x=np.array(q['point_mm']);f=np.array(p['normalized_direction'])*q['area_mm2']/area;reconstruction=max(reconstruction,float(abs(bc@points[nodes]-x).max()));minimum=min(minimum,float(bc.min()));w+=wrench(x,f)
    for i,node in enumerate(nodes):F[3*node:3*node+3,j]+=bc[i]*f
   patchW.append(w)
  qs=geo['source_quadrature'][k];M=np.zeros((6,6))
  for q in qs:
   W=h(np.array(q['point_mm']));M+=q['weight']*W@W.T
  for q in qs:
   W=h(np.array(q['point_mm']));f=q['weight']*np.linalg.solve(M,W).T
   for i,node in enumerate(q['nodes']):F[3*node:3*node+3,nc:]+=q['barycentric'][i]*f
  U=a['U'];fi,energy=internal(points,a['tetra'],U,body['conditional_E_MPa'],body['conditional_nu']);newF.append(F);newU.append(U);fullenergy.append(energy);C=F.T@U;rows.append(dict(part=body['part'],load_reconstruction_max_N=float(abs(F-a['F']).max()),barycentric_position_max_mm=reconstruction,minimum_barycentric=minimum,independent_basis_strain_work_relative=float(abs(energy-np.diag(C)).max()/abs(C).max()),basis_columns_unbalanced=True,patch_wrench_max_difference=float(abs(np.array(patchW).T-ops['body_wrench'][k,:,:nc]).max())))
  # Test actual optimizer combinations, not unbalanced unit columns whose
  # six algebraic gauge reactions must never be called physical support.
  for r in doc['rows']:
   if 'contact_forces_N' not in r:continue
   p=np.array(r['contact_forces_N']);w=np.array(r['external_wrench_N_Nmm']);coeff=np.r_[p,w if k==0 else -w];f=F@coeff;u=U@coeff;net=fi@coeff-f;W=sum((wrench(x,ff) for x,ff in zip(points,f.reshape(-1,3))),np.zeros(6));force=float(abs(net).max());ew=float(u@(fi@coeff));lw=float(u@f);maxworldforce=max(maxworldforce,float(abs(W[:3]).max()));maxworldmoment=max(maxworldmoment,float(abs(W[3:]).max())*.001)
   loadsverified.append(dict(part=body['part'],case=r['case'],independent_nodal_force_max_N=force,world_force_max_N=float(abs(W[:3]).max()),world_moment_max_Nm=float(abs(W[3:]).max())*.001,independent_strain_work_Nmm=ew,load_work_Nmm=lw,work_identity_relative=abs(ew-lw)/max(abs(lw),1e-30),original_force_pass=force<1e-8,original_world_moment_pass=float(abs(W[3:]).max())*.001<1e-10))
 checks=dict(actual85part_hashes=True,independent_boundary_reconstruction=all(r['load_reconstruction_max_N']<1e-9 and r['barycentric_position_max_mm']<1e-8 and r['minimum_barycentric']>-1e-8 for r in rows),independent_basis_energy=all(r['independent_basis_strain_work_relative']<1e-8 for r in rows),balanced_state_original_force=bool(loadsverified) and all(r['original_force_pass'] for r in loadsverified),balanced_state_original_moment=bool(loadsverified) and all(r['original_world_moment_pass'] for r in loadsverified),balanced_state_work_identity=bool(loadsverified) and all(r['work_identity_relative']<1e-8 for r in loadsverified),QP_nonnegative_complementarity=all(r.get('optimizer_success',False) and min(r['contact_forces_N'])>-1e-10 and r['maximum_negative_gap_mm']<1e-8 and r['active_stationarity_mm']<1e-8 for r in doc['rows']))
 # No external support: two-body contact + internal axial connector cannot
 # produce a net whole-assembly force/moment. This is a force identity, no LP.
 no_support=[]
 for r in doc['rows']:
  w=np.array(r['external_wrench_N_Nmm']);no_support.append(dict(case=r['case'],missing_external_force_N=float(np.linalg.norm(w[:3])),missing_external_moment_Nm=float(np.linalg.norm(w[3:]))*.001,actual_external_attachment_present=False,accepted=False))
 dump(out/'inputs.json',dict(candidate=doc['candidate'],source=ref(src/'summary.json'),verifier=ref(out/'verifier.py'),methods='Independent affine tetra gradients/constant strain Hooke forces and volume work; independent boundary load/force/moment reconstruction; no FEM library assembler, producer or optimizer imports.'))
 dump(out/'summary.json',dict(status='ACTUAL_P1_FINITE_ANCHOR_INDEPENDENT_AUDIT_PASS_LOCAL' if all(checks.values()) else 'ACTUAL_P1_FINITE_ANCHOR_INDEPENDENT_AUDIT_FAIL',candidate=doc['candidate'],inputs=ref(out/'inputs.json'),checks=checks,bodies=rows,balanced_state_rows=loadsverified,world_force_max_N=maxworldforce,world_moment_max_Nm=maxworldmoment,no_external_support_negative_control=no_support,accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Local numerical audit cannot qualify conditional material,major-shank spring,source trace,pressure regularity,mesh/time/globalenergy or hardware.','No bench attachment exists;source trace explicitly supplies missing resultant as a conditional Neumann sensitivity. Negative control rejects every nonzero unsupported mode.']))
 print(json.dumps(dict(checks=checks,world_force=maxworldforce,world_moment=maxworldmoment)));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
