"""SERIAL same-IVP actual8-step baseline/cache pair;no generic speed claim."""
import argparse,csv,hashlib,json,shutil,subprocess,xml.etree.ElementTree as ET
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--reverse',action='store_true');a=p.parse_args();src=ROOT/'results/autonomous_film_20261118_routed_unload_begin1307';m=json.loads((src/'summary.json').read_text());cache=ROOT/'results/autonomous_film_20261118_precise_cache_build1340';cm=json.loads((cache/'summary.json').read_text());base=ROOT/'results/autonomous_film_20261118_routed_resume1278';bm=json.loads((base/'summary.json').read_text())
 if m['status']!='EXPERIMENTAL' or m['process']['exit_code'] or m['sofa_errors'] or cm['status']!='PASS' or bm['status']!='PASS':raise ValueError('complete known actual IVP and separate cache build required')
 if sha(src/'scene.scn')!=m['scene_sha256'] or sha(src/'input.checkpoint')!=m['input_checkpoint_sha256'] or sha(SDK/'bin/runSofa-26.06.00')!=m['sdk_runner_sha256']:raise ValueError('actual IVP/SDK changed')
 for path,meta in ((base,bm),(cache,cm)):
  for f,d in meta['source_hashes'].items():
   if sha(path/'sources'/f)!=d:raise ValueError('compiled source changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');provenance=[];physical=('three.states.csv','three.rows.csv','three.policy.csv')+tuple(f'{kind}_{f}.csv' for kind in ('film','displacement') for f in range(3));tokens=(src/'input.checkpoint').read_text().split();forecast=2*m['process']['runtime_s']+30;r=dict(status='BLOCKED',scope='serial actual8-step19.6..21.2ms query-cache benchmark ONLY;NOT adopted speed/time/grasp certificate',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),actual_summary_sha256=sha(src/'summary.json'),cache_build_summary_sha256=sha(cache/'summary.json'),baseline_provider_summary_sha256=sha(base/'summary.json'),sdk_runner_sha256=m['sdk_runner_sha256'],predicted_each_child_runtime_s=forecast,owner_profile=False,force_hessian_direct_probe='NOT YET RUN',legacy_sampled_work='may be byte-identical but NOT restored physical work')
 if forecast>480:r['failure_reason']='measured policy forecast>480s;NOT OS exhaustion';write_json(out/'summary.json',r);return
 variants=[('baseline',bm),('cached',cm)]
 if a.reverse:variants.reverse()
 r['execution_order']=[label for label,meta in variants]
 for label,meta in variants:
  dest=out/label;dest.mkdir();binary=ROOT/meta['build_relative']/'libReGripThreeFilmResume.so'
  if sha(binary)!=meta['binary_sha256']:raise ValueError('executable changed')
  copied=tokens.copy()
  if label=='cached':copied[4]=hashlib.sha256(json.dumps(dict(binary=sha(binary),source_checkpoint=m['input_checkpoint_sha256'],source=meta['source_hashes']),sort_keys=True).encode()).hexdigest()
  if copied[:4]+copied[5:]!=tokens[:4]+tokens[5:]:raise ValueError('physical state changed')
  (dest/'input.checkpoint').write_text(' '.join(copied)+'\n');tree=ET.parse(src/'scene.scn');scene=tree.getroot();owner=scene.find('RoutedThreeFilmResumeODE');owner.set('checkpoint',str(dest/'input.checkpoint'));owner.set('identity',copied[4]);owner.attrib.pop('ownerCostFilename',None);owner.set('reuseJournalRows','1')
  for node in scene.iter():
   if node.tag=='RequiredPlugin' and node.get('pluginName','').endswith('/libReGripThreeFilmResume.so'):node.set('pluginName',str(binary))
   for k,v in list(node.attrib.items()):
    if k in ('filename','displacementFilename','publicMassFilename') and v.startswith(str(src)):node.set(k,str(dest)+v[len(str(src)):])
  tree.write(dest/'scene.scn');run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','8','--hideProgressBar',dest/'scene.scn'],dest/'process',480);errors=sum((dest/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log'));provenance.append(dict(variant=label,binary_sha256=sha(binary),scene_sha256=sha(dest/'scene.scn'),input_checkpoint_sha256=sha(dest/'input.checkpoint'),process=run,sofa_errors=errors))
  if run['exit_code'] or errors:r.update(status='FAIL',variants=provenance,failure_reason='actual child failed;no speed adoption');write_json(out/'summary.json',r);return
 hashes={label:{name:sha(out/label/name) for name in physical} for label in ('baseline','cached')};same={name:hashes['baseline'][name]==hashes['cached'][name] for name in physical};reference_same={name:sha(src/name)==hashes['baseline'][name] for name in physical};checkpoints=[]
 for name in sorted(x.name for x in (out/'baseline').glob('three.checkpoint_*.txt')):
  x=(out/'baseline'/name).read_text().split();y=(out/'cached'/name).read_text().split();checkpoints.append(dict(name=name,physical_tokens_exact_except_identity=x[:4]+x[5:]==y[:4]+y[5:],baseline_sha256=sha(out/'baseline'/name),cached_sha256=sha(out/'cached'/name)))
 runtimes={v['variant']:v['process']['runtime_s'] for v in provenance};b,c=runtimes['baseline'],runtimes['cached'];r.update(status='PASS' if all(same.values()) and all(reference_same.values()) and len(checkpoints)==8 and all(x['physical_tokens_exact_except_identity'] for x in checkpoints) else 'FAIL',variants=provenance,physical_csv_byte_exact=same,original_known_actual_csv_byte_exact=reference_same,raw_hashes=hashes,checkpoints=checkpoints,baseline_runtime_s=b,cached_runtime_s=c,observed_runtime_reduction_fraction=(b-c)/b,speed_interpretation='ONE serial8-step whole-child observation,not a whole-gripper speed factor;direct F/H probe still required before adoption');write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('variants','raw_hashes','checkpoints')}))
if __name__=='__main__':main()
