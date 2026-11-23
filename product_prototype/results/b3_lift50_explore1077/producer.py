"""Native Root+actual cable-origin motion; free object never prescribed."""
import argparse,csv,json,shutil,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results/b3_alarm_window485';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 origin=BASE/'results/b3_origin_observer1075';m=json.loads((origin/'summary.json').read_text());binary=Path(m['binary'])
 if sha(binary)!=m['binary_sha256'] or not m['observer_purity_1e12_pass']:raise ValueError('compiled observer/purity required')
 driven=json.loads((BASE/'results/b3_origin_motion1076/summary.json').read_text())
 if driven['maximum_origin_vs_root_error_m']>1e-12:raise ValueError('prior moving-origin contract required')
 meta=json.loads((src/'summary.json').read_text());tree=ET.parse(src/'scene.scn');root=tree.getroot();root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)))
 for n in root.iter():
  for k,v in list(n.attrib.items()):
   if str(src) in v:n.set(k,v.replace(str(src),str(out)))
 for f in range(3):
  n=root.find(f"./Node[@name='free{f}']");fixed=n.find('FixedProjectiveConstraint');ids=fixed.get('indices');n.remove(fixed)
  ET.SubElement(n,'LinearMovementProjectiveConstraint',indices=ids,keyTimes='-.0025 1.5975 1.8975 2.9975',movements='0 0 0 0 0 0 0 0 .005 0 0 .005')
  node=root.find(f"./Node[@name='finger{f}']")
  for c in range(2):ET.SubElement(node,'NativeCableOrigin',target=f'@../guides{f}/cable{c}/actuator',filename=str(out/f'origin_f{f}_c{c}.csv'),drive='1',begin='1.6',end='1.9',height='.005')
 for name in ('config.json','mesh.json','holding_protocol.json','motion_commands.json','initial_geometry.json','geometry_generator.py'):shutil.copy2(src/name,out/name)
 shutil.copytree(src/'source',out/'source');shutil.copytree(origin/'source',out/'origin_source')
 protocol=dict(classification='EXPLORATORY FUNCTIONAL LIFT;NOT physical qualification',mass_kg=.05,radius_mm=30,gravity_m_s2=9.81,friction_assumed=.3,reference_s=1.6,lift_end_s=1.9,end_window_s=[1.95,2.0],commanded_root_rise_mm=5,minimum_object_rise_mm=4,maximum_relative_vertical_slip_mm=2,maximum_end_speed_mm_s=5,minimum_support_gap_mm=5,maximum_support_force_N=1e-5,minimum_skin_weight_fraction=.8,maximum_guide_rail_vertical_force_N=1e-5,maximum_root_origin_API_error_m=1e-12,scope='Drive only original Root free subsets and cable pullPoints;object remains free. No100g lift claim. Ramp linear with explicit terminal hold;acceleration/work not certified.')
 (out/'lift_protocol.json').write_text(json.dumps(protocol,indent=2));tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes())
 pre=dict(expected_runtime_s=133.319*800/1200,estimate_basis='actual baseline4851200steps133.319s;changed-boundary runtime may differ',limit_s=480,memory_GiB=4,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),binary_hashes={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')},scene_sha256=sha(out/'scene.scn'),protocol_sha256=sha(out/'lift_protocol.json'),SDK='/home/ubuntu/SOFA/v26.06.00',baseline_scene_sha256=sha(src/'scene.scn'))
 (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','800','--hideProgressBar',out/'scene.scn'],out/'process',480)
 logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));counts={name:len(list(csv.DictReader((out/name).open()))) if (out/name).exists() else 0 for name in ['object.csv','finger0.csv','finger1.csv','finger2.csv']}
 meta.update(status='RUN_COMPLETED_NOT_QUALIFIED' if proc['exit_code']==0 and '[ERROR]' not in logs and all(x==800 for x in counts.values()) else 'FAIL_EXPLORATORY_LIFT_EXECUTION',steps=800,process=proc,source_commit=pre['source_commit'],scene_sha256=pre['scene_sha256'],classification=protocol['classification'],output_counts=counts,origin_binary_sha256=sha(binary),lift_protocol_sha256=sha(out/'lift_protocol.json'))
 for key in ('metrics','raw_hashes','source_hashes'):meta.pop(key,None)
 meta['raw_hashes']={f.name:sha(f) for f in out.glob('*.csv')};(out/'summary.json').write_text(json.dumps(meta,indent=2));print(json.dumps(dict(status=meta['status'],process=proc)))
if __name__=='__main__':main()
