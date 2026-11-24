"""Matched native sphere template/contact capability and angular impulse audit.
Vec3 centre mapping is not assumed equivalent to a physical rotating sphere.
"""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from observer_identity import compiled_pair_rows
def read(p):return list(csv.DictReader(p.open()))
def flat(x):return ' '.join(format(float(v),'.17g') for v in np.asarray(x).ravel())
def main(policies=('Min','Local')):
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/local_skin_triangle1565/Min';base=ET.parse(src/'scene.scn').getroot();v=np.fromstring(base.find("Node[@name='guide0']/Node[@name='collision']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);normal=np.cross(v[1]-v[0],v[2]-v[0]);normal/=np.linalg.norm(normal);tangent=np.cross(normal,[0,1,0]);tangent/=np.linalg.norm(tangent);records=[];binary,frozen=compiled_pair_rows()
 for policy in policies:
  for representation in ('Vec3','Rigid3'):
   d=out/(policy+representation);d.mkdir();root=ET.fromstring(ET.tostring(base));intersection=root.find('MinProximityIntersection')
   if policy=='Local':intersection.tag='LocalMinDistance'
   elif policy=='New':intersection.tag='NewProximityIntersection'
   parent=root.find("Node[@name='guide1']");parent.find('MechanicalObject').set('velocity',flat(np.r_[.1*tangent,[0,0,0]]));col=parent.find("Node[@name='collision']")
   if representation=='Rigid3':
    col.find('MechanicalObject').set('template','Rigid3d');col.find('MechanicalObject').set('position',parent.find('MechanicalObject').get('position'));col.find('SphereCollisionModel').set('template','Rigid3d');mapping=col.find('RigidMapping');mapping.tag='IdentityMapping';mapping.attrib.pop('globalToLocalCoords',None)
   for n in root.iter():
    for k,value in list(n.attrib.items()):n.set(k,value.replace(str(src),str(d)))
   ET.ElementTree(root).write(d/'scene.scn');process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',str(d/'scene.scn')],d/'process',60);response=read(d/'response1.csv') if (d/'response1.csv').exists() else [];states=read(d/'guide1.csv') if (d/'guide1.csv').exists() else [];logs=''.join((d/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));impulses=[np.fromstring(r['object_impulse_Ns_Nms'],sep=' ') for r in states];direct=read(d/'direct1.csv') if (d/'direct1.csv').exists() else []
   records.append(dict(policy=policy,sphere_representation=representation,process=process,error='[ERROR]'in logs,outputs=len(states),nonzero_response_rows=sum(float(r['lambda_Ns'])!=0 for r in response),maximum_sphere_angular_impulse_Nms=max((float(np.linalg.norm(z[3:])) for z in impulses),default=None),maximum_sphere_linear_impulse_Ns=max((float(np.linalg.norm(z[:3])) for z in impulses),default=None),maximum_direct_angular_J_component=max((float(abs(np.fromstring(r['J'],sep=' ')[3:]).max()) for r in direct),default=None),scene_sha256=sha(d/'scene.scn')))
 summary=dict(status='MATCHED_SPHERE_TEMPLATE_CAPABILITY_ONLY',records=records,initial_sphere_tangential_velocity_m_s=(.1*tangent).tolist(),scope='SameactualSkinfacet,actualspherecentre/R30,rootpipeline,mass/inertia/friction/initialtangentialvelocity across4variants. ONLYnativeintersectionandSphereMechanicalState/mappingrepresentation differ. Independenttwofreerigid initialtinyoverlap coupon,NOTwholeFEM/contactaccuracy/Holding. Vec3centre representation may erase sphere rotational contact coupling;MUST audit actualJ/impulse before any claimed fix.',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),observer_binary_sha256=sha(binary),observer_compiled_source_sha256=sha(frozen),SDK='/home/ubuntu/SOFA/v26.06.00',child_limit_s=60,memory_GiB=4);(out/'summary.json').write_text(json.dumps(summary,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
