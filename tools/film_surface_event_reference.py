"""Fresh bounded whole-surface kernel reference;no actual SOFA claim."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);build=ROOT/'build'/('film_surface_'+a.tag);build.mkdir(exist_ok=False)
    shutil.copy2(__file__,out/'runner.py');sources=[]
    for directory in ('film_impact','film_shell','film_rail_tendon','film_native_contact','film_sphere_contact'):
        sources+=list((ROOT/'models'/directory).glob('*.h'))
    sources+=[ROOT/'tests/test_whole_surface_event.cpp',ROOT/'tests/test_whole_surface_midpoint.cpp',ROOT/'tests/test_surface_roundoff.cpp']
    for s in sources:
        target=out/'sources'/s.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(s,target)
    write_json(out/'identity.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(s.relative_to(ROOT)):sha(s) for s in sources},sdk=None,scope='independent quadratic dense numerical path and dual impact'))
    records={}
    for name in ('whole_surface_event','whole_surface_midpoint','surface_roundoff'):
        binary=build/name;c=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',out/('sources/tests/test_'+name+'.cpp'),'-o',binary],out/(name+'_compile'),120)
        record=dict(status='FAIL',compile=c)
        if c['exit_code']==0:
            r=guarded([binary],out/name,30);record.update(status='PASS' if r['exit_code']==0 else 'FAIL',run=r,binary_sha256=sha(binary))
        records[name]=record
    result=dict(status='PASS' if all(r['status']=='PASS' for r in records.values()) else 'FAIL',records=records)
    write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'])))
if __name__=='__main__':main()
