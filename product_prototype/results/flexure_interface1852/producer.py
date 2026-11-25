"""Check physical space before treating a successful beam coupon as a hinge."""
import argparse,json,sys
from pathlib import Path
import numpy as np
import trimesh
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'sofa'))
from analyse import sha
from finite_csg64 import register
from bellcrank_link_geometry import shapes
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);register();rotor,_,_=shapes();rotor.apply_translation([3,0,0]);shaft=trimesh.creation.cylinder(radius=.25,segment=[[0,0,0],[2.3,0,0]],sections=32);assert shaft.is_volume
 hit=trimesh.boolean.intersection([rotor,shaft],engine='manifold64');volume=float(hit.volume) if len(hit.faces) else 0;assert volume>=0;rotor.export(out/'rotor_at_bending_flexure_tip_mm.stl');shaft.export(out/'flexure_before_declared07mm_bond_mm.stl')
 # Different axial shaft layout ends at the underside of an explicit solid hub.
 hub=trimesh.creation.box([24,2,1]);vertical=trimesh.creation.cylinder(radius=.25,segment=[[0,0,-3.5],[0,0,-.5]],sections=32);other=trimesh.boolean.intersection([hub,vertical],engine='manifold64');other_volume=float(other.volume) if len(other.faces) else 0;hub.export(out/'axial_torsion_solid_hub_envelope_mm.stl');vertical.export(out/'axial_torsion_shaft_envelope_mm.stl')
 d=dict(status='REJECT_STRAIGHT_CANTILEVER_DROP_IN_INTERFACE',straight_flexure_rotor_intersection_outside_declared_bond_mm3=volume,declared_bond_length_mm=.7,alternative_axial_shaft_hub_envelope_intersection_mm3=other_volume,source_sha256=sha(Path(__file__)),scope='Actual finite initial interface screen, not a failed Native beam response. Side-entry3mm flexure before last0.7mm bond lies inside24mm plate: cannot drop in without redesign. Alternative vertical3mm shaft meets solid hub at underside only; axial torsion (not bending) and real bond/clamp/strength need separate proof. No old design/collision deleted, no assembled product qualification.')
 (out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
