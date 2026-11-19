"""Append-only actual-scene guide overlap audit;does not revise old Raw verdicts."""
import argparse,json,xml.etree.ElementTree as ET,hashlib
import numpy as np
from mechanism_candidates import BASE
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[]
 for name in a.cases:
  src=BASE/'results'/name;tree=ET.parse(src/'scene.scn');groups=[];radii=[]
  for node in tree.findall('./Node'):
   if not node.get('name','').startswith('guides'):continue
   points=[];radius=[]
   for cable in node.findall('./Node'):
    if not cable.get('name','').startswith('cable'):continue
    q=np.fromstring(cable.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);r=float(cable.find('SphereCollisionModel').get('radius'));points.extend(q);radius.extend([r]*len(q))
   groups.append(np.array(points));radii.append(np.array(radius))
  gap=None
  if len(groups)>1:gap=min(float((np.linalg.norm(groups[i][:,None]-groups[j][None,:],axis=2)-radii[i][:,None]-radii[j][None,:]).min()*1000) for i in range(len(groups)) for j in range(i+1,len(groups)))
  records.append(dict(case=name,status='FAIL_INITIAL_GUIDE_PROXY_OVERLAP' if gap is not None and gap<0 else 'NO_INITIAL_INTERFINGER_PROXY_OVERLAP_OBSERVED' if gap is not None else 'SINGLE_FINGER_ONLY',initial_interfinger_proxy_gap_mm=gap,scene_sha256=hashlib.sha256((src/'scene.scn').read_bytes()).hexdigest(),scope='actual native collision spheres,not exact solid eyelet/support collision;negative means initial modeled overlap,not fabrication collision proof'))
 result=dict(status='FAIL' if any(r['status'].startswith('FAIL') for r in records) else 'INITIAL_PROXY_SCOPE_ONLY',records=records,disposition='holding motion/provenance observations are retained,but cannot qualify an initially overlapping assembly;no historical record rewritten');(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
