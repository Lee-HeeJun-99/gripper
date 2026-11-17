"""Same-DLL OFF/ON first-interval journal purity;NO SOFA source changes."""
import argparse,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'results/autonomous_film_20261118_three_film_event_rows964';sm=json.loads((src/'summary.json').read_text())
 if sm['status']!='PASS' or sm['process']['exit_code']!=0 or sm['sofa_errors']:raise ValueError('completed actual isolated event required')
 for name,digest in sm['plugins'].items():
  if sha(name)!=digest:raise ValueError('immutable physical plugin changed')
 estimate=2*sm['process']['runtime_s']+30
 if estimate>480:raise ValueError('each passive trial exceeds480s forecast')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};build=ROOT/'build'/('three_film_first_journal_'+a.tag);build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',archive/'models/film_three_finger_event','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None;result=dict(status='FAIL',scope='actual same-DLL first-interval journal OFF/ON purity,NOT full energy/time/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources=sources,configure=configure,compile=compile,predicted_each_runtime_s=estimate,sdk=str(SDK),runs={})
 if compile and compile['exit_code']==0:
  binary=build/'libReGripThreeFilmEvent.so';result['binary_sha256']=sha(binary);deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in line and '=> /' in line and str(SDK) not in line for line in deps.splitlines()):raise ValueError('journal SDK ABI mismatch')
  for mode in ('off','on'):
   trial=out/mode;trial.mkdir();tree=ET.parse(src/'scene.scn');scene=tree.getroot()
   for node in scene.iter():
    for k,v in list(node.attrib.items()):
     if k in ('filename','displacementFilename','publicMassFilename') and v.startswith(str(src)):node.set(k,str(trial)+v[len(str(src)):])
    if node.tag=='RequiredPlugin' and node.get('pluginName','').endswith('/libReGripThreeFilmEvent.so'):node.set('pluginName',str(binary))
   scene.find('ThreeFilmBracketedEventODE').set('firstIntervalJournal',str(int(mode=='on')));tree.write(trial/'scene.scn');run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',trial/'scene.scn'],trial/'process',480);errors=sum((trial/'process'/n).read_text(errors='replace').count('[ERROR]') for n in ('stdout.log','stderr.log'));result['runs'][mode]=dict(process=run,sofa_errors=errors,scene_sha256=sha(trial/'scene.scn'));write_json(out/'partial.json',result)
  names=['three.states.csv','three.rows.csv','three.policy.csv','three.event.csv','three.impact_rows.csv']+['film_'+str(f)+'.csv' for f in range(3)]+['displacement_'+str(f)+'.csv' for f in range(3)]
  if all(r['process']['exit_code']==0 and not r['sofa_errors'] for r in result['runs'].values()):
   exact={n:dict(before=sha(out/'off'/n),after=sha(out/'on'/n),original=sha(src/n)) for n in names};stages=list(csv.DictReader((out/'on/three.first_interval.csv').open()));stage_names=[r['stage'] for r in stages];weights=sum(float(r['weight_s']) for r in stages);valid=all(r['before']==r['after']==r['original'] for r in exact.values()) and stage_names==['initial','free_midpoint','pre_impact','post_impact','contact_initial','contact_midpoint','contact_end'] and abs(weights-.0002)<=1e-18;result.update(status='PASS' if valid else 'FAIL',eleven_physical_CSV_exact=exact,stage_names=stage_names,total_quadrature_time_s=weights,first_interval_sha256=sha(out/'on/three.first_interval.csv'),initial_state='same separated200us actual fixture,not grasp',full_energy_gate='BLOCKED:inventory not yet analyzed/root/friction/fullcycle absent')
 write_json(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','stage_names','total_quadrature_time_s','runs') if k in result}))
if __name__=='__main__':main()
