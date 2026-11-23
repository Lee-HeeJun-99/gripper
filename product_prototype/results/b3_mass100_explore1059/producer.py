"""Mass-only frozen B3 exploration; NOT physical/numerical qualification."""
import argparse,csv,json,shutil,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
from analyse import BASE,sha
from native_bending_coupon import guarded

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
 if Path(a.tag).name!=a.tag:raise ValueError('local tag required')
 src=BASE/'results/b3_alarm_window485';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 meta=json.loads((src/'summary.json').read_text());tree=ET.parse(src/'scene.scn');root=tree.getroot()
 plugins=[]
 for n in root.iter('RequiredPlugin'):
  name=n.get('pluginName','')
  if name.startswith('/'):
   f=Path(name);plugins.append(dict(path=name,sha256=sha(f)))
 expected={meta['binary_sha256'],meta['alarm_binary_sha256']}
 if not expected.issubset({r['sha256'] for r in plugins}):raise ValueError('frozen binary mismatch')
 body=root.find("./Node[@name='object']/UniformMass");original=body.get('vertexMass');v=original.split()
 if float(v[0])!=.05:raise ValueError('expected frozen50g baseline')
 v[0]='0.1';body.set('vertexMass',' '.join(v)) # normalized inertia unchanged; physical inertia scales with mass
 for n in root.iter():
  for k,value in list(n.attrib.items()):
   if str(src) in value:n.set(k,value.replace(str(src),str(out)))
 for name in ('config.json','mesh.json','holding_protocol.json','motion_commands.json','initial_geometry.json','geometry_generator.py'):
  shutil.copy2(src/name,out/name)
 c=json.loads((out/'config.json').read_text());c['simulation']['sphere_mass_kg']=.1;(out/'config.json').write_text(json.dumps(c,indent=2))
 protocol=json.loads((out/'holding_protocol.json').read_text());protocol['mass_kg']=.1
 protocol['scope']='EXPLORATORY FUNCTIONAL TEST; Native contact time/mesh gates FAIL; not product qualification'
 (out/'holding_protocol.json').write_text(json.dumps(protocol,indent=2));tree.write(out/'scene.scn')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes())
 pre=dict(classification='EXPLORATORY FUNCTIONAL TEST',baseline='b3_alarm_window485',baseline_scene_sha256=sha(src/'scene.scn'),source_sha=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),producer_sha256=sha(Path(__file__)),binary_hashes=plugins,SDK='/home/ubuntu/SOFA/v26.06.00',mass_change_kg=[.05,.1],original_vertexMass=original,candidate_vertexMass=body.get('vertexMass'),physics_change='ONLY object mass; normalized inertia unchanged.800steps to2s hold, no release run.',dt_s=.0025,steps=800,cost_forecast_s=133.319*800/1200,basis='actual4851200steps133.319s; estimate not guarantee',lift='BLOCKED_UNQUALIFIED_FREE_SUBSET_ROOT_FIXTURE',numerical_convergence='FAIL_EXISTING_BASELINE_NOT_RETESTED',physical_validation='NOT QUALIFIED')
 (out/'preflight.json').write_text(json.dumps(pre,indent=2))
 proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','800','--hideProgressBar',out/'scene.scn'],out/'process',480)
 logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'))
 counts={f:len(list(csv.DictReader((out/f).open()))) if (out/f).exists() else 0 for f in ['object.csv','finger0.csv','finger1.csv','finger2.csv']}
 meta.update(status='RUN_COMPLETED_NOT_QUALIFIED' if proc['exit_code']==0 and '[ERROR]' not in logs and all(n==800 for n in counts.values()) else 'FAIL_EXPLORATORY_EXECUTION',process=proc,steps=800,holding_protocol_sha256=sha(out/'holding_protocol.json'),scene_sha256=sha(out/'scene.scn'),source_commit=pre['source_sha'],classification=pre['classification'],sphere_mass_kg=.1,output_counts=counts,sofa_errors=logs.count('[ERROR]'),baseline_scene_sha256=pre['baseline_scene_sha256'])
 for key in ('metrics','raw_hashes','source_hashes'):meta.pop(key,None)
 meta['raw_hashes']={f.name:sha(f) for f in out.glob('*.csv')}
 (out/'summary.json').write_text(json.dumps(meta,indent=2));print(json.dumps(dict(status=meta['status'],process=proc,counts=counts)))
if __name__=='__main__':main()
