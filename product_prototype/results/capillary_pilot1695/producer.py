"""Bounded Native thinwall-ferrule geometry sensitivity; not real wire sliding."""
import argparse,json,xml.etree.ElementTree as ET
from pathlib import Path
from analyse import BASE,sha
from finite_hardware_grasp_pilot import run_three
from finite_guide_coupon import eyelet

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--duration',type=float,choices=(.6,1.2,2.),default=.6);p.add_argument('--pilot');p.add_argument('--pair-case');a=p.parse_args();src=BASE/'results/dispatch_finite_holding1586';design=BASE/'results/capillary_bored1694';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);d=json.loads((design/'summary.json').read_text());assert d['status']=='READY_BOUNDED_CAPILLARY_GEOMETRY_ONLY';root=ET.parse(design/'scene.scn').getroot();forecast=180.
 if a.duration>.6:
  assert a.pilot and a.pair_case;pr=json.loads((BASE/'results'/a.pilot/'summary.json').read_text());pair=json.loads((BASE/'results'/a.pair_case/'summary.json').read_text());assert pr['status']=='VALID_BOUNDED_EXPLORATION_ONLY' and pair['case']==a.pilot and pair['nonzero_rows']==0
  forecast=pr['process']['runtime_s']*a.duration/pr['duration_s']*2;assert forecast<420
 for node in root.iter():
  for key,value in list(node.attrib.items()):node.set(key,value.replace(str(design),str(out)))
 cfg=json.loads((design/'config.json').read_text());_,quality=eyelet(cfg,32)
 inter=dict(source_sha256=sha(Path(__file__)),geometry_source_sha256=sha(design/'summary.json'),geometry_scene_sha256=sha(design/'scene.scn'),supplier_dimensions_sha256=sha(design/'supplier_dimensions.json'),scope='One16RW thinwall ferrule + bore-relieved support geometry, not a force/dt/alarm/chamfer scan. Same physical Cable inputs/axes/centres/attachments, no object state override, all hardware collision models retained. Nominal304 tube dims NOT actual mass/strength/friction calibration. IdealCableConstraint only: finite-wire1675 crossing and contact-normal1678 BLOCKED unchanged.')
 (out/'intervention.json').write_text(json.dumps(inter,indent=2));(out/'supplier_dimensions.json').write_bytes((design/'supplier_dimensions.json').read_bytes());run_three(root,out,src,quality,d['all_parts'],round(a.duration/.0025),a.duration,forecast,configuration_source=design);(out/'producer.py').write_bytes(Path(__file__).read_bytes())
if __name__=='__main__':main()
