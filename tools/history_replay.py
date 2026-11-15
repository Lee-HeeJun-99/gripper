"""Optional replay of actual new-history states, never a physical gate."""
import csv,json,os
from history_common import ROOT,OUT,write_json,sha
from closure_common import SOFA
from trial_validation import read_states
from run_trial import execute_process
def main():
    source=OUT/'grasp/repeated';r=json.loads((source/'metrics.json').read_text())
    for name,digest in r['artifacts'].items():
        if sha(source/name)!=digest:raise ValueError('changed replay input '+name)
    out=OUT/'replay';out.mkdir(exist_ok=False);raw=read_states(source/'state.txt');patch={}
    with (source/'contact.csv.patch.csv').open() as f:
        for row in csv.DictReader(f):patch.setdefault(round(float(row['time']),7),[]).append([float(row[k]) for k in ('px','py','pz')])
    write_json(out/'replay.json',dict(config=r['config'],frames=[dict(time=s['time'],X=s['X'],contacts=patch.get(round(s['time'],7),[])) for s in raw],source_sha256=sha(source/'state.txt'),scope='actual saved guided three-finger research states; contact marker locations from NORMAL quadrature, not full tangent force samples; no full-grasp certificate'))
    rt=ROOT/'.runtime/python312';env=dict(PYTHONHOME=str(rt),PYTHONPATH=str(SOFA/'plugins/SofaPython3/lib/python3/site-packages')+':'+str(SOFA/'plugins/SofaPython3/lib'),LD_LIBRARY_PATH=str(rt/'lib')+':'+str(SOFA/'lib')+':'+str(SOFA/'plugins/SofaPython3/lib'),REGRIP_REPLAY_DATA=str(out/'replay.json'));os.environ.update(env);write_json(out/'environment.json',env)
    base=[str(SOFA/'bin/runSofa-26.06.00'),'--noautoload','--tmp','-l',str(SOFA/'plugins/SofaPython3/lib/libSofaPython3.so')];scene=str(ROOT/'scenes/closure_replay.py');cmd=base+['-g','batch','-a','-n',str(len(raw)),scene];write_json(out/'command.json',cmd);write_json(out/'gui_command.json',base+[scene]);p=execute_process(cmd,out,60);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();checks=dict(exit_clean=p['exit_code']==0,error_free='[ERROR]' not in log,complete=f'{len(raw)} iterations done' in log,measured_frames='REGRIP_REPLAY_FRAME 9' in log,on_off='REGRIP_REPLAY_COMMANDED_JAM True' in log and log.count('REGRIP_REPLAY_COMMANDED_JAM False')>=2)
    write_json(out/'metrics.json',dict(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,process=p,gui_launched=False,physical_simulation=False,source_sha256=sha(source/'state.txt'),scene_sha256=sha(ROOT/'scenes/closure_replay.py')));print(checks)
if __name__=='__main__':main()
