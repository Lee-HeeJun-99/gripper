"""Independent actual rigid-object impulse balance; no state/force modification."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha

def residuals(v,v0,imp,mass,radius,gravity,dt):
 dv=np.diff(np.vstack([v0,v]),axis=0)
 return mass*dv[:,:3]-mass*np.asarray(gravity)*dt-imp[:,:3],.4*mass*radius**2*dv[:,3:]-imp[:,3:]

def window_mask(t,lo,hi):
 # Original Holding includes both endpoints despite binary clock roundoff.
 return ((t>=lo-1e-12) if lo==1.6 else (t>lo+1e-12))&(t<=hi+1e-12)

def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;summary=json.loads((src/'summary.json').read_text());assert summary['process']['exit_code']==0,'Completed Native only';root=ET.parse(src/'scene.scn').getroot();protocol=json.loads((src/'holding_protocol.json').read_text());dt=float(root.get('dt'));mass_field=root.find("Node[@name='object']/UniformMass");mass=float(mass_field.get('totalMass') or mass_field.get('vertexMass').split()[0]);assert mass==protocol['mass_kg'];R=float(root.find("Node[@name='object']/Node/SphereCollisionModel").get('radius'));g=np.fromstring(root.get('gravity'),sep=' ');read=lambda f:list(csv.DictReader((src/f).open()));obj=read('object.csv');t=np.array([float(r['time_s']) for r in obj]);v=np.array([np.fromstring(r['rigid_v'],sep=' ') for r in obj]);q=np.array([np.fromstring(r['rigid_q'],sep=' ') for r in obj]);imp=np.array([np.fromstring(r['object_impulse_Ns_Nms'],sep=' ') for r in obj]);body=root.find("Node[@name='object']/MechanicalObject");v0=np.fromstring(body.get('velocity','0 0 0 0 0 0'),sep=' ');linear,angular=residuals(v,v0,imp,mass,R,g,dt);index={float(x):k for k,x in enumerate(t)};groups={k:np.zeros_like(imp) for k in ['skin0','skin1','skin2','support','hardware','unknown']}
 for r in csv.DictReader((src/'response_rows.csv').open()):
  models=[r['model0'],r['model1']]
  if not any(n.startswith('/object/') for n in models):continue
  other=next(n for n in models if not n.startswith('/object/'));key=next(('skin'+str(i) for i in range(3) if other.startswith(f'/finger{i}/skinCollision/')),None)
  if key is None:key='support' if other.startswith('/floor/') else 'hardware' if other.startswith(('/guides','/drive_','/finger')) else 'unknown'
  groups[key][index[float(r['time_s'])]]+=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ')
 support=np.array([np.fromstring(r['q'],sep=' ') for r in read('support.csv')]);supportR=float(root.find("Node[@name='floor']/SphereCollisionModel").get('radius'));gap=np.linalg.norm(q[:,:3]-support,axis=1)-R-supportR;maximum_iterations=int(root.find('BlockGaussSeidelConstraintSolver').get('maxIterations'));iterations=np.array([int(r['solver_iterations']) for r in obj]);windows=[]
 for lo,hi in [(0,.5),(.5,.6),(.6,1.),(1.,1.2),(1.2,1.6),(1.6,2.)]:
  mask=window_mask(t,lo,hi)
  if not mask.any():continue
  windows.append(dict(requested_window_s=[lo,hi],actually_covers_end=bool(t[-1]>=hi-1e-12),samples=int(mask.sum()),maximum_speed_mm_s=float(np.linalg.norm(v[mask,:3],axis=1).max()*1000),minimum_support_gap_mm=float(gap[mask].min()*1000),maximum_support_resultant_N=float(np.linalg.norm(groups['support'][mask,:3]/dt,axis=1).max()),mean_group_object_wrench_N_Nm={k:(x[mask]/dt).mean(0).tolist() for k,x in groups.items()},solver_iteration_limit_samples=int((iterations[mask]>=maximum_iterations).sum())))
 errors=dict(linear_momentum_max_error_Ns=float(abs(linear).max()),sphere_angular_momentum_max_error_Nms=float(abs(angular).max()),row_partition_error_Ns_Nms=float(abs(imp-sum(groups.values())).max()));valid=max(errors.values())<=protocol['gravity_momentum_impulse_residual_limit_Ns'];d=dict(status='PASS_OBJECT_DISCRETE_IMPULSE_BALANCE_ONLY' if valid else 'FAIL_OBJECT_IMPULSE_BALANCE',case=a.case,actual_duration_s=float(t[-1]),mass_kg=mass,radius_m=R,gravity_m_s2=g.tolist(),errors=errors,windows=windows,holding_window_fully_run=bool(t[-1]>=2.-1e-12),source_sha256=sha(Path(__file__)),input_hashes={f:sha(src/f) for f in ['summary.json','scene.scn','holding_protocol.json','object.csv','support.csv','response_rows.csv']},scope='Read-only actual object impulse/velocity/weight and model-pair partition. Sphere COM isotropic inertia; no q/v correction. Per-step signed wrench is not contact area or whole energy. Small momentum residual does NOT validate unconverged contact response, FEM dynamics or material. Prefix cannot pass Holding.');out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
