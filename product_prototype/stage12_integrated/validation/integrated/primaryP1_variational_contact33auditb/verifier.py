"""Independent integrated displacement, actual curved wrench and end-traction audit.
Boussinesq displacement differentiated to stress; explicit PDE/surface checks.
End witnesses reject halfspace as an actual finite-pin free-boundary solution.
"""
import json,sys,time,shutil
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.spatial.transform import Rotation
from baseline_registry import ROOT,REPO,ref,sha,dump
from verify_primary_pin_contact32 import integ

def bgdisp(a,nu):
 x,y,z=a.T;R=np.sqrt(x*x+y*y+z*z);b=1-2*nu
 # Displacement multiplied by4*pi*G for a unit inward normal point force.
 return np.c_[x*z/R**3-b*x/(R*(R+z)),y*z/R**3-b*y/(R*(R+z)),z*z/R**3+2*(1-nu)/R]
def bgstress(a,nu):
 D=np.empty((len(a),3,3))
 for j in range(3):
  ac=np.array(a,dtype=complex);ac[:,j]+=1e-25j;D[:,:,j]=bgdisp(ac,nu).imag/1e-25
 # G cancels. Units stress per force=1/mm², E-independent.
 return (D+D.transpose(0,2,1)+2*nu/(1-2*nu)*np.trace(D,axis1=1,axis2=2)[:,None,None]*np.eye(3))/(4*np.pi)
def stable_gap(p,center,axis,R):
 v=p-center;v=v-(v@axis)[:,None]*axis;rho=np.linalg.norm(v,axis=1)
 return (R*R-np.sum(v*v,axis=1))/(R+rho)
def kavg(nx,ny,dx,dt,q=64):
 z,w=leggauss(q);ix,iy=np.meshgrid(np.arange(nx),np.arange(ny),indexing='ij');D=np.zeros((nx,ny))
 for a,wa in zip(z,w):
  for b,wb in zip(z,w):D+=wa*wb/4*integ(ix*dx+a*dx/2,iy*dt+b*dt/2,dx/2,dt/2)/(dx*dt)
 ids=np.c_[ix.ravel(),iy.ravel()];return D[abs(ids[:,None,0]-ids[:,0]),abs(ids[:,None,1]-ids[:,1])]
