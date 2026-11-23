"""One-input research force exploration after measured support-deficit diagnosis."""
import argparse,csv,json,shutil,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results/b3_mass100_explore1059';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);tree=ET.parse(src/'scene.scn');root=tree.getroot();oldbytes=ET.tostring(root);controls=list(root.iter('NativeCableSequence'))
 if len(controls)!=3 or any(float(n.get('maximumForceN'))!=1.5 for n in controls):raise ValueError('exact100g1.5N baseline required')
 for n in controls:n.set('maximumForceN','2.5')
 for n in root.iter():
  for k,v in list(n.attrib.items()):
   if str(src) in v:n.set(k,v.replace(str(src),str(out)))
 for name in ('config.json','mesh.json','holding_protocol.json','motion_commands.json','initial_geometry.json','geometry_generator.py'):shutil.copy2(src/name,out/name)
 shutil.copytree(src/'source',out/'source');tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());meta=json.loads((src/'summary.json').read_text())
 protocol=dict(classification='EXPLORATORY FUNCTIONAL FORCE SENSITIVITY;NOT structural fix or motor specification',mass_kg=.1,force_N_per_cable=2.5,hold_window_s=[1.6,2.],minimum_skin_vertical_weight_fraction=.8,maximum_hardware_resultant_N=1e-5,holding_thresholds='unchanged holding_protocol.json',physical_validation='NOT QUALIFIED',hypothesis='1100 shows2mm slip before later solver saturation/normal reversal;early100gSkin support~.706N<.981N. A single research input increase tests available actuation sensitivity,not reliable capacity or a linear scaling law.',basis_sha256=sha(BASE/'results/b3_withdrawal_phases1100/summary.json'),changes=['NativeCableSequence.maximumForceN1.5->2.5 on each of3controllers;each drives2cables'],unchanged='geometry,mass,material,friction,dt,solver,contact,Root and support motion',expected_runtime_s=140.446,limit_s=480,memory_GiB=4)
 (out/'force_protocol.json').write_text(json.dumps(protocol,indent=2));binary_hashes={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')};(out/'preflight.json').write_text(json.dumps(dict(binary_hashes=binary_hashes,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),SDK='/home/ubuntu/SOFA/v26.06.00',scene_sha256=sha(out/'scene.scn'),protocol_sha256=sha(out/'force_protocol.json')),indent=2))
 # Verify no unexpected physical edit before launch:reverse only intended changes.
 for n in controls:n.set('maximumForceN','1.5')
 for n in root.iter():
  for k,v in list(n.attrib.items()):
   if str(out) in v:n.set(k,v.replace(str(out),str(src)))
 if ET.tostring(root)!=oldbytes:raise ValueError('unexpected Scene difference beyond intended force input')
 proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','800','--hideProgressBar',out/'scene.scn'],out/'process',480);logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));counts=[len(list(csv.DictReader((out/f'finger{f}.csv').open()))) if (out/f'finger{f}.csv').exists() else 0 for f in range(3)]
 meta.update(status='RUN_COMPLETED_NOT_QUALIFIED' if proc['exit_code']==0 and '[ERROR]' not in logs and counts==[800]*3 else 'FAIL_FORCE_EXPLORATION_EXECUTION',process=proc,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),classification=protocol['classification'],actual_maximum_command_N=2.5,scene_sha256=sha(out/'scene.scn'),holding_protocol_sha256=sha(out/'holding_protocol.json'),force_protocol_sha256=sha(out/'force_protocol.json'))
 for key in ('metrics','raw_hashes','source_hashes'):meta.pop(key,None)
 meta['raw_hashes']={f.name:sha(f) for f in out.glob('*.csv')};(out/'summary.json').write_text(json.dumps(meta,indent=2));print(json.dumps(dict(status=meta['status'],process=proc)))
if __name__=='__main__':main()
