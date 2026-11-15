"""Independent installed-engine native contact; SAME source rebuilt for its ABI."""
import os,json,argparse,shutil
import numpy as np
from beam_common import ROOT,OUT,BUILD,write_json,sha
from closure_common import SOFA
from closure_validation_suite import logged
from run_trial import execute_process
from trial_validation import read_states
def main():
    p=argparse.ArgumentParser();p.add_argument('--lat',type=int,choices=[12,24],default=12);p.add_argument('--name');args=p.parse_args();name=args.name or ('native_lat'+str(args.lat))
    if not name.replace('_','').isalnum():raise ValueError('native output name')
    out=OUT/name;out.mkdir(exist_ok=False)
    frame=BUILD/'native_frame/libReGripFrameClosure.so';beam=BUILD/'native_beam/libReGripConservativeBeam.so'
    for name,folder,directory,target in [('frame','models/closure_frame',frame.parent,'ReGripFrameClosure'),('beam','models/conservative_beam',beam.parent,'ReGripConservativeBeam')]:
        for stage,cmd in [('configure',['cmake','-S',folder,'-B',str(directory),'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SOFA)]),('build',['cmake','--build',str(directory),'--target',target,'-j2'])]:
            r=logged(cmd,out/(name+'_'+stage),180)
            if r['exit_code']:raise RuntimeError('native separate ABI build')
        logged(['ldd',str(frame if name=='frame' else beam)],out/(name+'_ldd'),15)
    source=out/'input';source.mkdir();config=json.loads((OUT/'grasp/Tz_v2/config.json').read_text());config['duration']=18.;write_json(source/'config.json',config);shutil.copy2(OUT/'grasp/Tz_v2/scene.scn',source/'scene.scn');runtime=ROOT/'.runtime/python312';scene=ROOT/'scenes/beam_native_surface.py';shutil.copy2(scene,out/'scene.py');env=dict(PYTHONHOME=str(runtime),PYTHONPATH=str(SOFA/'plugins/SofaPython3/lib/python3/site-packages')+':'+str(SOFA/'plugins/SofaPython3/lib'),LD_LIBRARY_PATH=str(runtime/'lib')+':'+str(SOFA/'lib')+':'+str(SOFA/'plugins/SofaPython3/lib'),REGRIP_NATIVE_SOURCE=str(source),REGRIP_NATIVE_OUT=str(out),REGRIP_NATIVE_SCENE=str(out/'scene.py'),REGRIP_NATIVE_FRAME=str(frame),REGRIP_NATIVE_BEAM=str(beam),REGRIP_NATIVE_STEPS='36000',REGRIP_SURFACE_LAT=str(args.lat),REGRIP_CONTACT_BUFFER='.001');os.environ.update(env);cmd=[str(runtime/'bin/python'),str(ROOT/'tools/beam_native_driver.py')];write_json(out/'command.json',cmd);write_json(out/'environment.json',env);process=execute_process(cmd,out,480);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();r=dict(status='FAIL',process=process,beam_sha256=sha(beam),frame_sha256=sha(frame),scene_sha256=sha(scene),engine='installed ONLY, matched-source beam/frame recompiled; NOT patched SDK native memory claim',scope='18s threeguided-finger native sphere Tz research,triangle/line/point,hard contact different from SDF compliance')
    try:
        if process['exit_code'] or '[ERROR]' in log or '36000 iterations done' not in log:raise ValueError('native errors/incomplete')
        raw=read_states(out/'state.txt');rows=[json.loads(s) for s in (out/'native.jsonl').read_text().splitlines()];obj=config['object_index'];F={round(s['time'],7):np.array(s['R']).reshape(-1,6) for s in raw};tail=[s for s in rows if 13.9-1e-8<=s['time']<14-1e-8];res=[];active=[]
        for s in tail:
            if s['generalized_impulse'] is None:raise ValueError('constraint row/multiplier mismatch')
            force=F[round(s['time'],7)]+np.array(s['generalized_impulse']).reshape(-1,6)/config['dt'];res.append(force[obj]);active.append(sum(np.array(s['lambda_impulse'])[::3]>1e-16))
        err=np.max(abs(np.array(res)),axis=0);checks=dict(force=float(err[:3].max()/1e-6)<1e-3,moment=float(err[3:].max()/5e-6)<1e-3,speed=max(np.max(abs(np.array(s['V'])[obj])) for s in tail)<1e-5,contact=min(active)>0);r.update(status='EXPERIMENTAL' if all(checks.values()) else 'FAIL',checks=checks,force_relative=float(err[:3].max()/1e-6),moment_relative=float(err[3:].max()/5e-6),minimum_positive_normal_contacts=int(min(active)),frames=len(rows),full_grasp_certified=False)
    except (ValueError,KeyError,OSError) as e:r['failure_reason']=str(e)
    # NumPy comparisons yield np.bool_; retain the measurements without rerunning
    # or overwriting the expensive native experiment when serializing them.
    if 'checks' in r:r['checks']={k:bool(v) for k,v in r['checks'].items()}
    r['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file()};write_json(out/'result.json',r);print(r['status'],r.get('checks'),r.get('failure_reason'))
if __name__=='__main__':main()
