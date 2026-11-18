"""Preserved independent MP reference on the NEW actual38ms IVP.

Historical compiled-source identity is deliberate,not a current-source build.
Does not change the actual Owner's38ms scope or launch an unqualified extension.
"""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--steps',type=int,choices=(64,128,256),default=64);p.add_argument('--reuse');a=p.parse_args();src=ROOT/'results/autonomous_film_20261118_three_film_recovery_chain1127_plan7';checkpoint=src/'three.checkpoint_280.txt';parent=json.loads((src/'summary.json').read_text());ledger=json.loads((ROOT/'reports/FILM_CONTACT_EVIDENCE_20261118_three_film_recovery_v12.json').read_text());old=ROOT/'results/autonomous_film_20261118_three_film_v5_long_base1118';proof=json.loads((old/'summary.json').read_text());binary=old/'reference'
 if parent['status']!='EXPERIMENTAL' or parent['process']['exit_code'] or sha(checkpoint)!=parent['raw_hashes'][checkpoint.name]:raise ValueError('complete accepted actual38ms parent required')
 for f in (checkpoint,old/'summary.json',binary):
  if sha(f)!=ledger['files'][str(f.relative_to(ROOT))]:raise ValueError('preserved V12 artifact identity failed')
 for name,digest in proof['sources'].items():
  if sha(old/'sources'/name)!=digest:raise ValueError('archived reference source changed')
 forecast=2*proof['run']['runtime_s']*a.steps/proof['steps']+30
 if a.reuse:
  previous=ROOT/'results'/('autonomous_film_'+a.reuse);profile=json.loads((previous/'summary.json').read_text())
  if profile['status']!='PASS' or profile['actual_checkpoint_sha256']!=sha(checkpoint) or profile['reference_binary_sha256']!=sha(binary):raise ValueError('same NEW38ms IVP/binary profile required')
  forecast=2*profile['process']['runtime_s']*a.steps/profile['steps']+30
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='BLOCKED',scope='independent preserved-kernel38..44.4ms FREE reference;NOT actual SOFA extension/recovery/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),historical_compiled_source_commit=proof['source_commit'],reference_source_provider=str(old/'sources'),reference_source_summary_sha256=sha(old/'summary.json'),reference_binary_sha256=sha(binary),actual_checkpoint_sha256=sha(checkpoint),parent_summary_sha256=sha(src/'summary.json'),steps=a.steps,duration_s=.0064,predicted_runtime_s=forecast,physics_launched=False,actual_owner_scope_unchanged=True)
 if forecast>480:result['failure']='measured policy forecast>480s,NOT OS exhaustion';write_json(out/'summary.json',result);print(json.dumps(result));return
 shutil.copy2(checkpoint,out/'input.checkpoint');shutil.copy2(binary,out/'reference');run=guarded([out/'reference',out/'input.checkpoint',str(a.steps),out/'recovery','common','.0064'],out/'process',480);result.update(status='PASS' if run['exit_code']==0 else 'FAIL',physics_launched=True,process=run)
 if run['exit_code']==0:result['metrics']=next(csv.DictReader((out/'recovery.metrics.csv').open()))
 result['failure_reason']=(out/'process/stderr.log').read_text().strip() or None;result['raw_hashes']={f.name:sha(f) for f in out.glob('recovery.*')};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('process','raw_hashes')}))
if __name__=='__main__':main()
