"""Stored/kinetic inventory only;no fabricated work or full energy closure."""
import argparse,csv,json,shutil
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((src/'summary.json').read_text());old=ROOT/'results/autonomous_film_20261118_three_film_actual_work946';proof=json.loads((old/'summary.json').read_text());binary=old/'reference'
 if meta['status']!='PASS' or sha(src/'states.csv')!=meta['states_sha256'] or sha(binary)!=proof['binary_sha256']:raise ValueError('completed immutable post state and full-AD observer required')
 for k,v in proof['sources'].items():
  if k.endswith('.h') and sha(src/'sources'/k)!=v:raise ValueError('compiled full-AD observer header changed:'+k)
 if sha(ROOT/'diagnostics/film_three_finger/DrivenPower.cpp')!=proof['sources']['diagnostics/film_three_finger/DrivenPower.cpp']:raise ValueError('observer driver changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');rows=list(csv.DictReader((src/'states.csv').open()));initial=(src/'initial.txt').read_text().splitlines();samples=[('initial',.0002,initial[1],initial[2])]+[('end'+str(i),float(r['time']),r['q'],r['v']) for i,r in enumerate(rows)];(out/'samples.txt').write_text(str(len(samples))+'\n'+'\n'.join(name+' '+format(t,'.17g')+' '+q+' '+v for name,t,q,v in samples)+'\n');shutil.copy2(src/'mass.txt',out/'mass.txt');run=guarded([binary,out/'mass.txt',out/'samples.txt',out/'observed.csv'],out/'run',120)
 result=dict(status='PASS' if run['exit_code']==0 else 'FAIL',scope='independent full-AD stored/kinetic inventory of saved post-impact states;NOT work/energy closure/SOFA/time certification',case=a.case,states_sha256=sha(src/'states.csv'),binary_sha256=sha(binary),observer_summary_sha256=sha(old/'summary.json'),source_summary_sha256=sha(src/'summary.json'),run=run,work=None,missing=['stage work','damping/contact/external work','whole event/time','full energy'])
 if run['exit_code']==0:result['observed_sha256']=sha(out/'observed.csv')
 write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],case=a.case)))
if __name__=='__main__':main()
