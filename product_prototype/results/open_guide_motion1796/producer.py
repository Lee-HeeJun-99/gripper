"""Prescribed mechanism FK clearance screen, NOT Native finger motion.
Uses authoritative float64 indexed geometry; never changes any object state.
"""
import argparse,json,time,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from open_guide_assembly import overlap
from open_hinge_coupon import BASE
from open_parallel_geometry_seed import sphere_gap
from yoke_bond_material_audit import surface
from analyse import sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='open_guide_projection1794');a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);started=time.monotonic()
    src=BASE/'results'/a.case;d=json.loads((src/'summary.json').read_text())
    scene=BASE/'results/capillary_hold1700/scene.scn';root=ET.parse(scene).getroot()
    obj=np.fromstring(root.find("Node[@name='object']/MechanicalObject").get('position'),sep=' ')[:3]
    inputs=[src/'summary.json',scene,Path(__file__)];model=[];old=[]
    for rec in d['records']:
        i,j=rec['finger'],rec['cable'];parts={}
        for name in rec['parts']:
            path=src/f'f{i}_c{j}_{name}_m.npz';inputs.append(path)
            with np.load(path,allow_pickle=False) as archive:
                m=trimesh.Trimesh(archive['vertices'],archive['faces'],process=False)
            assert m.is_volume and m.body_count==1;parts[name]=m
        theta=np.deg2rad(i*120);et=np.array([-np.sin(theta),np.cos(theta),0])
        c=parts['tube'].vertices.mean(0);outward=np.sign(c@et)*et
        r=np.array(rec['root_hinge_centres_m']);s=np.array(rec['carrier_hinge_centres_m'])
        normal=s[1]-s[0];normal/=np.linalg.norm(normal);rotation_axis=np.cross(outward,normal)
        assert abs(np.linalg.norm(rotation_axis)-1)<1e-12
        delta=s[0]-r[0];across=delta@outward;high=delta@normal;length=np.linalg.norm(delta)
        model.append((i,j,parts,r,s,outward,normal,rotation_axis,across,high,length))
        cable=root.find(f"Node[@name='guides{i}']/Node[@name='cable{j}']")
        for child in cable.findall('Node'):
            name=child.get('name','')
            if name.startswith(('support','eyelet')) and name not in ('support5','eyelet5'):
                old.append((dict(finger=i,cable=j,part=name),surface(child)))
    frames=[]
    for travel in np.linspace(0,.002,21):
        allparts=[];closure=0.;minimum_gap=None
        for i,j,parts,r,s,outward,normal,axis,across,high,length in model:
            angle=np.arccos((across-travel)/length)-np.arctan2(high,across)
            shift=-travel*outward+(np.sqrt(length**2-(across-travel)**2)-high)*normal
            for name,m in parts.items():
                m=m.copy()
                if name.startswith('link'):
                    level=int(name[-1]);T=trimesh.transformations.rotation_matrix(angle,axis,point=r[level]);m.apply_transform(T)
                    endpoint=(T@np.r_[s[level],1])[:3];closure=max(closure,float(abs(endpoint-s[level]-shift).max()))
                elif name in ('carrier','tube') or name.startswith('pin_carrier'):m.apply_translation(shift)
                gap=sphere_gap(m,obj);assert gap is not None
                minimum_gap=gap if minimum_gap is None else min(minimum_gap,gap)
                allparts.append((dict(finger=i,cable=j,part=name),m))
        hits=[]
        for k,(ident,m) in enumerate(allparts):
            for other,n in allparts[k+1:]+old:
                volume=overlap(m,n)
                if volume>0:hits.append(dict(left=ident,right=other,intersection_mm3=volume))
        frames.append(dict(inward_travel_mm=travel*1000,closure_error_m=closure,minimum_object_gap_mm=minimum_gap*1000,solid_intersections=hits))
    failures=[r for r in frames if r['solid_intersections'] or r['minimum_object_gap_mm']<0 or r['closure_error_m']>1e-12]
    result=dict(status='REJECTED_SAMPLED_MECHANISM_MOTION' if failures else 'SAMPLED_RIGID_MECHANISM_CLEARANCE_ONLY',
        case=a.case,frames=frames,first_failing_travel_mm=failures[0]['inward_travel_mm'] if failures else None,
        runtime_seconds=time.monotonic()-started,inputs=[dict(path=str(p.relative_to(BASE.parent)),sha256=sha(p)) for p in inputs],
        scope='21prescribed rigid mechanism FK samples0..2mm with stationary original root/finger reference. Not actual Native/FEM trajectory, continuous sweep, finite-wire dynamics or contact-force proof. All bodies retained, positive solid overlaps are failures. Initial straight-wire failures of1794 unchanged, not evaluated as a new valid wire. No grasp qualification.')
    (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(dict(status=result['status'],first_failing_travel_mm=result['first_failing_travel_mm'],
        total_intersections=sum(len(r['solid_intersections']) for r in frames),maximum_closure_error_m=max(r['closure_error_m'] for r in frames),runtime_seconds=result['runtime_seconds']),indent=2))

if __name__=='__main__':main()
