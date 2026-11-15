"""Bounded native calibration and quantitative force-unit checks."""
import os,json,shutil,argparse
import numpy as np
from closure_common import ROOT,OUT,SOFA,write_json,sha
from run_trial import execute_process
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--name',default='native_calibration');parser.add_argument('--dt',type=float,choices=[.001,.0005],default=.001);parser.add_argument('--intersection',choices=['MinProximityIntersection','LocalMinDistance'],default='MinProximityIntersection');args=parser.parse_args()
    out=OUT/args.name;out.mkdir(parents=True,exist_ok=False);scene=ROOT/'scenes/closure_native_calibration.py';shutil.copy2(scene,out/'scene.py');runtime=ROOT/'.runtime/python312'
    environment=dict(PYTHONHOME=str(runtime),PYTHONPATH=str(SOFA/'plugins/SofaPython3/lib/python3/site-packages')+':'+str(SOFA/'plugins/SofaPython3/lib'),LD_LIBRARY_PATH=str(runtime/'lib')+':'+str(SOFA/'lib')+':'+str(SOFA/'plugins/SofaPython3/lib'),REGRIP_NATIVE_OUT=str(out),REGRIP_NATIVE_DT=str(args.dt),REGRIP_INTERSECTOR=args.intersection);os.environ.update(environment);write_json(out/'environment.json',environment);steps=round(4/args.dt)
    command=[str(SOFA/'bin/runSofa-26.06.00'),'--noautoload','--tmp','-l',str(SOFA/'plugins/SofaPython3/lib/libSofaPython3.so'),'-g','batch','-a','-n',str(steps),'--hideProgressBar',str(out/'scene.py')];write_json(out/'command.json',command);process=execute_process(command,out,90);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();r=dict(process=process,status='FAIL',source_sha256=sha(out/'scene.py'),scope='independent native free BOX/plane calibration, side2/m=.01/I=.00666667, no object constraint or extra moment; NOT sphere convergence or100mm gripper certification',dt=args.dt)
    if process['exit_code']==0 and '[ERROR]' not in log and 'behavior is undefined' not in log and f'{steps} iterations done' in log and (out/'native.jsonl').exists():
        rows=[json.loads(s) for s in (out/'native.jsonl').read_text().splitlines()];tail=[s for s in rows if .8<s['time']<1.];normal=[s for s in rows if .3<s['time']<.5];slip=[s for s in rows if 1.3<s['time']<1.5];release=[s for s in rows if 1.8<s['time']<2.]
        r['frames']=len(rows)
        try:
            force_error=max(np.max(abs(np.array(s['constraint_wrench'])/args.dt+s['external'])) for s in tail);normal_fn=float(np.mean([s['constraint_wrench'][2]/args.dt for s in normal]));stick_speed=max(float(np.max(abs(np.array(s['V'][0])))) for s in tail);slip_speed=max(abs(s['V'][0][0]) for s in slip);release_rows=max(len(s['lambda_raw']) for s in release)
            recontact=any(s['time']>3.2 and s['constraint_wrench'] and s['constraint_wrench'][2]>0 for s in rows)
            r.update(normal_constraint_force=normal_fn,normal_applied_force=.01,normal_raw_multiplier=float(np.mean([s['constraint_wrench'][2] for s in normal])),force_interpretation='J^T lambda is generalized IMPULSE; divide bydt for mean physical force. EulerImplicit factors position=dt, velocity=1; independently checked by static balance.',stick_force_moment_abs_error=float(force_error),stick_max_speed=stick_speed,slip_speed=slip_speed,release_constraint_rows=release_rows,recontact=recontact,status='PASS' if abs(normal_fn-.01)<1e-6 and force_error<1e-5 and stick_speed<1e-5 and slip_speed>1e-4 and release_rows==0 and recontact and len(rows)==400 else 'FAIL')
        except (TypeError,ValueError,IndexError) as e:r['failure_reason']=str(e)
    r['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file()};write_json(out/'result.json',r);print(r)
if __name__=='__main__':main()
