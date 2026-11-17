"""Actual event-to-first-peak,only after complete independent same-input run."""
import argparse,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--reference',required=True);a=p.parse_args();ref=ROOT/'results'/('autonomous_film_'+a.reference);rs=json.loads((ref/'summary.json').read_text());src=ROOT/'results/autonomous_film_20261118_three_film_event_rows964';source=json.loads((src/'summary.json').read_text());continuation=json.loads((ROOT/'results/autonomous_film_20261118_three_film_event_sustained966/summary.json').read_text());impact=source['process']['runtime_s'];estimate=2*impact+2*(continuation['process']['runtime_s']-impact)*49/7+30
 if rs['status']!='PASS' or rs['completed_rows']!=50 or rs['dt']!=.0002 or rs['duration']!=.01 or rs.get('input_clock')!='accumulated' or estimate>480 or sha(ref/'reference.csv.states.csv')!=rs['states_sha256']:raise ValueError('complete matching-accumulated-clock peak and measured<=480s cost required;do NOT repeat old multiplied-clock mismatch')
 for name,digest in source['plugins'].items():
  if sha(name)!=digest:raise ValueError('immutable source plugin changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()}
 for name,digest in rs['sources'].items():
  if name.endswith('.h') and sources.get(name)!=digest:raise ValueError('independent peak header changed:'+name)
 build=ROOT/'build'/('three_film_peak_'+a.tag);build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',archive/'models/film_three_finger_event','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None;result=dict(status='FAIL',scope='actual separated impact through FIRST C2 peak10ms,NOT closing from rest/hold/release/time/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources=sources,reference=a.reference,reference_summary_sha256=sha(ref/'summary.json'),predicted_runtime_s=estimate,macro_steps=50,dt=.0002,duration=.01,sdk=str(SDK),configure=configure,compile=compile)
 if compile and compile['exit_code']==0:
  binary=build/'libReGripThreeFilmEvent.so';result['binary_sha256']=sha(binary);deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in line and '=> /' in line and str(SDK) not in line for line in deps.splitlines()):raise ValueError('peak SDK ABI mismatch')
  tree=ET.parse(src/'scene.scn');root=tree.getroot()
  for node in root.iter():
   for k,v in list(node.attrib.items()):
    if k in ('filename','displacementFilename','publicMassFilename') and v.startswith(str(src)):node.set(k,str(out)+v[len(str(src)):])
   if node.tag=='RequiredPlugin' and node.get('pluginName','').endswith('/libReGripThreeFilmEvent.so'):node.set('pluginName',str(binary))
  owner=root.find('ThreeFilmBracketedEventODE');owner.tag='ThreeFilmFirstPeakODE';owner.set('maxSteps','64');tree.write(out/'scene.scn');shutil.copy2(src/'public_mass_reference.txt',out/'public_mass_reference.txt');result['scene_sha256']=sha(out/'scene.scn');result['plugins']={n.get('pluginName'):sha(n.get('pluginName')) for n in root.findall('RequiredPlugin') if n.get('pluginName','').startswith('/')}
  run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','50','--hideProgressBar',out/'scene.scn'],out/'process',480);result['process']=run;result['sofa_errors']=sum((out/'process'/n).read_text(errors='replace').count('[ERROR]') for n in ('stdout.log','stderr.log'))
  if run['exit_code']==0 and not result['sofa_errors']:
   actual=list(csv.DictReader((out/'three.states.csv').open()));expected=list(csv.DictReader((ref/'reference.csv.states.csv').open()));rows=list(csv.DictReader((out/'three.rows.csv').open()))
   if len(actual)!=50 or len(expected)!=50 or len(rows)!=441:raise ValueError('incomplete peak state/stage journal')
   errors={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(actual,expected)) for k in ('q','v')};clock=max(abs(float(x['time'])-float(y['time'])) for x,y in zip(actual,expected));minimum=min(float(r['minimum_gap']) for r in actual);momentum=max(float(r['momentum_residual']) for r in actual);vn=max(float(r['normal_velocity_residual']) for r in actual);event_exact=sha(out/'three.event.csv')==sha(src/'three.event.csv');result.update(reference_max_abs=errors,absolute_api_gate=1e-12,clock_max_abs_s=clock,minimum_gap_mm=minimum,momentum_max_Ns=momentum,normal_velocity_max_mm_s=vn,common_event_exact=event_exact,status='PASS' if max(errors.values())<1e-12 and clock<=1e-12 and minimum>=-1e-10 and momentum<=1e-17 and vn<=1e-10 and event_exact else 'FAIL');result['raw_hashes']={n.name:sha(n) for n in out.glob('*.csv')}
 write_json(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','scope','reference_max_abs','process','sofa_errors') if k in result}))
if __name__=='__main__':main()
