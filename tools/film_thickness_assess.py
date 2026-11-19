"""Preserved-data comparison: static geometry versus actual free SOFA coupon."""
import argparse,csv,json,os,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
 names=('20261119_thickness_full1780','20261119_thickness_profile1784','20261119_thickness_sofa1782','20261119_thickness_default_regression1783','20261119_thickness_clearance1787','20261119_thickness_profile_clearance1788','20261119_thickness_unload1785','20261119_thickness_profile_unload1789')
 summaries={n:json.loads((ROOT/'results'/('autonomous_film_'+n)/'summary.json').read_text()) for n in names}
 hashes={n:sha(ROOT/'results'/('autonomous_film_'+n)/'summary.json') for n in names}
 newer=ROOT/'results/autonomous_film_20261119_thickness_default_regression1783';older=ROOT/'results/autonomous_film_20261119_precise_static_cycle1755'
 regression={f:sha(newer/f)==sha(older/f) for f in ('contact.states.csv','contact.rows.csv','contact.wrench.csv','contact.newton.csv')}
 r=dict(status='ASSESSED_NOT_GRASP_QUALIFIED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_summary_sha256=hashes,default_static_byte_regression=regression,scope='actual passive geometry API plus independent static comparisons;NO dynamic thickness-contact certification/grasp',actual_sofa=summaries[names[2]]['status'],contact_area=None,pressure=None,holding_capacity=None,root_work=None)
 os.environ.setdefault('MPLCONFIGDIR','/tmp/regrip-matplotlib');import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,axes=plt.subplots(1,2,figsize=(10,4));metrics={}
 for n,label in zip(names[:2],('Original route','Profile4.5/outboard10')):
  path=ROOT/'results'/('autonomous_film_'+n);rows=list(csv.DictReader((path/'contact.states.csv').open()));q=np.array([np.fromstring(x['q'],sep=' ').reshape(-1,3) for x in rows]);T=np.array([float(x['T_N'])*1e6 for x in rows]);tip=q[:,100:105,2].mean(axis=1);mid=q[:,50:55,2].mean(axis=1);axes[0].plot(T,tip,label=label+' tip');axes[0].plot(T,mid,'--',label=label+' mid')
  metrics[n]=dict(last_skin_width_mean_tip_z_mm=float(tip[-1]),last_skin_width_mean_mid_z_mm=float(mid[-1]),last_contact_rows=int(rows[-1]['active_force_rows']),last_tendon_stroke_mm=summaries[n]['rest_cable_length_mm']-float(rows[-1]['cable_length_mm']),force_residual_N=float(rows[-1]['residual_N']))
 actual=ROOT/'results/autonomous_film_20261119_thickness_sofa1782/on';rows=list(csv.DictReader((actual/'actual.csv').open()));g=list(csv.DictReader((actual/'actual.csv.envelope.csv').open()));time=[float(x['time'])*1e6 for x in rows];mins=[min(float(x['buffered_envelope_gap_mm']) for x in g if float(x['time'])==float(row['time'])) for row in rows];axes[1].plot(time,mins);axes[0].set(xlabel='Tension per rail [uN]',ylabel='Local Skin displacement [mm]',title='Independent static constrained equilibria');axes[0].legend(fontsize=6);axes[1].set(xlabel='Physical time [us]',ylabel='Minimum envelope gap [mm]',title='Actual SOFA passive audit: NO contact force');fig.tight_layout();fig.savefig(out/'thickness_results.png');plt.close(fig)
 r['static_metrics']=metrics;r['source_status']={n:m['status'] for n,m in summaries.items()};r['figure_sha256']=sha(out/'thickness_results.png');write_json(out/'summary.json',r);print(json.dumps(r))
if __name__=='__main__':main()
