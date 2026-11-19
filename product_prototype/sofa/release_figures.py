"""Clipped-view actual release states;object coordinates are NEVER relocated."""
import argparse,csv,json,hashlib,os,xml.etree.ElementTree as ET
import numpy as np
from mechanism_candidates import BASE
os.environ.setdefault('MPLCONFIGDIR','/tmp/regrip-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);m=json.loads((src/'summary.json').read_text());mesh=json.loads((src/'mesh.json').read_text());tri=np.array(mesh['triangles']);cfg=json.loads((src/'config.json').read_text());obj=read(src/'object.csv');t=np.array([float(r['time_s']) for r in obj]);oq=np.array([np.fromstring(r['rigid_q'],sep=' ')[:3] for r in obj])*1000;q=[];rows0=None
 if m['status']!='RUN_COMPLETED_NOT_QUALIFIED':raise ValueError('complete actual trial required')
 for f in range(m['fingers']):
  rows=read(src/f'finger{f}.csv');q.append(np.array([np.fromstring(r['q_m'],sep=' ').reshape(-1,3) for r in rows])*1000)
  if f==0:rows0=rows
 P=np.array([[.7071067811865476,-.7071067811865476,0],[.4082482904638631,.4082482904638631,.8164965809277261]]);fig,axes=plt.subplots(1,4,figsize=(14,5));frames=[]
 for ax,target in zip(axes,(.5,2.,2.3875,3.)):
  k=int(np.argmin(abs(t-target)));xy=oq[k]@P.T
  for f,points in enumerate(q):ax.add_collection(PolyCollection(points[k,tri]@P.T,facecolor=('teal','goldenrod','royalblue')[f],edgecolor='black',linewidth=.1,alpha=.6))
  ax.add_patch(plt.Circle(xy,cfg['simulation']['sphere_radius_mm'],fill=False,color='crimson'));ax.set(xlim=(-90,90),ylim=(-140,30),xlabel='projected mm',ylabel='projected mm');ax.set_aspect('equal');ax.set_title(f'Actual t={t[k]:.4f}s')
  if not(-90<=xy[0]<=90 and -140<=xy[1]<=30):ax.text(.02,.02,f'Object outside fixed view\nactual z={oq[k,2]:.1f}mm',transform=ax.transAxes,color='crimson',fontsize=8)
  frames.append(dict(actual_time_s=float(t[k]),object_xyz_mm=oq[k].tolist(),viewport='fixed projection limits;coordinates unchanged;out-of-view body annotated'))
 fig.suptitle(f'ACTUAL SOFA RELEASE — NOT QUALIFIED;scale1;fixed clipped viewport\ndt={m["dt_s"]}s;Tmax={m.get("maximum_cable_force_N")}N;R30/50g,mu0.3 assumed;stateSHA={hashlib.sha256((src/"finger0.csv").read_bytes()).hexdigest()[:12]};binarySHA={m["binary_sha256"][:12]}',fontsize=9);fig.tight_layout(rect=(0,0,1,.87));fig.savefig(out/'actual_release_states.png',dpi=180);fig.savefig(out/'actual_release_states.svg');plt.close(fig)
 skin=np.zeros(len(t));index={x:k for k,x in enumerate(t)}
 for r in read(src/'response_rows.csv'):
  if any('/object/' in r[x] for x in ('model0','model1')) and any('/skinCollision/' in r[x] for x in ('model0','model1')):skin[index[float(r['time_s'])]]+=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ')[2]/m['dt_s']
 fig,axes=plt.subplots(3,1,figsize=(9,8),sharex=True);axes[0].plot(t,[float(r['command_N']) for r in rows0]);axes[0].set_ylabel('command N/cable');axes[1].plot(t,skin);axes[1].axhline(.05*9.81,ls='--',color='grey',label='weight');axes[1].legend();axes[1].set_ylabel('Skin object Fz N');axes[2].plot(t,oq[:,2]-cfg['simulation']['sphere_center_mm'][2]);axes[2].set_yscale('symlog',linthresh=2);axes[2].set(ylabel='object dz mm (symlog)',xlabel='actual time s')
 for ax in axes:ax.grid(True)
 fig.suptitle('Actual native force/hold/unload/free-fall — NOT energy/time convergence or Lift PASS');fig.tight_layout();fig.savefig(out/'release_journal.png',dpi=180);plt.close(fig);identity=dict(status='ACTUAL_STATE_VISUALIZATION_NOT_QUALIFIED',case=a.case,frames=frames,source_commit=m['source_commit'],binary_sha256=m['binary_sha256'],dt_s=m['dt_s'],source_state_sha256=hashlib.sha256((src/'finger0.csv').read_bytes()).hexdigest(),source_sha256=hashlib.sha256(__import__('pathlib').Path(__file__).read_bytes()).hexdigest());(out/'summary.json').write_text(json.dumps(identity,indent=2));print(str(out))
if __name__=='__main__':main()
