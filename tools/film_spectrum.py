"""Independent tangent spectrum at a recorded 21x5 penalty-film state."""
import argparse,json,shutil
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    if not a.tag.replace('_','').isalnum():raise ValueError('tag')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
    source=ROOT/'diagnostics/film_shell/ContactSpectrum.cpp';raw=ROOT/'results/autonomous_film_20261116_bdf2_transient18/4/journal.csv';binary=out/'spectrum'
    shutil.copy2(source,out/'ContactSpectrum.cpp')
    build=logged(['g++','-O2','-std=c++17','-I/usr/include/eigen3',source,'-o',binary],out/'build',180)
    if build['exit_code']:write_json(out/'summary.json',dict(status='FAIL',build=build));return
    run=logged([binary,raw],out/'run',480)
    result=dict(source_sha256=sha(source),binary_sha256=sha(binary),raw_sha256=sha(raw),build=build,run=run,classification='Independent FEM tangent spectrum at actual SOFA coordinates;not time accuracy proof')
    if run['exit_code']==0:result['metrics']=json.loads((out/'run/stdout.log').read_text())
    write_json(out/'summary.json',result);print(json.dumps(result.get('metrics',result)))

if __name__=='__main__':main()
