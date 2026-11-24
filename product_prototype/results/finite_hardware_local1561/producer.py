"""Native facet-feature ownership intervention,not relaxed tolerance or erased collision."""
import argparse,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
from analyse import BASE,sha
from finite_hardware_grasp_pilot import run_three
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/finite_hardware_three1556';old=ET.parse(src/'scene.scn').getroot();root=ET.fromstring(ET.tostring(old));intersection=root.find('MinProximityIntersection');assert intersection is not None;intersection.tag='LocalMinDistance'
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 # Independent normalization verifies EXACTLY this one installed-component change.
 normalized=ET.fromstring(ET.tostring(root));normalized.find('LocalMinDistance').tag='MinProximityIntersection'
 for n in normalized.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(out),str(src)))
 assert ET.tostring(normalized)==ET.tostring(old)
 meta=json.loads((src/'preflight.json').read_text());(out/'intervention.json').write_text(json.dumps(dict(status='DECLARED_NATIVE_GEOMETRIC_POLICY_INTERVENTION',source_scene_sha256=sha(src/'scene.scn'),source_run_sha256=sha(src/'summary.json'),only_change='MinProximityIntersection -> LocalMinDistance;allmodels/radii/mesh/material/mass/cable/friction/buffer/solverthresholdsunchanged',hypothesis='Facetfeature filtering may remove redundant inactivepoint/edge contactblocks that made1556timeout;notuniqueproof ofcostcause orphysicalaccuracy',scope='Differentnativegeometriccontactpolicy,not time/mesh/collisioncorrectnessPASS;allfinitehardwaremodelsremainenabled;no fullHoldingclaim from.6s',source_sha256=sha(Path(__file__))),indent=2));run_three(root,out,src,meta['eyelet'],meta['parts'],240,.6,420.)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());pre=json.loads((out/'preflight.json').read_text());pre['entrypoint_sha256']=sha(Path(__file__));pre['intervention_sha256']=sha(out/'intervention.json');(out/'preflight.json').write_text(json.dumps(pre,indent=2))
if __name__=='__main__':main()
