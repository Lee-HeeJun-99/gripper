"""Operator-owned goal-loop policy, not a physical release gate or worker privilege."""
import hashlib,json,math,re
from pathlib import Path

PASS='STAGE1_STAGE2_INTEGRATED_DIGITAL_RELEASE_PASS'
LIMIT=re.compile(r'usage_limit_reached|rate_limit_exceeded|insufficient_quota|billing_hard_limit|quota exceeded|usage limit reached|you.{0,3}ve hit your usage limit|not enough credits|out of credits',re.I)
def finite(v):
    if isinstance(v,float):return math.isfinite(v)
    if isinstance(v,dict):return all(finite(x) for x in v.values())
    if isinstance(v,list):return all(finite(x) for x in v)
    return True
def stream_health(path,stderr):
    """Only real CLI error events/stderr classify limits; never quoted research text."""
    errors=[];usage=[]
    if path.exists():
        with path.open() as f:
            for line in f:
                try:r=json.loads(line)
                except ValueError:continue # a killed worker may leave one partial final line
                if r.get('type') in ('error','turn.failed'):errors.append(json.dumps(r))
                if r.get('type')=='turn.completed' and isinstance(r.get('usage'),dict):usage.append(r['usage'])
    tail=stderr.read_text(errors='replace')[-16000:] if stderr.exists() else ''
    return dict(external_limit=any(LIMIT.search(x) for x in errors+[tail]),CLI_failed=bool(errors),usage=usage)
def numeric_payload(v):
    """Ignore provenance/tag/time/count-only churn when comparing engineering results."""
    if isinstance(v,bool) or v is None:return None
    if isinstance(v,(int,float)):return v
    if isinstance(v,list):
        children=[numeric_payload(x) for x in v];return [x for x in children if x is not None] or None
    if isinstance(v,dict):
        skip=('path','source','producer','hash','sha','time','timestamp','elapsed','duration','tag','command','version','count','exit_code','pid','iteration')
        result={k:numeric_payload(x) for k,x in v.items() if not any(s in k.lower() for s in skip)}
        return {k:x for k,x in result.items() if x is not None} or None
    return None
def engineering_record(request,repo):
    """Additional progress check, never replaces unchanged Supervisor/gates.

    The caller first runs supervised_save.validate: every byte/hash/path is
    already checked. Reject prose-only activity and repeated numerical outputs.
    """
    p=request.get('engineering_progress',{});category=p.get('category')
    if category not in ('DESIGN_CHANGE','ACTUAL_PRODUCT_VALIDATION','BLOCKER_EVIDENCE'):raise ValueError('Missing engineering category')
    if not isinstance(p.get('task_id'),str) or not p['task_id'] or not isinstance(p.get('mechanism'),str) or not p['mechanism']:raise ValueError('Missing exact task/mechanism')
    if not p.get('system_gate_ids') or not all(isinstance(x,str) for x in p['system_gate_ids']):raise ValueError('Missing affected system gates')
    listed={r['path']:r for r in request['files']};results=[]
    for r in request['results']:
        name=r if isinstance(r,str) else r['path'];d=json.loads((repo/name).read_text())
        if not finite(d):raise ValueError('Nonfinite actual result')
        results.append(d)
    metrics=[numeric_payload(d) for d in results];metrics=[v for v in metrics if v is not None]
    design=p.get('actual_change_files',[])
    if len(design)!=len(set(design)) or any(n not in listed for n in design):raise ValueError('Unlisted/duplicate actual design file')
    allowed=('.step','.stp','.stl')
    solids=[n for n in design if Path(n).suffix.lower() in allowed and '/cad/' in n]
    if category=='DESIGN_CHANGE' and not solids:raise ValueError('No actual changed product solid')
    if category!='BLOCKER_EVIDENCE' and not metrics:raise ValueError('No actual numerical engineering output')
    if category=='ACTUAL_PRODUCT_VALIDATION':
        model=p.get('candidate_reference',{});name=model.get('path','');candidate=repo/name
        if not name or Path(name).is_absolute() or '..' in Path(name).parts or not candidate.is_file():raise ValueError('Missing actual candidate reference')
        if hashlib.sha256(candidate.read_bytes()).hexdigest()!=model.get('SHA256'):raise ValueError('Stale actual candidate reference')
        definition=json.loads(candidate.read_text())
        if not definition.get('part_references') and not definition.get('parts'):raise ValueError('Not a product candidate definition')
    # Source/retag changes alone do not make old unchanged metrics new progress.
    fingerprint=dict(category=category,mechanism=p['mechanism'],metrics=metrics,
        changed_solid_hashes=sorted(listed[n]['SHA256'] for n in solids))
    signature=hashlib.sha256(json.dumps(fingerprint,sort_keys=True,allow_nan=False).encode()).hexdigest()
    return dict(task_id=p['task_id'],category=category,mechanism=p['mechanism'],system_gate_ids=p['system_gate_ids'],signature=signature,summary_statuses=[d['status'] for d in results],next_task_id=p.get('next_task_id'),strategy_change=p.get('strategy_change') is True)
def outcome(returncode,timed_out,health,saved,record,seen):
    if health['external_limit']:return 'EXTERNAL_ACCOUNT_OR_SERVICE_LIMIT'
    if saved:
        if record['signature'] in seen:return 'REPEATED_ENGINEERING_OUTPUT'
        if record['category']=='BLOCKER_EVIDENCE':return 'BLOCKER_REVIEW_SAVED'
        return 'VERIFIED_ENGINEERING_CYCLE' # FAIL physics is still a valid engineering result
    if timed_out:return 'TIME_LIMIT_RECOVERY_REQUIRED'
    if returncode!=0 or health['CLI_failed']:return 'WORKER_EXECUTION_FAILURE'
    return 'NO_ENGINEERING_PROGRESS'
