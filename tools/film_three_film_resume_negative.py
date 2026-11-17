"""Same-DLL checkpoint negative controls;reject before any accepted step."""
import argparse,json,shutil,xml.etree.ElementTree as ET
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--parent',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.parent);meta=json.loads((src/'summary.json').read_text())
 if meta['status']!='PASS' or sha(src/'input.checkpoint')!=meta['checkpoint_sha256']:raise ValueError('qualified immutable transfer required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');runs={}
 # Token offsets in the versioned fixed-1953-DOF checkpoint protocol.
 cases={'identity':(4,'0'*64,'header/provenance/time'),'quaternion':(5+3906,'2','finite/quaternion/local-chart'),'mass':(5+3906+4,'1','exact public nodal mass'),'mapping':(5+3906+4+693+36,'999','root mapping'),'row':(-6,'999','accepted contact owner')}
 for name,(index,value,message) in cases.items():
  trial=out/name;trial.mkdir();tokens=(src/'input.checkpoint').read_text().split();tokens[index]=value;(trial/'input.checkpoint').write_text(' '.join(tokens)+'\n');tree=ET.parse(src/'scene.scn');scene=tree.getroot();scene.find('ThreeFilmResumeODE').set('checkpoint',str(trial/'input.checkpoint'))
  for node in scene.iter():
   for k,v in list(node.attrib.items()):
    if k in ('filename','displacementFilename','publicMassFilename') and v.startswith(str(src)):node.set(k,str(trial)+v[len(str(src)):])
tree.write(trial/'scene.scn');run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',trial/'scene.scn'],trial/'process',60);logs=''.join((trial/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));state=trial/'three.states.csv';no_commit=not state.exists() or len(state.read_text().splitlines())<=1;runs[name]=dict(status='PASS' if message in logs and no_commit else 'FAIL',expected_rejection=message,no_accepted_commit=no_commit,process=run,checkpoint_sha256=sha(trial/'input.checkpoint'))
 write_json(out/'summary.json',dict(status='PASS' if all(r['status']=='PASS' for r in runs.values()) else 'FAIL',scope='actual same-DLL corrupted checkpoint rejection;NOT physics performance',binary_sha256=meta['binary_sha256'],parent_summary_sha256=sha(src/'summary.json'),runs=runs));print(json.dumps({n:r['status'] for n,r in runs.items()}))
if __name__=='__main__':main()
