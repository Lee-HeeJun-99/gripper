"""Independent Native initial guide points vs new shared CAD route coordinate file."""
import argparse,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha,cable_node

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/force_release_clear_support375';cad=BASE/'meshes/precurve_distal40_route_audit_v10';cfg=json.loads((src/'config.json').read_text());routes=json.loads((cad/'guide_routes_mm.json').read_text())['routes'];tree=ET.parse(src/'scene.scn');records=[]
 for route in routes:
  finger=cfg['palm']['angles_deg'].index(route['angle_deg']);cable=0 if route['side']==-1 else 1;native=np.fromstring(cable_node(tree,finger,cable).find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);points=np.array(route['points_mm'])[1:]*.001
  if points.shape!=native.shape:raise ValueError('guide counts differ')
  records.append(dict(finger=finger,cable=cable,max_position_error_m=float(np.max(abs(points-native)))))
 result=dict(status='PASS_INITIAL_ROUTE_IDENTITY_ONLY' if all(r['max_position_error_m']<=1e-12 for r in records) else 'FAIL',scope='Initial guide-center coordinates only;NOT guide solids,supports,STEP,moving interference or fabrication validation',records=records,configuration_bytes_equal=(cad/'config.json').read_bytes()==(src/'config.json').read_bytes(),source_sha256=sha(Path(__file__)),input_hashes={str(p.relative_to(BASE)):sha(p) for p in (src/'scene.scn',cad/'guide_routes_mm.json',cad/'config.json')})
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
