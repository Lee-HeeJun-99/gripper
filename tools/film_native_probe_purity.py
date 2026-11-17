"""Passive probe extension regression using archived completed Native trials."""
import argparse,csv,json,shutil
from curve_common import ROOT,sha,write_json
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--before',required=True);p.add_argument('--after',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
    left=ROOT/'results'/('autonomous_film_'+a.before);right=ROOT/'results'/('autonomous_film_'+a.after);x=json.loads((left/'identity.json').read_text());y=json.loads((right/'identity.json').read_text());changes=[k for k in set(x['source_hashes'])|set(y['source_hashes']) if x['source_hashes'].get(k)!=y['source_hashes'].get(k) and k.endswith(('.h','.cpp','/CMakeLists.txt'))]
    if changes!=['models/rigid_impact_reference/NativeFreeBodyProbe.cpp']:raise ValueError('not a passive probe-only compiled-source change:'+str(changes))
    for key in ('generic_correction','actual_solver','object_mass','object_inertia_per_mass','gravity','rayleigh_mass','initial_body_omega','initial_film_tip_velocity'):
        if x[key]!=y[key]:raise ValueError('physical input changed:'+key)
    checks={};hashes={}
    for steps in ('8','16','32'):
        for directory in (left,right):
            summary=json.loads((directory/'summary.json').read_text())
            if summary['cases'][steps]['execution_status']!='PASS':raise ValueError('incomplete physics trial')
        files={}
        for name in ('film.csv','displacement.csv'):
            l=left/steps/name;r=right/steps/name;files[name]=sha(l)==sha(r);hashes[str(l)]=sha(l);hashes[str(r)]=sha(r)
        l=list(csv.DictReader((left/steps/'body.csv').open()));r=list(csv.DictReader((right/steps/'body.csv').open()));files['all_existing_body_columns_exact']=len(l)==len(r) and all(all(row[k]==other[k] for k in row) for row,other in zip(l,r));checks[steps]=files
    status='PASS' if all(all(files.values()) for files in checks.values()) else 'FAIL';write_json(out/'summary.json',dict(status=status,scope='passive probe-only source change regression;two binaries,NOT same-binary toggle',before=a.before,after=a.after,changed_compiled_sources=changes,binary_before=x['binary_sha256'],binary_after=y['binary_sha256'],checks=checks,hashes=hashes));print(json.dumps(dict(status=status,checks=checks)))
if __name__=='__main__':main()
