"""Finite,stress-free distal contact-layer candidate,not measured material.

Bottom vertices exactly coincide with existing Skin material nodes. They will
be perfectly bonded by a Native subset mapping;upper vertices remain free.
"""
import argparse,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
from mechanism_candidates import world,stl

def geometry(src):
 c=json.loads((src/'config.json').read_text());local=np.array(json.loads((src/'mesh.json').read_text())['local_positions_mm'])
 parents=np.flatnonzero((local[:,0]>=80)&(local[:,2]==.1));bottom=local[parents];assert len(parents)==20
 points=np.array([p+[0,0,z] for p in bottom for z in (0,.5)])
 ids=lambda i,j,k:2*(4*i+j)+k
 tets=[]
 for i in range(4):
  for j in range(3):
   box=[ids(i+a,j+b,k) for a,b,k in ((0,0,0),(1,0,0),(0,1,0),(1,1,0),(0,0,1),(1,0,1),(0,1,1),(1,1,1))]
   for split in ((0,1,3,7),(0,3,2,7),(0,2,6,7),(0,6,4,7),(0,4,5,7),(0,5,1,7)):
    tet=[box[k] for k in split]
    if np.linalg.det((points[tet[1:]]-points[tet[0]]).T)<0:tet[1],tet[2]=tet[2],tet[1]
    tets.append(tet)
 faces={}
 for a,b,d,e in tets:
  for f in ((b,d,e),(a,e,d),(a,b,e),(a,d,b)):faces.setdefault(tuple(sorted(f)),[]).append(f)
 surface=np.array([f[0] for f in faces.values() if len(f)==1]);tets=np.array(tets);root=ET.parse(src/'scene.scn').getroot();records=[];qref=[]
 center=np.array(c['simulation']['sphere_center_mm'])*.001;R=.03
 for finger,angle in enumerate(c['palm']['angles_deg']):
  q=np.array([world(c,p,angle) for p in points])*.001;qref.append(q)
  film=np.fromstring(root.find(f"./Node[@name='finger{finger}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)
  assert abs(q[::2]-film[parents]).max()<1e-15
  det=np.linalg.det((q[tets[:,1:]]-q[tets[:,0,None]]).transpose(0,2,1));near=trimesh.triangles.closest_point(q[surface],np.repeat(center[None],len(surface),axis=0));gap=float((np.linalg.norm(near-center,axis=1)-R).min())
  # Conservative finite guide sphere separation from every pad triangle.
  guidepoints=[]
  for cable in range(2):guidepoints.extend(np.fromstring(root.find(f"./Node[@name='guides{finger}']/Node[@name='cable{cable}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3))
  gg=[]
  for g in guidepoints:
   closest=trimesh.triangles.closest_point(q[surface],np.repeat(g[None],len(surface),axis=0));gg.append(float(np.linalg.norm(closest-g,axis=1).min()-np.hypot(.0015,.001)))
  records.append(dict(finger=finger,minimum_initial_pad_object_gap_m=gap,minimum_initial_pad_own_guide_sphere_gap_m=min(gg),minimum_signed_tet_determinant_m3=float(det.min()),volume_m3=float(det.sum()/6),mass_kg=float(det.sum()/6*1000)))
 return dict(local_positions_mm=points.tolist(),bottom_Skin_parent_indices=parents.tolist(),tetrahedra=tets.tolist(),triangles=surface.tolist(),world_reference_m=[q.tolist() for q in qref],records=records)

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results/b3_railback_grasp1001298';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);g=geometry(src)
 for i,q in enumerate(g['world_reference_m']):stl(out/f'contact_layer_finger{i}_reference.stl',np.array(q)*1000,g['triangles'])
 safe=all(r['minimum_initial_pad_object_gap_m']>=.0002 and r['minimum_initial_pad_own_guide_sphere_gap_m']>0 and r['minimum_signed_tet_determinant_m3']>0 for r in g['records'])
 d=dict(status='PASS_LIMITED_INITIAL_GEOMETRY' if safe else 'REJECT_INITIAL_GEOMETRY',source_scene_sha256=sha(src/'scene.scn'),source_commit=__import__('subprocess').check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),records=g['records'],design=dict(start_mm=80,end_mm=100,thickness_mm=.5,young_modulus_Pa=1e6,poisson_ratio=.3,density_kg_m3=1000,material_scope='HYPOTHETICAL linear elastic contact-layer sensitivity;not measured silicone/PET or layer jamming',bond='IDEAL_PERFECT_BOND_NOT_MEASURED'),scope='Exact existing Skin bottom-node match,initial pad-sphere distance and same-finger finite guide proxy only. New finite volume/mass;not equal-material comparison. No swept clearance,self-contact,assembly,pressure or area qualification.',physical_validation='NOT QUALIFIED')
 (out/'mesh.json').write_text(json.dumps(g));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d))
if __name__=='__main__':main()
