"""All-mode frozen shared-contact diagnostic from an ACTUAL post-impact state.

Single bilateral row,constant tangent/force/normal,not unilateral SOFA dynamics.
No eigenmode is removed or stiffened. Five free rigid tangent/spin modes do not
couple to the frozen normal row and are explicitly outside film observables.
"""
import argparse,csv,json,os,shutil,subprocess
import numpy as np
from scipy.linalg import eigh,expm
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--residual',required=True);p.add_argument('--duration',type=float,default=.000625);a=p.parse_args()
 src=ROOT/'results'/('autonomous_film_'+a.residual);meta=json.loads((src/'summary.json').read_text());case=ROOT/'results'/('autonomous_film_'+meta['case'])
 if meta['status']!='PASS' or not 0<a.duration<=.001:raise ValueError('completed actual residual and bounded<=1ms diagnostic required')
 post=min((s for s in csv.DictReader((case/'coupled.event_states.csv').open()) if s['stage']=='post'),key=lambda s:float(s['time']))
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models')
 cpp=archive/'diagnostics/film_coupled_reintegrated/ContactModes.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_coupled_reintegrated/ContactModes.cpp',cpp)
 (out/'input.txt').write_text((src/'input.txt').read_text()+'\n'+post['local_velocity']+'\n'+post['body_velocity']+'\n'+post['body_omega']+'\n')
 binary=out/'reference';compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120);run=guarded([binary,out/'input.txt',out/'matrices.txt'],out/'run',60) if compile['exit_code']==0 else None
 result=dict(status='FAIL',scope='independent frozen BILATERAL single-row FEM;NOT actual nonlinear/unilateral SOFA time gate',actual_case=meta['case'],compile=compile,run=run,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},input_sha256=sha(out/'input.txt'),post_state_sha256=sha(case/'coupled.event_states.csv'),omitted_coupling='five free rigid tangent/spin coordinates,exactly uncoupled from frozen normal row;NO film eigenmode removed')
 if run and run['exit_code']==0:
  raw=np.fromstring((out/'matrices.txt').read_text(),sep=' ');n=int(raw[0]);c,m,fn,vn,gap,triangle=raw[1:7];z=raw[7:];E=z[:n*n].reshape(n,n);K=z[n*n:2*n*n].reshape(n,n);M=z[2*n*n:3*n*n].reshape(n,n);j,v,F=z[3*n*n:].reshape(3,n)
  lam,phi=eigh(K,E);alpha=phi.T@E@v;beta=phi.T@F;jphi=j@phi
  eig_res=np.linalg.norm(K@phi-(E@phi)*lam)/max(np.linalg.norm(K@phi),1e-300);reconstruction=np.linalg.norm(phi@alpha-v)/np.linalg.norm(v)
  # Independent full film + rigid-normal acceleration KKT versus elimination.
  miF=np.linalg.solve(M,F-j*fn);mij=np.linalg.solve(M,j);imp=(fn/m-j@miF)/(j@mij+1/m);af=miF+mij*imp;eliminated=np.linalg.solve(E,F)
  kkt_error=np.linalg.norm(af-eliminated)/np.linalg.norm(eliminated);normal_acceleration=float(j@af-(fn-imp)/m)
  sample=np.linspace(0,a.duration,257);exact=np.empty((len(sample),n,2));initial=np.column_stack((np.zeros(n),alpha))
  for k,w in enumerate(lam):
   A=np.array([[0.,1.,0.],[-w,-c,beta[k]],[0.,0.,0.]])
   for t,time in enumerate(sample):exact[t,k]=(expm(A*time)@np.array([0.,alpha[k],1.]))[:2]
  reaction=fn-m*(jphi@beta)+m*(exact[:,:,0]@(lam*jphi));velocity=exact[:,:,1]@phi.T
  rows=[];B=np.zeros((n,3,3));B[:,0,1]=1;B[:,1,0]=-lam;B[:,1,1]=-c;B[:,1,2]=beta;I=np.broadcast_to(np.eye(3),(n,3,3));B2=B@B
  plot_curves=[]
  for method in ('midpoint','gauss2','radau2'):
   for steps in (64,128,256):
    h=a.duration/steps
    if method=='midpoint':transfer=np.linalg.solve(I-h*B/2,I+h*B/2)
    elif method=='gauss2':transfer=np.linalg.solve(I-h*B/2+h*h*B2/12,I+h*B/2+h*h*B2/12)
    else:transfer=np.linalg.solve(I-2*h*B/3+h*h*B2/6,I+h*B/3)
    y=np.column_stack((np.zeros(n),alpha,np.ones(n)));traj=[y[:,:2].copy()]
    for step in range(steps):
     y=np.einsum('nij,nj->ni',transfer,y);traj.append(y[:,:2].copy())
    traj=np.array(traj);idx=np.arange(0,257,256//steps);ref=exact[idx];dv=(traj[:,:,1]-ref[:,:,1])@phi.T;dr=m*((traj[:,:,0]-ref[:,:,0])@(lam*jphi))
    rows.append(dict(method=method,steps=steps,dt=h,velocity_relative=float(np.linalg.norm(dv)/np.linalg.norm(velocity[idx])),reaction_relative=float(np.linalg.norm(dr)/np.linalg.norm(reaction[idx])),reaction_absolute_N=float(np.max(np.abs(dr)))))
    if steps==64:plot_curves.append((method,sample[idx],dr))
  with (out/'modes.csv').open('w') as f:
   w=csv.writer(f);w.writerow(['eigenvalue_s2','signed_velocity_amplitude','normal_mode','frozen_force_amplitude']);w.writerows(zip(lam,alpha,jphi,beta))
  with (out/'reaction.csv').open('w') as f:
   w=csv.writer(f);w.writerow(['time','signed_bilateral_reaction_N']);w.writerows(zip(sample,reaction))
  os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
  fig,axes=plt.subplots(1,2,figsize=(11,4));axes[0].plot(sample,reaction);axes[0].set_ylabel('Signed frozen reaction [N]')
  for method,time,error in plot_curves:axes[1].plot(time,error,label=method)
  axes[1].set_ylabel('64-step reaction error vs expm [N]');axes[1].legend()
  for ax in axes:ax.set_xlabel('Time since actual impact [s]');ax.grid()
  fig.suptitle('Independent frozen bilateral FEM;NOT actual nonlinear SOFA result');fig.tight_layout();fig.savefig(out/'frozen_methods.png',dpi=160);plt.close(fig)
  result.update(status='PASS' if eig_res<1e-10 and reconstruction<1e-10 and kkt_error<1e-10 and abs(normal_acceleration)<1e-9 else 'FAIL',binary_sha256=sha(binary),metrics=dict(film_modes=n,negative_eigenvalues=int(np.sum(lam<0)),maximum_angular_frequency=float(np.sqrt(max(0,lam[-1]))),eigen_residual=float(eig_res),initial_velocity_reconstruction=float(reconstruction),full_shared_KKT_acceleration_relative=float(kkt_error),normal_acceleration_residual=normal_acceleration,actual_normal_velocity=vn,actual_gap=gap,triangle=int(triangle),minimum_signed_bilateral_reaction_N=float(reaction.min()),maximum_signed_bilateral_reaction_N=float(reaction.max()),method_errors=rows),warning='negative signed reaction invalidates sustained UNILATERAL interpretation;frozen diagnostic remains bilateral')
 write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k in ('status','metrics')}))
if __name__=='__main__':main()
