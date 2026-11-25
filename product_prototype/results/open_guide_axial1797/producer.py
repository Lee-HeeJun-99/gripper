"""Connect actual fork/link geometry to a three-foot base and tube collar.
Finite candidate only; original scene, tubes and saved results immutable.
"""
import argparse
import itertools
import json
import sys
import time
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from captured_carriage_candidate import wire
from open_hinge_coupon import BASE, build
from open_parallel_geometry_seed import sphere_gap
from yoke_bond_material_audit import surface
from analyse import sha

def overlap(a,b):
    if np.any(a.bounds[1]<b.bounds[0]) or np.any(b.bounds[1]<a.bounds[0]):return 0.
    hit=trimesh.boolean.intersection([a,b],engine='manifold')
    volume=float(hit.volume)*1e9 if len(hit.faces) else 0.
    assert np.isfinite(volume) and volume>=0
    return volume

def union(parts):return trimesh.boolean.union(parts,engine='manifold')

def flat_strut(a,b,axis):
    along=b-a;length=np.linalg.norm(along);along/=length
    assert abs(along@axis)<1e-10
    basis=np.stack([along,np.cross(axis,along),axis],axis=1)
    T=np.eye(4);T[:3,:3]=basis;T[:3,3]=(a+b)/2
    return trimesh.creation.box([length+.0006,.0006,.0003],transform=T)

