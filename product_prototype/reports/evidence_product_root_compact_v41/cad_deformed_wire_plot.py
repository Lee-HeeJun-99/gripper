"""Clearly labelled old accepted-state / hypothetical-wire overlay and sampled gap plots."""
import argparse,csv,json,subprocess,os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/regrip-wire-mpl')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from manufacturing_assembly import BASE,sha
from generate import mesh

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/product_deformed_frozen747_analysis/summary.json';full=BASE/'results/product_wire_object_all746/summary.json';d=json.loads(src.read_text());allframes=json.loads(full.read_text());old=BASE/'results/b3_alarm_window485';finger=old/'finger0.csv';obj=old/'object.csv';cfgpath=old/'config.json';cfg=json.loads(cfgpath.read_text());nodes=np.asarray(mesh(cfg)[0]);rows=list(csv.DictReader(finger.open()));objects=list(csv.DictReader(obj.open()));time=np.array([float(r['time_s']) for r in rows]);fig,axs=plt.subplots(1,2,figsize=(13,5))
 for index,t in enumerate((d['selected_times_s'][0],d['selected_times_s'][2])):
  k=int(np.argmin(abs(time-t)));q=np.fromstring(rows[k]['q_m'],sep=' ').reshape(-1,3)*1000;skin=nodes[:,2]>=0;line=np.array([q[skin&(nodes[:,0]==x)].mean(axis=0) for x in np.unique(nodes[skin,0])]);axs[0].plot(line[:,0],line[:,2],label=f'OLD Native skin width-mean t={time[k]:.4f}s')
  r=next(r for r in d['records'] if r['finger']==0 and r['cable']==0 and r['time_s']==t);route=np.array(r['route_mm']);axs[0].plot(route[:,0],route[:,2],'--',label=f'NEW hypothetical wire t={t:.4f}s')
  centre=np.fromstring(objects[k]['rigid_q'],sep=' ')[:3]*1000;axs[0].add_patch(Circle(centre[[0,2]],cfg['simulation']['sphere_radius_mm'],fill=False,alpha=.4))
 axs[0].set_aspect('equal');axs[0].set_xlabel('world X projection [mm]');axs[0].set_ylabel('world Z [mm]');axs[0].set_title('Old accepted Skin + proposed wire OVERLAY\nNot candidate dynamics/contact proof');axs[0].legend(fontsize=7)
 times=np.array(allframes['selected_times_s']);gaps=np.array([r['sphere_gap_lower_bound_mm'] for r in allframes['records']]).reshape(-1,6)
 axs[1].plot(times,gaps.min(axis=1));axs[1].axhline(0,color='red',linestyle=':');axs[1].set_xlabel('old accepted physical time [s]');axs[1].set_ylabel('minimum sampled wire/sphere gap lower bound [mm]');axs[1].set_title('1200saved frames / 6proposed wires\nNot continuous-time clearance');fig.suptitle('Frozen OLD485 dt=2.5ms;NEW V21 wire diameter0.5 / proposed bendR2mm');fig.tight_layout();path=out/'accepted_state_wire_screen.png';fig.savefig(path,dpi=160);plt.close(fig)
 result=dict(status='LABELLED_FROZEN_MOTION_VISUALIZATION_NOT_SOFA_CANDIDATE_RESULT',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),producer_sha256=sha(__file__),input_hashes={str(p.relative_to(BASE.parent)):sha(p) for p in (src,full,finger,obj,cfgpath)},figure_sha256=sha(path),actual_old_native_data=True,new_wire_is_design_overlay=True)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(path)
if __name__=='__main__':main()
