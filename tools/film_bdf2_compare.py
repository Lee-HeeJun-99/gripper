"""Compare actual SOFA's BDF2 startup/history against independent Newton."""
import csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged

def main():
    out=ROOT/'results/autonomous_film_20261116_bdf2_reference17';out.mkdir(exist_ok=False)
    source=ROOT/'diagnostics/film_shell/BDF2Reference.cpp';shutil.copy2(source,out/'BDF2Reference.cpp')
    binary=out/'reference'
    build=logged(['g++','-O2','-std=c++17','-I/usr/include/eigen3',source,'-o',binary],out/'build',180)
    if build['exit_code']:write_json(out/'summary.json',dict(status='FAIL',build=build));return
    run=logged([binary,'4','.4'],out/'run',480)
    reference=list(csv.DictReader((out/'run/stdout.log').open())) if run['exit_code']==0 else []
    actual_path=ROOT/'results/autonomous_film_20261116_bdf2_stage16/1/journal.csv'
    actual=list(csv.DictReader(actual_path.open()));metrics={}
    if len(reference)==len(actual)==4:
        for key in ('tip_z','U','max_speed'):
            absolute=max(abs(float(a[key])-float(b[key])) for a,b in zip(actual,reference));scale=max(abs(float(b[key])) for b in reference)
            metrics[key]=dict(absolute=absolute,relative=absolute/scale,status='PASS' if absolute/scale<1e-5 else 'FAIL')
    result=dict(source='Independent BDF2 FEM versus actual SOFA, not measured material',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_sha256=sha(source),binary_sha256=sha(binary),actual_sha256=sha(actual_path),build=build,run=run,metrics=metrics,status='PASS' if len(metrics)==3 and all(v['status']=='PASS' for v in metrics.values()) else 'FAIL')
    write_json(out/'summary.json',result);print(json.dumps(result,indent=2))

if __name__=='__main__':main()
