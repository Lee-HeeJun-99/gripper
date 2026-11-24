"""Actual accepted Native motion/response plot,not conceptual geometry."""
import argparse,csv,json,os
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);os.environ.setdefault('MPLCONFIGDIR','/tmp/regrip-matplotlib');import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,ax=plt.subplots(2,1,figsize=(9,7),sharex=True);hashes={}
 for name,label in (('b3_mass100_explore1059','Original joint'),('b3_railback_grasp1001298','Rail-back joint')):
  src=BASE/'results'/name;rows=list(csv.DictReader((src/'object.csv').open()));t=np.array([float(r['time_s']) for r in rows]);z=np.array([np.fromstring(r['rigid_q'],sep=' ')[2] for r in rows]);index={x:i for i,x in enumerate(t)};skin=np.zeros(len(t));support=np.zeros(len(t))
  with (src/'response_rows.csv').open() as f:
   for r in csv.DictReader(f):
    models=r['model0']+r['model1']
    if '/object/'not in models:continue
    i=index[float(r['time_s'])];v=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ')[2]/.0025
    if '/skinCollision/'in models:skin[i]+=v
    elif '/floor/'in models:support[i]+=v
  ref=np.argmin(abs(t-1.));ax[0].plot(t,(z-z[ref])*1000,label=label);ax[1].plot(t,skin,label=label+' Skin');ax[1].plot(t,support,'--',label=label+' Support');hashes[name]={f:sha(src/f) for f in ('object.csv','response_rows.csv')}
 ax[0].set_ylabel('Object Z relative to t=1s [mm]');ax[1].set(ylabel='Actual response force Z [N]',xlabel='Recorded accepted time [s]');ax[1].axhline(.981,color='k',ls=':',label='100g weight');ax[0].legend();ax[1].legend(ncol=2)
 for a0 in ax:a0.axvspan(1.6,2,color='grey',alpha=.12);a0.grid(alpha=.2)
 fig.suptitle('Actual Native SOFA — both exploratory Holding FAIL\nNo time/mesh/product qualification');fig.tight_layout();fig.savefig(out/'comparison.png',dpi=140);fig.savefig(out/'comparison.svg');plt.close(fig);(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(dict(status='ACTUAL_NATIVE_VISUALIZATION_ONLY',inputs=hashes,physical_validation='NOT QUALIFIED'),indent=2))
if __name__=='__main__':main()
