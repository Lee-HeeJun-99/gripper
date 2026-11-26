"""Hash every existing immutable integrated result and reconcile source archives."""
import argparse,json,subprocess,platform,shutil
from pathlib import Path
import numpy,scipy
from baseline_registry import ROOT,REPO,S1,S2,sha,ref,dump,integrity
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'validation/provenance'/a.tag
    inputs=sorted([*ROOT.rglob('summary.json'),*ROOT.rglob('failure.json')]);out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    archives={sha(f):f for f in ROOT.rglob('*.py')};errors=[];recovered=[];manifest=[]
    def walk(x,source):
        if isinstance(x,dict):
            if 'path' in x and 'SHA256' in x:
                path=Path(x['path']);full=REPO/path
                if path.is_absolute() or '..' in path.parts:errors.append(str(source)+':unsafe path')
                elif not full.is_file() or sha(full)!=x['SHA256']:
                    if x['SHA256'] in archives:recovered.append(dict(result=ref(source),declared=x,matching_source_archive=ref(archives[x['SHA256']]),current_source_changed=True))
                    else:errors.append(dict(result=str(source.relative_to(ROOT)),missing_or_changed=x))
            for v in x.values():walk(v,source)
        elif isinstance(x,list):
            for v in x:walk(v,source)
    for path in inputs:
        doc=json.loads(path.read_text());walk(doc,path);manifest.append(dict(file=ref(path),actual_status=doc.get('status'),scope=doc.get('scope','IMPLEMENTATION FAILURE OR METADATA')))
    protected=subprocess.check_output(['git','diff','--name-only','4e7130d','--','product_prototype/stage1_manufacturing','product_prototype/stage2_load_transfer'],cwd=REPO,text=True).strip()
    if protected:errors.append('historical Stage1/Stage2 changed:'+protected)
    errors+=integrity(json.loads((ROOT/'CURRENT_BASELINE.json').read_text()))
    result=dict(status='PASS' if not errors else 'FAIL',scope='ARTIFACT / SOURCE ARCHIVE INTEGRITY ONLY, NOT PHYSICAL RELEASE',results=manifest,errors=errors,historical_sources_resolved=recovered,
        python=platform.python_version(),numpy=numpy.__version__,scipy=scipy.__version__,platform=platform.platform(),
        protected_Stage1_Stage2_unchanged=not protected,producer=ref(out/'producer.py'),Native_executed=False,hardware_measured=False)
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],results=len(manifest),errors=errors,historical_sources_resolved=len(recovered)),indent=2))
if __name__=='__main__':main()
