"""Actual fixed-Tmax pulse versus extended Hold. Work is deliberately NOT matched."""
import argparse,csv,json,os,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from film_transmission_linear import shape
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();cases=('20261118_transmission_gauss_cycle1169','20261118_transmission_hold50_1187');data=[];hashes={}
 for case in cases:
  src=ROOT/'results'/('autonomous_film_'+case);proof=json.loads((src/'summary.json').read_text())
  if proof['status']!='PASS' or proof['process']['exit_code']:raise ValueError('completed actual strict API controls required')
  for file,digest in proof['raw_hashes'].items():
   if sha(src/file)!=digest:raise ValueError('actual raw changed')
  rows=list(csv.DictReader((src/'actual.csv').open()));metrics=[dict(time=float(r['time']),T_end=float(r['T_end']),**shape(np.fromstring(r['q'],sep=' '))) for r in rows];data.append((proof,rows,metrics));hashes[case]=sha(src/'summary.json')
 for key in ('mass_kg','volume_mm3','material','root','public_mass_sha256','dt_s','duration_s','bond_stiffness_N_mm','guide_offset_mm','scheme'):
  if data[0][0][key]!=data[1][0][key]:raise ValueError('not a one-factor control comparison: '+key)
 for key in ('maximum_N_per_rail','ramp_s','C2'):
  if data[0][0]['control'][key]!=data[1][0]['control'][key]:raise ValueError('shared control prefix differs')
 if any(x['time']!=y['time'] for x,y in zip(data[0][1],data[1][1])):raise ValueError('actual epochs differ')
 prefix={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(data[0][1],data[1][1]) if float(x['time'])<=.02) for k in ('q','v')}
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,axes=plt.subplots(2,2,figsize=(11,8))
 for label,(_,_,metrics) in zip(('original pulse','longer Hold'),data):
  for ax,key in zip(axes.flat,('T_end','skin_tip_z','skin_root_tip_total_angle_rad','skin_tip_width_warp_z_mm')):ax.plot([r['time']*1000 for r in metrics],[r[key] for r in metrics],label=label);ax.set_xlabel('actual time [ms]');ax.set_ylabel(key);ax.legend(fontsize=8)
 fig.suptitle('Actual SOFA Film/Rails, no contact;Tmax=0.0001N/rail;dt=200us\nDLL '+data[0][0]['binary_sha256'][:12]+' / '+data[1][0]['binary_sha256'][:12]+';different work;NOT grasp');fig.tight_layout();fig.savefig(out/'actual_hold_comparison.png',dpi=150);plt.close(fig)
 result=dict(status='PASS' if max(prefix.values())<1e-12 else 'FAIL',scope='one-factor ACTUAL same-Tmax control comparison;NOT matched-work superiority/contact/grasp',source_summaries=hashes,shared_pre20ms_api_max_abs=prefix,api_gate=1e-12,actual_endpoint={case:d[2][-1] for case,d in zip(cases,data)},matched_actuation_work=False,contact_area=None,pressure=None,holding_capacity=None,figure_sha256=sha(out/'actual_hold_comparison.png'));write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k!='actual_endpoint'}))
if __name__=='__main__':main()
