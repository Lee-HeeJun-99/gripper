"""Causal comparison:nonlinear3film versus frozen symmetric modal reference."""
import argparse,csv,json,math,os,shutil
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs=3,required=True);p.add_argument('--frozen',required=True);a=p.parse_args();observed={};inputs={}
 for case in a.cases:
  src=ROOT/'results'/('autonomous_film_'+case);meta=json.loads((src/'summary.json').read_text())
  if meta['status']!='PASS':raise ValueError('completed independent nonlinear reference required')
  observed[meta['steps']]=float(list(csv.DictReader((src/'states.csv').open()))[-1]['U_rails']);inputs[case]=dict(summary=sha(src/'summary.json'),states=sha(src/'states.csv'))
 if set(observed)!={4,8,16}:raise ValueError('known4/8/16 diagnostic only')
 src=ROOT/'results'/('autonomous_film_'+a.frozen)
 if json.loads((src/'summary.json').read_text())['status']!='PASS':raise ValueError('completed independent frozen calculation required')
 rows=list(csv.DictReader((src/'modal.csv').open()));frozen={int(r['steps']):float(r['U_rails']) for r in rows};reference=frozen[0];order=math.log(abs((observed[4]-observed[8])/(observed[8]-observed[16])),2);frozen_order=math.log(abs((frozen[4]-frozen[8])/(frozen[8]-frozen[16])),2)
 result=dict(status='OBSERVED',scope='independent frozen linear symmetric sector versus nonlinear reference;NOT actual SOFA/causal proof/fulltime certificate',observed_order=order,frozen_order=frozen_order,nonlinear_U_rails=observed,frozen_U_rails=frozen,frozen_to_nonlinear_relative={n:abs(frozen[n]-observed[n])/abs(observed[n]) for n in (4,8,16)},omega_max_rad_s=float(rows[0]['omega_max']),hypotheses=dict(event_time='not required:these trials start touching and have no impact',time_discretization='supported if frozen fixed-normal model reproduces fourth-order rail energy trend',roundoff='small absolute energy ALONE is not evidence of roundoff;raw errors and fail remain',remaining='frozen sector omits nonlinear feature changes/in-plane dynamics;not full causal proof'),old_gate='855 remains FAIL;no absolute-energy exemption',inputs=inputs,frozen_hashes={f:sha(src/f) for f in ('summary.json','modal.csv')})
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,axes=plt.subplots(1,2,figsize=(10,4));n=[4,8,16];axes[0].plot(n,[observed[k] for k in n],'o-',label='nonlinear FEM');axes[0].plot(n,[frozen[k] for k in n],'x--',label='frozen fixed-normal');axes[0].axhline(reference,color='k',ls=':',label='frozen modal reference');axes[0].set_ylabel('Rail energy [N mm]');axes[1].loglog(n,[abs(observed[k]-reference)/abs(reference) for k in n],'o-');axes[1].set_ylabel('Error versus FROZEN reference (not full physics gate)')
 for ax in axes:ax.set_xlabel('steps over100us');ax.grid()
 axes[0].legend(fontsize=7);fig.suptitle('Independent FEM diagnostic;NOT actual SOFA/grasp qualification');fig.tight_layout();fig.savefig(out/'rail_time_diagnostic.png',dpi=160);plt.close(fig);write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k in ('observed_order','frozen_order','frozen_to_nonlinear_relative','omega_max_rad_s')},indent=2))
if __name__=='__main__':main()
