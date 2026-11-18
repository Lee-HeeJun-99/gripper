"""Actual V5 controller corruption rejection before any accepted state."""
import argparse,json,shutil,xml.etree.ElementTree as ET
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'results/autonomous_film_20261118_three_film_persistent_recovery1111';meta=json.loads((src/'summary.json').read_text());checkpoint=src/'three.checkpoint_207.txt'
 if meta['status']!='PASS' or sha(checkpoint)!=meta['raw_hashes'][checkpoint.name]:raise ValueError('unchanged actual V5 checkpoint required')
 original=checkpoint.read_text().split();next_dt=original[original.index('EXPECTED_NEXT_DT')+1];cases={'next_dt':('EXPECTED_NEXT_DT','.000101','accumulated clock/next-dt invalid'),'remaining':('STEPS_REMAINING','2','counter/duration/current-dt invalid'),'used_dt':('USED_DT','.0002','counter/duration/current-dt invalid'),'global_counter':(None,'206','counter/duration/current-dt invalid')};out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');results={}
 for name,(label,value,message) in cases.items():
  trial=out/name;trial.mkdir();tokens=original.copy();tokens[tokens.index(label)+1 if label else 3]=value;(trial/'input.checkpoint').write_text(' '.join(tokens)+'\n');tree=ET.parse(src/'scene.scn');scene=tree.getroot();scene.set('time',original[1]);scene.set('dt',next_dt);owner=scene.find('ThreeFilmPersistentRecoveryODE');owner.set('checkpoint',str(trial/'input.checkpoint'))
  for node in scene.iter():
   for key,text in list(node.attrib.items()):
    if key in ('filename','displacementFilename','publicMassFilename') and text.startswith(str(src)):node.set(key,str(trial)+text[len(str(src)):])
  tree.write(trial/'scene.scn');run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',trial/'scene.scn'],trial/'process',60);logs=''.join((trial/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));state=trial/'three.states.csv';no_commit=not state.exists() or len(state.read_text().splitlines())<=1;results[name]=dict(status='PASS' if message in logs and no_commit else 'FAIL',expected_rejection=message,no_accepted_commit=no_commit,input_checkpoint_sha256=sha(trial/'input.checkpoint'),process=run)
 write_json(out/'summary.json',dict(status='PASS' if all(r['status']=='PASS' for r in results.values()) else 'FAIL',scope='actual bounded V5 controller corruption guards;NOT physics/recovery certificate',parent_summary_sha256=sha(src/'summary.json'),source_checkpoint_sha256=sha(checkpoint),binary_sha256=meta['binary_sha256'],cases=results));print(json.dumps({n:r['status'] for n,r in results.items()}))
if __name__=='__main__':main()