def load(path):
    m=trimesh.load_mesh(path,process=True); assert m.is_volume
    return m

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True)
    p.add_argument('--bearing-pockets',action='store_true')
    p.add_argument('--routed-connections',action='store_true')
    p.add_argument('--clearance-stack',action='store_true')
    p.add_argument('--projected-foot-stack',action='store_true')
    p.add_argument('--axial-link-plane',action='store_true');a=p.parse_args()
    started=time.monotonic();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    seed_path=BASE/'results/open_parallel_seed1768/summary.json'
    scene=BASE/'results/capillary_hold1700/scene.scn'
    root=ET.parse(scene).getroot();seed=json.loads(seed_path.read_text())
    obj=np.fromstring(root.find("Node[@name='object']/MechanicalObject").get('position'),sep=' ')[:3]
    allparts=[];records=[];wires=[];old=[];inputs=[Path(__file__),seed_path,scene,Path(__file__).parent/'open_hinge_coupon.py']
    hinge_shapes=build()
    corners=np.array(list(itertools.product((-.0003,.0003),repeat=3)))
    for rec in seed['records']:
        i,j=rec['finger'],rec['cable'];prefix=f'f{i}_c{j}'
        cable=root.find(f"Node[@name='guides{i}']/Node[@name='cable{j}']")
        tube=surface(cable.find("Node[@name='eyelet5']"));v=tube.vertices;n=len(v)//4
        c=v.mean(0);axis=v[2*n:].mean(0)-v[:2*n].mean(0);axis/=np.linalg.norm(axis)
        r=np.array(rec['root_hinge_centres_m']);s=np.array(rec['initial_platform_centres_m'])
        normal=s[1]-s[0];normal/=np.linalg.norm(normal)
        feet=np.array(rec['original_feet_m'])
        if a.clearance_stack:
            # Derived surface stack, NOT a guide/tension/offset parameter scan:
            # root foot half-height .3 + moving hub .75 + gap .05 = 1.10mm;
            # carrier outer collar1.1755 + moving hub.75 + gap.05 =1.9755mm.
            foot_height=.0003
            if a.projected_foot_stack:
                foot_height=float((((feet[:,None]+corners).reshape(-1,3)-feet.mean(0))@normal).max())
            r+=normal*max(0.,foot_height+.00075+.00005-float((r[0]-feet.mean(0))@normal))
            s+=normal*max(0.,.0019755-float((s[0]-c)@normal))
        along=s[0]-r[0];along/=np.linalg.norm(along)
        axial_shift=.00125 if a.axial_link_plane else 0.
        r+=axis*axial_shift;s+=axis*axial_shift
        local={};leaves={};pins={}
        for endpoint in ('root','carrier'):
            for level in (0,1):
                centre=r[level] if endpoint=='root' else s[level]
                direction=along if endpoint=='root' else -along
                basis=np.stack([direction,np.cross(axis,direction),axis],axis=1)
                shapes=[]
                for shape in hinge_shapes:
                    m=trimesh.Trimesh(shape.vertices*.001@basis.T+centre,shape.faces,process=False)
                    assert m.is_volume
                    shapes.append(m)
                if endpoint=='carrier':
                    for k in (0,1):
                        shapes[k]=trimesh.boolean.difference([shapes[k],wire(c-axis*.003,c+axis*.003,.0008755)],engine='manifold')
                local[endpoint,level],leaves[endpoint,level],pins[endpoint,level]=shapes
        root_back=r-.0013*along;carrier_back=s+.0013*along
        base=trimesh.convex.convex_hull(np.vstack([(feet[:,None]+corners).reshape(-1,3),
            (root_back[:,None]+corners).reshape(-1,3)]))
        fixed=union([base,local['root',0],local['root',1],wire(*root_back,.00035)])
        # Explicit real solid connections, not a rigid mapping across empty space.
        collar=trimesh.boolean.difference([
            wire(c-axis*.0004,c+axis*.0004,.0011755),
            wire(c-axis*.002,c+axis*.002,.0008755)],engine='manifold')
        carrier=union([collar,local['carrier',0],local['carrier',1],
            wire(*carrier_back,.00035),wire(carrier_back[0],c+normal*.0010755,.0003)])
        carrier=trimesh.boolean.difference([carrier,
            wire(c-axis*.003,c+axis*.003,.0008755)],engine='manifold')
        if a.routed_connections:
            # New load path: no convex filling of the lower pivot cavity.
            # Root feet join a rear spine; carrier uses two axial cheek plates
            # outside the moving .4mm leaf, instead of a central round strut.
            foot_base=trimesh.convex.convex_hull((feet[:,None]+corners).reshape(-1,3))
            fixed=union([foot_base,wire(feet.mean(0),root_back[0],.0003),
                wire(*root_back,.00035),local['root',0],local['root',1]])
            plates=[flat_strut(carrier_back[0]-axis*axial_shift+sign*axis*.0004,
                c+normal*.0010755+sign*axis*.0004,axis) for sign in (-1,1)]
            ties=[wire(carrier_back[0]+sign*axis*.0004,
                carrier_back[0]-axis*axial_shift+sign*axis*.0004,.0003) for sign in (-1,1)] if a.axial_link_plane else []
            carrier=union([collar,local['carrier',0],local['carrier',1],
                wire(*carrier_back,.00035),*plates,*ties])
            carrier=trimesh.boolean.difference([carrier,
                wire(c-axis*.003,c+axis*.003,.0008755)],engine='manifold')
        if a.bearing_pockets:
            # Machine finite bearing spaces out of NEW structural material only.
            # Radius .75 hub+.05 nominal radial gap, axial .4 leaf+.05 each side.
            def pocket(body,centres):
                tools=[]
                for centre in centres:
                    tools.extend([wire(centre-axis*.00025,centre+axis*.00025,.0008),
                        wire(centre-axis*.003,centre+axis*.003,.0003)])
                return trimesh.boolean.difference([body,*tools],engine='manifold')
            fixed=pocket(fixed,r);carrier=pocket(carrier,s)
        parts=dict(root=fixed,carrier=carrier,tube=tube)
        for level in (0,1):
            parts[f'link{level}']=union([leaves['root',level],leaves['carrier',level]])
            for endpoint in ('root','carrier'):
                parts[f'pin_{endpoint}{level}']=pins[endpoint,level]
        path=np.fromstring(cable.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)
        wires.append((dict(finger=i,cable=j),wire(path[-2],path[-1],.00025)))
        props={}
        for name,m in parts.items():
            m.export(out/f'{prefix}_{name}_m.stl')
            # PLY/STL are visualization interchange. NPZ is authoritative
            # float64 indexed topology and is independently roundtrip checked.
            m.export(out/f'{prefix}_{name}_m.ply',encoding='binary',vertex_normal=False)
            archive=out/f'{prefix}_{name}_m.npz'
            np.savez_compressed(archive,vertices=m.vertices,faces=m.faces)
            with np.load(archive,allow_pickle=False) as stored:
                assert np.array_equal(stored['vertices'],m.vertices) and np.array_equal(stored['faces'],m.faces)
            props[name]=dict(closed_positive_solid=bool(m.is_volume),components=int(m.body_count),
                volume_mm3=float(m.volume)*1e9,object_gap_mm=sphere_gap(m,obj)*1000)
            allparts.append((dict(finger=i,cable=j,part=name),m))
        records.append(dict(finger=i,cable=j,parts=props,original_feet_inside_root=fixed.contains(feet).tolist(),
            root_hinge_centres_m=r.tolist(),carrier_hinge_centres_m=s.tolist(),
            root_foot_plane_height_mm=float((r[0]-feet.mean(0))@normal)*1000,
            carrier_tube_axis_distance_mm=float((s[0]-c)@normal)*1000))
        for child in cable.findall('Node'):
            name=child.get('name','')
            # Original support5 is replaced only in this candidate, tube5 retained.
            if name.startswith(('support','eyelet')) and name not in ('support5','eyelet5'):
                old.append((dict(finger=i,cable=j,part=name),surface(child)))
    pair_hits=[];wire_hits=[]
    for k,(ident,m) in enumerate(allparts):
        for other,n in allparts[k+1:]+old:
            volume=overlap(m,n)
            if volume>0:pair_hits.append(dict(left=ident,right=other,intersection_mm3=volume))
        for ident_wire,n in wires:
            volume=overlap(m,n)
            if volume>0:wire_hits.append(dict(part=ident,wire=ident_wire,intersection_mm3=volume))
    invalid=[dict(finger=r['finger'],cable=r['cable'],part=k) for r in records for k,v in r['parts'].items()
        if not v['closed_positive_solid'] or v['components']!=1 or v['object_gap_mm']<0]
    d=dict(status='REJECTED_INITIAL_ASSEMBLY' if pair_hits or wire_hits or invalid else 'INITIAL_ASSEMBLY_SCREEN_ONLY',
        records=records,solid_intersections=pair_hits,wire_intersections=wire_hits,invalid_parts=invalid,
        runtime_seconds=time.monotonic()-started,
        inputs=[dict(path=str(f.relative_to(BASE.parent)),sha256=sha(f)) for f in inputs],
        command=sys.argv,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),binary_sha256=None,sdk='NOT USED: finite CSG geometry only',
        scope='New physically connected base/carrier candidate from actual1778 parts. Nominal geometry assumptions only. All reported solid overlaps are failures, not ignored same-finger rows. Initial inscribed-wire witnesses only; no continuous or Native dynamics. Pins unretained. Skin/Rail, force transfer, actuation, strength and hardware mass NOT QUALIFIED. No grasp PASS.')
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2))
    print(json.dumps(dict(status=d['status'],runtime_seconds=d['runtime_seconds'],invalid=invalid,pair_hit_count=len(pair_hits),wire_hit_count=len(wire_hits),pair_hits=pair_hits[:6]),indent=2))

if __name__=='__main__':main()
