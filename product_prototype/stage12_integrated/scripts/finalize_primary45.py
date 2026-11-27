"""Preserve first cycle45 record and publish explicit prose-count correction."""
import json,copy
from baseline_registry import ROOT,REPO,ref,sha,dump
from supervised_save import validate,changed,untracked
from goal_manager_policy import engineering_record
load=lambda p:json.loads(p.read_text())
def main():
 rt=ROOT/'runtime/goal_authorized_20261127_7';v=ROOT/'validation/integrated';orig=v/'primary_cycle45_record/summary.json';prior=load(orig);assert prior['assembly_finite_pose_count']==70
 out=v/'primary_cycle45_final';out.mkdir();d=copy.deepcopy(prior);d['predecessor_record']=ref(orig);d['note']=d['note'].replace('88finiteposesclear','70finiteposesclear');d['record_correction']='First record prose says88 finiteposes;actual measured field was70 throughout. Correct value70;firstrecord retained unchanged. No numerical evidence or criteria changed.'
 gp=ROOT/'models/primary_system_gate_state50.json';g=copy.deepcopy(load(ROOT/'models/primary_system_gate_state49.json'));g['predecessor']=ref(ROOT/'models/primary_system_gate_state49.json');g['record_correction']=d['record_correction'];g['note']=g['note'].replace('88finiteposesclear','70finiteposesclear')
 for row in g['gates']:row['reason']=row['reason'].replace('88finiteposesclear','70finiteposesclear')
 dump(gp,g);d['system_gates']=ref(gp);dump(out/'summary.json',d)
 for filename in ['PRIMARY_PRODUCT.json','CURRENT_CANDIDATE.json','INTEGRATED_TASKS.json','NEXT_TASK.json']:
  p=ROOT/filename;x=load(p)
  def fix(q):
   if isinstance(q,str):return q.replace('88finiteposesclear','70finiteposesclear')
   if isinstance(q,list):return [fix(t) for t in q]
   if isinstance(q,dict):
    if q==ref(orig):return ref(out/'summary.json')
    if q==ref(ROOT/'models/primary_system_gate_state49.json'):return ref(gp)
    return {k:fix(t) for k,t in q.items()}
   return q
  x=fix(x)
  if filename=='CURRENT_CANDIDATE.json':x['primary_state']=ref(ROOT/'PRIMARY_PRODUCT.json')
  dump(p,x)
 checkpoint=ROOT/'CHECKPOINT.md';text=checkpoint.read_text().replace('88finiteposesclear','70finiteposesclear');prefix='# Cycle45 final record correction\n\nMeasured finite assembly/tool poses: **70**, all clear. The first cycle45 record prose incorrectly said88; its numerical field was70. Original record/report remain preserved. Authoritative final record: `validation/integrated/primary_cycle45_final/summary.json`;all22UNQUALIFIED state: `models/primary_system_gate_state50.json`. CAD/loadpath/results are unchanged by this count correction.\n\n---\n\n';checkpoint.write_text(prefix+text);(ROOT/'reports/primaryP1_benchattachment45_record_correction.md').write_text(prefix)
 req=load(rt/'save_request45.json');req['results'][0]=ref(out/'summary.json');old=set(load(rt/'checkpoint_before45.json')['preexisting_untracked'])
 def update():req['files']=[ref(REPO/p) for p in sorted(changed(REPO)|(untracked(REPO)-old))]
 update();validate(REPO,req,req['expected_HEAD'],old);rec=engineering_record(req,REPO);dump(out/'preflight.json',dict(status='READ_ONLY_EXACT_BYTE_SAVE_PREFLIGHT_PASS',engineering_record=rec,finite_pose_count=70,all22_unqualified=True,queue_RUNNING=0,analysis_children_reaped=True));update();validate(REPO,req,req['expected_HEAD'],old);engineering_record(req,REPO);dump(rt/'save_request45.json',req);print(json.dumps(dict(files=len(req['files']),request=ref(rt/'save_request45.json'),results=req['results'])))
if __name__=='__main__':main()
