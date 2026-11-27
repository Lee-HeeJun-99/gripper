"""Independent actual four-state fixed-attachment/string load geometry.
No new producer, string solver or Root port implementation imported.
"""
import sys,json,time,shutil
import numpy as np
from scipy.integrate import solve_ivp
from scipy.spatial.transform import Rotation
from baseline_registry import ROOT,REPO,ref,dump
from primary_support_feedback import body
from primary_gravity_swivel import ARM

def W(q,f):return np.r_[f,np.cross(q,f)]
def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');src=ROOT/'validation/integrated/primaryP1_attached_loads1/summary.json';s=json.loads(src.read_text());a=np.load(REPO/s['source_field']['path']);forces=np.load(REPO/s['output']['path']);trial=np.load(src.parent/'trial_field.npz')['u_mm'];mass=json.loads((ROOT/'validation/integrated/primaryP1_seated_string1/mass_points.json').read_text());mu=next(p['mass_kg'] for p in mass if p['mode']=='wire')/.12404617484274723;gravity=np.array([0,0,-9.80665]);w=mu*gravity;rows=[];mo=int(a['motor_offset'])
 for tag,u in [('initial',a['u_mm']),('trial',trial),('rootY_minus',a['u_mm']-.0001*forces['original_RootY_direction']),('rootY_plus',a['u_mm']+.0001*forces['original_RootY_direction'])]:
  st=json.loads((src.parent/(tag+'_loads.json')).read_text())['upstream'];c=st['string'];z=np.array(c['state']);Rm=Rotation.from_rotvec(u[mo+3:mo+6]).as_matrix();C=np.array([0,0,.020])+u[mo:mo+3]*.001;axis=Rm[:,1];r=.01125;A=np.array(c['A_m']);B=np.array(c['B_m']);Q=np.array(c['Q_m']);E=np.array(c['E_m']);hA=Rm@z[:3];l0=c['lead_length_m'];lw=c['contact_length_m'];l1=c['free_length_m'];Fe=np.array(c['Fe_N']);hB=hA-w*l0;hQ=-Fe+w*l1
  def integ(h,L):
   g=np.linalg.norm(w);ee=w/g;hp=h@ee;ht=h-hp*ee;b=np.linalg.norm(ht);return ht/g*(np.arcsinh(hp/b)-np.arcsinh((hp-g*L)/b))+ee/g*(np.hypot(b,hp)-np.hypot(b,hp-g*L))
  free=max(float(np.max(abs(A+integ(hA,l0)-B))),float(np.max(abs(Q+integ(hQ,l1)-E))))
  def ode(t,y):
   q,h=y[:3],y[3:6];rad=q-C-axis*((q-C)@axis);er=rad/np.linalg.norm(rad);et=np.cross(er,axis);H=np.linalg.norm(h);lam=(h@et)**2/(H*r)-w@er;f=lam*er;return np.r_[h/H,-w-f,q,f,np.cross(q,f)]
  sol=solve_ivp(ode,(0,lw),np.r_[B,hB,np.zeros(9)],rtol=2e-12,atol=2e-14);yy=sol.y[:,-1];eta=z[6];ce,se=np.cos(eta),np.sin(eta);Ry=np.array([[ce,0,se],[0,1,0],[-se,0,ce]]);tail=C+Rm@Ry@np.array([-.003,0,.01125]);WG=np.array(c['wire_gravity_wrench_N_Nm']);balance=-W(A,hA)+W(E,-Fe)+WG-W(tail,mu*.006*gravity)+np.r_[yy[9:12],yy[12:15]]
  # Independent area-weighted proper rotation on actual Root x50.5 face.
  X=a['F0_ROOT_BACK_points_mm'];o=int(a['F0_ROOT_BACK_offset']);ids=abs(X[:,0]-50.5)<1e-5;ww=a['Root_port_weights_mm2'][ids];x=X[ids];xx=x+u[o:o+3*len(X)].reshape(-1,3)[ids];c0=np.average(x,axis=0,weights=ww);c1=np.average(xx,axis=0,weights=ww);R,_=Rotation.align_vectors(xx-c1,x-c0,weights=ww);R=R.as_matrix();tr=(c1-R@c0)*.001;_,_,ports,_=body(mass,np.array(st['state']),st['n'],st['swivel_beta_rad'],(R.T@gravity)[[0,2]],True);ep=ports['P']+ARM*np.array([np.sin(st['swivel_beta_rad']),np.cos(st['swivel_beta_rad'])]);attached=R@np.array([ep[0],0,ep[1]])+tr;attachment=float(np.max(abs(attached-E)));endpoint=float(np.max(abs(yy[:3]-Q)));ft=float(np.max(abs(yy[3:6]-hQ)));rootFy=st['Root_origin_wrench_N_Nm'][1];checks=dict(ODE=bool(sol.success),closed_free=free<1e-10,wrap_endpoint=endpoint<1e-10,wrap_force=ft<1e-8,wire_force=np.linalg.norm(balance[:3])<1e-8,wire_moment=np.linalg.norm(balance[3:])<1e-10,actual_Root_attachment=attachment<1e-10,no_auxiliary_slip=abs(z[7])<1e-8,Y_force_transmission=abs(rootFy-Fe[1])<1e-10)
  rows.append(dict(state=tag,checks={k:bool(v) for k,v in checks.items()},free_endpoint_error_m=free,wrap_endpoint_error_m=endpoint,wrap_force_error_N=ft,wire_balance_N_Nm=balance.tolist(),actual_Root_attachment_error_m=attachment,actual_root_forceY_N=rootFy))
 # Old result was RESIDUAL wrench internal-external; load wrench has opposite sign.
 old=json.loads((ROOT/'validation/integrated/primaryP1_finite_increment2/trial_loads.json').read_text());dy=np.array([0,old['root_freeY_increment_mm']*.001,0]);missing=np.cross(dy,old['upstream']['Root_origin_wrench_N_Nm'][:3]);oldload=np.array(old['applied_current_wrench_N_Nm'][3:]);signerr=float(np.max(abs(oldload+missing)));checks={z['state']:all(z['checks'].values()) for z in rows};checks['old_load_vs_residual_sign']=signerr<1e-10
 result=dict(status='ACTUAL_P1_ATTACHED_ENDPOINT_GEOMETRY_INDEPENDENT_PASS' if all(checks.values()) else 'ACTUAL_P1_ATTACHED_ENDPOINT_GEOMETRY_INDEPENDENT_FAIL',candidate=s['candidate'],source=ref(src),source_field=s['source_field'],verifier=ref(out/'verifier.py'),checks=checks,states=rows,old_external_load_plus_missing_couple_error_Nm=signerr,all_actual_upstream_states_verified=4,SOFA_runs=0,new_equilibrium_solved=False,actual_support_updates=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Independent Root proper rotation and string closed-form/arc-length force ODE, four actual source/trial/RootY contrasts. Existing planar body kinematics reused only to reconstruct cable endpoint; no new full3D Finger qualification.','Corrects attached1 diagnostic wrong comparison sign between external load and internal-minus-external residual. Original attached1 FAIL retained, original RootY fixed-target gauge conflict remains real.','No finite-bending/continuous wire sweep/BRep/tolerance/friction/source capacity/global energy/physical anchor/mesh/full3Finger certificate. Attached endpoint loads must be coupled to augmented RootY equality with zero gauge reaction before an accepted update.'])
 dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
