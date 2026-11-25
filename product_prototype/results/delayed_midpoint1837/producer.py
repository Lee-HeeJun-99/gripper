"""Test a necessary sign condition before proposing previous-sample damping."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from b3_cable_phase_pilot import parse
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--evaluation-rate',choices=('accepted','midpoint'),default='midpoint');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_cable_deformed1829';rows=list(csv.DictReader((src/'phases.csv').open()));metrics=[]
 for k in range(240):
  d={r['phase']:r for r in rows if int(r['step'])==k};b=d['build_end'];e=d['accepted_end'];P,_=parse(b['parent_J'],11,6);vb=np.fromstring(b['parent_v'],sep=' ').reshape(-1,6);ve=np.fromstring(e['parent_v'],sep=' ').reshape(-1,6)
  previous_rate=-float((P*vb).sum());accepted_rate=-float((P*ve).sum())
  # Infinitesimal b>0, tension may only decrease from its existing ceiling.
  # This coefficient is a local frozen-row power diagnostic, not a rerun.
  evaluated_rate=accepted_rate if a.evaluation_rate=='accepted' else (previous_rate+accepted_rate)/2
  coefficient=-min(previous_rate,0)*evaluated_rate
  metrics.append(dict(step=k,previous_frozen_parent_rate_m_s=previous_rate,accepted_frozen_parent_rate_m_s=accepted_rate,evaluated_frozen_parent_rate_m_s=evaluated_rate,incremental_power_per_damping_coefficient=coefficient))
 positive=[r for r in metrics if r['incremental_power_per_damping_coefficient']>0]
 d=dict(status='REJECT_UNCONDITIONAL_INCREMENTAL_PASSIVITY_CLAIM' if positive else 'NO_COUNTEREXAMPLE_IN_SAVED_PREFIX_NOT_PROOF',evaluation_rate=a.evaluation_rate,positive_incremental_power_samples=len(positive),samples=len(metrics),first_counterexample=positive[0] if positive else None,maximum_positive_coefficient=max(r['incremental_power_per_damping_coefficient'] for r in metrics),source_sha256=sha(Path(__file__)),input_sha256=sha(src/'phases.csv'),scope='Read-only frozen-row accepted or midpoint virtual-power sign test on actual baseline for hypothetical infinitesimal law deltaT=b*min(previous_rate,0). No gain or controller applied. Even midpoint generalized products are not a global coupled B3 kinetic/energy balance. Positive relative power does NOT imply absolute motor power positive, nor predict a controlled trajectory. Rejects unconditional sign argument, not all feedback. Original1829FAIL remains.')
 (out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