def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');start=time.monotonic();src=ROOT/'validation/integrated/primaryP1_variational_contact33/summary.json';s=json.loads(src.read_text());a=np.load(REPO/s['fields']['path']);inp=json.loads((REPO/s['inputs']['path']).read_text());assert sha(REPO/s['candidate']['path'])==s['candidate']['SHA256'];nu=inp['conditional_nu'];E=inp['conditional_E_MPa'];c=inp['opposing_compliance_factor']*(1-nu*nu)/(np.pi*E);rows=[];end=[];FD=[]
 for row in s['results']:
  if row['target_gauss_order']!=48:continue
  assert not(ROOT/'runtime/STOP').exists();key=row['key'];x,t=a[key+'_x_t_mm'].T;f=a[key+'_force_N'];dx=row['dx_mm'];dt=row['dt_mm'];r=row['r_mm'];R=row['R_mm'];yc,zc=row['axis_yz_mm'];K=c*kavg(row['nx'],row['ny'],dx,dt);u=K@f;rho=np.sqrt(R*R-4*(R-r)*r*np.sin(t/(2*r))**2);Jsum=np.zeros(12);z,w=leggauss(12);maxJ=0.;maxRigid=0.;FDerr=0.
  # Independent exact cylinder geometry, matrix free sum of physical tractions.
  for v,wv in zip(z,w):
   for b,wb in zip(z,w):
    xp=x+v*dx/2;tp=t+b*dt/2;p=np.c_[xp,yc+R-r+r*np.cos(tp/r),zc+r*np.sin(tp/r)];center=np.array([0,yc,zc]);rel=p-center;rel[:,0]=0;n=rel/np.linalg.norm(rel,axis=1)[:,None];bp=center+R*n;bp[:,0]=xp;J=np.c_[-n,-np.cross(p,n),n,np.cross(bp,n)];Jsum+=wv*wb/4*(J.T@f)
    rigid=np.r_[np.array([.7,-.2,.3]),np.array([.15,.27,-.21])];maxRigid=max(maxRigid,float(abs(J@np.r_[rigid,rigid]).max()))
    if v==z[0] and b==z[0]:
     ids=np.linspace(0,len(p)-1,12,dtype=int);ps=p[ids];ns=n[ids];js=J[ids];dJ=[];h=2e-5
     for j in range(12):
      values=[]
      for sign in [-1,1]:
       pp=ps.copy();cc=center.copy();axis=np.array([1.,0,0]);unit=np.eye(3)[j%3]
       if j<3:pp+=sign*h*unit
       elif j<6:pp=Rotation.from_rotvec(sign*h*unit).apply(pp)
       elif j<9:cc+=sign*h*unit
       else:
        rot=Rotation.from_rotvec(sign*h*unit);cc=rot.apply(cc);axis=rot.apply(axis)
       values.append(stable_gap(pp,cc,axis,R))
      dJ.append((values[1]-values[0])/(2*h))
     FDerr=float(abs(np.array(dJ).T-js).max());FD.append(dict(key=key,finite_difference_step=h,max_gap_J_error=FDerr))
  rel_energy=abs(float(f@u/2)/row['energy_Nmm']-1);rows.append(dict(key=key,asinh_Galerkin64_vs_log48_max_displacement_relative=float(abs(u-a[key+'_average_displacement_mm']).max()/row['indentation_mm']),independent_local_energy_relative=rel_energy,independent_curved_wrench_error=float(abs(Jsum-row['body_wrench_N_Nmm']).max()),common6rigid_gap_error=maxRigid,force_error_N=float(abs(f.sum()-row['conditional_load_N'])),finite_difference_J_error=FDerr))
  if row['ny']==24 and row['nx']==16:
   # Actual Root pin tip x=48.5 is free, pin extends to50.5. Only Front port
   # starts there. Rail port still contributes a residual at the same tip.
   # Test real interior points on the circular free tip, depth measured from
   # the loaded crown, transverse0. Stress is from local scalar kernel's
   # underlying Root Boussinesq halfspace, using the SAME solved pressures.
   zq,wq=leggauss(24)
   for depth in [.02,.1,.5]:
    traction=np.zeros(3)
    for aa,wa in zip(zq,wq):
     for bb,wb in zip(zq,wq):
      rel=np.c_[48.5-(x+aa*dx/2),-(t+bb*dt/2),np.full(len(x),depth)];sig=bgstress(rel,nu);traction-=wa*wb/4*np.einsum('nij,n->ij',sig,f)[:,0]
    # Actual circular tip membership: y=yc+1-depth,z=zc.
    end.append(dict(port=row['port'],tip_point_mm=[48.5,yc+R-depth,zc],depth_mm=depth,actual_pin_disk_interior=(1-depth)**2<r*r,halfspace_nonzero_free_tip_traction_MPa=traction.tolist(),traction_norm_MPa=float(np.linalg.norm(traction)),normalization_P_over_Lr_MPa=row['conditional_load_N']/((row['interval_mm'][1]-row['interval_mm'][0])*r),free_boundary_required_traction_MPa=[0,0,0],finite_end_boundary_satisfied=False))
 # Differentiate the stated displacement independently with real central
 # differences; verify Navier equilibrium and traction-free unloaded plane.
 samples=np.array([[.3,.4,.2],[-.7,.2,.6],[.1,-.8,.3]]);sig=bgstress(samples,nu);h=1e-5;D=np.stack([(bgdisp(samples+h*np.eye(3)[j],nu)-bgdisp(samples-h*np.eye(3)[j],nu))/(2*h) for j in range(3)],axis=2);ss=(D+D.transpose(0,2,1)+2*nu/(1-2*nu)*np.trace(D,axis1=1,axis2=2)[:,None,None]*np.eye(3))/(4*np.pi);div=np.zeros((len(samples),3))
 for j in range(3):div+=(bgstress(samples+h*np.eye(3)[j],nu)[:,:,j]-bgstress(samples-h*np.eye(3)[j],nu)[:,:,j])/(2*h)
 surface=bgstress(np.array([[.3,.4,0],[-.7,.2,0],[.1,-.8,0]]),nu)[:,:,2];controls=dict(complex_step_vs_real_stress_error=float(abs(sig-ss).max()),interior_divergence_error=float(abs(div).max()),unloaded_halfspace_surface_traction_error=float(abs(surface).max()))
 checks=dict(independent_integrated_displacement=all(v['asinh_Galerkin64_vs_log48_max_displacement_relative']<1e-4 for v in rows),independent_local_energy=all(v['independent_local_energy_relative']<1e-4 for v in rows),exact_curved_wrench=all(v['independent_curved_wrench_error']<1e-12 for v in rows),common_rigid_work=all(v['common6rigid_gap_error']<1e-12 for v in rows),finite_difference_gap_pullback=all(v['finite_difference_J_error']<1e-4 for v in rows),stress_derivative_controls=controls['complex_step_vs_real_stress_error']<1e-7 and controls['interior_divergence_error']<1e-6 and controls['unloaded_halfspace_surface_traction_error']<1e-12,actual_tip_membership=all(v['actual_pin_disk_interior'] for v in end))
 dump(out/'summary.json',dict(status='ACTUAL_P1_INDEPENDENT_VARIATIONAL_CURVED_WORK_AND_FREE_TIP_REJECTION',candidate=s['candidate'],source=ref(src),verifier=ref(out/'verifier.py'),checks=checks,results=rows,finite_difference_results=FD,free_end_traction_witnesses=end,Boussinesq_formula_controls=controls,newly_qualified_system_gate_ids=[],whole_system_release=False,accepted_product_equilibria=0,elapsed_s=time.monotonic()-start,limitations=['Independent64targetGauss vs48 is numerical integration only; no full mesh/contact convergence.','Pointwise complementarity still FAILS in producer probes.','Root-halfspace free-tip residual is a necessary boundary-condition rejection, not a solved finite-body correction or actual measured stress. Opposing body residual not cancelled against Root.','Radial closest-point normal/pullback certified for smooth cylinder interior only; no finite axial edge contact/large rotation/sourcefield/fullsupport/globalenergy release.']))
 print(json.dumps(dict(checks=checks,controls=controls,max_gap_J_error=max(v['finite_difference_J_error'] for v in rows),max_independent_displacement_relative=max(v['asinh_Galerkin64_vs_log48_max_displacement_relative'] for v in rows),free_tip_traction_norms_MPa=[v['traction_norm_MPa'] for v in end])))
if __name__=='__main__':main()
