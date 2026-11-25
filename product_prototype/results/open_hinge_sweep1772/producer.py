"""Finite clevis coupon; mm construction, NOT a Native guide or strength test."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import trimesh

BASE = Path(__file__).resolve().parents[1]

def box(size, centre):
    return trimesh.creation.box(size, transform=trimesh.transformations.translation_matrix(centre))

def cylinder(r, length, z=0):
    return trimesh.creation.cylinder(radius=r, height=length, sections=96,
        transform=trimesh.transformations.translation_matrix([0, 0, z]))

def union(parts):
    return trimesh.boolean.union(parts, engine='manifold')

def build():
    # Separate central moving leaf and two fixed fork leaves. Pin retention
    # is deliberately NOT implied by the unheaded geometry-only pin.
    moving = union([cylinder(.75, .4), box([2.5, .8, .4], [1.25, 0, 0])])
    moving = trimesh.boolean.difference([moving, cylinder(.3, 2)], engine='manifold')
    leaves = []
    for z in (-.4, .4):
        leaf = union([cylinder(.75, .3, z), box([1.5, .8, .3], [-.75, 0, z])])
        leaves.append(trimesh.boolean.difference([leaf, cylinder(.3, 2)], engine='manifold'))
    fixed = union([*leaves, box([.4, .8, 1.1], [-1.3, 0, 0])])
    return fixed, moving, cylinder(.25, 1.3)

def main():
    p = argparse.ArgumentParser(); p.add_argument('--tag', required=True)
    p.add_argument('--sweep', action='store_true'); a = p.parse_args()
    out = BASE/'results'/a.tag; out.mkdir(exist_ok=False)
    fixed, moving, pin = build()
    assert all(m.is_volume and m.body_count == 1 for m in (fixed, moving, pin))
    records = []
    angles = np.linspace(0, 70, 141) if a.sweep else [0.]
    for angle in angles:
        leaf = moving.copy()
        leaf.apply_transform(trimesh.transformations.rotation_matrix(np.deg2rad(angle), [0, 0, 1]))
        hits = {}
        for name, x, y in [('fork_leaf', fixed, leaf), ('fork_pin', fixed, pin), ('leaf_pin', leaf, pin)]:
            hit = trimesh.boolean.intersection([x, y], engine='manifold')
            volume = float(hit.volume) if len(hit.faces) else 0.
            assert np.isfinite(volume) and volume >= 0, 'invalid CSG result'
            hits[name] = volume
        records.append(dict(angle_deg=float(angle), intersections_mm3=hits))
    for name, mesh in [('fork', fixed), ('leaf', moving), ('unretained_pin', pin)]:
        mesh = mesh.copy(); mesh.apply_scale(.001); mesh.export(out/f'{name}_m.stl')
    maximum = max(v for r in records for v in r['intersections_mm3'].values())
    d = dict(status='SAMPLED_HINGE_GEOMETRY_PASS' if maximum == 0 else 'HINGE_GEOMETRY_FAIL',
        maximum_intersection_mm3=maximum, samples=records,
        axial_gap_each_side_mm=.05, nominal_radial_pin_clearance_mm=.05,
        fork_wall_mm=.3, central_leaf_mm=.4, stack_mm=1.1,
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        scope='Independent hinge coupon only. Sampled finite-solid intersections, not continuous collision, Native dynamics, installed six-guide compatibility or strength. Nominal dimensions are assumptions. Pin retention, tolerances, bearing friction, materials, fatigue and assembly tools NOT MEASURED. No original collision model removed; no grasp PASS.')
    (out/'summary.json').write_text(json.dumps(d, indent=2))
    (out/'producer.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({k:v for k,v in d.items() if k != 'samples'}, indent=2))

if __name__ == '__main__': main()
