"""Same-binary actual SOFA separated-film scheduling A/B; no physics gate waiver."""
import argparse,csv,hashlib,json,shutil,statistics,subprocess,xml.etree.ElementTree as ET
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
 parent=ROOT/'results/autonomous_film_20261119_stationary_gauss800_actual1618';m=json.loads((parent/'summary.json').read_text())
 proof=ROOT/'results/autonomous_film_20261119_gauss_parallel1630'
 # Resolve the uniquely qualified probe without guessing its tag.
 if not proof.exists():
  matches=list((ROOT/'results').glob('*1630'))
  if len(matches)!=1:raise ValueError('unique1630 probe required')
  proof=matches[0]
 pm=json.loads((proof/'summary.json').read_text())
 if m['status']!='PASS' or pm['status']!='PASS':raise ValueError('qualified actual and parallel probe required')
 for f,d in m['source_hashes'].items():
  if sha(parent/'sources'/f)!=d:raise ValueError('qualified source changed')
 for f,d in m['raw_hashes'].items():
  if sha(parent/f)!=d:raise ValueError('qualified raw changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(parent/'sources/models',archive/'models')
 for model in ('film_lateral_gauss_parallel','film_stationary_gauss_parallel'):shutil.copytree(ROOT/'models'/model,archive/'models'/model)
 base=archive/'models/film_stationary_gauss/GaussOwner.cpp';text=base.read_text();anchor='void registerFilmLateralField(sofa::core::ObjectFactory*);'
 if text.count(anchor)!=1:raise ValueError('exact registry anchor required')
 base.write_text(text.replace(anchor,'#ifndef REGRIP_STATIONARY_GAUSS_EMBEDDED\n'+anchor)+'\n#endif\n')
 build=ROOT/'build'/('stationary_gauss_parallel_'+a.tag);build.mkdir(exist_ok=False)
 r=dict(status='FAIL',scope='same-binary actual isolated50→50.8ms separated Gauss scheduling ONLY;NOT global time/energy/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),parent_summary_sha256=sha(parent/'summary.json'),probe_summary_sha256=sha(proof/'summary.json'),sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),root_work=None)
 r['configure']=guarded(['cmake','-S',archive/'models/film_stationary_gauss_parallel','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120)
 r['compile']=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if r['configure']['exit_code']==0 else None
 if not r['compile'] or r['compile']['exit_code']!=0:write_json(out/'summary.json',r);return
 binary=build/'libReGripStationaryGaussParallelPilot.so';deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
 if 'not found' in deps or any('libSofa.' in z and '=> /' in z and str(SDK) not in z for z in deps.splitlines()):raise ValueError('SDK ABI mismatch')
 sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};identity=hashlib.sha256(json.dumps(dict(source=sources,binary=sha(binary)),sort_keys=True).encode()).hexdigest();r.update(source_hashes=sources,binary_sha256=sha(binary),identity=identity,build_relative=str(build.relative_to(ROOT)))
 runs=[]
 for i,workers in enumerate((1,3,3,1,1,3)):
  folder=out/('trial'+str(i));folder.mkdir();tokens=(parent/'input.checkpoint').read_text().split();tokens[4]=identity;(folder/'input.checkpoint').write_text(' '.join(tokens)+'\n');tree=ET.parse(parent/'scene.scn');scene=tree.getroot();owner=scene.find('StationaryGaussExpandedPilotODE');owner.tag='StationaryGaussParallelPilotODE';owner.set('filmWorkers',str(workers));owner.set('identity',identity);owner.set('checkpoint',str(folder/'input.checkpoint'))
  for node in scene.iter():
   for k,v in list(node.attrib.items()):
    if k=='pluginName' and v.endswith('/libReGripStationaryGaussPilot.so'):
     if sha(v)!=m['binary_sha256']:raise ValueError('parent binary changed')
     node.set(k,str(binary))
    elif v.startswith(str(parent)):node.set(k,str(folder)+v[len(str(parent)):])
  tree.write(folder/'scene.scn');run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',folder/'scene.scn'],folder/'process',480);errors=sum((folder/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log'));record=dict(workers=workers,process=run,sofa_errors=errors,scene_sha256=sha(folder/'scene.scn'));runs.append(record)
  if run['exit_code'] or errors:break
  execution=next(csv.DictReader((folder/'three.gauss.execution.csv').open()));record['execution']=execution
  if int(execution['workers'])!=workers:raise ValueError('runtime worker selection mismatch')
  record['physical_hashes']={f.name:sha(f) for f in folder.iterdir() if f.suffix in ('.csv','.txt') and f.name!='three.gauss.execution.csv'}
  record['EXACT_vs_trial0']=record['physical_hashes']==runs[0]['physical_hashes']
  for name in ('three.states.csv','three.gauss.stages.csv','three.gauss.clearance.csv'):
   record.setdefault('EXACT_vs_qualified_actual',{})[name]=sha(folder/name)==sha(parent/name)
 r['trials']=runs
 good=len(runs)==6 and all(x.get('EXACT_vs_trial0') and all(x.get('EXACT_vs_qualified_actual',{}).values()) for x in runs)
 if good:
  wall={str(w):statistics.median(x['process']['runtime_s'] for x in runs if x['workers']==w) for w in (1,3)};kernel={str(w):statistics.median(float(x['execution']['kernel_inclusive_seconds']) for x in runs if x['workers']==w) for w in (1,3)};r.update(status='PASS' if wall['3']<wall['1'] and kernel['3']<kernel['1'] else 'FAIL',median_wall_s=wall,median_kernel_inclusive_s=kernel,wall_ratio=wall['3']/wall['1'],kernel_ratio=kernel['3']/kernel['1'])
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','trials','configure','compile')}))
if __name__=='__main__':main()
