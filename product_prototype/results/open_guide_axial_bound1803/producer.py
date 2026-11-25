"""Conditional all-angle link/tube separation by invariant axial slabs.
No trajectory fitting, no collision-distance relaxation, no Native execution.
"""
import argparse,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from open_hinge_coupon import BASE
import sys
sys.path.insert(0,str(BASE/'sofa'))
from analyse import sha

def read(path):
    with np.load(path,allow_pickle=False) as arc:m=trimesh.Trimesh(arc['vertices'],arc['faces'],process=False)
    assert m.is_volume and m.body_count==1;return m

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/open_guide_axial64_1799'
    scene=BASE/'results/capillary_hold1700/scene.scn';root=ET.parse(scene).getroot()
    # Read actual configured response distance; never decrease it for a PASS.
    distances=[float(n.get('contactDistance')) for n in root.iter() if n.get('contactDistance') is not None]
    assert distances and len(set(distances))==1;response_gap=distances[0]
    records=[];inputs=[scene,src/'summary.json',Path(__file__)]
    for i in range(3):
        for j in range(2):
            f=src/f'f{i}_c{j}_tube_m.npz';inputs.append(f);tube=read(f)
            v=tube.vertices;n=len(v)//4;centre=v.mean(0);axis=v[2*n:].mean(0)-v[:2*n].mean(0);axis/=np.linalg.norm(axis)
            # NPZ preserves indexed ORIGINAL tube ring ordering.
            z=(v-centre)@axis;lo,hi=float(z.min()),float(z.max())
            for level in (0,1):
                f=src/f'f{i}_c{j}_link{level}_m.npz';inputs.append(f);link=read(f)
                axial=(link.vertices-centre)@axis;l,h=float(axial.min()),float(axial.max())
                gap=max(l-hi,lo-h)
                records.append(dict(finger=i,cable=j,link=level,tube_axial_interval_mm=[lo*1000,hi*1000],
                    link_axial_interval_mm=[l*1000,h*1000],all_angle_solid_separation_lower_bound_mm=gap*1000,
                    meets_unchanged_native_response_gap=gap>=response_gap))
    d=dict(status='CONDITIONAL_SOLID_SEPARATION_ONLY_NATIVE_BUFFER_FAIL' if all(r['all_angle_solid_separation_lower_bound_mm']>0 for r in records) and not all(r['meets_unchanged_native_response_gap'] for r in records) else 'REVIEW_AXIAL_BOUND',
        native_contact_distance_m=response_gap,records=records,
        inputs=[dict(path=str(p.relative_to(BASE.parent)),sha256=sha(p)) for p in inputs],
        scope='Exact projection bounds of actual stored faceted solids, apart from floating point. Rotation about parallel hinge axes and tube in-plane translation leave both axial intervals invariant for EVERY crank angle; a common rigid root transform also preserves them. Does not prove nonparallel/flexible-joint/FEM motion, carrier/other-body separation, continuous wire contact, manufacturing tolerance or force transmission. Positive50um solid gap does NOT pass unchanged200um Native contact response distance. No alarm-distance edits or ignored contact rows.')
    (out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(dict(status=d['status'],native_contact_distance_mm=response_gap*1000,
        minimum_axial_gap_mm=min(r['all_angle_solid_separation_lower_bound_mm'] for r in records)),indent=2))

if __name__=='__main__':main()
