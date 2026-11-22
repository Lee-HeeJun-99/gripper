"""Independent response-row momentum audit;preserve raw rigid-journal discrepancy."""
import argparse,csv,json,subprocess,time
from pathlib import Path
import numpy as np
from analyse import BASE,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.case;meta=json.loads((src/'summary.json').read_text());start=time.monotonic();rows=list(csv.DictReader((src/'eyelet.csv').open()));totals={};pairs={};nonzero=0
 for r in csv.DictReader((src/'response.csv').open()):
  if not r.get('time_s') or not r.get('object_impulse_Ns_Nms'):continue
  t=float(r['time_s']);value=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ')
  if len(value)!=6:raise ValueError('incomplete response journal row')
  totals[t]=totals.get(t,np.zeros(6))+value
  if float(r['lambda_Ns']):
   nonzero+=1;key=(r['model0'],r['model1']);pairs[key]=pairs.get(key,0)+1
 q=np.array([np.fromstring(r['rigid_q'],sep=' ') for r in rows]);v=np.array([np.fromstring(r['rigid_v'],sep=' ') for r in rows]);imp=np.array([totals.get(float(r['time_s']),np.zeros(6)) for r in rows]);journal=np.array([np.fromstring(r['object_impulse_Ns_Nms'],sep=' ') for r in rows]);m=meta['ASSUMED_eyelet_mass_kg'];initial=np.array(meta['initial_v']);delta=m*(v[:,:3]-np.vstack([initial[:3],v[:-1,:3]]));error=float(np.max(abs(delta-imp[:,:3])));discrepancy=float(np.max(abs(journal-imp)));criterion=5e-12
 result=dict(status='RESPONSE_ROW_MOMENTUM_SCOPE_PASS' if error<=criterion else 'FAIL_RESPONSE_ROW_MOMENTUM',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(p):sha(p) for p in (Path(__file__),src/'summary.json',src/'eyelet.csv',src/'response.csv')},rows=len(rows),nonzero_response_rows=nonzero,active_model_pairs=[dict(model0=k[0],model1=k[1],nonzero_rows=n) for k,n in pairs.items()],maximum_linear_momentum_residual_Ns=error,diagnostic_criterion_Ns=criterion,maximum_rigid_vs_response_impulse_discrepancy=discrepancy,rigid_journal_impulse_qualified=bool(discrepancy<=criterion),maximum_axial_travel_mm=float(np.max(abs(q[:,2]))*1000),runtime_s=time.monotonic()-start,fabrication_ready=False,scope='Actual response rows vs mΔv at SAME accepted times,massassumption unchanged. Raw rigid journal discrepancy is preserved,NOT attributed to physics without observer-contract evidence. No angular/wholeenergy/time/impactlaw or actualjoint/retentionstrength qualification;position stop is not a restitution law.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
