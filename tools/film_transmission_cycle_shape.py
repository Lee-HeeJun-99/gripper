"""Actual no-contact50ms cycle versus separately labeled independent static shape."""
import argparse,csv,json,os,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from film_transmission_linear import shape
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'results/autonomous_film_20261118_transmission_gauss_cycle1169';meta=json.loads((src/'summary.json').read_text());static=ROOT/'results/autonomous_film_20261118_transmission_static_hybrid1165';proof=json.loads((static/'summary.json').read_text())
 for parent,record in ((src,meta),(static,proof)):
  if record['status']!='PASS':raise ValueError('completed API/static results required')
  for name,digest in record['raw_hashes'].items():
   if sha(parent/name)!=digest:raise ValueError('immutable shape data changed')
 rows=list(csv.DictReader((src/'actual.csv').open()));eq=list(csv.DictReader((static/'equilibrium.states.csv').open()))[-1];out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');records=[dict(time=float(r['time']),T_end=float(r['T_end']),**shape(np.fromstring(r['q'],sep=' '))) for r in rows]
 with (out/'shape.csv').open('w') as stream:
  writer=csv.DictWriter(stream,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
 os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,axes=plt.subplots(2,2,figsize=(12,8))
 for time in (.01,.02,.03,.05):
  row=min(rows,key=lambda r:abs(float(r['time'])-time));u=np.fromstring(row['q'],sep=' ').reshape(231,3)
  for ax,offset,ny in ((axes[0,0],0,5),(axes[0,1],105,3)):
   points=u[offset:offset+21*ny].reshape(21,ny,3).mean(axis=1);ax.plot(np.linspace(0,100,21)+points[:,0],points[:,2],label=f'actual {float(row["time"])*1000:.1f}ms')
 for ax in axes[0]:ax.set_xlabel('local x [mm]');ax.set_ylabel('local z [mm], no amplification');ax.legend(fontsize=7)
 axes[0,0].set_title('Actual SOFA skin width-mean');axes[0,1].set_title('Actual SOFA left rail width-mean')
 axes[1,0].plot([r['time']*1000 for r in records],[r['skin_tip_z'] for r in records],label='skin mean');axes[1,0].plot([r['time']*1000 for r in records],[r['skin_centre_tip_z'] for r in records],label='skin centre');axes[1,0].set_xlabel('time [ms]');axes[1,0].set_ylabel('actual tip z [mm]');axes[1,0].legend()
 u=np.fromstring(eq['q'],sep=' ').reshape(231,3)
 for offset,ny,label in ((0,5,'skin'),(105,3,'left rail')):
  points=u[offset:offset+21*ny].reshape(21,ny,3).mean(axis=1);axes[1,1].plot(np.linspace(0,100,21)+points[:,0],points[:,2],label=label)
 axes[1,1].set_aspect('equal');axes[1,1].set_title('Independent static equilibrium, NOT SOFA result');axes[1,1].set_xlabel('local x [mm]');axes[1,1].set_ylabel('local z [mm]');axes[1,1].legend()
 fig.suptitle('No object/contact: actual C2 unload ends30ms, free motion to50ms\n'+meta['binary_sha256'][:16]+' / static at constant T=0.0001N per rail');fig.tight_layout();fig.savefig(out/'actual_cycle_and_static.png',dpi=150);plt.close(fig)
 result=dict(status='PASS',scope='read-only actual50ms shape and separately labeled static visualization;NOT wrapping/recovery completion',actual_summary_sha256=sha(src/'summary.json'),static_summary_sha256=sha(static/'summary.json'),endpoint=records[-1],full_cycle_time_convergence='NOT RUN',contact_area=None,holding_load=None,source_sha256=sha(__file__),raw_hashes={n:sha(out/n) for n in ('shape.csv','actual_cycle_and_static.png')});write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
