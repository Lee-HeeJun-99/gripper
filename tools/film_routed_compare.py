"""Read-only SAME accepted physical epochs;route contrast,not time/grasp gate."""
import argparse,csv,json,os,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_transmission_linear import shape
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--baseline',required=True);p.add_argument('--candidate',required=True);p.add_argument('--exact-baseline',action='store_true');a=p.parse_args();data=[];identities={}
 for name in (a.baseline,a.candidate):
  src=ROOT/'results'/('autonomous_film_'+name);m=json.loads((src/'summary.json').read_text())
  if m['status']!='PASS' or not m['all_contexts_exact']:raise ValueError('completed actual trajectories required')
  for f,d in m['raw_hashes'].items():
   if sha(src/f)!=d:raise ValueError('accepted raw changed')
  data.append((src,m,{float(r['time']):r for r in csv.DictReader((src/'actual.csv').open())}));identities[name]=dict(summary_sha256=sha(src/'summary.json'),binary_sha256=m['binary_sha256'])
 times=sorted(set(data[0][2])&set(data[1][2]))
 if not times:raise ValueError('no EXACT common accepted time;no interpolation')
 if a.exact_baseline and (data[0][1].get('amplitude_mm',0.)!=data[1][1].get('amplitude_mm',0.) or data[0][1]['raw_hashes']['public_mass.txt']!=data[1][1]['raw_hashes']['public_mass.txt'] or set(data[0][2])!=set(data[1][2])):raise ValueError('exact regression requires same geometry/public mass/ALL accepted times')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');records=[];maximum={k:0. for k in ('q','v')}
 for time in times:
  for k in maximum:maximum[k]=max(maximum[k],float(np.max(abs(np.fromstring(data[0][2][time][k],sep=' ')-np.fromstring(data[1][2][time][k],sep=' ')))))
  for i,(src,m,rows) in enumerate(data):
   r=rows[time];q=np.fromstring(r['q'],sep=' ');u=q.reshape(231,3);s=shape(q);s.update(time_s=time,case=(a.baseline,a.candidate)[i],skin_centre75_z_mm=float(u[75+2,2]),skin_mean75_z_mm=float(u[75:80,2].mean()),T_end_N=float(r['T_end']));records.append(s)
 with (out/'shape.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
 os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,axes=plt.subplots(2,2,figsize=(12,8))
 for i,(src,m,rows) in enumerate(data):
  label=('existing route','quadratic route')[i] if not a.exact_baseline else ('provider A,same geometry','provider B,same geometry')[i];r=rows[times[-1]];u=np.fromstring(r['q'],sep=' ').reshape(231,3);skin=u[:105].reshape(21,5,3);centre=skin[:,2];mean=skin.mean(axis=1);axes[0,0].plot(np.linspace(0,100,21)+mean[:,0],mean[:,2],label=label+' mean');axes[0,0].plot(np.linspace(0,100,21)+centre[:,0],centre[:,2],ls='--',label=label+' centre')
  rr=[r for r in records if r['case']==(a.baseline,a.candidate)[i]];t=[r['time_s']*1000 for r in rr]
  for ax,key in ((axes[0,1],'skin_mean75_z_mm'),(axes[1,0],'skin_tip_z'),(axes[1,1],'skin_root_tip_total_angle_rad')):ax.plot(t,[r[key] for r in rr],label=label)
 axes[0,0].set(xlabel='actual local x [mm]',ylabel='actual z [mm],scale1',title=f'Accepted shape at {times[-1]*1000:.3g}ms')
 for ax,title,unit in ((axes[0,1],'Skin at material75mm','z [mm]'),(axes[1,0],'Skin width-mean tip','z [mm]'),(axes[1,1],'Skin root-tip3D angle','rad')):ax.set(xlabel='physical time [ms]',ylabel=unit,title=title)
 for ax in axes.ravel():ax.legend(fontsize=7)
 fig.suptitle('Actual SOFA NO object/contact;not wrapping/holding certification\nSame core/mass/C2 prescribed tension;different work and unmodeled wire hardware');fig.tight_layout();fig.savefig(out/'actual_route_comparison.png',dpi=150);plt.close(fig)
 result=dict(status='PASS' if not a.exact_baseline or max(maximum.values())<=1e-12 else 'FAIL',scope='read-only actual route/shape comparison;NOT contact/holding/lift superiority',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_summaries=identities,common_exact_epochs=len(times),interpolation=False,endpoint_time_s=times[-1],endpoint=[r for r in records if r['time_s']==times[-1]],baseline_api_difference=maximum if a.exact_baseline else None,core_volume='same;wire/guide hardware NOT MEASURED',matched_work=False,contact_area=None,contact_pressure=None,holding_load=None,raw_hashes={n:sha(out/n) for n in ('shape.csv','actual_route_comparison.png')});write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k!='endpoint'}))
if __name__=='__main__':main()
