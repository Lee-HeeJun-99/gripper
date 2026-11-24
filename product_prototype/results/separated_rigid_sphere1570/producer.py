"""No-contact reference on actual INITIAL Skin geometry,not merely birth capability."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
from native_bending_coupon import guarded
def read(p):return list(csv.DictReader(p.open()))
def flat(v):return ' '.join(format(float(x),'.17g') for x in np.asarray(v).ravel())
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/finite_hardware_new1569';source=ET.parse(src/'scene.scn').getroot();n=source.find("Node[@name='finger0']/Node[@name='skinCollision']");vertices=np.fromstring(n.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);faces=np.fromstring(n.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3);centre=np.fromstring(source.find("Node[@name='object']/MechanicalObject").get('position'),sep=' ')[:3];tri=vertices[faces];near=trimesh.triangles.closest_point(tri,np.repeat(centre[None],len(tri),axis=0));gap=float(np.linalg.norm(near-centre,axis=1).min()-.03);assert gap>.0002;template=BASE/'results/rigid_sphere_contract1567/MinRigid3';records=[]
 for policy in ('Min','New'):
  d=out/policy;d.mkdir();root=ET.parse(template/'scene.scn').getroot()
  if policy=='New':root.find('MinProximityIntersection').tag='NewProximityIntersection'
  for i,position in enumerate((vertices.mean(0),centre)):
   parent=root.find(f"Node[@name='guide{i}']");parent.find('MechanicalObject').set('position',flat(np.r_[position,[0,0,0,1]]));parent.find('MechanicalObject').set('velocity','0 0 0 0 0 0');col=parent.find("Node[@name='collision']")
   if i==0:col.find('MechanicalObject').set('position',flat(vertices));top=col.find('MeshTopology');top.set('position',flat(vertices));top.set('triangles',flat(faces))
   else:col.find('MechanicalObject').set('position',flat(np.r_[centre,[0,0,0,1]]))
  for component in root.iter():
   for k,v in list(component.attrib.items()):component.set(k,v.replace(str(template),str(d)))
  ET.ElementTree(root).write(d/'scene.scn');process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',str(d/'scene.scn')],d/'process',60);rows=read(d/'response1.csv') if (d/'response1.csv').exists() else [];states=[r for i in (0,1) for r in read(d/f'guide{i}.csv')];logs=''.join((d/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));maximum=max((float(abs(np.fromstring(r['rigid_v'],sep=' ')).max()) for r in states),default=None);active=sum(float(r['lambda_Ns'])!=0 for r in rows);records.append(dict(policy=policy,process=process,error='[ERROR]'in logs,nonzero_actual_response_rows=active,maximum_actual_velocity_component=maximum,status='PASS_SEPARATED_STATIC_REFERENCE_ONLY' if process['exit_code']==0 and '[ERROR]'not in logs and len(states)==4 and active==0 and maximum<=1e-12 else 'FAIL_SPURIOUS_STATIC_CONTACT_OR_EXECUTION',scene_sha256=sha(d/'scene.scn')))
 d=dict(status='INITIAL_GEOMETRY_NO_CONTACT_REFERENCE_ONLY',records=records,actual_minimum_triangle_sphere_gap_mm=gap*1000,contact_buffer_mm=.2,scope='ActualINITIALSkin+RigidSphere geometry,isolatedtwofreerigids/noFEM/cable/support/gravity/initialvelocity. ValidseparationrequireszeroresponseANDzeromotion;birthcapabilityaloneneverqualifieswholeNativepolicy. Positivegapcomputedindependentlyfromtriangles.',source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
