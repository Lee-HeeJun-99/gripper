"""Same-binary one-factor mass-input counterfactual;preserves actual FAIL."""
import argparse,csv,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--actual',required=True);p.add_argument('--public',required=True);p.add_argument('--model',required=True);a=p.parse_args();paths=[ROOT/'results'/('autonomous_film_'+s) for s in (a.actual,a.public,a.model)];meta=[json.loads((p/'summary.json').read_text()) for p in paths];rows=[list(csv.DictReader((paths[0]/'three.states.csv').open()))]+[list(csv.DictReader((p/'states.csv').open())) for p in paths[1:]]
 if meta[1]['status']!='PASS' or meta[2]['status']!='PASS' or meta[1]['binary_sha256']!=meta[2]['binary_sha256'] or meta[1]['sources']!=meta[2]['sources'] or not meta[1].get('public_mass_identity') or meta[2].get('public_mass_identity'):raise ValueError('same binary/source,public ON/model OFF required')
 for k in ('steps','duration','maximum_tension_N','control','initial','exact_order_fallback','adaptive_gap_control'):
  if meta[1][k]!=meta[2][k]:raise ValueError('more than one factor changed:'+k)
 if any(len(x)!=meta[1]['steps'] for x in rows) or any(max(abs(float(x['time'])-float(y['time'])) for x,y in zip(rows[0],r))>1e-12 for r in rows[1:]):raise ValueError('incomplete/alignment mismatch')
 errors={label:{k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(rows[0],r)) for k in ('q','v')} for label,r in zip(('public','model'),rows[1:])}
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if max(errors['public'].values())==0 and errors['model']['v']>1e-12 else 'FAIL',scope='same-binary one-factor evidence for independent API comparison mismatch,NOT general time/energy/grasp',actual=a.actual,public=a.public,model=a.model,errors=errors,absolute_api_gate=1e-12,actual_original_status=meta[0]['status'],raw_hashes={p.name:{name:sha(p/name) for name in ('summary.json','three.states.csv') if (p/name).exists()} for p in paths},interpretation='actual public nodal mass doubles,not model reconstruction,are required for EXACT same-input reference;no tolerance/physical actual-state changes')
 write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
