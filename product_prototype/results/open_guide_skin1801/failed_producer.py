"""Actual new mechanism material vs every initial Skin/Rail tetrahedron.
Original support5 is the declared historical root bond domain only, not a
permission to ignore arbitrary same-finger intersections.
"""
import argparse,json,time,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from open_hinge_coupon import BASE
from finite_csg64 import register
from yoke_bond_material_audit import surface
from analyse import sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='open_guide_axial64_1799');a=p.parse_args()
    register();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);started=time.monotonic()
    src=BASE/'results'/a.case;scene=BASE/'results/capillary_hold1700/scene.scn'
    root=ET.parse(scene).getroot();d=json.loads((src/'summary.json').read_text());fem=[]
    for i in range(3):
        node=root.find(f"Node[@name='finger{i}']")
        q=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)
        t=np.fromstring(node.find('MeshTopology').get('tetrahedra'),sep=' ',dtype=int).reshape(-1,4)
        assert np.isfinite(q).all();fem.append((q,t))
    records=[];inputs=[scene,src/'summary.json',Path(__file__),Path(__file__).parent/'finite_csg64.py']
    for rec in d['records']:
        i,j=rec['finger'],rec['cable']
        for name in rec['parts']:
            if name=='tube':continue # Preserved original material, not a new part.
            path=src/f'f{i}_c{j}_{name}_m.npz';inputs.append(path)
            with np.load(path,allow_pickle=False) as arc:m=trimesh.Trimesh(arc['vertices'],arc['faces'],process=False)
            assert m.is_volume and m.body_count==1
            old_volume=float(m.volume)
            if name=='root':
                old=surface(root.find(f"Node[@name='guides{i}']/Node[@name='cable{j}']/Node[@name='support5']"))
                m=trimesh.boolean.difference([m,old],engine='manifold64')
            bad=[];tested=0
            for fi,(q,t) in enumerate(fem):
                points=q[t];mask=np.all(points.max(1)>=m.bounds[0],axis=1)&np.all(points.min(1)<=m.bounds[1],axis=1)
                for k in np.flatnonzero(mask):
                    tested+=1;cell=trimesh.convex.convex_hull(points[k])
                    hit=trimesh.boolean.intersection([m,cell],engine='manifold64')
                    volume=float(hit.volume)*1e9 if len(hit.faces) else 0.
                    assert np.isfinite(volume) and volume>=0
                    if volume>0:bad.append(dict(finger=fi,tetrahedron=int(k),new_overlap_mm3=volume))
            records.append(dict(finger=i,cable=j,part=name,original_bond_domain_subtracted=name=='root',
                excluded_old_domain_mm3=(old_volume-float(m.volume))*1e9,tested_cells=tested,new_material_FEM_overlaps=bad))
    bad=[r for r in records if r['new_material_FEM_overlaps']]
    result=dict(status='FAIL_NEW_MATERIAL_SKIN_RAIL_INTERSECTION' if bad else 'PASS_INITIAL_NEW_MATERIAL_FEM_SEPARATION_ONLY',
        case=a.case,records=records,runtime_seconds=time.monotonic()-started,
        inputs=[dict(path=str(p.relative_to(BASE.parent)),sha256=sha(p)) for p in inputs],
        scope='Read-only initial faceted solid/FEM screen, not actual dynamic deformation, bond strength, continuous clearance or Native grasp. All three finger meshes tested. Only root original support5 bond domain excluded explicitly. OriginalFEM/raw/verdict unchanged; current straight-wire failure remains FAIL.')
    (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(dict(status=result['status'],tested_cells=sum(r['tested_cells'] for r in records),
        positive_overlap_cells=sum(len(r['new_material_FEM_overlaps']) for r in records),runtime_seconds=result['runtime_seconds']),indent=2))

if __name__=='__main__':main()
