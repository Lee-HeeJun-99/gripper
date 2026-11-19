"""Scientific plots from accepted native CSV paths;no prescribed deformation."""
import argparse,csv,json,hashlib,os,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import cable_node
BASE=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);os.environ.setdefault('MPLCONFIGDIR','/tmp/regrip-matplotlib');import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 cases=['cable_B_single_out_051','cable_A_single_surface_052','cable_D_pair_out_054','rigidified_out14_actuation_131'];fig,axes=plt.subplots(3,1,figsize=(9,10));metadata={}
 for case in cases:
  src=BASE/'results'/case;rows=list(csv.DictReader((src/'finger0.csv').open()));tree=ET.parse(src/'scene.scn');node=cable_node(tree,0,0);pull=np.fromstring(node.find('CableConstraint').get('pullPoint'),sep=' ');rest=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);L0=np.linalg.norm(np.diff(np.vstack([pull,rest]),axis=0),axis=1).sum();t=np.array([float(r['time_s']) for r in rows]);stroke=np.array([L0-np.linalg.norm(np.diff(np.vstack([pull,np.fromstring(r['guide0_q_m'],sep=' ').reshape(-1,3)]),axis=0),axis=1).sum() for r in rows])*1000;dt=json.loads((src/'summary.json').read_text())['dt_s'];F=np.array([float(r['cable0_force_raw'])/dt for r in rows]);mask=t<=1+1e-12;zoom=(t>=.95)&mask;axes[0].plot(t[mask],stroke[mask],label=case);axes[1].plot(t[zoom],stroke[zoom],'.-',ms=2,label=case);axes[2].plot(t[mask],F[mask],label=case);metadata[case]=dict(csv_sha256=sha(src/'finger0.csv'),summary_sha256=sha(src/'summary.json'))
 command=np.array([float(r['command_m']) for r in rows])*1000;axes[0].plot(t[mask],command[mask],'k--',label='C2 command,not deformation');axes[0].set(ylabel='Actual path shortening mm');axes[1].set(ylabel='Hold path shortening mm',xlabel='Actual accepted time s');axes[2].set(ylabel='Cable tension N = impulse/dt',xlabel='Actual accepted time s')
 for ax in axes:ax.legend(fontsize=7);ax.grid(alpha=.2)
 fig.suptitle('Native accepted-state cable paths\nRigid guide case adds hardware mass/rigidity;NOT matched-model superiority');fig.tight_layout();fig.savefig(out/'cable_coupling.png');plt.close(fig);(out/'summary.json').write_text(json.dumps(dict(scope='actual CSV path plot,command line explicitly distinguished;not grasp certification',sources=metadata,source_sha256=sha(Path(__file__))),indent=2))
if __name__=='__main__':main()
