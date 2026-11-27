"""User-authorized supervisor-only local save; no arbitrary shell commands.

The research child keeps its workspace sandbox. This module runs ONLY in the
separately authorized external supervisor. No permission escalation by child.
"""
import hashlib,json,subprocess
from pathlib import Path

BASE='product_prototype/'
ROOTS=tuple(BASE+s+'/' for s in ('stage12_integrated','stage1_manufacturing','stage2_load_transfer'))
COMMON={BASE+'reports/CHECKPOINT.md',BASE+'reports/AUTONOMOUS_RESUME.md','reports/INTEGRATED_CURRENT_STATUS.md','reports/INTEGRATED_NEXT_TASKS.md'}
PROTECTED={'session_manager.py','manager_controls.py','supervised_save.py','supervised_save_controls.py','commit_guard.py','criteria.json'}
RAW={'surface.csv','detector.csv','response_rows.csv','layer_pairs.csv'}
def git(repo,*args):return subprocess.check_output(['git',*args],cwd=repo,text=True).strip()
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def untracked(repo):return set(subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=repo).decode().split('\0'))-{''}
def changed(repo):return set(subprocess.check_output(['git','diff','HEAD','--name-only','--no-renames','-z'],cwd=repo).decode().split('\0'))-{''}
def safe_path(repo,name):
    p=Path(name)
    if not isinstance(name,str) or not name or any(ord(c)<32 for c in name) or p.is_absolute() or '..' in p.parts or p.as_posix()!=name:raise ValueError('Unsafe path')
    if not (name.startswith(ROOTS) or name in COMMON) or '/runtime/' in name or p.name in PROTECTED or p.name in RAW:raise ValueError('Unapproved save scope')
    full=repo/p
    if any((repo/Path(*p.parts[:i])).is_symlink() for i in range(1,len(p.parts)+1)):raise ValueError('Symlink save rejected')
    if not full.is_file() or full.stat().st_size>=50_000_000:raise ValueError('Missing/deleted/oversize file')
    return full
def validate(repo,request,head,old_untracked):
    repo=Path(repo)
    if git(repo,'rev-parse','HEAD')!=head or request.get('expected_HEAD')!=head:raise ValueError('HEAD changed or mismatched')
    records=request.get('files',[]);names=[r['path'] for r in records]
    if not names or len(names)!=len(set(names)):raise ValueError('Empty/duplicate save list')
    if set(names)&set(old_untracked):raise ValueError('Pre-existing untracked work belongs to user')
    if set(names)!=changed(repo)|(untracked(repo)-set(old_untracked)):raise ValueError('Save list does not exactly cover this cycle changes')
    if git(repo,'diff','--cached','--name-only'):raise ValueError('Unexpected pre-staged files')
    for r in records:
        full=safe_path(repo,r['path'])
        if digest(full)!=r['SHA256']:raise ValueError('Stale content hash')
        # Existing immutable CAD, results and BOM must be preserved; use new tags.
        relative=r['path'][len(BASE):]
        immutable=any('/'+x+'/' in '/'+relative for x in ('validation','results','cad','bom'))
        existed=subprocess.run(['git','cat-file','-e',head+':'+r['path']],cwd=repo,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
        if immutable and existed:raise ValueError('Existing evidence/CAD/BOM mutation rejected')
    results=request.get('results',[])
    if not results:raise ValueError('No actual new result references')
    for r in results:
        if isinstance(r,str):
            matches=[record for record in records if record['path']==r]
            if len(matches)!=1:raise ValueError('Result path not uniquely listed')
            r=matches[0] # digest already verified above; never infer a hash
        if r not in records or Path(r['path']).name!='summary.json':raise ValueError('Result not in save list')
        doc=json.loads(safe_path(repo,r['path']).read_text())
        if not isinstance(doc.get('status'),str) or doc.get('test_only') is True:raise ValueError('Not a research result')
    message=request.get('message','')
    if not isinstance(message,str) or not 1<=len(message)<=160 or '\n' in message:raise ValueError('Invalid commit message')
    return names
def save(repo,request,head,old_untracked,guard,guard_SHA):
    names=validate(repo,request,head,old_untracked)
    if digest(guard)!=guard_SHA:raise ValueError('Trusted staged guard changed')
    subprocess.run(['git','--literal-pathspecs','add','--',*names],cwd=repo,check=True)
    staged=set(subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=repo).decode().split('\0'))-{''}
    if staged!=set(names):raise ValueError('Unexpected staged paths; preserve index and halt')
    for r in request['files']:
        raw=subprocess.check_output(['git','show',':'+r['path']],cwd=repo)
        if hashlib.sha256(raw).hexdigest()!=r['SHA256']:raise ValueError('Indexed content mismatch')
    import sys
    subprocess.run([sys.executable,str(guard)],cwd=repo,check=True)
    subprocess.run(['git','commit','-m',request['message']],cwd=repo,check=True)
    return dict(status='LOCAL_COMMIT_SAVED_NOT_RELEASE',before_HEAD=head,after_HEAD=git(repo,'rev-parse','HEAD'),files=request['files'],results=request['results'])
