"""Read-only element energy/strain/curvature inventory of actual reference coupon."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from layer_bending_reference import element,elastic
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/reinforcement_bending1380';D=elastic(250e6,.3);records=[]
 for name in ('baseline','reinforced'):
  folder=src/name;x=np.load(folder/'reference.npz');q=x['q'];u=x['static_u'];F=x['F'];tets=x['tetrahedra'];energy={'old_core':0.,'added_backing':0.};strainmax=0.;detmin=1.;strain_energy_shear=0.
  for i,t in enumerate(tets):
   V,B,_=element(q[t],D);e=B@u[t].ravel();U=float(.5*V*e@D@e);energy['old_core' if i<600 else 'added_backing']+=U;strainmax=max(strainmax,float(abs(e).max()));strain_energy_shear+=float(.5*V*e[3:]@D[3:,3:]@e[3:]);detmin=min(detmin,float(np.linalg.det(((q+u)[t[1:]]-(q+u)[t[0]]).T)/np.linalg.det((q[t[1:]]-q[t[0]]).T)))
  static=float(sum(energy.values()));pre=json.loads((folder/'preflight.json').read_text());rows=list(csv.DictReader((folder/'states.csv').open()));dt=pre['dt_s'];mass=np.repeat(x['nodal_mass_kg'],3);K=x['K'];local=np.array(json.loads((BASE/'results/b3_railback_grasp1001298/mesh.json').read_text())['local_positions_mm']);fixed=np.zeros(len(q),bool);fixed[:252]=local[:,0]<=5
  if len(q)>252:fixed[252:]=np.array(json.loads((BASE/'results/proximal_reinforcement_geometry1364/mesh.json').read_text())['local_positions_mm'])[1::2,0]<=5
  free=np.flatnonzero(np.repeat(~fixed,3));M=mass[free];kf=K[np.ix_(free,free)];from scipy.linalg import cho_factor,cho_solve
  factor=cho_factor(np.diag(M)+dt*dt*kf);ur=np.zeros(len(free));vr=ur.copy();history=[]
  for r in rows:
   vr=cho_solve(factor,M*vr+dt*(F.ravel()[free]-kf@ur));ur+=dt*vr;qa=np.fromstring(r['q'],sep=' ');va=np.fromstring(r['v'],sep=' ');expected=q.ravel().copy();expected[free]+=ur;history.append(dict(time_s=float(r['time_s']),max_q_error_m=float(abs(qa-expected).max()),max_v_error_m_s=float(abs(va[free]-vr).max())))
  records.append(dict(name=name,reference_energy_by_material_J=energy,reference_work_energy_absolute_error_J=abs(static-.5*float(F.ravel()@u.ravel())),reference_shear_energy_fraction=strain_energy_shear/static,reference_max_engineering_strain=strainmax,reference_min_deformed_volume_ratio=detmin,native_reference_error_history=history,first_strict_velocity_failure_s=next((r['time_s'] for r in history if r['max_v_error_m_s']>1e-12),None)))
 d=dict(status='READ_ONLY_REFERENCE_ENERGY_AND_NATIVE_ERROR_INVENTORY',records=records,scope='Energy/strain of independent static linear reference,NOT actual Native energy API or equilibrium. Native q/v comparison keeps strict1e-12FAIL. Shear fraction alone does not prove locking;no Guide/Cable/contact in eithercoupon. No fitted modulus or newphysics.',physical_validation='NOT QUALIFIED',input_hashes={str(f.relative_to(BASE)):sha(f) for name in ('baseline','reinforced') for f in (src/name/'reference.npz',src/name/'states.csv')});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d))
if __name__=='__main__':main()
