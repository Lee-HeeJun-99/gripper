"""Different direct tensile transmission; no old Guide collision removal.
Actual root origins and terminal bonded-foot centroids, radius0.25mm.
"""
import argparse,json,sys,time,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'sofa'))
from analyse import sha
from captured_carriage_candidate import wire
from finite_csg64 import register

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);started=time.monotonic();register()
    scene=BASE/'results/capillary_hold1700/scene.scn';root=ET.parse(scene).getroot()
    centre=np.fromstring(root.find("Node[@name='object']/MechanicalObject").get('position'),sep=' ')[:3]
    fem=[]
    for i in range(3):
        node=root.find(f"Node[@name='finger{i}']")
        q=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)
        t=np.fromstring(node.find('MeshTopology').get('tetrahedra'),sep=' ',dtype=int).reshape(-1,4)
        fem.append((q,t))
    records=[]
    for i in range(3):
        guide=root.find(f"Node[@name='guides{i}']")
        feet=np.fromstring(guide.find("Node[@name='anchors']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)
        for j in range(2):
            origin=np.fromstring(guide.find(f"Node[@name='cable{j}']/CableConstraint").get('pullPoint'),sep=' ')
            terminal=feet[j*18+15:j*18+18].mean(0);delta=terminal-origin;length=np.linalg.norm(delta)
            fraction=float(np.clip((centre-origin)@delta/(delta@delta),0,1));closest=origin+fraction*delta
            gap=float(np.linalg.norm(closest-centre)-.03-.00025)
            solid=wire(origin,terminal,.00025);solid.export(out/f'f{i}_c{j}_direct_span_m.stl')
            # Only last0.5mm is the explicit endpoint attachment domain. This
            # does not assert a manufactured clip exists or ignore foreign FEM.
            clear_endpoint=terminal-.0005*delta/length;trimmed=wire(origin,clear_endpoint,.00025)
            hits=[];tested=0
            for fi,(q,t) in enumerate(fem):
                check=trimmed if fi==i else solid;points=q[t]
                mask=np.all(points.max(1)>=check.bounds[0],axis=1)&np.all(points.min(1)<=check.bounds[1],axis=1)
                for k in np.flatnonzero(mask):
                    tested+=1;cell=trimesh.convex.convex_hull(points[k])
                    hit=trimesh.boolean.intersection([check,cell],engine='manifold64')
                    volume=float(hit.volume)*1e9 if len(hit.faces) else 0.
                    assert np.isfinite(volume) and volume>=0
                    if volume>0:hits.append(dict(finger=fi,tetrahedron=int(k),intersection_mm3=volume))
            records.append(dict(finger=i,cable=j,origin_m=origin.tolist(),terminal_m=terminal.tolist(),
                wire_radius_mm=.25,span_length_mm=float(length*1000),exact_sphere_capsule_gap_mm=gap*1000,
                closest_span_fraction=fraction,unit_tension_terminal_force_direction=(-delta/length).tolist(),
                endpoint_force_distribution_assumption=[1/3]*3,initial_material_intersections=hits,tested_cells=tested))
    result=dict(status='REJECTED_DIRECT_TENDON_SPAN' if any(r['exact_sphere_capsule_gap_mm']<0 or r['initial_material_intersections'] for r in records) else 'INITIAL_DIRECT_TENDON_GEOMETRY_ONLY',
        records=records,runtime_seconds=time.monotonic()-started,source_sha256=sha(Path(__file__)),scene_sha256=sha(scene),
        csg_source_sha256=sha(Path(__file__).parent/'finite_csg64.py'),native_run=False,
        scope='Actual new force-path candidate, NOT terminal-position scan or old collision models disabled. Intermediate guides do not exist in this concept; no Native scene generated. Sphere/capsule separation exact analytic, positive FEM intersection an inscribed-facet witness. Endpoint clip/root drum/manufacture/mass/strength NOT QUALIFIED. Direct-span rejection does NOT prove all flexible/bent or rerouted tendons impossible; bending contact with object would require a distinct physical model and cannot be mislabeled Skin-only grip.')
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(dict(status=result['status'],minimum_sphere_gap_mm=min(r['exact_sphere_capsule_gap_mm'] for r in records),positive_material_cells=sum(len(r['initial_material_intersections']) for r in records),runtime_seconds=result['runtime_seconds']),indent=2))

if __name__=='__main__':main()
