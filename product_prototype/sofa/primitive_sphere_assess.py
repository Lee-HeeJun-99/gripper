"""Compare actual primitive contact to discrete momentum and friction expectations."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def assess(case):
 src=BASE/'results'/case;pre=json.loads((src/'preflight.json').read_text());mass=pre['mass_kg'];dt=pre['dt_s'];mu=pre['mu'];radius=pre['radius_m'];force=pre.get('tangential_force_N',.01)
 with (src/'rigid.csv').open() as f:rows=list(csv.DictReader(f))
 previous=np.zeros(3);reference_v=0.;initial_x=pre.get('initial_x_m',0.);reference_x=initial_x;res=[];xref=[];vref=[];gaps=[];tangent=[];normal=[];ratios=[];last=[];margins=[]
 for r in rows:
  t=float(r['time_s']);tau=t-dt;F=np.array([force*np.clip((tau-.01)/.002,0,1),0,-.4*np.clip(tau/.01,0,1)]);v=np.fromstring(r['rigid_v'],sep=' ');q=np.fromstring(r['rigid_q'],sep=' ');I=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ')[:3]
  res.append(float(np.linalg.norm((1+dt)*mass*v[:3]-mass*previous-dt*F-I)));previous=v[:3]
  reference_v=(reference_v+dt*F[0]/mass)/(1+dt);reference_x+=dt*reference_v;xref.append(abs(q[0]-reference_x));vref.append(abs(v[0]-reference_v));gaps.append(float(q[2]-radius));margins.append(float(min(.025-abs(q[0]),.01-abs(q[1]))))
  if t>=.014:normal.append(float(I[2]/dt));tangent.append(float(I[0]/dt));ratios.append(float(abs(I[0])/I[2]) if I[2]>0 else None);last.append(dict(time_s=t,x_m=float(q[0]),vx_m_s=float(v[0]),contact_force_N=(I/dt).tolist()))
 scope='Finite-radius laboratory contact component ONLY;not time/mesh convergence,energy,thin-layer jamming,grasp or hardware qualification'
 criteria=dict(finite=all(np.isfinite(v) for v in gaps+res+xref+vref),no_penetration=min(gaps)>=-1e-12,impulse_identity=max(res)<=1e-12,no_iteration_saturation=all(int(r['solver_iterations'])<1000 for r in rows))
 if mu==0:criteria.update(frictionless_x_reference=max(xref)<=1e-12,frictionless_v_reference=max(vref)<=1e-12,zero_lateral_contact=max(abs(x) for x in tangent)<=1e-12)
 elif force<mu*.4:criteria.update(stick_displacement=abs(last[-1]['x_m']-initial_x)<=1e-12,force_balance=max(abs(x+force) for x in tangent)<=1e-10)
 else:criteria.update(positive_slip=last[-1]['vx_m_s']>0,coulomb_saturation=bool([x for x in ratios if x is not None]) and max(abs(x-mu) for x in ratios if x is not None)<=1e-10)
 criteria['sphere_projection_within_support_face']=min(margins)>0
 criteria['positive_normal_support']=bool(normal) and min(normal)>0
 criteria={k:bool(v) for k,v in criteria.items()}
 valid_ratios=[x for x in ratios if x is not None]
 return dict(status='PASS_PRIMITIVE_COMPONENT_SCOPE_ONLY' if all(criteria.values()) else 'FAIL_COMPONENT_EXPECTATIONS',scope=scope,criteria=criteria,maximum_impulse_residual_Ns=max(res),minimum_bottom_gap_m=min(gaps),final=last[-1],mu=mu,tangential_force_N=force,normal_force_mean_N=float(np.mean(normal)),friction_ratio_range=[min(valid_ratios),max(valid_ratios)] if valid_ratios else None,maximum_frictionless_reference_x_error_m=max(xref) if mu==0 else None,maximum_frictionless_reference_v_error_m_s=max(vref) if mu==0 else None,input_hashes={str((src/f).relative_to(BASE)):sha(src/f) for f in ('rigid.csv','preflight.json','scene.scn')})
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',default=['primitive_sphere_slip1225','primitive_sphere_friction1226']);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records={c:assess(c) for c in a.cases};d=dict(status='PASS_SCOPED_COMPONENT_EXPECTATIONS' if all(r['status'].startswith('PASS') for r in records.values()) else 'FAIL_COMPONENT',records=records,physical_product_validation='NOT QUALIFIED',source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d))
if __name__=='__main__':main()
