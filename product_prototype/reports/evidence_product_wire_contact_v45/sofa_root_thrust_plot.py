"""Actual accepted Native coupon journals,including invalid prefix,not concept imagery."""
import argparse,csv,json,os,subprocess
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/regrip-native-thrust-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from analyse import BASE,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);cases=['product_root_native810','product_root_native_strict815','product_root_intersection817'];labels=['LocalMinDistance/defaultpolicy','LocalMinDistance/unscaled+allVerified (NaN prefix)','MinProximity/unscaled+allVerified'];fig,axes=plt.subplots(2,2,figsize=(12,8));inputs=[Path(__file__)];records=[]
 for case,label in zip(cases,labels):
  file=BASE/'results'/case/'wheel.csv';inputs.append(file);rows=list(csv.DictReader(file.open()));t=np.array([float(r['time_s']) for r in rows]);q=np.array([np.fromstring(r['rigid_q'],sep=' ') for r in rows]);v=np.array([np.fromstring(r['rigid_v'],sep=' ') for r in rows]);imp=np.array([np.fromstring(r['object_impulse_Ns_Nms'],sep=' ') for r in rows]);finite=np.isfinite(q).all(axis=1)&np.isfinite(v).all(axis=1);axes[0,0].plot(t[finite]*1000,q[finite,2]*1000,label=label);axes[0,1].plot(t[finite]*1000,v[finite,2]*1000,label=label);axes[1,0].plot(t[finite]*1000,np.linalg.norm(v[finite,3:],axis=1),label=label);axes[1,1].plot(t[finite]*1000,np.cumsum(imp[finite,2]),label=label);records.append(dict(case=case,finite_rows=int(finite.sum()),nonfinite_rows=int((~finite).sum())))
  if (~finite).any():
   for ax in axes.flat:ax.axvline(t[~finite][0]*1000,color='red',linestyle=':',alpha=.6)
 for ax,y in zip(axes.flat,('Axial position [mm]','Axial velocity [mm/s]','Angular speed [rad/s]','Cumulative axial impulse [Ns]')):ax.set(xlabel='Actual accepted time [ms]',ylabel=y);ax.grid();ax.legend(fontsize=6)
 fig.suptitle('Actual Native SOFA v26.06.00 coupon / dt0.25ms / BE / fixed annular lands\nResearch m=0.1g,v0=10mm/s,gravity0,mu0;no wire/fork/axle/holding qualification');fig.tight_layout();fig.savefig(out/'native_thrust_policy.png',dpi=160);plt.close(fig);d=dict(status='ACTUAL_NATIVE_JOURNAL_FIGURE_NOT_PHYSICS_PASS',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(x):sha(x) for x in inputs},records=records,figure_sha256=sha(out/'native_thrust_policy.png'),scope='Onlyactualjournalq/v/impulses;nonfiniteprefix shownwithredline,norepaired/interpolated/prescribedstates. Finiteplotsarenotfulltime/energy/convergencecertification.',fabrication_ready=False)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
