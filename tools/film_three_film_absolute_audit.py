"""Restore original absolute1e-12 API gate without editing old run records."""
import argparse,json,shutil
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args();cases={}
 for case in a.cases:
  path=ROOT/'results'/('autonomous_film_'+case);m=json.loads((path/'summary.json').read_text())
  if m['process']['exit_code']!=0 or m['sofa_errors']:raise ValueError('absolute comparison never overrides runtime failure')
  for n,h in m['raw_hashes'].items():
   if sha(path/n)!=h:raise ValueError('actual raw changed:'+n)
  errors=dict(m['reference_max_abs']);errors.update({'continued_'+k:v for k,v in m.get('continued_reference_max_abs',{}).items()});cases[case]=dict(status='PASS' if max(errors.values())<1e-12 else 'FAIL',errors=errors,original_status=m['status'],absolute_api_gate=1e-12,original_summary_sha256=sha(path/'summary.json'),explanation='original inherited gate restored;old loose1e-11 runner records preserved,NOT permission to loosen physical criteria')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if all(c['status']=='PASS' for c in cases.values()) else 'FAIL',scope='strict original absolute1e-12 actual/reference audit ONLY;NOT all physical gates',cases=cases);write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
