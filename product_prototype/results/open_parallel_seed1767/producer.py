"""Actual finite open-link SEED, not finished hinges or Native-ready assembly.
Creates all six mechanisms from actual old guide/three-foot coordinates.
Finite rods, carrier and root envelopes are checked against fixed R30 sphere.
Hub axial overlap is explicitly UNQUALIFIED until clevis/pin spaces are built.
"""
import argparse,json,sys,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'sofa'))
from analyse import sha
from yoke_bond_material_audit import surface
from captured_carriage_candidate import wire

def hub(p,axis):return wire(p-axis*.0002,p+axis*.0002,.00075)
def hollow_link(a,b,axis):
 whole=trimesh.boolean.union([wire(a,b,.0004),hub(a,axis),hub(b,axis)],engine='manifold')
 return trimesh.boolean.difference([whole,wire(a-axis*.002,a+axis*.002,.0003),wire(b-axis*.002,b+axis*.002,.0003)],engine='manifold')
def sphere_gap(mesh,c):
 near=trimesh.triangles.closest_point(mesh.triangles,np.repeat(c[None],len(mesh.faces),axis=0));return float(np.linalg.norm(near-c,axis=1).min()-.03)

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/capillary_hold1700';root=ET.parse(src/'scene.scn').getroot();obj=np.fromstring(root.find("Node[@name='object']/MechanicalObject").get('position'),sep=' ')[:3];records=[];cubes=np.array(list(__import__('itertools').product((-.0004,.0004),repeat=3)))
 for i in range(3):
  parent=root.find(f"Node[@name='guides{i}']");feet=np.fromstring(parent.find("Node[@name='anchors']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);theta=np.deg2rad(i*120);et=np.array([-np.sin(theta),np.cos(theta),0])
  for j in range(2):
   tube=surface(parent.find(f"Node[@name='cable{j}']/Node[@name='eyelet5']"));v=tube.vertices;N=len(v)//4;c=v.mean(0);axis=v[2*N:].mean(0)-v[:2*N].mean(0);axis/=np.linalg.norm(axis);side=np.sign(c@et);outward=side*et;normal=np.cross(axis,outward);normal/=np.linalg.norm(normal)
   if normal@(c-obj)<0:normal=-normal
   foot=feet[j*18+15:j*18+18];f=foot.mean(0);span=float((c-f)@outward);root_height=.00085;rootA=c-span*outward+(root_height-float((c-f)@normal))*normal;rootB=rootA+.003*normal
   mount_radius=.0008255+.00005;platform_height=mount_radius+.0003+.0003;P=c+platform_height*normal;delta=P-rootA;across=float(delta@outward);high=float(delta@normal);assert across>.002 and high>0,'deadcentre/negative initial mechanical branch';L=float(np.linalg.norm(delta));initial=np.arctan2(high,across);history=[]
   fixed=trimesh.convex.convex_hull(np.vstack([(foot[:,None]+cubes[None]).reshape(-1,3),rootA+cubes,rootB+cubes]));assert fixed.is_volume;fixed.export(out/f'f{i}_c{j}_root_ENVELOPE_m.stl')
   for travel in (0.,.0005,.001,.0015,.002):
    angle=np.arccos((across-travel)/L);shift=-travel*outward+(L*np.sin(angle)-high)*normal;A=P+shift;B=A+.003*normal;link0=hollow_link(rootA,A,axis);link1=hollow_link(rootB,B,axis);ring=tube.copy();ring.apply_translation(shift)
    collar=wire(c+shift-axis*.0004,c+shift+axis*.0004,mount_radius+.0003);spine=wire(A,B,.0004);carrier=trimesh.boolean.union([collar,spine,hub(A,axis),hub(B,axis)],engine='manifold');carrier=trimesh.boolean.difference([carrier,wire(c+shift-axis*.002,c+shift+axis*.002,mount_radius),wire(A-axis*.002,A+axis*.002,.0003),wire(B-axis*.002,B+axis*.002,.0003)],engine='manifold');parts=dict(link0=link0,link1=link1,carrier=carrier,ring=ring)
    assert all(m.is_volume for m in parts.values());gap=min(sphere_gap(m,obj) for m in [fixed,*parts.values()]);closure=max(abs(np.linalg.norm(A-rootA)-L),abs(np.linalg.norm(B-rootB)-L),float(abs((B-A)-(rootB-rootA)).max()))
    history.append(dict(inward_travel_mm=travel*1000,relative_crank_angle_deg=float(np.degrees(angle-initial)),guide_dorsal_motion_mm=float(shift@normal)*1000,minimum_new_sphere_gap_mm=gap*1000,kinematic_closure_error_m=closure,connected_components={k:int(m.body_count) for k,m in parts.items()}))
    if travel in (0.,.002):
     for name,mesh in parts.items():mesh.export(out/f'f{i}_c{j}_{name}_{int(travel*1000)}mm_m.stl')
   records.append(dict(finger=i,cable=j,original_feet_m=foot.tolist(),root_hinge_centres_m=[rootA.tolist(),rootB.tolist()],initial_platform_centres_m=[P.tolist(),(P+.003*normal).tolist()],link_length_mm=L*1000,initial_crank_angle_deg=float(np.degrees(initial)),history=history))
 d=dict(status='OPEN_PARALLEL_FINITE_ENVELOPE_SEED_NOT_NATIVE_READY',records=records,minimum_sampled_object_gap_mm=min(x['minimum_new_sphere_gap_mm'] for r in records for x in r['history']),maximum_closure_error_m=max(x['kinematic_closure_error_m'] for r in records for x in r['history']),source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),native_component_sha256=sha(BASE/'results/open_parallel_range1766/summary.json'),scope='New explicit finite concept geometry, all six original guide positions/foot patterns and actual OD/ID2mm tube kept initially. Five joint stroke samples are prescribed MECHANISM kinematics, not FEM or Native grasp, and never applied to an object. Ideal1DOF open loop is supported only by1766component coupon. Root bodies are ENVELOPES; hinge hubs currently overlap axially and require physical clevis/spacer/pin machining. Foreign hardware, new-material Skin clearance, incoming finite-wire path and continuous stroke are NOT QUALIFIED. Real materials/strength/friction/mass/inertia and fabrication are NOT MEASURED. No full Native launch from this seed and no sleeve-size scan.');(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in d.items() if k!='records'},indent=2))
if __name__=='__main__':main()
