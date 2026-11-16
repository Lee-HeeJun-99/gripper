"""Mapped-mass actual SOFA versus independent reduced-coordinate BDF2."""
import csv,json,shutil
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged

def main():
    out=ROOT/'results/autonomous_film_20261116_hard_reference26';out.mkdir(exist_ok=False)
    source=ROOT/'diagnostics/film_shell/HardSlopeReference.cpp';binary=out/'reference';shutil.copy2(source,out/'HardSlopeReference.cpp')
    build=logged(['g++','-O2','-std=c++17','-I/usr/include/eigen3',source,'-o',binary],out/'build',180)
    if build['exit_code']:write_json(out/'summary.json',dict(status='FAIL',build=build));return
    ref=logged([binary,'4','.4'],out/'reference_run',480)
    sdk=ROOT/'build/grasp_20261115/sofa_patched';plugin=ROOT/'build/film_shell_20261116_hard_transient25/libReGripFilmShell.so'
    template=ROOT/'results/autonomous_film_20261116_hard_slope24/1/scene.scn';case=out/'actual';case.mkdir()
    scene=template.read_text().replace(str(template.parent/'journal.csv'),str(case/'journal.csv')).replace('absoluteResidualStoppingThreshold="1e-13"','absoluteResidualStoppingThreshold="1e-15"')
    (case/'scene.scn').write_text(scene);run=logged([sdk/'bin/graph_probe',sdk,case/'scene.scn','4','0',plugin],case/'process',480)
    actual=list(csv.DictReader((case/'journal.csv').open())) if (case/'journal.csv').exists() else []
    reference=list(csv.DictReader((out/'reference_run/stdout.log').open())) if ref['exit_code']==0 else []
    metrics={}
    if len(actual)==len(reference)==4:
        for key in ('tip_z','U','max_speed'):
            absolute=max(abs(float(a[key])-float(b[key])) for a,b in zip(actual,reference));scale=max(abs(float(b[key])) for b in reference)
            metrics[key]=dict(absolute=absolute,relative=absolute/scale,status='PASS' if absolute/scale<1e-5 else 'FAIL')
    # Verify mapped-residual changes did not alter the unmapped benchmark.
    original=ROOT/'results/autonomous_film_20261116_bdf2_stage16/1';plain=out/'unmapped';plain.mkdir()
    (plain/'scene.scn').write_text((original/'scene.scn').read_text().replace(str(original/'journal.csv'),str(plain/'journal.csv')))
    regression=logged([sdk/'bin/graph_probe',sdk,plain/'scene.scn','4','0',plugin],plain/'process',480)
    old=list(csv.DictReader((original/'journal.csv').open()));new=list(csv.DictReader((plain/'journal.csv').open())) if (plain/'journal.csv').exists() else []
    change=max(abs(float(a['tip_z'])-float(b['tip_z'])) for a,b in zip(old,new)) if len(old)==len(new)==4 else None
    result=dict(source='Independent exact-slope FEM versus actual SOFA mapped-mass BDF2;not grasp',source_sha256=sha(source),binary_sha256=sha(binary),plugin_sha256=sha(plugin),build=build,reference_process=ref,actual_process=run,metrics=metrics,unmapped_regression=dict(process=regression,max_tip_absolute=change,status='PASS' if change is not None and change<1e-10 else 'FAIL'),status='PASS' if len(metrics)==3 and all(v['status']=='PASS' for v in metrics.values()) else 'FAIL')
    write_json(out/'summary.json',result);print(json.dumps(result,indent=2))

if __name__=='__main__':main()
