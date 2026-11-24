"""Installed NewProximity preserves tested RigidSphere/mesh angular coupling.
All finite eyelet/support geometry and actual physical inputs remain enabled.
"""
import argparse,json,xml.etree.ElementTree as ET
from pathlib import Path
from analyse import BASE,sha
from finite_hardware_grasp_pilot import run_three
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--duration',type=float,choices=(.6,1.2,2.),default=.6);p.add_argument('--pilot');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/finite_hardware_three1556';old=ET.parse(src/'scene.scn').getroot();root=ET.fromstring(ET.tostring(old));probe=BASE/'results/new_rigid_sphere_contract1568';cap=json.loads((probe/'summary.json').read_text());rigid=next(r for r in cap['records'] if r['sphere_representation']=='Rigid3');assert rigid['process']['exit_code']==0 and not rigid['error'] and rigid['nonzero_response_rows']>0 and rigid['maximum_direct_angular_J_component']>0
 intersection=root.find('MinProximityIntersection');assert intersection is not None;intersection.tag='NewProximityIntersection'
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 normalized=ET.fromstring(ET.tostring(root));normalized.find('NewProximityIntersection').tag='MinProximityIntersection'
 for n in normalized.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(out),str(src)))
 assert ET.tostring(normalized)==ET.tostring(old)
 forecast=120.
 if a.duration>.6:
  assert a.pilot;prior=json.loads((BASE/'results'/a.pilot/'summary.json').read_text());prior_i=json.loads((BASE/'results'/a.pilot/'intervention.json').read_text());assert prior['status']=='VALID_BOUNDED_EXPLORATION_ONLY' and prior_i['source_scene_sha256']==sha(src/'scene.scn');forecast=prior['process']['runtime_s']*a.duration/prior['duration_s']*2;assert forecast<420
 meta=json.loads((src/'preflight.json').read_text());(out/'intervention.json').write_text(json.dumps(dict(source_scene_sha256=sha(src/'scene.scn'),source_sha256=sha(Path(__file__)),capability_probe_sha256=sha(probe/'summary.json'),only_change='MinProximityIntersection -> installedNewProximityIntersection;NOobjectstate/templatechange;ALLfiniteGuideANDSupportcollisionmodels/radii/mesh/material/mass/inertia/cable/friction/buffer/solverthresholdsunchanged',hypothesis='Actualmatched1567isolatesLocalRigidSpheremeshmissingresponse;NewRigidSphere1568retainsactualangularJ andresponse. FreshwholeFEMgap/responseandhardwarebracing required,notcouponpromotion.',forecast_s=forecast),indent=2));run_three(root,out,src,meta['eyelet'],meta['parts'],round(a.duration/.0025),a.duration,forecast);(out/'producer.py').write_bytes(Path(__file__).read_bytes());pre=json.loads((out/'preflight.json').read_text());pre['entrypoint_sha256']=sha(Path(__file__));pre['intervention_sha256']=sha(out/'intervention.json');(out/'preflight.json').write_text(json.dumps(pre,indent=2))
if __name__=='__main__':main()
