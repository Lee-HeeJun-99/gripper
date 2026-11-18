"""Source-bound actual zero-load face release; independent reference required."""
import argparse,csv,hashlib,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--reference',required=True);a=p.parse_args()
 ref=ROOT/'results'/('autonomous_film_'+a.reference);proof=json.loads((ref/'summary.json').read_text());parent=ROOT/'results/autonomous_film_20261119_stationary_to268_1573';m=json.loads((parent/'summary.json').read_text());cp=ref/'input.checkpoint'
 if proof['status']!='PASS' or proof['grid'] not in (32,64,128) or proof.get('external_force_N')!=[0,0,0] or m['status']!='PASS' or sha(cp)!=proof['input_checkpoint_sha256'] or sha(cp)!=m['raw_hashes']['three.checkpoint_134.txt']:raise ValueError('qualified same-IVP zero-load reference and actual checkpoint required')
 for path,meta in ((ref,proof),(parent,m)):
  for f,d in meta['source_hashes'].items():
   if sha(path/'sources'/f)!=d:raise ValueError('immutable source archive changed')
  for f,d in meta['raw_hashes'].items():
   if sha(path/f)!=d:raise ValueError('immutable raw changed')
 if sha(ref/'reference')!=proof['binary_sha256']:raise ValueError('reference binary changed')
 tokens=cp.read_text().split();time,h=float(tokens[1]),float(tokens[2]);forecast=2*proof['process']['runtime_s']+30
 if tokens[0]!='REGRIP_STATIONARY_CONTACT_V1' or tokens[4]!=m['identity'] or h!=.0002 or not .0267<time<.0269:raise ValueError('typed stationary accumulated-clock fixture required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ref/'sources/models',archive/'models');shutil.copytree(ROOT/'models/film_stationary_release',archive/'models/film_stationary_release')
 # Older qualified persistent archive has unconditional plugin registration.
 # Wrap registration ONLY;never copy a newer physical owner over the archive.
 owner_source=archive/'models/film_lateral_rest_contact/StationaryImpact.cpp';owner_text=owner_source.read_text();anchor='void registerFilmLateralField(sofa::core::ObjectFactory*);'
 if '#ifndef REGRIP_STATIONARY_CONTACT_EMBEDDED' not in owner_text:
  if owner_text.count(anchor)!=1:raise ValueError('exact historical registration anchor differs')
  owner_source.write_text(owner_text.replace(anchor,'#ifndef REGRIP_STATIONARY_CONTACT_EMBEDDED\n'+anchor)+'\n#endif\n')
 # Embedded legacy owners still compile their EDGE overload even though this
 # owner invokes only the qualified FACE overload. Preserve that old API body
 # alongside (not instead of) the independently qualified face equations.
 for header,anchor in (('film_routed_contact/AdmissibleRelease.h','inline Result resolve('),('film_three_finger_resume/AccelerationRelease.h','inline AccelerationRelease accelerationRelease(')):
  original=(parent/'sources/models'/header).read_text();adapted=archive/'models'/header;text=adapted.read_text()
  if original.count(anchor)!=1 or text.count(anchor)!=1 or 'const std::vector<EdgeOwner>&edges' not in original or 'const std::vector<ContactOwner>&edges' not in text:raise ValueError('exact archived edge/qualified face overload anchors required')
  body=original[original.index(anchor):original.rindex('\n}')];at=text.rindex('\n}');adapted.write_text(text[:at]+'\n'+body+'\n'+text[at:])
 sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};build=ROOT/'build'/('stationary_release_'+a.tag);build.mkdir(exist_ok=False)
 configure=guarded(['cmake','-S',archive/'models/film_stationary_release','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None
 r=dict(status='FAIL',scope='ACTUAL zero-load stationary-origin face release26.8..27ms ONLY;NOT whole time/energy/wrapping/holding/lift',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,reference_summary_sha256=sha(ref/'summary.json'),parent_summary_sha256=sha(parent/'summary.json'),source_checkpoint_sha256=sha(cp),configure=configure,compile=compile,predicted_child_runtime_s=forecast,sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),external_force_N=[0,0,0],root_work=None,legacy_sampled_work='NOT restored/spliced',release_time='collocation admissibility/RK stages,NOT certified continuous exit time',momentum_metric='sum of reduced segment residual norms;NOT independent global defect')
 if compile and compile['exit_code']==0:
  binary=build/'libReGripStationaryRelease.so';deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in x and '=> /' in x and str(SDK) not in x for x in deps.splitlines()):raise ValueError('SDK ABI mismatch')
  identity=hashlib.sha256(json.dumps(dict(source=sources,binary=sha(binary),input=sha(cp)),sort_keys=True).encode()).hexdigest();original=tokens.copy();tokens[4]=identity;(out/'input.checkpoint').write_text(' '.join(tokens)+'\n')
  if tokens[:4]+tokens[5:]!=original[:4]+original[5:]:raise ValueError('physical checkpoint changed')
  if sha(parent/'scene.scn')!=m['scene_sha256']:raise ValueError('actual scene changed')
  tree=ET.parse(parent/'scene.scn');scene=tree.getroot();scene.set('time',format(time,'.17g'));owner=scene.find('StationaryPersistentODE')
  if owner is None or owner.get('externalForce') not in ('0 0 0','0.0 0.0 0.0'):raise ValueError('actual zero-load owner required')
  # Keep the inherited validated maximum-step budget unchanged. This isolated
  # owner separately rejects count!=0 and runSofa executes exactly ONE step.
  owner.tag='StationaryReleaseODE';owner.set('checkpoint',str(out/'input.checkpoint'));owner.set('identity',identity);owner.set('endTime',format(time+h,'.17g'));owner.set('releaseGrid',str(proof['grid']));owner.attrib.pop('ownerCostFilename',None)
  for node in scene.iter():
   if node.tag=='RequiredPlugin' and node.get('pluginName','').endswith('/libReGripStationaryImpact.so'):
    if sha(node.get('pluginName'))!=m['binary_sha256']:raise ValueError('actual parent binary changed')
    node.set('pluginName',str(binary))
   for k,v in list(node.attrib.items()):
    if k in ('filename','displacementFilename','publicMassFilename') and v.startswith(str(parent)):node.set(k,str(out)+v[len(str(parent)):])
  tree.write(out/'scene.scn');r.update(binary_sha256=sha(binary),build_relative=str(build.relative_to(ROOT)),identity=identity,input_checkpoint_sha256=sha(out/'input.checkpoint'),scene_sha256=sha(out/'scene.scn'))
  if forecast>480:r.update(status='BLOCKED',failure_reason='measured policy forecast>480s;NOT OS exhaustion');write_json(out/'summary.json',r);return
  run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',out/'scene.scn'],out/'process',480);errors=sum((out/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log'));r.update(process=run,sofa_errors=errors)
  if run['exit_code']==0 and not errors:
   actual=list(csv.DictReader((out/'three.states.csv').open()));expected=list(csv.DictReader((ref/'states.csv').open()));metrics=next(csv.DictReader((out/'three.release.metrics.csv').open()));aa=list(csv.DictReader((out/'three.release.rk.csv').open()));bb=list(csv.DictReader((ref/'states.csv.rk.csv').open()));api={k:float(np.max(abs(np.fromstring(actual[0][k],sep=' ')-np.fromstring(expected[0][k],sep=' ')))) for k in ('q','v')};stage=0.;clock=len(aa)==len(bb)==4*proof['grid']
   for x,y in zip(aa,bb):
    clock=clock and all(float(x[k])==float(y[k]) for k in ('time','weight_s','mask'));stage=max(stage,*(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for k in ('q','v','force')))
   end=float(actual[0]['time']);r.update(status='PASS' if len(actual)==1 and max(api.values())<=1e-12 and stage<=1e-12 and clock and end==float(expected[0]['time']) and float(metrics['minimum_gap_mm'])>=-1e-10 and float(metrics['momentum_bound_Ns'])<=1e-17 and int(metrics['final_mask'])==0 and float(metrics['outgoing_normal_velocity_mm_s'])>0 else 'FAIL',reference_max_abs=api,RK_stage_max_abs=stage,all_RK_times_weights_masks_exact=clock,end_time_s=end,release_metrics=metrics)
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.txt','.csv')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','configure','compile','process','raw_hashes')}))
if __name__=='__main__':main()
