"""Physical modal participation from completed SOFA states, not eigenvalues alone."""
import argparse,csv,json,subprocess,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    if not a.tag.replace('_','').isalnum():raise ValueError('tag')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
    base=ROOT/'results/autonomous_film_20261116_contact_6400_43'
    summary=json.loads((base/'summary.json').read_text())
    if summary['process_status']!='PASS':raise RuntimeError('incomplete actual source')
    path=base/'1/journal.csv';rows=list(csv.DictReader(path.open()))
    if len(rows)!=summary['expected_rows']:raise RuntimeError('partial journal')
    times=np.array([float(r['time']) for r in rows]);x=np.array([np.fromstring(r['x'],sep=' ').reshape(-1,3) for r in rows])
    rest=x[0].copy();rest[:,2]=0;u=x-rest
    h=2/len(rows);v=np.zeros_like(u);v[0]=u[0]/h;v[1]=(1.5*u[1]-2*u[0])/h
    v[2:]=(1.5*u[2:]-2*u[1:-1]+.5*u[:-2])/h
    reconstructed=np.max(np.linalg.norm(v,axis=2),axis=1);recorded=np.array([float(r['max_speed']) for r in rows])
    error=float(max(abs(reconstructed-recorded)))
    if error>1e-8:raise RuntimeError('kinematic reconstruction failed '+str(error))
    source=ROOT/'diagnostics/film_shell/ContactParticipation.cpp';shutil.copy2(source,out/source.name)
    build=logged(['g++','-std=c++17','-O2','-ffp-contract=off','-I/usr/include/eigen3',source,'-o',out/'participation'],out/'compile',180)
    if build['exit_code']:raise RuntimeError('modal build failure')
    report={}
    for target in (1.3,1.405,1.415,1.5,1.75,2.):
        i=int(np.argmin(abs(times-target)));snapshot=out/f'state_{target}.csv'
        np.savetxt(snapshot,np.concatenate([u[i],v[i]],axis=1),delimiter=',',header='ux,uy,uz,vx,vy,vz',comments='')
        stage=out/f'modal_{target}';process=logged([out/'participation',snapshot],stage,60)
        if process['exit_code']:raise RuntimeError('modal execution')
        report[str(target)]=dict(actual_time=float(times[i]),metrics=json.loads((stage/'stdout.log').read_text()),process=process)
    write_json(out/'summary.json',dict(source='actual SOFA coordinates;independent frozen tangent eigensolve',input_sha256=sha(path),source_sha256=sha(source),binary_sha256=sha(out/'participation'),
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),maximum_reconstructed_speed_error=error,states=report,
        limitation='Kinematic BDF2 reconstruction validated against recorded maximum speed, not direct full velocity output. Tangent mode fractions do not certify nonlinear energy closure.'))
    print(json.dumps(dict(speed_error=error,summary=str(out/'summary.json'))))

if __name__=='__main__':main()
