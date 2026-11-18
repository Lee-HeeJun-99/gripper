"""Actual stage force-path and accepted-state shape;no inferred contact loads."""
import argparse,csv,json,os,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from film_transmission_linear import shape
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'results/autonomous_film_20261118_transmission_hold_force1200';meta=json.loads((src/'summary.json').read_text());actual=ROOT/'results/autonomous_film_20261118_transmission_hold50_1187';proof=json.loads((actual/'summary.json').read_text())
 if meta['status']!='PASS' or proof['status']!='PASS' or meta['parent_summary_sha256']!=sha(actual/'summary.json'):raise ValueError('complete actual stage observer required')
 for parent,m in ((src,meta),(actual,proof)):
  for file,digest in m['raw_hashes'].items():
   if sha(parent/file)!=digest:raise ValueError('actual stage/state raw changed')
 force=list(csv.DictReader((src/'work.csv').open()));rows=list(csv.DictReader((actual/'actual.csv').open()));states=[dict(time=float(r['time']),**shape(np.fromstring(r['q'],sep=' '))) for r in rows];old=ROOT/'results/autonomous_film_20261118_transmission_hold_work1194';prior=json.loads((old/'summary.json').read_text())
 if sha(old/'work.csv')!=prior['raw_hashes']['work.csv']:raise ValueError('old work observer raw changed')
 old_rows=list(csv.DictReader((old/'work.csv').open()));exact=len(old_rows)==len(force) and all(all(x[k]==y[k] for k in x) for x,y in zip(old_rows,force))
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,axes=plt.subplots(3,2,figsize=(12,10));tf=np.array([float(r['time'])*1000 for r in force]);tq=np.array([r['time']*1000 for r in states])
 for ax,key in zip((axes[0,0],axes[1,0],axes[2,0]),('T','attachment_skin_force_norm_N','tendon_work_Nmm')):ax.plot(tf,[float(r[key]) for r in force]);ax.set_ylabel(key+' (actual stages)')
 for key in ('skin_tip_z','skin_centre_tip_z','left_tip_z'):axes[0,1].plot(tq,[r[key] for r in states],label=key)
 for key in ('skin_mid_z','left_mid_z'):axes[1,1].plot(tq,[r[key] for r in states],label=key)
 for key in ('skin_root_tip_total_angle_rad','left_root_tip_total_angle_rad'):axes[2,1].plot(tq,[r[key] for r in states],label=key)
 axes[0,1].set_ylabel('actual tip displacement [mm]');axes[1,1].set_ylabel('actual midspan displacement [mm]');axes[2,1].set_ylabel('actual total tangent angle [rad]')
 for ax in axes[:,1]:ax.legend(fontsize=7)
 for ax in axes.flat:ax.set_xlabel('physical time [ms]')
 fig.suptitle('Actual no-contact Film/Rails/Tendon;Gauss dt=200us;DLL '+proof['binary_sha256'][:12]+'\nTmax=0.0001N/rail;attachment curve is nodal-vector NORM,NOT grasp resultant or pressure');fig.tight_layout();fig.savefig(out/'actual_force_path.png',dpi=150);plt.close(fig)
 result=dict(status='PASS' if exact else 'FAIL',scope='actual stage-force path visualization and observer noninterference check;NOT time/energy/grasp certification',actual_summary_sha256=sha(actual/'summary.json'),observer_summary_sha256=sha(src/'summary.json'),prior_work_summary_sha256=sha(old/'summary.json'),previous_work_columns_byte_exact=exact,contact_force=None,object_motion=None,contact_area=None,pressure=None,temporal_interpretation='Initial zero direct skin tendon force does not imply a finite dead-time;coupled ODE yields higher-order delayed response,not a measured propagation speed.',image_sha256=sha(out/'actual_force_path.png'));write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
