"""Static scientific plot of completed actual SOFA all-pair time evidence."""
import argparse,json,os,shutil
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
 inputs=('20261117_coupled_radau_time737','20261117_coupled_lobatto_time747');measurements=[];hashes={};physical=None
 for method,case in zip(('RadauIIA3','LobattoIIIA4'),inputs):
  path=ROOT/'results'/('autonomous_film_'+case)/'summary.json';data=json.loads(path.read_text());hashes[case]=sha(path);finest=max(data['cases'],key=lambda name:data['cases'][name]['identity']['steps']);durations={c['identity']['duration'] for c in data['cases'].values()}
  if durations!={.000009765625}:raise ValueError('plot requires SAME measured physical interval')
  identity=data['cases'][finest]['identity'];current={k:identity[k] for k in ('duration','body_mass','inertia_per_mass','rayleigh_mass','source_event_sha256','initial_displacement','initial_velocity','initial_body_center','initial_body_velocity')}
  if physical is None:physical=current
  elif physical!=current:raise ValueError('method comparison physical inputs differ')
  for pair,record in data['pairs'].items():
   if pair.endswith('__'+finest):
    coarse=pair.split('__')[0];meta=data['cases'][coarse]['identity'];measurements.append(dict(method=method,dt=meta['duration']/meta['steps'],errors={k:record['errors'][k]['relative_error'] for k in ('local_velocity','common_window_regular_body_force','U_attachment')},source_commit=meta['source_commit'],binary=meta['binary_sha256']))
 if len(measurements)!=4:raise ValueError('incomplete measured comparisons;do not emit empty PASS chart')
 os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,axes=plt.subplots(1,3,figsize=(13,4));keys=('local_velocity','common_window_regular_body_force','U_attachment')
 for method in ('RadauIIA3','LobattoIIIA4'):
  rows=sorted([r for r in measurements if r['method']==method],key=lambda r:r['dt'])
  for ax,key in zip(axes,keys):ax.loglog([r['dt'] for r in rows],[100*r['errors'][key] for r in rows],'o-',label=method)
 for ax,key in zip(axes,keys):ax.axhline(.1,color='red',ls='--',label='unchanged0.1% gate');ax.set_xlabel('Physical dt [s]');ax.set_ylabel('Relative difference vs quarter-grid [%]');ax.set_title(key);ax.grid();ax.legend(fontsize=7)
 fig.suptitle('ACTUAL SOFA:9.765625us persistent coupon only;NOT full contact/grasp');fig.tight_layout();fig.savefig(out/'actual_collocation_time.png',dpi=180);fig.savefig(out/'actual_collocation_time.svg');plt.close(fig)
 write_json(out/'summary.json',dict(status='PASS',scope='visualization of completed actual all-pair metrics;NOT additional physics certification',input_hashes=hashes,measurements=measurements,displacement_amplification=None))
if __name__=='__main__':main()
