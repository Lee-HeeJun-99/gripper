"""Byte-exact physical CSV comparison for a passive three-film commit guard."""
import argparse,json,shutil
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--before',required=True);p.add_argument('--after',required=True);a=p.parse_args();folders=[ROOT/'results'/('autonomous_film_'+name) for name in (a.before,a.after)];meta=[json.loads((d/'identity.json').read_text()) for d in folders]
 if any(json.loads((d/'summary.json').read_text())['status']!='PASS' for d in folders):raise ValueError('complete actual executions required')
 changed=[k for k in set(meta[0]['sources'])|set(meta[1]['sources']) if meta[0]['sources'].get(k)!=meta[1]['sources'].get(k)]
 if changed!=['models/film_three_finger/ThreeFilmOwner.cpp']:raise ValueError('not the isolated passive actual commit-guard change:'+str(changed))
 for key in ('reference','reference_state_sha256','dt','steps','geometry','external_force_N','tension_per_rail_N','gravity','friction','self_collision'):
  if meta[0][key]!=meta[1][key]:raise ValueError('physical configuration changed:'+key)
 names=['three.states.csv','three.rows.csv','three.policy.csv',*[f'film_{i}.csv' for i in range(3)],*[f'displacement_{i}.csv' for i in range(3)]];checks={name:dict(before=sha(folders[0]/name),after=sha(folders[1]/name)) for name in names}
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if all(v['before']==v['after'] for v in checks.values()) else 'FAIL',scope='nine physical CSVs exact across isolated read-only actual-body commit guard;NOT overall physics certificate',before=a.before,after=a.after,changed_source=changed,files=checks);write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],checked=len(checks))))
if __name__=='__main__':main()
