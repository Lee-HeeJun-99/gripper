"""Contact-location-derived outer-rim chamfer,not collision disabling/route scan."""
import argparse,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
from finite_hardware_grasp_pilot import run_three,flat
def ring(n=32):
 # Retain OD3, ID1.2 and length2mm. 0.3mm45deg external edge relief
 # exceeds unchanged0.2mm pair buffer locally; minimum end wall remains0.6mm.
 profile=[(-1.,.6),(-1.,1.2),(-.7,1.5),(.7,1.5),(1.,1.2),(1.,.6)]
 v=np.array([[x,r*np.cos(t),r*np.sin(t)] for x,r in profile for t in np.arange(n)*2*np.pi/n]);faces=[]
 for a in range(len(profile)):
  b=(a+1)%len(profile)
  for k in range(n):
   j=(k+1)%n;faces.extend(((a*n+k,a*n+j,b*n+j),(a*n+k,b*n+j,b*n+k)))
 m=trimesh.Trimesh(v,faces,process=False);m.fix_normals();assert m.is_watertight and m.is_winding_consistent and m.volume>0;return m
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--duration',type=float,choices=(.6,2.),default=.6);p.add_argument('--pilot');a=p.parse_args();src=BASE/'results/dispatch_finite_hardware1583';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);root=ET.parse(src/'scene.scn').getroot();m=ring();parts=[];forecast=130.
 if a.duration> .6:
  assert a.pilot;d=json.loads((BASE/'results'/a.pilot/'summary.json').read_text());assert d['status']=='VALID_BOUNDED_EXPLORATION_ONLY';forecast=d['process']['runtime_s']*a.duration/d['duration_s']*2;assert forecast<420
 # Only the six final guide rings change; all supports, other rings, cable
 # force/route/attachments and collision feature types remain unchanged.
 for i in range(3):
  for j in range(2):
   node=root.find(f"Node[@name='guides{i}']/Node[@name='cable{j}']/Node[@name='eyelet5']");v=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);n=len(v)//4;centre=v.mean(0);axis=v[2*n:].mean(0)-v[:2*n].mean(0);axis/=np.linalg.norm(axis);ey=v[0]-centre-axis*((v[0]-centre)@axis);ey/=np.linalg.norm(ey);basis=np.stack([axis,ey,np.cross(axis,ey)],axis=1);new=m.vertices*.001@basis.T+centre;old=trimesh.Trimesh(v,np.fromstring(node.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3),process=False);node.find('MechanicalObject').set('position',flat(new));node.find('MeshTopology').set('position',flat(new));node.find('MeshTopology').set('triangles',flat(m.faces));mapping=node.find('RigidMapping');owner=mapping.get('rigidIndexPerPoint').split()[0];mapping.set('rigidIndexPerPoint',' '.join([owner]*len(new)));assert {x.tag for x in node if x.tag.endswith('CollisionModel')}=={'TriangleCollisionModel','LineCollisionModel','PointCollisionModel'};parts.append(dict(finger=i,cable=j,old_volume_mm3=float(old.volume)*1e9,new_volume_mm3=float(m.volume),end_radial_wall_mm=.6,outer_radius_mm=1.5,bore_radius_mm=.6,length_mm=2.,chamfer_mm=.3))
 for node in root.iter():
  for k,v in list(node.attrib.items()):node.set(k,v.replace(str(src),str(out)))
 pre=json.loads((src/'preflight.json').read_text());inter=dict(source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),contact_evidence_sha256=sha(BASE/'results/eyelet_contact_location1590/summary.json'),hypothesis='All5138actualhardware-contactpoints onexternalendrim;finite0.3mm45degreeouterchamfer removesedgewithoutmovingCableloadpath orshrinkingOD/bore/length. No prior chamferscans.',parts=parts,inherited_mass_inertia='UNCHANGED for matched collision-geometry sensitivity; removed ringvolume explicit, real density/COM/inertia uncalibrated. NOT same-material fabricatedpart validation.',scope='Finite external edge geometry sensitivity ONLY; ALL hardwarecollisionsenabled. No buffer/dt/friction/force/ODE/FEM/constraint change. Actual new dynamics required; oldHoldingNOTreused.');(out/'intervention.json').write_text(json.dumps(inter,indent=2));run_three(root,out,src,pre['eyelet'],pre['parts'],round(a.duration/.0025),a.duration,forecast);(out/'producer.py').write_bytes(Path(__file__).read_bytes())
if __name__=='__main__':main()
