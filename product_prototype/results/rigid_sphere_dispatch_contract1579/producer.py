"""Strict stock-Min equivalence and mesh-only no-op tests for registration adapter."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def read(p):return list(csv.DictReader(p.open()))
def flat(x):return ' '.join(format(float(v),'.17g') for v in np.asarray(x).ravel())
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);build=BASE/'results/rigid_sphere_dispatch_build1578';meta=json.loads((build/'summary.json').read_text());binary=Path(meta['binary']);assert meta['status']=='PASS_BUILD_ONLY_NOT_PHYSICS' and sha(binary)==meta['binary_sha256'];assert sha(build/'Dispatch.cpp')==meta['compiled_source_sha256'];source=BASE/'results/rigid_sphere_contract1567/MinRigid3';records=[]
 for feature in ('triangle','point','line','mixed_spheres','separated_surface'):
  pair=[]
  for policy in ('Min','Dispatch'):
   d=out/(feature+'_'+policy);d.mkdir();src=BASE/'results/separated_rigid_sphere1570/Min' if feature=='separated_surface' else source;root=ET.parse(src/'scene.scn').getroot();sphere=root.find("Node[@name='guide1']");col=root.find("Node[@name='guide0']/Node[@name='collision']")
   if feature in ('point','line'):
    v=np.fromstring(col.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);n=np.cross(v[1]-v[0],v[2]-v[0]);n/=np.linalg.norm(n);centre=(v[0] if feature=='point' else(v[0]+v[1])/2)+n*(.03-.0001);sphere.find('MechanicalObject').set('position',flat(np.r_[centre,[0,0,0,1]]));sphere.find("Node[@name='collision']/MechanicalObject").set('position',flat(np.r_[centre,[0,0,0,1]]))
    for e in list(col):
     if 'CollisionModel'in e.tag and e.tag!=feature.capitalize()+'CollisionModel':col.remove(e)
   elif feature=='mixed_spheres':
    parent=root.find("Node[@name='guide0']");parent.find('MechanicalObject').set('position','0 0 0 0 0 0 1');col.find('MechanicalObject').set('position','0 0 0')
    for e in list(col):
     if 'CollisionModel'in e.tag or e.tag=='MeshTopology':col.remove(e)
    ET.SubElement(col,'SphereCollisionModel',radius='.035',group='1');sphere.find('MechanicalObject').set('position','.0649 0 0 0 0 0 1');sphere.find('MechanicalObject').set('velocity','0 .1 0 0 0 0');sphere.find("Node[@name='collision']/MechanicalObject").set('position','.0649 0 0 0 0 0 1')
   if policy=='Dispatch':
    root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)));root.find('MinProximityIntersection').tag='NativeRigidSphereLocalProximity'
   for n in root.iter():
    for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(d)))
   ET.ElementTree(root).write(d/'scene.scn');process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',str(d/'scene.scn')],d/'process',60);logs=''.join((d/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));states=[read(d/f'guide{i}.csv') if (d/f'guide{i}.csv').exists() else [] for i in (0,1)];response=read(d/'response1.csv') if (d/'response1.csv').exists() else [];direct=read(d/'direct1.csv') if (d/'direct1.csv').exists() else [];pair.append(dict(policy=policy,process=process,error='[ERROR]'in logs,outputs=[len(x) for x in states],active_rows=sum(float(r['lambda_Ns'])!=0 for r in response),maximum_angular_J=max((float(abs(np.fromstring(r['J'],sep=' ')[3:]).max()) for r in direct),default=0),scene_sha256=sha(d/'scene.scn'),_states=states))
  maximum=0.
  if all(r['outputs']==[2,2] for r in pair):
   for xs,ys in zip(pair[0]['_states'],pair[1]['_states']):
    for x,y in zip(xs,ys):
     assert x['time_s']==y['time_s']
     for k in ('rigid_q','rigid_v','object_impulse_Ns_Nms'):maximum=max(maximum,float(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')).max()))
  else:maximum=float('inf')
  for r in pair:r.pop('_states')
  ok=all(r['process']['exit_code']==0 and not r['error'] and r['outputs']==[2,2] for r in pair) and maximum<=1e-12 and (all(r['active_rows']==0 for r in pair) if feature=='separated_surface' else all(r['active_rows']>0 and r['maximum_angular_J']>0 for r in pair));records.append(dict(feature=feature,variants=pair,maximum_q_v_impulse_error_vs_stock_Min=maximum,status='PASS_STRICT_NATIVE_MIN_EQUIVALENCE_ONLY' if ok else 'FAIL_NATIVE_DISPATCH_EQUIVALENCE'))
 # Separate mesh-only case proves registration does not alter Local mesh paths.
 src=BASE/'results/b3_finite_local32_536/1';root=ET.parse(src/'scene.scn').getroot();root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)));assert root.find('LocalMinDistance') is not None;root.find('LocalMinDistance').tag='NativeRigidSphereLocalProximity';d=out/'mesh_only_noop';d.mkdir()
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(d)))
 ET.ElementTree(root).write(d/'scene.scn');count=len(read(src/'guide0.csv'));process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(count),'--hideProgressBar',str(d/'scene.scn')],d/'process',60);maximum=0.;complete=True
 for i in (0,1):
  xs=read(src/f'guide{i}.csv');ys=read(d/f'guide{i}.csv') if(d/f'guide{i}.csv').exists() else [];complete&=len(xs)==len(ys)
  for x,y in zip(xs,ys):
   for k in ('rigid_q','rigid_v','object_impulse_Ns_Nms'):maximum=max(maximum,float(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')).max()))
 logs=''.join((d/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));noop=dict(process=process,maximum_mesh_only_q_v_impulse_error_vs_stock_Local=maximum,outputs_per_body=count,complete=complete,status='PASS_NATIVE_MESH_ONLY_NOOP' if complete and process['exit_code']==0 and '[ERROR]'not in logs and maximum<=1e-12 else 'FAIL_MESH_ONLY_NOOP');ok=all(r['status']=='PASS_STRICT_NATIVE_MIN_EQUIVALENCE_ONLY' for r in records) and noop['status']=='PASS_NATIVE_MESH_ONLY_NOOP';d=dict(status='PASS_NATIVE_DISPATCH_COUPONS_ONLY' if ok else 'FAIL_NATIVE_DISPATCH_CONTRACT',records=records,mesh_only=noop,binary=str(binary),binary_sha256=sha(binary),compiled_source_sha256=sha(build/'Dispatch.cpp'),source_sha256=sha(Path(__file__)),scope='InstalledNativeMinRigidSpherefunctions+NativeLocalotherpaths;strict1e-12stockq/v/Jlambdaequivalence on5primitive/referencecases andmesh-onlynoop. NotwholeB3/time/mesh/globalenergy/physicalqualification. NoSDK/ODE/forcefield/constraintsolver/contactlawrewritten.');(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in d.items() if k!='records'},indent=2))
if __name__=='__main__':main()
