"""Actual accepted constraint residuals;independent panel scales,no error floors."""
import argparse,json,os
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from layer_constraint_comparison import load
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);os.environ['MPLCONFIGDIR']=str(out/'mpl_cache');import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,axes=plt.subplots(2,2,figsize=(10,6));records=[]
 for col,case in enumerate(('layer_refined_interface1266','layer_clean_unscaled1273')):
  stats,q,v,t,_=load(case);q0=np.array(json.loads((BASE/'results'/case/'mesh.json').read_text())['q0']);lo=np.flatnonzero((q0[:,2]==.0002)&(q0[:,0]>0));hi=lo-1;Cq=q[1][:,hi]-q[0][:,lo]-[0,0,.000002];Cv=v[1][:,hi]-v[0][:,lo];axes[0,col].plot(t*1e3,abs(Cq).max(axis=(1,2))*1e9);axes[1,col].plot(t*1e3,abs(Cv).max(axis=(1,2))*1e6);axes[0,col].set_title('Actual Native '+('scaled termination' if col==0 else 'unscaled termination'));axes[0,col].set_ylabel('max |Cq| [nm]');axes[1,col].set_ylabel('max |Cv| [um/s]');axes[1,col].set_xlabel('Accepted physical time [ms]');records.append(stats)
 fig.suptitle('Same 20 ms / same numeric tolerance — panel scales independent; NOT time convergence');fig.tight_layout();fig.savefig(out/'actual_constraint_residuals.png',dpi=140);fig.savefig(out/'actual_constraint_residuals.svg');plt.close(fig);d=dict(status='ACTUAL_ACCEPTED_STATE_FIGURES_ONLY',scope='No interpolation,error floor,prescribed state or conceptual grasp geometry. Independent panel scales explicitly labeled. Not physical product qualification.',input_hashes={str((BASE/'results'/c/'layer0.csv').relative_to(BASE)):sha(BASE/'results'/c/'layer0.csv') for c in ('layer_refined_interface1266','layer_clean_unscaled1273')},source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d))
if __name__=='__main__':main()
