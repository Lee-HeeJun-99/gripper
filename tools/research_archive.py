"""Immutable source checkpoint for a new diagnostic/build artifact namespace."""
import argparse,shutil
from research_common import ROOT,OUT,sha,write_json,identity
def main():
    p=argparse.ArgumentParser();p.add_argument('name');a=p.parse_args();out=OUT/('source_checkpoint_'+a.name);out.mkdir(exist_ok=False);paths=[]
    for folder in('models/material_point_contact','diagnostics/autonomous'):
        paths.extend(q for q in(ROOT/folder).rglob('*')if q.is_file()and'__pycache__'not in q.parts)
    paths.append(ROOT/'tests/test_material_point.cpp');hashes={}
    for source in paths:
        name=str(source.relative_to(ROOT));target=out/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);hashes[name]=sha(source)
    write_json(out/'manifest.json',dict(sources=hashes,identity=identity(),scope='checkpoint at recorded diagnostic source state, not reconstruction of early failed v1/v2 unit sources'))
if __name__=='__main__':main()
