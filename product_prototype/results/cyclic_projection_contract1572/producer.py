"""Same physical collision facets,cyclic vertex start;NO SDK/physics solver patch."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from new_projection_audit import acute_faces,HEADER
def flat(x):return ' '.join(format(float(v),'.17g') for v in np.asarray(x).ravel())
def canonicalize(root):
 records=[]
 for node in root.iter('Node'):
  if node.find('TriangleCollisionModel') is None:continue
  topology=node.find('MeshTopology');mechanical=node.find('MechanicalObject');assert topology is not None and mechanical.get('template')=='Vec3d';vertices=np.fromstring(mechanical.get('position'),sep=' ').reshape(-1,3);old=np.fromstring(topology.get('triangles'),sep=' ',dtype=int).reshape(-1,3);new=acute_faces(vertices,old);assert np.array_equal(np.sort(old,axis=1),np.sort(new,axis=1));norm=lambda f:np.cross(vertices[f[:,1]]-vertices[f[:,0]],vertices[f[:,2]]-vertices[f[:,0]]);error=float(abs(norm(old)-norm(new)).max());assert error<=1e-12;topology.set('triangles',flat(new));records.append(dict(node=node.get('name'),facets=len(old),changed_starts=int(np.any(old!=new,axis=1).sum()),same_unordered_facets=True,normal_cross_product_error_m2=error))
 assert records;return records
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[]
 for name,source in [('separated','separated_rigid_sphere1570/New'),('loaded','new_rigid_sphere_contract1568/NewRigid3')]:
  src=BASE/'results'/source;d=out/name;d.mkdir();root=ET.parse(src/'scene.scn').getroot();assert root.find('NewProximityIntersection') is not None;changes=canonicalize(root)
  for n in root.iter():
   for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(d)))
  ET.ElementTree(root).write(d/'scene.scn');process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',str(d/'scene.scn')],d/'process',60);states=[r for i in (0,1) for r in read(d/f'guide{i}.csv')];rows=read(d/'response1.csv');direct=read(d/'direct1.csv');logs=''.join((d/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));active=sum(float(r['lambda_Ns'])!=0 for r in rows);velocity=max(float(abs(np.fromstring(r['rigid_v'],sep=' ')).max()) for r in states);angular=max((float(abs(np.fromstring(r['J'],sep=' ')[3:]).max()) for r in direct),default=0);ok=process['exit_code']==0 and '[ERROR]'not in logs and len(states)==4 and ((active==0 and velocity<=1e-12) if name=='separated' else(active>0 and angular>0));records.append(dict(case=name,process=process,changes=changes,source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(d/'scene.scn'),actual_nonzero_response_rows=active,maximum_actual_velocity_component=velocity,maximum_direct_angular_J_component=angular,status='PASS_SCOPED_NATIVE_CYCLIC_CONTRACT' if ok else 'FAIL_CYCLIC_CONTACT_CONTRACT'))
 d=dict(status='PASS_SEPARATED_AND_LOADED_NATIVE_CYCLIC_COUPONS_ONLY' if all(r['status']=='PASS_SCOPED_NATIVE_CYCLIC_CONTRACT' for r in records) else 'FAIL_CYCLIC_PROJECTION_COUPONS',records=records,scope='CyclicvertexpermutationONLYonactualcollisionfacets;coordinates/unorderedfacets/orientation/mass/material/SphereRigid3/input/Nativecomponentsunchanged. InstalledNewprojectionbranch orderingworkaroundcandidate,notSDKpatch/customcontactsolver or fullgrasp/time/mesh/energyqualification.',header_sha256=sha(HEADER),source_sha256=sha(Path(__file__)),helper_sha256=sha(BASE/'sofa/new_projection_audit.py'));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'projection_reference.py').write_bytes((BASE/'sofa/new_projection_audit.py').read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
