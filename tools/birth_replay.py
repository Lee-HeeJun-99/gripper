"""Prepare optional SOFA replay from measured states; not a new physics run."""
import csv,json
from birth_common import ROOT,OUT,sha,write_json
from closure_common import SOFA
from trial_validation import read_states
def main():
    source=OUT/'grasp/base';r=json.loads((source/'metrics.json').read_text())
    for name,digest in r['artifacts'].items():
        if sha(source/name)!=digest:raise ValueError('changed replay input '+name)
    out=OUT/'replay';out.mkdir(exist_ok=False);states=read_states(source/'state.txt');patch={}
    with(source/'contact.csv.patch.csv').open()as f:
        for row in csv.DictReader(f):patch.setdefault(round(float(row['time']),7),[]).append([float(row[k])for k in('px','py','pz')])
    write_json(out/'replay.json',dict(config=r['config'],frames=[dict(time=s['time'],X=s['X'],contacts=patch.get(round(s['time'],7),[]))for s in states],source_sha256=sha(source/'state.txt'),scope='actual recorded coordinates; contact markers are normal quadrature only; no full grasp approval'))
    rt=ROOT/'.runtime/python312';env=dict(PYTHONHOME=str(rt),PYTHONPATH=str(SOFA/'plugins/SofaPython3/lib/python3/site-packages')+':'+str(SOFA/'plugins/SofaPython3/lib'),LD_LIBRARY_PATH=str(rt/'lib')+':'+str(SOFA/'lib')+':'+str(SOFA/'plugins/SofaPython3/lib'),REGRIP_REPLAY_DATA=str(out/'replay.json'));write_json(out/'environment.json',env)
    command=[str(SOFA/'bin/runSofa-26.06.00'),'--noautoload','--tmp','-l',str(SOFA/'plugins/SofaPython3/lib/libSofaPython3.so'),str(ROOT/'scenes/closure_replay.py')];write_json(out/'gui_command.json',command)
    write_json(out/'metrics.json',dict(status='EXPERIMENTAL',prepared=True,gui_launched=False,headless_replay_executed=False,physical_simulation=False,frames=len(states),source_sha256=sha(source/'state.txt'),scene_sha256=sha(ROOT/'scenes/closure_replay.py')));print('prepared',len(states),'measured frames; GUI NOT RUN')
if __name__=='__main__':main()
