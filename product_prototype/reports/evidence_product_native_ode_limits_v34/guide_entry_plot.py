"""Plot actual Native direct-row states;not a prescribed impact trajectory."""
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_row_dynamics520';summary=json.loads((src/'summary.json').read_text());data=json.loads((src/'steps.json').read_text());fig,axes=plt.subplots(1,2,figsize=(11,4));evidence=[]
 for case in ('b3_direct_rows513','b3_direct_rows514','b3_direct_rows515'):
  r=next(x for x in summary['records'] if x['case']==case and x['alarm_mm']==5);ds=[x for x in data if x['case']==case and x['alarm_mm']==5];axes[0].plot([x['time_s']*1000 for x in ds],[x['accepted_row_velocity_m_s'][0] for x in ds],'o-',label=f"dt={r['dt_s']*1000:g}ms")
  axes[1].plot([x['time_s']*1000 for x in ds],[x['normal_impulse_Ns']*1e9 for x in ds],'o-')
 for r in summary['records']:
  f=r['first_nonzero_normal_row'];w=np.array(f['effective_inverse_mass_per_kg']);linear=2/1e-5
  evidence.append(dict(case=r['case'],alarm_mm=r['alarm_mm'],first_dt_s=r['dt_s'],used_normal_inverse_mass_per_kg=float(w[0,0]),translational_inverse_mass_per_kg=linear,rotational_fraction_of_normal_inverse_mass=float(1-linear/w[0,0]),first_kinetic_change_J=f['kinetic_change_J'],first_gap_over_dt_target_m_s=f['installed_gap_over_dt_target_m_s']))
 axes[0].set(xlabel='Actual discrete output time [ms]',ylabel='Accepted velocity on USED normal row [m/s]',title='Alarm5mm;default loop;not event-time aligned');axes[0].legend();axes[1].set(xlabel='Actual discrete output time [ms]',ylabel='Native normal impulse [nN s]',title='Impulse is NOT a force peak');fig.suptitle('SOFA26.06 free Guide pair;sourceffd2426;row binary6a00b4e75ef3\n10mg/body,isotropic I=1e-11kg m2,mu=.3;NOT attached B3/grasp/energy PASS',fontsize=10);fig.tight_layout();fig.savefig(out/'actual_native_entry.png',dpi=160);plt.close(fig)
 result=dict(status='ACTUAL_NATIVE_ROW_VISUALIZATION_ONLY',scope='Rotational fraction is this FREE off-centre pair effective mass,NOT attached film/guide inertia certification. Positive kinetic change is numerical inventory,NOT heat.',source_sha256=sha(Path(__file__)),inputs={str((src/n).relative_to(BASE.parent)):sha(src/n) for n in ('summary.json','steps.json')},effective_mass=evidence)
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(evidence[:2],indent=2))
if __name__=='__main__':main()
