"""Initial physical hinge placement screen against ACTUAL six incoming wires.
Not an integrated carrier/root: preserves that limitation explicitly.
"""
import argparse
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from open_hinge_coupon import build, BASE
from captured_carriage_candidate import wire
from open_parallel_geometry_seed import sphere_gap
from yoke_bond_material_audit import surface

def main():
    p=argparse.ArgumentParser(); p.add_argument('--tag', required=True)
    p.add_argument('--hardware', action='store_true')
    p.add_argument('--new-pairs', action='store_true')
    p.add_argument('--mount-relief', action='store_true'); a=p.parse_args()
    out=BASE/'results'/a.tag; out.mkdir(exist_ok=False)
    seed_path=BASE/'results/open_parallel_seed1768/summary.json'
    seed=json.loads(seed_path.read_text())
    scene=BASE/'results/capillary_hold1700/scene.scn'; root=ET.parse(scene).getroot()
    obj=np.fromstring(root.find("Node[@name='object']/MechanicalObject").get('position'), sep=' ')[:3]
    hinges=build(); records=[]; placed=[]; disconnected=[]
    for record in seed['records']:
        i,j=record['finger'],record['cable']
        parent=root.find(f"Node[@name='guides{i}']/Node[@name='cable{j}']")
        path=np.fromstring(parent.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)
        # Entire incoming segment, not a point at its distal end.
        incoming=wire(path[-2],path[-1],.00025)
        tube=parent.find("Node[@name='eyelet5']/MechanicalObject")
        vertices=np.fromstring(tube.get('position'),sep=' ').reshape(-1,3)
        n=len(vertices)//4; axis=vertices[2*n:].mean(0)-vertices[:2*n].mean(0); axis/=np.linalg.norm(axis)
        for level,(r,c) in enumerate(zip(record['root_hinge_centres_m'],record['initial_platform_centres_m'])):
            r=np.array(r); c=np.array(c); along=c-r; along/=np.linalg.norm(along)
            # Orthogonal construction; original seed should already be planar.
            assert abs(along@axis)<1e-10
            for endpoint,centre,direction in [('root',r,along),('carrier',c,-along)]:
                basis=np.stack([direction,np.cross(axis,direction),axis],axis=1)
                for name,local in zip(('fork','leaf','unretained_pin'),hinges):
                    m=trimesh.Trimesh(local.vertices*.001@basis.T+centre,local.faces,process=False)
                    assert m.is_volume
                    if a.mount_relief and endpoint=='carrier' and name!='unretained_pin':
                        tube_centre=vertices.mean(0)
                        cutter=wire(tube_centre-axis*.003,tube_centre+axis*.003,.0008755)
                        m=trimesh.boolean.difference([m,cutter],engine='manifold')
                        if not m.is_volume or m.body_count!=1:
                            disconnected.append(dict(finger=i,cable=j,level=level,part=name,components=int(m.body_count)))
                    hit=trimesh.boolean.intersection([m,incoming],engine='manifold')
                    volume=float(hit.volume)*1e9 if len(hit.faces) else 0.
                    assert np.isfinite(volume) and volume>=0
                    gap=sphere_gap(m,obj)
                    records.append(dict(finger=i,cable=j,level=level,endpoint=endpoint,part=name,
                        straight_wire_intersection_mm3=volume,object_gap_mm=None if gap is None else gap*1000))
                    placed.append((dict(finger=i,cable=j,level=level,endpoint=endpoint,part=name),m))
                    m.export(out/f'f{i}_c{j}_{level}_{endpoint}_{name}_m.stl')
    hardware_hits=[]
    if a.hardware:
        old=[]
        for i in range(3):
            for j in range(2):
                cable=root.find(f"Node[@name='guides{i}']/Node[@name='cable{j}']")
                for child in cable.findall('Node'):
                    name=child.get('name','')
                    if name.startswith(('support','eyelet')) and name!='support5':
                        old.append((dict(finger=i,cable=j,part=name),surface(child)))
        for ident,m in placed:
            for target,n in old:
                if np.any(m.bounds[1]<n.bounds[0]) or np.any(n.bounds[1]<m.bounds[0]): continue
                hit=trimesh.boolean.intersection([m,n],engine='manifold')
                volume=float(hit.volume)*1e9 if len(hit.faces) else 0.
                assert np.isfinite(volume) and volume>=0
                if volume>0: hardware_hits.append(dict(hinge=ident,original=target,intersection_mm3=volume))
    new_hits=[]
    if a.new_pairs:
        def owner(ident):
            if ident['part']=='leaf': return (ident['finger'],ident['cable'],'link',ident['level'])
            if ident['part']=='fork': return (ident['finger'],ident['cable'],ident['endpoint'])
            return tuple(ident.values())
        for k,(ident,m) in enumerate(placed):
            for other,n in placed[k+1:]:
                if np.any(m.bounds[1]<n.bounds[0]) or np.any(n.bounds[1]<m.bounds[0]): continue
                hit=trimesh.boolean.intersection([m,n],engine='manifold')
                volume=float(hit.volume)*1e9 if len(hit.faces) else 0.
                assert np.isfinite(volume) and volume>=0
                if volume>0: new_hits.append(dict(left=ident,right=other,intersection_mm3=volume,
                    proposed_same_rigid_owner=owner(ident)==owner(other)))
    failures=[r for r in records if r['straight_wire_intersection_mm3']>0 or r['object_gap_mm'] is None or r['object_gap_mm']<0]
    d=dict(status='PLACEMENT_REJECTED' if failures or hardware_hits or disconnected or any(not h['proposed_same_rigid_owner'] for h in new_hits) else 'INITIAL_HINGE_WIRE_OBJECT_SCREEN_ONLY',
        new_pair_screen_executed=a.new_pairs,new_part_intersections=new_hits,
        mount_relief=a.mount_relief, disconnected_parts=disconnected,
        hardware_screen_executed=a.hardware, original_hardware_intersections=hardware_hits,
        records=records, failures=failures, source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        seed_sha256=hashlib.sha256(seed_path.read_bytes()).hexdigest(),
        hinge_source_sha256=hashlib.sha256((Path(__file__).parent/'open_hinge_coupon.py').read_bytes()).hexdigest(),
        scene_sha256=hashlib.sha256(scene.read_bytes()).hexdigest(),
        scope='Actual original wire endpoints and seed hinge positions, finite radius .25mm inscribed96/64facet solids. Positive overlap is an obstruction witness; zero is not universal circular clearance proof. Initial pose only. Fork/leaf geometry not joined to root/carrier; foreign hardware, Skin, assembly retention, moving wire, strength and Native integration NOT QUALIFIED. No grasp trial.')
    (out/'summary.json').write_text(json.dumps(d,indent=2)); (out/'producer.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(dict(status=d['status'],parts=len(records),failures=failures,hardware_hits=hardware_hits,disconnected=disconnected,new_hits=new_hits),indent=2))

if __name__=='__main__': main()
