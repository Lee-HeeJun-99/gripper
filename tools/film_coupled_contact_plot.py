"""Stored actual coupled states only;show failed contrasts without smoothing."""
import argparse,csv,json,os,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'))
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,axes=plt.subplots(2,2,figsize=(12,8));evidence={}
 for case in a.cases:
  source=ROOT/'results'/('autonomous_film_'+case);meta=json.loads((source/'identity.json').read_text());summary=json.loads((source/'summary.json').read_text())
  if summary['status']!='PASS':raise ValueError('completed actual state required')
  states=list(csv.DictReader((source/'coupled.states.csv').open()));events=list(csv.DictReader((source/'coupled.events.csv').open()));t=np.array([float(s['time']) for s in states]);label=('mid-J' if meta.get('midpoint_contact') else 'end-J')+' N='+str(meta['steps']);style='-' if meta.get('midpoint_contact') else '--'
  axes[0,0].plot(t,[float(s['U_attachment']) for s in states],style,label=label)
  axes[0,1].plot(t,[np.fromstring(s['body_velocity'],sep=' ')[2] for s in states],style,label=label)
  axes[1,0].plot(t,[np.fromstring(s['local_velocity'],sep=' ')[3*77+2] for s in states],style,label=label)
  atoms=sorted(set(r['time'] for r in events),key=float)
  axes[1,1].plot([float(time) for time in atoms],[sum(float(r['impulse']) for r in events if r['time']==time) for time in atoms],'o',label=label)
  evidence[case]=dict(source_commit=meta['source_commit'],binary_sha256=meta['binary_sha256'],dt=meta['duration']/meta['steps'],hashes={f:sha(source/f) for f in ('identity.json','coupled.states.csv','coupled.events.csv')})
 for ax,title,unit in zip(axes.flat,('Attachment energy','Actual free sphere z velocity','Skin centerline z velocity at x=75mm','Instantaneous physical impact atoms'),('force mm','mm/s','mm/s','force s')):
  ax.set_title(title);ax.set_xlabel('physical time [s]');ax.set_ylabel(unit);ax.set_xlim(.974,1.001);ax.grid();ax.legend(fontsize=8)
 fig.suptitle('Actual single-film/free-sphere C2 SOFA states / no amplification\nEndpoint vs midpoint contact: full time gate FAIL,not qualified grasp')
 fig.tight_layout();fig.savefig(out/'contact_comparison.png',dpi=160);fig.savefig(out/'contact_comparison.svg');plt.close(fig)
 write_json(out/'summary.json',dict(status='PASS',scope='visualization of stored actual SOFA states;NOT physics qualification',displacement_amplification=1,units='research N-mm-s convention,not measured material',sources=evidence))
 print(json.dumps(dict(status='PASS',image=str(out/'contact_comparison.png'))))
if __name__=='__main__':main()
