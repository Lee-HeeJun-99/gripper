"""Explicit Native point-normal computation contrast for LocalMinDistance."""
import argparse,json,xml.etree.ElementTree as ET
from pathlib import Path
from analyse import BASE,sha
from finite_hardware_grasp_pilot import run_three
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/finite_hardware_local1561';root=ET.parse(src/'scene.scn').getroot();assert root.find('LocalMinDistance') is not None;models=list(root.iter('PointCollisionModel'));assert models and all(x.get('computeNormals') is None for x in models)
 for n in models:n.set('computeNormals','1')
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 meta=json.loads((src/'preflight.json').read_text());(out/'intervention.json').write_text(json.dumps(dict(source_scene_sha256=sha(src/'scene.scn'),source_sha256=sha(Path(__file__)),only_change='PointCollisionModel computeNormals=1 onallactualsurfaces;allgeometries/contactbuffers/filters/solvers unchanged',hypothesis='Missing explicitlycomputedpointnormals couldexplainLocalMinDistance rejectingSkinresponse despitephysicalpenetration. Actualcrosscheckrequired;rejectfamilyifstillmissingcontact.',models=len(models)),indent=2));run_three(root,out,src,meta['eyelet'],meta['parts'],240,.6,2*json.loads((src/'summary.json').read_text())['process']['runtime_s']);(out/'producer.py').write_bytes(Path(__file__).read_bytes())
if __name__=='__main__':main()
