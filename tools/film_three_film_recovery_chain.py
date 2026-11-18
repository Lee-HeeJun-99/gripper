"""Foreground-only bounded V5 plan continuation;no daemon or automatic restart."""
import argparse,json,subprocess,sys
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--plans',type=int,choices=range(1,8),default=7);a=p.parse_args()
 for name in ('20261118_three_film_extended_api1125','20261118_three_film_extended_resume1126'):
  if json.loads((ROOT/'results'/('autonomous_film_'+name)/'summary.json').read_text())['status']!='PASS':raise ValueError('exact API and resume gates required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);parent='20261118_three_film_extended_actual1124';step=224;done=[]
 result=dict(status='EXPERIMENTAL',scope='bounded foreground actual unloaded FREE plans;NOT completed shape recovery/grasp/full time',completed=done,automatic_restart=False)
 for i in range(a.plans):
  tag=a.tag+'_plan'+str(i+1);command=[sys.executable,ROOT/'tools/film_three_film_v5_resume.py','--tag',tag,'--parent',parent,'--step',str(step),'--steps','8','--restart-plan']
  with (out/('plan'+str(i+1)+'.log')).open('w') as log:run=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=520)
  path=ROOT/'results'/('autonomous_film_'+tag)/'summary.json'
  if run.returncode or not path.exists():result.update(status='FAIL',failure='child runner failed;inspect preserved plan log');break
  proof=json.loads(path.read_text());done.append(dict(tag=tag,summary_sha256=sha(path),status=proof['status'],time_s=proof.get('actual_end_time_s')));write_json(out/'summary.json',result)
  if proof['status']!='EXPERIMENTAL':result.update(status='FAIL',failure='accepted-state plan gate failed');break
  parent=tag;step+=8
 result.update(last_parent=parent,last_step=step);write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
