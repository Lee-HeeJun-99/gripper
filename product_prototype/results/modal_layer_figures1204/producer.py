"""Actual Native accepted-state plots;invalid contact states labeled FAIL."""
import argparse,csv,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);fig,ax=plt.subplots(2,1,figsize=(9,8),layout='constrained');files=[]
 for case,label in [('b3_first_mode_base1184','Actual Native base'),('b3_first_mode_half1185','Actual Native half')]:
  f=BASE/'results'/case/'trace.json';files.append(f);rows=json.loads(f.read_text());ax[0].plot([r['time_s'] for r in rows],[r['actual_modal_displacement'] for r in rows],label=label)
 rows=json.loads((BASE/'results/b3_first_mode_base1184/trace.json').read_text());ax[0].plot([r['time_s'] for r in rows],[r['continuous_modal_displacement'] for r in rows],'--',label='Independent continuous reference');ax[0].set(ylabel='Mass-normalized modal displacement',title='Single bending-mode Native FEM; time gate FAIL, not grasp evidence')
 for case,label in [('layer_free1189','No pressure control'),('layer_pressure_friction1191','Step pressure — overlap FAIL'),('layer_ramp_pilot1193','Ramp pressure — overlap FAIL')]:
  rows=[]
  for i in (0,1):
   f=BASE/'results'/case/f'layer{i}.csv';files.append(f);rows.append(list(csv.DictReader(f.open())))
  q=[np.array([np.fromstring(r['q'],sep=' ').reshape(-1,3) for r in rr]) for rr in rows];order=(q[1][:,::2,2]-q[0][:,1::2,2]).min(axis=1);ax[1].plot([float(r['time_s']) for r in rows[0]],order*1e6,label=label)
 ax[1].axhline(0,color='black',linestyle=':');ax[1].set(ylabel='Corresponding interface Z order (µm)',title='Actual accepted states; Z order is NOT a certified surface gap')
 for panel in ax:panel.set_xlabel('Physical time (s)');panel.grid(alpha=.3);panel.legend(fontsize=8)
 fig.savefig(out/'actual_native_modes_and_layer_failures.png',dpi=150);fig.savefig(out/'actual_native_modes_and_layer_failures.svg');plt.close(fig);(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(dict(status='ACTUAL_NATIVE_STATE_FIGURES_ONLY',physical_validation='NOT QUALIFIED',input_hashes={str(f.relative_to(BASE)):sha(f) for f in files}),indent=2))
if __name__=='__main__':main()
