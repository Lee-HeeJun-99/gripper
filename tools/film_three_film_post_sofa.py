"""Actual common-impact then post-contact dt refinement,NOT whole-impact time."""
import argparse,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--reference',required=True);p.add_argument('--refinement',type=int,choices=(1,2,4),required=True);p.add_argument('--reuse');p.add_argument('--sync-child-clocks',action='store_true');a=p.parse_args();ref=ROOT/'results'/('autonomous_film_'+a.reference);rs=json.loads((ref/'summary.json').read_text());src=ROOT/'results/autonomous_film_20261118_three_film_event_rows964';source=json.loads((src/'summary.json').read_text());baseline=json.loads((ROOT/'results/autonomous_film_20261118_three_film_event_sustained966/summary.json').read_text());steps=1+7*a.refinement;estimate=2*baseline['process']['runtime_s']*steps/8+30
 if rs['status']!='PASS' or rs['steps']!=7*a.refinement or estimate>480 or baseline['status']!='PASS' or sha(ref/'states.csv')!=rs['states_sha256']:raise ValueError('completed physical post-reference and measured policy budget required')
 for n,digest in source['plugins'].items():
  if sha(n)!=digest:raise ValueError('immutable source plugin changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()}
 for n,digest in rs['sources'].items():
  if n.endswith('.h') and sources[n]!=digest:raise ValueError('post-reference kernel changed:'+n)
 build=ROOT/'build'/('three_film_post_'+a.tag)
 if a.reuse:
  prior=ROOT/'results'/('autonomous_film_'+a.reuse);old=json.loads((prior/'summary.json').read_text());build=ROOT/'build'/('three_film_post_'+a.reuse);compiled=lambda d:{k:v for k,v in d.items() if k.endswith(('.h','.cpp','/CMakeLists.txt'))}
  if old['status']!='PASS' or sha(build/'libReGripThreeFilmEvent.so')!=old['binary_sha256']:raise ValueError('actual same completed binary required')
  reuse_proof=None
  if compiled(old['sources'])!=compiled(sources):
   # GCC's emitted dependency closure,not an arbitrary filename exemption.
   # No included file may change;an added unreferenced research header cannot
   # affect this immutable DLL. Guard target CMake separately as well.
   dep=build/'CMakeFiles/ReGripThreeFilmEvent.dir/ThreeFilmEventOwner.cpp.o.d';prefix=str(prior/'sources')+'/';tokens=dep.read_text().replace('\\\n',' ').split();dependencies=sorted({str(Path(t).resolve().relative_to((prior/'sources').resolve())) for t in tokens if t.startswith(prefix)})
   if not dependencies or 'models/film_three_finger_event/ThreeFilmEventOwner.cpp' not in dependencies:raise ValueError('missing actual compiler dependency closure')
   dependencies.append('models/film_three_finger_event/CMakeLists.txt')
   for name in dependencies:
    if old['sources'].get(name)!=sources.get(name) or sha(prior/'sources'/name)!=old['sources'].get(name):raise ValueError('compiled dependency/CMake changed:'+name)
   changed=sorted(k for k in compiled(old['sources']).keys()|compiled(sources).keys() if old['sources'].get(k)!=sources.get(k));reuse_proof=dict(dependency_sha256=sha(dep),checked_included_sources=dependencies,changed_unlinked_files=changed,scope='same immutable DLL;ONLY compiler-proven unlinked source differences allowed')
  configure=compile=dict(exit_code=0,reused=a.reuse)
 else:
  build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',archive/'models/film_three_finger_event','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None
 result=dict(status='FAIL',scope='actual SAME common200us impact,then7/14/28 persistent steps;NOT whole-event refinement/release/full energy/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources=sources,reference=a.reference,reference_summary_sha256=sha(ref/'summary.json'),reference_states_sha256=sha(ref/'states.csv'),refinement=a.refinement,macro_steps=steps,duration=.0016,common_impact_dt=.0002,post_contact_dt=.0002/a.refinement,predicted_runtime_s=estimate,configure=configure,compile=compile,sdk=str(SDK))
 if a.reuse and reuse_proof:result['compiled_dependency_reuse_proof']=reuse_proof
 if compile and compile['exit_code']==0:
  binary=build/'libReGripThreeFilmEvent.so';result['binary_sha256']=sha(binary);deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in l and '=> /' in l and str(SDK) not in l for l in deps.splitlines()):raise ValueError('post-continuation SDK ABI mismatch')
  tree=ET.parse(src/'scene.scn');root=tree.getroot()
  for node in root.iter():
   for k,v in list(node.attrib.items()):
    if k in ('filename','displacementFilename','publicMassFilename') and v.startswith(str(src)):node.set(k,str(out)+v[len(str(src)):])
   if node.tag=='RequiredPlugin' and node.get('pluginName','').endswith('/libReGripThreeFilmEvent.so'):node.set('pluginName',str(binary))
  owner=root.find('ThreeFilmBracketedEventODE');owner.tag='ThreeFilmVariableContinuationODE';owner.set('maxSteps','32');ET.SubElement(root,'ThreeFilmPostImpactClock',dict(name='post_clock',refinement=str(a.refinement),synchronizeChildren=str(int(a.sync_child_clocks)),filename=str(out/'clock.csv')));tree.write(out/'scene.scn');shutil.copy2(src/'public_mass_reference.txt',out/'public_mass_reference.txt');result['synchronize_child_clocks']=a.sync_child_clocks;result['scene_sha256']=sha(out/'scene.scn');result['plugins']={n.get('pluginName'):sha(n.get('pluginName')) for n in root.findall('RequiredPlugin') if n.get('pluginName','').startswith('/')}
  run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',out/'scene.scn'],out/'process',480);result['process']=run;result['sofa_errors']=sum((out/'process'/n).read_text(errors='replace').count('[ERROR]') for n in ('stdout.log','stderr.log'))
  if run['exit_code']==0 and not result['sofa_errors'] and (out/'clock.csv').exists():
   actual=list(csv.DictReader((out/'three.states.csv').open()));expected=list(csv.DictReader((ref/'states.csv').open()));clock=list(csv.DictReader((out/'clock.csv').open()));rows=list(csv.DictReader((out/'three.rows.csv').open()))
   if len(actual)!=steps or len(expected)!=steps-1 or len(clock)!=steps or len(rows)!=9*(steps-1):raise ValueError('incomplete actual clocks/states/stages')
   error={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(actual[1:],expected)) for k in ('q','v')};clock_error=max(abs(float(x['time'])-float(y['time'])) for x,y in zip(actual[1:],expected));schedule=all(float(r['used_dt'])==(.0002 if i==0 else .0002/a.refinement) for i,r in enumerate(clock)) and abs(float(actual[-1]['time'])-.0016)<=1e-12
   event_equal=all(sha(out/n)==sha(src/n) for n in ('three.event.csv','three.impact_rows.csv'));minimum=min(float(r['minimum_gap']) for r in actual);momentum=max(float(r['momentum_residual']) for r in actual);vn=max(float(r['normal_velocity_residual']) for r in actual);result.update(reference_max_abs=error,clock_max_abs_s=clock_error,schedule_valid=schedule,common_event_exact=event_equal,minimum_gap_mm=minimum,momentum_max_Ns=momentum,normal_velocity_max_mm_s=vn)
   result['status']='PASS' if max(error.values())<=1e-11 and clock_error<=1e-12 and schedule and event_equal and minimum>=-1e-10 and momentum<=1e-17 and vn<=1e-10 else 'FAIL';result['raw_hashes']={n.name:sha(n) for n in out.glob('*.csv')}
 write_json(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','refinement','reference_max_abs','common_event_exact','schedule_valid','process','sofa_errors') if k in result}))
if __name__=='__main__':main()
