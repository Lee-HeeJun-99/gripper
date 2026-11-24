"""Scientific plot of accepted no-object Native data;virtual sphere explicit."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/opposed_release1401';ref=BASE/'results/opposed_zero_reference1403';rows=list(csv.DictReader((src/'finger0.csv').open()));zero=list(csv.DictReader((ref/'finger0.csv').open()));local=np.array(json.loads((src/'mesh.json').read_text())['local_positions_mm']);stations=np.unique(local[:,0]);masks=[(local[:,0]==s)&(local[:,2]==.1) for s in stations];q0=np.fromstring(ET.parse(src/'scene.scn').getroot().find("Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)
 def centre(q):return np.array([q[m].mean(0) for m in masks])*1000
 def angle(q):
  d=np.diff(centre(q)[:,[0,2]],axis=0);return float(np.degrees(np.arctan2(-d[-1,0],-d[-1,1])))
 t=np.array([float(r['time_s']) for r in rows]);qs=[np.fromstring(r['q_m'],sep=' ').reshape(-1,3) for r in rows];fig,axes=plt.subplots(1,2,figsize=(11,5));left=axes[0];left.plot(t,[angle(q) for q in qs],label='Accepted Skin tip tangent',color='tab:blue');left.set(xlabel='Physical time [s]',ylabel='Projected tip tangent [deg]');right=left.twinx();right.plot(t,[float(r['command_N']) for r in rows],color='tab:orange',ls='--',label='Cable input / cable');right.set_ylabel('Input force per cable [N]');left.axvline(.6,color='grey',ls=':');left.axvline(.9,color='grey',ls=':');left.set_title('Actual Native no-object open / unload');left.legend(loc='upper right');right.legend(loc='lower left');left.grid(alpha=.2)
 ax=axes[1];p0=centre(q0);ax.plot(p0[:,0],p0[:,2],'--',color='grey',label='Manufactured rest (reference)')
 for time in (.5,.6,.9,1.2):
  i=int(np.argmin(abs(t-time)));p1=centre(qs[i]);ax.plot(p1[:,0],p1[:,2],label=f'Accepted t={t[i]:.1f}s')
 pz=centre(np.fromstring(zero[-1]['q_m'],sep=' ').reshape(-1,3));ax.plot(pz[:,0],pz[:,2],':',color='black',lw=2,label='Zero-input gravity reference 1.2s');ax.add_patch(plt.Circle((0,-65),30,fill=False,ls=':',color='black',label='VIRTUAL R30; no sphere in Native'));ax.set(xlabel='Radial coordinate [mm]',ylabel='World z [mm]',title='Width-mean Skin centreline; NOT grasp');ax.axis('equal');ax.grid(alpha=.2);ax.legend(fontsize=7);fig.suptitle('Actual no-object Native actuation; time/mesh/hardware NOT qualified',fontsize=10);fig.tight_layout()
 for suffix in ('png','svg'):fig.savefig(out/f'accepted_open_release.{suffix}',dpi=150)
 plt.close(fig);d=dict(status='ACTUAL_ACCEPTED_STATE_FIGURE_ONLY',scope='Restreference/zero-inputreference/virtualsphere explicitly distinguished. No actualobjectcontact orprescribed dynamicshape. No Wrapping/Holding claim.',input_hashes={str(f.relative_to(BASE)):sha(f) for case in (src,ref) for f in (case/'finger0.csv',case/'scene.scn')});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(str(out/'accepted_open_release.png'))
if __name__=='__main__':main()
