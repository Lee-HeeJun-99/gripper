"""Short actual SOFA trapezoid versus independent nonlinear mapped FEM."""
import argparse,csv,json,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    if not a.tag.replace('_','').isalnum():raise ValueError('tag')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
    campaign=ROOT/'results/autonomous_film_20261116_trapezoid_reference69';build=ROOT/'build/film_shell_20261116_trapezoid_reference69'
    summary=json.loads((campaign/'summary.json').read_text())
    if summary['process_status']!='PASS':raise RuntimeError('actual process failure')
    scene=(campaign/'1/scene.scn').read_text()
    if 'order="1" theta=".5"' not in scene or '<FilmRampLoad ' not in scene:raise RuntimeError('wrong actual algorithm/input')
    process=logged([build/'film_trapezoid_reference','4','.4'],out/'reference',180)
    if process['exit_code']:raise RuntimeError('independent reference failed')
    actual=list(csv.DictReader((campaign/'1/journal.csv').open()));reference=list(csv.DictReader((out/'reference/stdout.log').open()))
    if len(actual)!=4 or len(reference)!=4:raise RuntimeError('rows')
    metrics={}
    for key in ('tip_z','U','max_speed'):
        x=np.array([float(r[key]) for r in actual]);y=np.array([float(r[key]) for r in reference]);absolute=float(max(abs(x-y)));scale=float(max(abs(y)))
        metrics[key]=dict(max_absolute=absolute,relative=absolute/scale,status='PASS' if absolute/scale<1e-5 else 'FAIL')
    write_json(out/'summary.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        source_sha256=sha(ROOT/'diagnostics/film_shell/TrapezoidReference.cpp'),binary_sha256=sha(build/'film_trapezoid_reference'),actual_journal_sha256=sha(campaign/'1/journal.csv'),
        process=process,metrics=metrics,status='PASS' if all(v['status']=='PASS' for v in metrics.values()) else 'FAIL',
        scope='short actual mapped trapezoid versus independent nonlinear FEM;not contact time/grasp qualification'))
    print(json.dumps(metrics,indent=2))

if __name__=='__main__':main()
