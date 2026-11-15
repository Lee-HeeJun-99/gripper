"""Prepare optional basic SOFA replay from hash-verified measured states."""
import os,json,argparse
from grasp_common import ROOT,SOFA,OUT,write_json,sha
from trial_validation import read_states
from run_trial import execute_process

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--name',default='visualization');parser.add_argument('--source',default='settled_sphere_xplus');parser.add_argument('--all-frames',action='store_true');args=parser.parse_args()
    source=OUT/'trials'/args.source;record=json.loads((source/'metrics.json').read_text())
    for name,digest in record['artifacts'].items():
        if sha(source/name)!=digest:raise RuntimeError('replay input changed')
    out=OUT/args.name;out.mkdir(exist_ok=False);raw=read_states(source/'state.txt');write_json(out/'replay.json',dict(config=record['config'],frames=[dict(time=r['time'],X=r['X']) for r in raw],source_sha256=sha(source/'state.txt'),scope='recorded positions/quaternions, NOT simulated animation or new physics'))
    runtime=ROOT/'.runtime/python312';environment=dict(PYTHONHOME=str(runtime),PYTHONPATH=str(SOFA/'plugins/SofaPython3/lib/python3/site-packages')+':'+str(SOFA/'plugins/SofaPython3/lib'),LD_LIBRARY_PATH=str(runtime/'lib')+':'+str(SOFA/'lib')+':'+str(SOFA/'plugins/SofaPython3/lib'),REGRIP_REPLAY_DATA=str(out/'replay.json'));os.environ.update(environment);write_json(out/'environment.json',environment)
    base=[str(SOFA/'bin/runSofa-26.06.00'),'--noautoload','--tmp','-l',str(SOFA/'plugins/SofaPython3/lib/libSofaPython3.so')];scene=str(ROOT/'scenes/grasp_replay.py');steps=len(raw) if args.all_frames else 10;command=base+['-g','batch','-a','-n',str(steps),scene];write_json(out/'command.json',command);write_json(out/'gui_command.json',base+[scene]);p=execute_process(command,out,30);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text()
    complete=f'{steps} iterations done' in log and (not args.all_frames or 'REGRIP_REPLAY_COMMANDED_JAM True' in log and log.count('REGRIP_REPLAY_COMMANDED_JAM False')>=2)
    result=dict(process=p,status='PASS' if p['exit_code']==0 and '[ERROR]' not in log and 'behavior is undefined' not in log and 'REGRIP_REPLAY_FRAME 9' in log and complete else 'FAIL',gui_launched=False,physical_simulation=False,input_frames=len(raw),replayed_frames=steps,commanded_jam_on_off_observed='REGRIP_REPLAY_COMMANDED_JAM True' in log and log.count('REGRIP_REPLAY_COMMANDED_JAM False')>=2,source_sha256=sha(source/'state.txt'),replay_code_sha256=sha(ROOT/'scenes/grasp_replay.py'))
    result['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file()};write_json(out/'result.json',result);print(result['status'])

if __name__=='__main__':main()
