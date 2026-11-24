"""One nominal-volume rail redistribution candidate vs actual guide feet.

Not a Native run or section-stiffness certification. Reject before meshing if
an existing attachment leaves the proposed rail. Do not silently move anchors.
"""
import argparse,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from mechanism_candidates import width
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_railback_grasp1001298';c=json.loads((src/'config.json').read_text());local=np.array(json.loads((src/'mesh.json').read_text())['local_positions_mm']);root=ET.parse(src/'scene.scn').getroot();original_width=c['finger']['rail_width'];thickness=c['finger']['rail_thickness'];proximal_width=2.2;transition=70.;distal_width=(original_width*100-proximal_width*transition)/(100-transition);records=[]
 for i in range(3):
  pairs=np.fromstring(root.find(f"Node[@name='finger{i}']/SubsetMultiMapping").get('indexPairs'),sep=' ',dtype=int).reshape(-1,2)
  for parent,(owner,index) in enumerate(pairs):
   if owner!=1:continue
   x,y,z=local[parent];assert z==-.5;old_margin=abs(y)-(width(c,x)/2-original_width);candidate_width=proximal_width if x<=transition else distal_width;margin=abs(y)-(width(c,x)/2-candidate_width);records.append(dict(finger=i,parent_FEM_node=parent,guide_anchor_index=int(index),material_reference_mm=[float(x),float(y),float(z)],original_rail_inner_margin_mm=float(old_margin),candidate_rail_width_mm=candidate_width,candidate_rail_inner_margin_mm=float(margin),inside_candidate=bool(margin>=0)))
 rejected=[r for r in records if not r['inside_candidate']];d=dict(status='REJECT_FIXED_ANCHOR_RAIL_REDISTRIBUTION' if rejected else 'PASS_ANCHOR_FOOTPRINT_ONLY',candidate=dict(original_width_mm=original_width,proximal_width_mm=proximal_width,transition_mm=transition,distal_width_mm=distal_width,rail_thickness_mm=thickness,original_nominal_one_rail_volume_mm3=original_width*100*thickness,candidate_nominal_one_rail_volume_mm3=(proximal_width*transition+distal_width*(100-transition))*thickness),anchors_checked=len(records),anchors_outside=len(rejected),minimum_margin_mm=min(r['candidate_rail_inner_margin_mm'] for r in records),records=records,scope='Exact local coordinates of actual3pointRailback anchors. Equal NOMINAL section-area integral only,not exact curved tetra volume,mass,EI,dynamics or manufacturing. Abrupt70mm width step is a design-screen assumption. No Native run for rejected geometry. No existing anchor removed or moved.',prior_review=['reports/REGRIP_TENDON_TRANSMISSION_AND_WRAPPING.md uniform railaspect1649–1660 uses separate custommodel,not thisproximalNativecandidate','product_prototype/reports/B3_RAIL_BACK_ATTACHMENT_20261123.md keeps3point36anchors/rank6;do not thinawaytheirfootprint'],input_hashes={f:sha(src/f) for f in ('scene.scn','mesh.json','config.json')},source_sha256=sha(Path(__file__)),source_commit=__import__('subprocess').check_output(['git','rev-parse','HEAD'],text=True).strip(),physical_validation='NOT QUALIFIED',next='Candidate must preserve distal2mmfootprint or explicitly redesignsupports. Review added proximal reinforcement vs footprint-preserving redistribution;no blind width sweep.' )
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps({k:d[k] for k in ('status','anchors_checked','anchors_outside','minimum_margin_mm','candidate')}))
if __name__=='__main__':main()
