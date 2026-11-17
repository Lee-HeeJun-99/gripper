"""Bounded independent impact references, not SOFA dynamics certification."""
import argparse,json,subprocess,shutil
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--tag',required=True)
    parser.add_argument('--only',choices=('projected_impact','impact_birth_restart','film_projected_impact','film_birth_subintegration'),nargs='+');args=parser.parse_args()
    out=ROOT/'results'/('autonomous_film_'+args.tag);out.mkdir(exist_ok=False)
    shutil.copy2(__file__,out/'runner.py')
    build=ROOT/'build'/('film_impact_'+args.tag);build.mkdir(exist_ok=False)
    names=args.only or ('projected_impact','impact_birth_restart','film_projected_impact','film_birth_subintegration')
    sources=list((ROOT/'models/film_impact').glob('*.h'))+[ROOT/'tests'/('test_'+s+'.cpp') for s in names]
    sources+=list((ROOT/'models/film_rail_tendon').glob('*.h'))+list((ROOT/'models/film_shell').glob('*.h'))+list((ROOT/'models/film_native_contact').glob('*.h'))+list((ROOT/'models/film_sphere_contact').glob('*.h'))
    for source in sources:
        target=out/'sources'/source.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
    write_json(out/'identity.json',dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(s.relative_to(ROOT)):sha(s) for s in sources},scope='independent mathematical validation;SDK not linked'))
    records={}
    for name in names:
        binary=build/name
        compile_result=guarded(['g++','-std=c++17','-O2','-ffp-contract=off','-I/usr/include/eigen3',out/'sources/tests'/('test_'+name+'.cpp'),'-o',binary],out/(name+'_build'),120)
        record=dict(compile=compile_result,status='FAIL')
        if compile_result['exit_code']==0:
            record['binary_sha256']=sha(binary);record['run']=guarded([binary],out/name,30)
            text=(out/name/'stdout.log').read_text()
            if record['run']['exit_code']==0 and 'PASS ' in text:record['status']='PASS'
        records[name]=record
    write_json(out/'summary.json',dict(status='PASS' if all(r['status']=='PASS' for r in records.values()) else 'FAIL',scope='independent references only;actual SOFA impact NOT RUN',records=records))
    print(json.dumps({k:v['status'] for k,v in records.items()}))
if __name__=='__main__':main()
