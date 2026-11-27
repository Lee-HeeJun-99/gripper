"""Freeze actually tested sources before operator improvements; no result overwrite."""
import argparse,json,shutil
from baseline_registry import ROOT,REPO,sha,ref,dump
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();folder=ROOT/'validation/integrated'/a.tag;d=json.loads((folder/'summary.json').read_text());out=folder/'SOURCE_ARCHIVE.json'
    if out.exists():raise FileExistsError(out)
    rows=[]
    for name in ('goal_manager','policy','unchanged_supervisor'):
        r=d[name];source=REPO/r['path'];assert sha(source)==r['SHA256'];dest=folder/('tested_'+source.name);shutil.copyfile(source,dest);rows.append(dict(original=r,frozen=ref(dest)))
    dump(out,dict(status='TESTED_SOURCE_ARCHIVE_SAVED',sources=rows,original_result=ref(folder/'summary.json')))
if __name__=='__main__':main()
