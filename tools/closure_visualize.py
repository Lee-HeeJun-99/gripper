"""Recorded three-finger positions/contact points, hash checked before replay."""
import csv,json,os
from closure_frame_common import ROOT,OUT,SOFA,write_json,sha
from trial_validation import read_states
from run_trial import execute_process
def main():
    source=OUT/'trials/pilot_Tz';r=json.loads((source/'metrics.json').read_text())
    for name,digest in r['artifacts'].items():
        if sha(source/name)!=digest:raise ValueError('corrupt replay input '+name)
    out=OUT/'replay';out.mkdir(exist_ok=False);raw=read_states(source/'state.txt');patch={}
    with (source/'contact.csv.patch.csv').open() as f:
        for row in csv.DictReader(f):patch.setdefault(round(float(row['time']),7),[]).append([float(row[k]) for k in ('px','py','pz')])
    write_json(out/'replay.json',dict(config=r['config'],frames=[dict(time=s['time'],X=s['X'],contacts=patch.get(round(s['time'],7),[])) for s in raw],source_sha256=sha(source/'state.txt'),scope='measured state and sampled contact positions only, no synthetic trajectory; pilot not full grasp certificate'))
    runtime=ROOT/'.runtime/python312';environment=dict(PYTHONHOME=str(runtime),PYTHONPATH=str(SOFA/'plugins/SofaPython3/lib/python3/site-packages')+':'+str(SOFA/'plugins/SofaPython3/lib'),LD_LIBRARY_PATH=str(runtime/'lib')+':'+str(SOFA/'lib')+':'+str(SOFA/'plugins/SofaPython3/lib'),REGRIP_REPLAY_DATA=str(out/'replay.json'));os.environ.update(environment);write_json(out/'environment.json',environment)
    base=[str(SOFA/'bin/runSofa-26.06.00'),'--noautoload','--tmp','-l',str(SOFA/'plugins/SofaPython3/lib/libSofaPython3.so')];scene=str(ROOT/'scenes/closure_replay.py');command=base+['-g','batch','-a','-n',str(len(raw)),scene];write_json(out/'command.json',command);write_json(out/'gui_command.json',base+[scene]);p=execute_process(command,out,60);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();checks=dict(exit_clean=p['exit_code']==0,error_free='[ERROR]' not in log,complete=f'{len(raw)} iterations done' in log,actual_frames='REGRIP_REPLAY_FRAME 9' in log,on_off='REGRIP_REPLAY_COMMANDED_JAM True' in log and log.count('REGRIP_REPLAY_COMMANDED_JAM False')>=2)
    result=dict(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,process=p,gui_launched=False,physical_simulation=False,frames=len(raw),source_sha256=sha(source/'state.txt'),scene_sha256=sha(ROOT/'scenes/closure_replay.py'));result['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file()};write_json(out/'result.json',result);print(result['status'])
if __name__=='__main__':main()
