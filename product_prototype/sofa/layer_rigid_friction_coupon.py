"""Independent stock rigid thin-layer/support friction component control.
Not flexible-layer stiffness or vacuum jamming. No custom physics components.
"""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import trimesh
from analyse import BASE,sha
from native_bending_coupon import guarded

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--mu',type=float,choices=[0,.3],required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/layer_pressure_pilot1188';old=ET.parse(src/'scene.scn').getroot();root=ET.Element('Node',name='root',dt='.0002',gravity='0 0 0');flat=lambda x:' '.join(format(float(v),'.17g') for v in np.array(x).ravel())
 for n in old.findall('RequiredPlugin'):root.append(n)
 ET.SubElement(root,'RequiredPlugin',pluginName='Sofa.Component.Mapping.NonLinear')
 for tag in ('FreeMotionAnimationLoop','BlockGaussSeidelConstraintSolver','CollisionPipeline','BruteForceBroadPhase','BVHNarrowPhase','MinProximityIntersection','CollisionResponse','EulerImplicitSolver','SparseLDLSolver','GenericConstraintCorrection'):root.append(old.find(tag))
 root.find('CollisionResponse').set('responseParams','mu='+str(a.mu));root.find('EulerImplicitSolver').set('rayleighStiffness','0');mass=1400*.04*.01*.0002
 for i in (0,1):
  node=ET.SubElement(root,'Node',name='support' if i==0 else 'layer');dims=np.array([.05,.02,.002] if i==0 else [.04,.01,.0002]);centre=[0,0,-.001] if i==0 else [0,0,.000102];ET.SubElement(node,'MechanicalObject',name='rigid',template='Rigid3d',position=flat([*centre,0,0,0,1]));I=[(dims[1]**2+dims[2]**2)/12,(dims[0]**2+dims[2]**2)/12,(dims[0]**2+dims[1]**2)/12];ET.SubElement(node,'UniformMass',template='Rigid3d',vertexMass=flat([mass,np.prod(dims),I[0],0,0,0,I[1],0,0,0,I[2]]))
  if i==0:ET.SubElement(node,'FixedProjectiveConstraint',indices='0')
  else:
   ET.SubElement(node,'LinearForceField',template='Rigid3d',points='0',times='0 .01 .02',forces=flat([[0,0,0,0,0,0],[0,0,-.4,0,0,0],[0,0,-.4,0,0,0]]));ET.SubElement(node,'LinearForceField',template='Rigid3d',points='0',times='0 .01 .012 .02',forces=flat([[0]*6,[0]*6,[.01,0,0,0,0,0],[.01,0,0,0,0,0]]));ET.SubElement(node,'NativeRigidJournal',body='@rigid',solver='@../constraints',filename=str(out/'rigid.csv'),auditMass='1')
  surface=ET.SubElement(node,'Node',name='collision');box=trimesh.creation.box(extents=dims);ET.SubElement(surface,'MeshTopology',position=flat(box.vertices),triangles=flat(box.faces));ET.SubElement(surface,'MechanicalObject',name='surface',template='Vec3d',position=flat(box.vertices))
  for tag in ('TriangleCollisionModel','LineCollisionModel','PointCollisionModel'):ET.SubElement(surface,tag,group=str(i+1))
  ET.SubElement(surface,'RigidMapping',input='@../rigid',output='@surface',globalToLocalCoords='0',initialPoints=flat(box.vertices))
 ET.SubElement(root,'NativeDetectionPairs',narrow='@narrow',filename=str(out/'layer_pairs.csv'));ET.ElementTree(root).write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','100','--hideProgressBar',str(out/'scene.scn')];pre=dict(command=cmd,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),SDK='/home/ubuntu/SOFA/v26.06.00',mu=a.mu,mass_kg=mass,normal_force_N=.4,tangential_force_N=.01,friction_capacity_assumption_N=a.mu*.4,initial_gap_m=.000002,dt_s=.0002,estimated_runtime_s=3,child_limit_s=60,memory_GiB=4,scope='Assumed rigid layer over rigid thick support,normal preload then tangential load. Separate contact/friction component only,not layer jamming.',binary_hashes={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')});(out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',60);rows=list(csv.DictReader((out/'rigid.csv').open())) if (out/'rigid.csv').exists() else [];logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));q=np.array([np.fromstring(r['rigid_q'],sep=' ') for r in rows]);d=dict(status='RIGID_FRICTION_COMPONENT_STATES_ONLY' if proc['exit_code']==0 and '[ERROR]' not in logs and len(rows)==100 else 'FAIL_EXECUTION',process=proc,outputs=len(rows),final_x_m=float(q[-1,0]) if len(q) else None,minimum_centre_z_m=float(q[:,2].min()) if len(q) else None,physical_validation='NOT QUALIFIED',layer_jamming='NOT VALIDATED');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
