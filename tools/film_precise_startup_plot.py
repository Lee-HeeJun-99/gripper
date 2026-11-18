"""Scientific plots from actual SOFA material displacements,not concept poses."""
import argparse,csv,json,shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from curve_common import ROOT,sha,write_json
from film_transmission_linear import shape
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--all-time-tendon',action='store_true');a=p.parse_args();names=(['20261119_precise_tendon_actual1718','20261119_precise_tendon_actual_half1719','20261119_precise_tendon_actual_quarter1720'] if a.all_time_tendon else ['20261119_precise_startup_base1688','20261119_precise_startup_half1689','20261119_precise_startup_quarter1690']);time=ROOT/'results'/('autonomous_film_20261119_precise_tendon_all_time1721' if a.all_time_tendon else 'autonomous_film_20261119_precise_startup_actual_time1691');tm=json.loads((time/'summary.json').read_text())
 if tm['status']!='PASS':raise ValueError('qualified short-window actual assessment required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');fig,axes=plt.subplots(1,3,figsize=(14,4));records=[];sources={}
 for name in names:
  parent=ROOT/'results'/('autonomous_film_'+name);meta=json.loads((parent/'summary.json').read_text());rows=list(csv.DictReader((parent/'actual.csv').open()))
  if meta['status']!='PASS' or sha(parent/'actual.csv')!=meta['raw_hashes']['actual.csv']:raise ValueError('immutable actual states required')
  sources[name]=sha(parent/'summary.json');data=[]
  for row in rows:
   s=shape(np.fromstring(row['q'],sep=' '));data.append(dict(time_s=float(row['time']),skin_mean_tip_z=s['skin_tip_z'],left_tip_z=s['left_tip_z'],steps=meta['steps']))
  records+=data;t=[x['time_s']*1e6 for x in data]
  for ax,key in zip(axes[:2],('skin_mean_tip_z','left_tip_z')):ax.plot(t,[x[key] for x in data],'.-',label=str(meta['steps'])+' steps')
 for ax,title in zip(axes[:2],('Skin width-mean tip displacement','Left Rail tip displacement')):ax.set(xlabel='Physical time (microseconds)',ylabel='Material displacement (mm)',title=title);ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0));ax.legend()
 if a.all_time_tendon:
  error_rows=list(csv.DictReader((time/'errors.csv').open()));errors={label:max(float(x['relative']) for x in error_rows if x['pair']==label and x['relative'])*100 for label in ('0_1','1_2','0_2')}
 else:errors={label:max(x['relative'] for x in pair.values())*100 for label,pair in tm['errors'].items()}
 axes[2].bar(list(errors),list(errors.values()));axes[2].axhline(.1,color='r',label='0.1% gate');axes[2].set(ylabel='Maximum relative state/shape error (%)',title='All recorded common times;no floor' if a.all_time_tendon else 'ENDPOINT all-pairs ONLY;no floor');axes[2].legend();fig.suptitle('ACTUAL SOFA free startup,200us,Tmax100uN/rail,C2 ramp10ms;NO contact/wrapping claim');fig.tight_layout();fig.savefig(out/'actual_startup.png',dpi=160);plt.close(fig)
 with (out/'actual_startup.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
 write_json(out/'summary.json',dict(status='PASS',scope='plot of immutable actual material displacements;NOT visible world deformation/contact/grasp',actual_summaries=sources,time_assessment_sha256=sha(time/'summary.json'),displacement_amplification='NONE;axis uses actual mm with scientific notation',png_sha256=sha(out/'actual_startup.png'),csv_sha256=sha(out/'actual_startup.csv')))
if __name__=='__main__':main()
