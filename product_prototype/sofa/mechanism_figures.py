"""Scientific figures from completed native accepted states,no invented deformation."""
import argparse,csv,json,os,hashlib
import numpy as np
from mechanism_candidates import BASE,world
os.environ.setdefault('MPLCONFIGDIR','/tmp/regrip-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--cases',nargs='+',required=True);p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);fig,axes=plt.subplots(2,2,figsize=(13,9));identities={}
 for name in a.cases:
  src=BASE/'results'/name;meta=json.loads((src/'summary.json').read_text());cfg=json.loads((src/'config.json').read_text());m=json.loads((src/'mesh.json').read_text());local=np.array(m['local_positions_mm']);rows=read(src/'finger0.csv');t=np.array([float(r['time_s']) for r in rows]);q=np.array([np.fromstring(r['q_m'],sep=' ').reshape(-1,3) for r in rows]);stations=np.unique(local[:,0]);line=np.stack([q[:,(local[:,0]==x)&(local[:,2]==cfg['finger']['skin_thickness'])].mean(axis=1) for x in stations],axis=1);d=np.diff(line,axis=1);u=d/np.linalg.norm(d,axis=2)[:,:,None];angle=np.rad2deg(np.arccos(np.clip(np.sum(u[:,0]*u[:,-1],axis=1),-1,1)));rest=np.array([world(cfg,x) for x in local])*.001;tip=local[:,0]==100;motion=np.linalg.norm(q[:,tip].mean(axis=1)-rest[tip].mean(axis=0),axis=1)*1000
  if meta['status']!='RUN_COMPLETED_NOT_QUALIFIED':raise ValueError('no partial process visualization as complete result')
  axes[0,0].plot(t,angle,label=name);axes[0,1].plot(t,motion,label=name);k=int(np.argmin(abs(t-.75)));axes[1,0].plot(line[k,:,0]*1000,line[k,:,2]*1000,label=name+' t='+format(t[k],'.4f')+'s');axes[1,1].plot(t,[float(r['cable0_force_raw'])/meta['dt_s'] for r in rows],label=name)
  identities[name]=dict(source_commit=meta['source_commit'],binary_sha256=meta['binary_sha256'],dt_s=meta['dt_s'],config_sha256=meta['config_sha256'],input=dict(stroke_mm=meta.get('stroke_mm'),maximum_cable_force_N=meta.get('maximum_cable_force_N')),finger_csv_sha256=hashlib.sha256((src/'finger0.csv').read_bytes()).hexdigest())
 for ax,x,y in [(axes[0,0],'time s','root-to-tip chord angle deg'),(axes[0,1],'time s','width-mean tip displacement mm'),(axes[1,0],'world radial coordinate mm','world vertical coordinate mm'),(axes[1,1],'time s','cable0 impulse / dt N')]:ax.set_xlabel(x);ax.set_ylabel(y);ax.grid(True);ax.legend(fontsize=7)
 axes[1,0].set_aspect('equal');fig.suptitle('ACTUAL NATIVE SOFA ACCEPTED STATES — NOT QUALIFIED GRASP;deformation scale1')
 fig.text(.02,.02,'Fixed R30;E250MPa,nu0.3,mu0.3 assumed;input conditions in figure_identity.json;force/stroke models are distinct inputs',fontsize=8)
 fig.text(.02,.005,'Sources: '+'; '.join(k+'@'+v['source_commit'][:7]+' dt='+str(v['dt_s']) for k,v in identities.items()),fontsize=6);fig.tight_layout(rect=(0,.06,1,.95));fig.savefig(out/'mechanism_comparison.png',dpi=180);fig.savefig(out/'mechanism_comparison.svg');plt.close(fig)
 (out/'figure_identity.json').write_text(json.dumps(identities,indent=2));(out/'summary.json').write_text(json.dumps(dict(status='ACTUAL_STATE_FIGURES_NOT_QUALIFIED_RESULT',cases=a.cases,scope='no prescribed deformation,projection radial-Z;no contact area or pressure inferred',identities=identities),indent=2));print(str(out))
if __name__=='__main__':main()
