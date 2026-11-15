"""Prepare optional basic SOFA replay from hash-verified measured states."""
import os,json
from grasp_common import ROOT,SOFA,OUT,write_json,sha
from trial_validation import read_states
from run_trial import execute_process

def main():
    source=OUT/'trials/settled_sphere_xplus';record=json.loads((source/'metrics.json').read_text())
    for name,digest in record['artifacts'].items():
        if sha(source/name)!=digest:raise RuntimeError('replay input changed')
    out=OUT/'visualization';out.mkdir(exist_ok=False);raw=read_states(source/'state.txt');write_json(out/'replay.json',dict(config=record['config'],frames=[dict(time=r['time'],X=r['X']) for r in raw],source_sha256=sha(source/'state.txt'),scope='recorded positions/quaternions, NOT simulated animation or new physics'))
    runtime=ROOT/'.runtime/python312';environment=dict(PYTHONHOME=str(runtime),PYTHONPATH=str(SOFA/'plugins/SofaPython3/lib/python3/site-packages')+':'+str(SOFA/'plugins/SofaPython3/lib'),LD_LIBRARY_PATH=str(runtime/'lib')+':'+str(SOFA/'lib')+':'+str(SOFA/'plugins/SofaPython3/lib'),REGRIP_REPLAY_DATA=str(out/'replay.json'));os.environ.update(environment);write_json(out/'environment.json',environment)
    base=[str(SOFA/'bin/runSofa-26.06.00'),'--noautoload','--tmp','-l',str(SOFA/'plugins/SofaPython3/lib/libSofaPython3.so')];scene=str(ROOT/'scenes/grasp_replay.py');command=base+['-g','batch','-a','-n','10',scene];write_json(out/'command.json',command);write_json(out/'gui_command.json',base+[scene]);p=execute_process(command,out,30);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text()
    result=dict(process=p,status='PASS' if p['exit_code']==0 and '[ERROR]' not in log and 'REGRIP_REPLAY_FRAME 9' in log else 'FAIL',gui_launched=False,physical_simulation=False,input_frames=len(raw),source_sha256=sha(source/'state.txt'))
    result['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file()};write_json(out/'result.json',result);print(result['status'])

if __name__=='__main__':main()
