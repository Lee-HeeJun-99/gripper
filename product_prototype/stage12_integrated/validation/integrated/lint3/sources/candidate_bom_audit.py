"""Changed-part manufacturing dimensions must match actual referenced STEP."""
import argparse,csv,json,sys,shutil
from pathlib import Path
import numpy as np
from baseline_registry import ROOT,S1,REPO,ref,dump,sha
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds
def main():
    p=argparse.ArgumentParser();p.add_argument('--packet',required=True);p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'validation/stage1'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/'bom'/a.packet/'summary.json';packet=json.loads(source.read_text());bom=REPO/packet['BOM']['path'];assert sha(bom)==packet['BOM']['SHA256'];rows=list(csv.DictReader(bom.open()));old={r['part_ID']:r for r in csv.DictReader((S1/'bom/revAA_mbd1/STAGE1_BOM.csv').open())};errors=[];checks=[]
    if len(rows)!=304 or {r['part_ID'] for r in rows}!=set(old):errors.append('part inventory mismatch')
    for row in rows:
        step=REPO/row['STEP']
        if not step.is_file() or sha(step)!=row['STEP_SHA256']:errors.append(row['part_ID']+':STEP missing/stale');continue
        if row['STEP_SHA256']!=old[row['part_ID']]['STEP_SHA256']:
            b=bounds(read(step));expected=np.array([b[:3],b[3:]]);stored=np.array(json.loads(row['datum_bounds_mm']));dimension=np.array(json.loads(row['dimensions_XYZ_mm']));err=float(max(abs(expected-stored).max(),abs(expected[1]-expected[0]-dimension).max()))
            checks.append(dict(part=row['part_ID'],bounds_dimension_error_mm=err,maximum_mm=1e-6,status='PASS' if err<1e-6 else 'FAIL'))
    result=dict(status='PASS' if not errors and all(r['status']=='PASS' for r in checks) else 'FAIL',scope='304ID/HASH LINKS + CHANGED PART ACTUAL CAD DIMENSIONS ONLY',checks=checks,errors=errors,source=ref(source),BOM=ref(bom),producer=ref(out/'producer.py'),product_release=False)
    dump(out/'summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
