"""Read-only convergence plot; independent numerical trajectories, not SOFA states."""
import argparse,json,os,shutil
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,axes=plt.subplots(2,1,figsize=(11,8));inputs={}
 for case in a.cases:
  src=ROOT/'results'/('autonomous_film_'+case);m=json.loads((src/'summary.json').read_text());inputs[case]=sha(src/'summary.json')
  if 'time_pairs' not in m:raise ValueError('completed numerical comparisons required')
  values={}
  for label,pair in m['time_pairs'].items():
   macro=int(label.split('_')[0][5:]);values[macro]=max(values.get(macro,0),pair['all_film_v']['relative']*100)
  axes[0].plot(sorted(values),[values[x] for x in sorted(values)],marker='o',label=case)
  defects={}
  for label,pair in m['signed_defect_pairs'].items():
   macro=int(label.split('_')[0][5:]);defects[macro]=max(defects.get(macro,0),pair['absolute'])
  axes[1].plot(sorted(defects),[defects[x] for x in sorted(defects)],marker='o',label=case)
 axes[0].axhline(.1,color='red',linestyle='--',label='unchanged0.1% time gate');axes[0].set_ylabel('maximum all-pair film velocity difference [%]');axes[1].set_ylabel('max signed partial-defect absolute difference [N mm]')
 for ax in axes:ax.set_xlabel('common800us epoch after actual50ms seed');ax.grid();ax.legend(fontsize=6)
 fig.suptitle('INDEPENDENT numerical recovery-window comparisons,NOT actual SOFA long-window states\nSame actual stationary50ms seed;zero tension/load,unchanged materials;not heat/grasp certification');fig.tight_layout();fig.savefig(out/'window_time.png',dpi=160);plt.close(fig);r=dict(status='PASS',scope='read-only plot generation ONLY;input physical FAIL statuses unchanged',input_summary_hashes=inputs,image_sha256=sha(out/'window_time.png'));write_json(out/'summary.json',r);print(json.dumps(r))
if __name__=='__main__':main()
