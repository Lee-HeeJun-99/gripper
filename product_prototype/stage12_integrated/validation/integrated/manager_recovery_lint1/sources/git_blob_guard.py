"""Read-only all-new-history size guard; never rewrites Git or scans credentials."""
import argparse,json,subprocess
from baseline_registry import ROOT,REPO,ref,dump
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'validation/provenance'/a.tag;out.mkdir(parents=True,exist_ok=False)
    base='4e7130d847cfaf09498a382d35bfc1ce0c5d4570'
    def git(*args):return subprocess.check_output(['git',*args],cwd=REPO,text=True)
    head=git('rev-parse','HEAD').strip();ancestor=subprocess.run(['git','merge-base','--is-ancestor',base,head],cwd=REPO).returncode==0
    objects=git('rev-list','--objects',base+'..'+head).splitlines();names={s.split(' ',1)[0]:s.split(' ',1)[1] if ' ' in s else '' for s in objects}
    lines=subprocess.check_output(['git','cat-file','--batch-check=%(objectname) %(objecttype) %(objectsize)'],cwd=REPO,input=('\n'.join(names)+'\n').encode()).decode().splitlines();blobs=[]
    for line in lines:
        digest,kind,size=line.split()
        if kind=='blob':blobs.append(dict(SHA=digest,bytes=int(size),path=names[digest]))
    bad=[b for b in blobs if b['bytes']>=50_000_000]
    protected=git('diff','--name-only',base,'--','product_prototype/stage1_manufacturing','product_prototype/stage2_load_transfer').strip()
    result=dict(status='PASS' if ancestor and not bad and not protected else 'FAIL',scope='NEW REACHABLE BLOBS ONLY; UNTRACKED ORIGINAL DATA ARE NOT REMOVED',audited_HEAD=head,baseline=base,baseline_ancestor=ancestor,blob_count=len(blobs),bad=bad,largest=sorted(blobs,key=lambda b:b['bytes'],reverse=True)[:5],protected_Stage1_Stage2_unchanged=not protected,producer=ref(Path(__file__)))
    dump(out/'summary.json',result);print(json.dumps(result,indent=2));raise SystemExit(0 if result['status']=='PASS' else 2)
if __name__=='__main__':main()
