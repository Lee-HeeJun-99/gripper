"""Selected full native surface simulation; no source benchmark overwritten."""
import os,json,shutil,argparse
import numpy as np
from closure_common import ROOT,OUT,SOFA,BUILD,sha,write_json,provenance
from run_trial import execute_process
from trial_validation import read_states
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--lat',type=int,choices=[12,24,48],default=24);parser.add_argument('--name',default='native_gripper');args=parser.parse_args();out=OUT/args.name;out.mkdir(exist_ok=False);source=OUT/'trials/wrenches_Fxplus';config=json.loads((source/'config.json').read_text());runtime=ROOT/'.runtime/python312';scene=ROOT/'scenes/closure_native_gripper.py';shutil.copy2(scene,out/'scene.py');steps=round(config['duration']/config['dt']);plugin=BUILD/'release/libReGripClosure.so'
    env=dict(PYTHONHOME=str(runtime),PYTHONPATH=str(SOFA/'plugins/SofaPython3/lib/python3/site-packages')+':'+str(SOFA/'plugins/SofaPython3/lib'),LD_LIBRARY_PATH=str(runtime/'lib')+':'+str(SOFA/'lib')+':'+str(SOFA/'plugins/SofaPython3/lib'),REGRIP_NATIVE_SOURCE=str(source),REGRIP_NATIVE_OUT=str(out),REGRIP_NATIVE_SCENE=str(out/'scene.py'),REGRIP_NATIVE_PLUGIN=str(plugin),REGRIP_NATIVE_STEPS=str(steps),REGRIP_SURFACE_LAT=str(args.lat));os.environ.update(env);command=[str(runtime/'bin/python'),str(ROOT/'tools/closure_native_driver.py')];write_json(out/'command.json',command);write_json(out/'environment.json',env);write_json(out/'config.json',config);p=execute_process(command,out,480);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();result=dict(status='FAIL',process=p,provenance=provenance(),source_sha256=sha(out/'scene.py'),binary_sha256=sha(plugin),scope='independent native hard-contact triangle film skin, not calibrated PET or identical normal compliance to SDF; no global grasp certificate',object_latitude_divisions=args.lat)
    try:
        if p['exit_code'] or '[ERROR]' in log or 'behavior is undefined' in log or f'{steps} iterations done' not in log:raise ValueError('native engine error/incomplete')
        states=read_states(out/'native_state.txt');rows=[json.loads(s) for s in (out/'native_states.jsonl').read_text().splitlines()];obj=config['object_index'];tail=[r for r in rows if config['hold_until']-.1-1e-8<=r['time']<config['hold_until']-1e-8];forces={round(r['time'],7):np.array(r['R']).reshape(-1,6)[obj] for r in states};residual=[]
        for row in tail:
            if row['constraint_impulse'] is None:raise ValueError('missing constraint impulse')
            impulse=np.array(row['constraint_impulse']).reshape(-1,6)[obj] if row['constraint_impulse'] else np.zeros(6);residual.append(forces[round(row['time'],7)]+impulse/config['dt'])
        if not tail or len(rows)!=steps//20:raise ValueError('native frames/tail missing')
        absolute=np.max(abs(np.array(residual)),axis=0);fr=float(absolute[:3].max()/abs(config['load']));mr=float(absolute[3:].max()/(abs(config['load'])*config['object_radius']));speed=float(max(np.max(abs(np.array(r['V'])[obj,:3])) for r in tail));checks=dict(force=fr<1e-3,moment=mr<1e-3,velocity=speed<1e-5)
        result.update(status='EXPERIMENTAL' if all(checks.values()) else 'FAIL',execution_completed=True,hold_subchecks=checks,frames=len(rows),object_force_relative=fr,object_moment_relative=mr,object_speed=speed,minimum_hold_constraint_rows=min(len(r['constraint_forces']) for r in tail),max_raw_multiplier=max((max(map(abs,r['constraint_forces']),default=0) for r in rows),default=0))
    except (ValueError,OSError,KeyError,IndexError) as e:result['failure_reason']=str(e)
    result['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file()};write_json(out/'result.json',result);print(result)
if __name__=='__main__':main()
