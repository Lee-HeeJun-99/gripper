"""Read-only one-factor ACTUAL SOFA transmission comparison; no contact claims."""
import argparse,csv,json,os,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from film_transmission_linear import shape
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
 cases=('20261118_transmission_common_base1144','20261118_transmission_bond10_1150','20261118_transmission_offset_reverse1151')
 # Resolve the baseline name without guessing or selecting an incomplete run.
 candidates=list((ROOT/'results').glob('*1144'))
 if len(candidates)!=1:raise ValueError('unique actual baseline1144 required')
 cases=(candidates[0].name.removeprefix('autonomous_film_'),)+cases[1:]
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');records=[];histories=[];proofs=[]
 for case in cases:
  src=ROOT/'results'/('autonomous_film_'+case);proof=json.loads((src/'summary.json').read_text())
  if proof['status']!='PASS' or proof['process']['exit_code']:raise ValueError('completed strict actual API case required')
  for name,digest in proof['raw_hashes'].items():
   if sha(src/name)!=digest:raise ValueError('immutable actual data changed')
  rows=list(csv.DictReader((src/'actual.csv').open()));history=[]
  for row in rows:history.append(dict(time=float(row['time']),**shape(np.fromstring(row['q'],sep=' '))))
  records.append(dict(case=case,summary_sha256=sha(src/'summary.json'),binary_sha256=proof['binary_sha256'],endpoint=history[-1],bond_stiffness_N_mm=proof['bond_stiffness_N_mm'],guide_offset_mm=proof['guide_offset_mm']))
  histories.append(history);proofs.append(proof)
 for key in ('mass_kg','material_volume_mm3','duration_s'):
  if any(p.get(key)!=proofs[0].get(key) for p in proofs):raise ValueError('comparison input differs: '+key)
 os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,axes=plt.subplots(2,2,figsize=(11,8))
 for history,record in zip(histories,records):
  for ax,key in zip(axes.flat,('skin_tip_z','skin_centre_tip_z','left_tip_z','skin_root_tip_total_angle_rad')):
   ax.plot([r['time']*1000 for r in history],[r[key] for r in history],label=record['case'].split('transmission_')[-1]);ax.set_xlabel('actual time [ms]');ax.set_ylabel(key)
 for ax in axes.flat:ax.legend(fontsize=7)
 fig.suptitle('Actual SOFA single-film, no object/contact; fixed tension NOT matched work\nTmax=0.0001 N/rail; source f70a46f + archived campaign sources');fig.tight_layout();fig.savefig(out/'actual_comparison.png',dpi=150);plt.close(fig)
 result=dict(status='PASS',scope='read-only actual single-film one-factor comparison;NOT wrapping/contact/holding superiority',cases=records,contact_area=None,contact_pressure=None,holding_capacity=None,matched_actuation_work=False,final_design='NOT SELECTED',figure_sha256=sha(out/'actual_comparison.png'))
 write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
