"""Same IVP passive stage-label A/B;not a solver/time-convergence experiment."""
import argparse,csv,json,shutil
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();cases=['20261118_lateral_after252_four_actual1494','20261118_lateral_stage_labels1496'];data=[]
 for name in cases:
  path=ROOT/'results'/('autonomous_film_'+name);m=json.loads((path/'summary.json').read_text())
  if m['status']!='PASS' or m['process']['exit_code'] or m['sofa_errors']:raise ValueError('qualified actual A/B required')
  for f,d in m['raw_hashes'].items():
   if sha(path/f)!=d:raise ValueError('actual raw changed')
  data.append((path,m))
 x,y=data;changed={k for k in set(x[1]['source_hashes'])|set(y[1]['source_hashes']) if x[1]['source_hashes'].get(k)!=y[1]['source_hashes'].get(k)}
 if changed!={'models/film_three_finger/ThreeFilmOwner.cpp'}:raise ValueError('passive-only expected source change differs')
 files=['three.states.csv']+[f'{prefix}_{f}.csv' for prefix in ('film','displacement') for f in range(3)];exact={f:(x[0]/f).read_bytes()==(y[0]/f).read_bytes() for f in files};rows=[list(csv.DictReader((z[0]/'three.rows.csv').open())) for z in data];oldkeys=list(rows[0][0]);rowExact=rows[0]==[{k:r[k] for k in oldkeys} for r in rows[1]]
 checkpoints=[]
 for n in range(127,131):
  xx=(x[0]/f'three.checkpoint_{n}.txt').read_text().split();yy=(y[0]/f'three.checkpoint_{n}.txt').read_text().split();checkpoints.append(xx[:4]+xx[5:]==yy[:4]+yy[5:])
 labels=all(r['force_kind']==('acceleration_constraint' if r['stage']=='0' else 'collocation_stage') and float(r['used_h_s'])>0 for r in rows[1])
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if all(exact.values()) and rowExact and all(checkpoints) and labels else 'FAIL',scope='actual passive stage-label query/state/physical checkpoint purity ONLY',summaries=[sha(z[0]/'summary.json') for z in data],source_changed=sorted(changed),byte_exact_journals=exact,all_old_row_columns_exact=rowExact,physical_checkpoint_tokens_exact=checkpoints,stage_labels_valid=labels,runtime_s=[z[1]['process']['runtime_s'] for z in data],runtime_note='single A/B only;NOT a speedup/overhead benchmark',api_gate=1e-12,whole_time='FAIL remains',whole_energy='BLOCKED');write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
