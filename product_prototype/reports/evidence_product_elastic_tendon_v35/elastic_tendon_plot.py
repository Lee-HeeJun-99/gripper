"""Actual Native accepted states/API values, not concept geometry."""
import argparse,json,subprocess
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from analyse import BASE,sha
from native_elastic_tendon import exact

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 inputs={name:BASE/'results'/name/'summary.json' for name in ('b3_native_elastic_tendon693','b3_native_elastic_newton695','b3_native_spring_energy697','b3_native_spring_potential_adapter699')};data={k:json.loads(v.read_text()) for k,v in inputs.items()}
 fig,axes=plt.subplots(2,2,figsize=(11,7))
 for key,label in [('b3_native_elastic_tendon693','Native Newmark'),('b3_native_elastic_newton695','Native BDF1+Newton')]:
  r=next(r for r in data[key]['records'] if r['mode']=='taut_release' and r['dt_s']==.00025);t=np.asarray([f['time_s'] for f in r['frames']]);q=[f['q'][1][2]*1000 for f in r['frames']];v=[f['v'][1][2] for f in r['frames']]
  axes[0,0].plot(t*1000,q,label=label);axes[0,1].plot(t*1000,v,label=label)
 t=np.linspace(0,.008,500);ref=np.asarray([exact(x) for x in t]);axes[0,0].plot(t*1000,ref[:,0]*1000,'k--',label='Independent analytic elastic string');axes[0,1].plot(t*1000,ref[:,1],'k--',label='Independent analytic elastic string')
 for key,label in [('b3_native_spring_energy697','Stock Native potential API'),('b3_native_spring_potential_adapter699','Potential-only adapter API')]:
  r=next(r for r in data[key]['records'] if r['mode']=='taut_release');frames=r['frames'];value='actual_native_potential_J' if '697' in key else 'actual_potential_J';axes[1,0].plot([f['time_s']*1000 for f in frames],[f[value]*1000 for f in frames],label=label)
 frames=data['b3_native_spring_energy697']['records'][0]['frames'];axes[1,0].plot([f['time_s']*1000 for f in frames],[f['independent_unilateral_potential_J']*1000 for f in frames],'k--',label='Accepted-q unilateral reconstruction')
 for key,label in [('b3_native_elastic_tendon693','Newmark physical inventory'),('b3_native_elastic_newton695','BDF1 physical inventory')]:
  r=next(r for r in data[key]['records'] if r['mode']=='taut_release' and r['dt_s']==.00025);axes[1,1].plot([f['time_s']*1000 for f in r['frames']],[f['reconstructed_energy_J']*1000 for f in r['frames']],label=label)
 axes[1,1].axhline(5.,color='k',ls='--',label='Initial physical energy')
 for ax,y in zip(axes.flat,('Moving point displacement [mm]','Velocity [m/s]','Potential [mJ]','Physical energy reconstruction [mJ]')):ax.set_xlabel('Physical time [ms]');ax.set_ylabel(y);ax.legend(fontsize=7);ax.grid(alpha=.3)
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip()
 fig.suptitle('ACTUAL Native SOFA26.06 accepted states/API | dt250us | m1g, assumed k100N/m\nNo damping/gravity/contact; elastic string, NOT prescribed-tension B3; time Gate FAIL',fontsize=10)
 fig.text(.01,.005,'Source parent '+commit+'; frozen producers/scene/binary hashes in cases693/695/697/699',fontsize=7);fig.tight_layout(rect=[0,.03,1,.92]);fig.savefig(out/'actual_native_elastic_tendon.png',dpi=160);plt.close(fig)
 result=dict(status='ACTUAL_NATIVE_VISUALIZATION_NOT_PHYSICS_GATE',source_commit=commit,producer_sha256=sha(Path(__file__)),input_hashes={k:sha(v) for k,v in inputs.items()},figure_sha256=sha(out/'actual_native_elastic_tendon.png'))
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
