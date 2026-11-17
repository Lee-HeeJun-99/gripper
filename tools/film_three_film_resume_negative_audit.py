"""Read-only reassessment of the empty-unflushed-header harness mistake."""
import argparse,json,shutil
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);old=json.loads((src/'summary.json').read_text());out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');runs={}
 for name,r in old['runs'].items():
  process=src/name/'process'
  for n,h in r['process']['artifacts'].items():
   if sha(process/n)!=h:raise ValueError('negative raw changed')
  path=src/name/'three.states.csv';lines=path.read_text().splitlines() if path.exists() else [];logs=''.join((process/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));safe=not lines or (len(lines)==1 and lines[0].startswith('time,'));ok=safe and r['expected_rejection'] in logs and r['process']['exit_code']!=0;runs[name]=dict(status='PASS' if ok else 'FAIL',accepted_rows=0 if safe else None,observed_lines=len(lines),specific_guard_message=r['expected_rejection'],exit_code=r['process']['exit_code'])
 result=dict(status='PASS' if all(r['status']=='PASS' for r in runs.values()) else 'FAIL',scope='read-only reassessment of SAME actual negative runs;NOT new SOFA execution',case=a.case,case_summary_sha256=sha(src/'summary.json'),reason='old harness wrongly required one header line;abort can leave empty buffered file;both contain zero accepted rows',known_limitation='invalid bwdInit throws and process aborts;no silent partial physics continuation',runs=runs);write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
