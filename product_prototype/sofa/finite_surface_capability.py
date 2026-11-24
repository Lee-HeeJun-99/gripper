"""Actual failed wire/guide shape as a STATIC INITIAL rigid contact capability coupon.
Not a checkpoint, elastic wire actuation, grasp or a validated inertia model.
"""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
csv.field_size_limit(16*1024*1024)
def flat(x):return ' '.join(format(float(v),'.17g') for v in np.asarray(x).ravel())
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--build-case',default='intersector_registry_build1663');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/wire_local_mesh_pilot1655';build=BASE/'results'/a.build_case;meta=json.loads((build/'summary.json').read_text());binary=Path(meta['binary']);assert sha(binary)==meta['binary_sha256'] and sha(build/'Registry.cpp')==meta['compiled_source_sha256'];w=BASE/'results/wire_local_mesh_facet_reference1660/points.json';t=json.loads(w.read_text())[0]['time_s'];q=None
 for r in read(src/'surface.csv'):
  if float(r['time_s'])==t:q=np.fromstring(r['q'],sep=' ').reshape(-1,3);break
 assert q is not None;records=[]
 for probe in (False,True):
  d=out/('probe' if probe else 'control');d.mkdir();root=ET.parse(src/'scene.scn').getroot();wire=root.find("Node[@name='wire']");oldsurface=wire.find("Node[@name='wireSurface']");faces=oldsurface.find('MeshTopology').get('triangles')
  for n in list(wire):wire.remove(n)
  root.insert(0,ET.Element('RequiredPlugin',pluginName='Sofa.Component.Mass'));ET.SubElement(wire,'EulerImplicitSolver',rayleighMass='0',rayleighStiffness='0');ET.SubElement(wire,'SparseLDLSolver',template='CompressedRowSparseMatrixd');ET.SubElement(wire,'MechanicalObject',name='dofs',template='Rigid3d',position=flat(np.r_[q.mean(0),[0,0,0,1]]),velocity='0 0 0 0 0 0');ET.SubElement(wire,'UniformMass',template='Rigid3d',vertexMass='.00001 1e-8 1e-6 0 0 0 1e-6 0 0 0 1e-6');ET.SubElement(wire,'GenericConstraintCorrection');ET.SubElement(wire,'NativeRigidJournal',body='@dofs',solver='@../unusedJournalSolver',filename=str(d/'states.csv'));col=ET.SubElement(wire,'Node',name='wireSurface');ET.SubElement(col,'MeshTopology',position=flat(q),triangles=faces);ET.SubElement(col,'MechanicalObject',name='surface',position=flat(q));ET.SubElement(col,'RigidMapping',input='@../dofs',output='@surface',globalToLocalCoords='1')
  for kind in ('Triangle','Line','Point'):ET.SubElement(col,kind+'CollisionModel',group='1')
  ET.SubElement(col,'NativePointJournal',body='@surface',filename=str(d/'surface.csv'))
  if probe:ET.SubElement(root,'RequiredPlugin',pluginName=str(binary));ET.SubElement(root,'ReGripIntersectorRegistry',filename=str(d/'registry.csv'))
  for n in root.iter():
   for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(d)))
  ET.ElementTree(root).write(d/'scene.scn');(d/'geometry.json').write_bytes((src/'geometry.json').read_bytes());(d/'preflight.json').write_text(json.dumps(dict(source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(d/'scene.scn'),initial_source_frame_s=t,initial_positions_sha256=sha(src/'surface.csv'),observer_binary_sha256=sha(binary),observer_compiled_source_sha256=meta['compiled_source_sha256'],change='ALL actual6144wirefaces andcomplete768Guidefaces/features preserved. Isolate initial geometry intooneFREErigidwire (assumedpositive mass/inertia,not calibrated) atzero INITIAL velocity;NOFEM/cable/endpointfixture. NOT a checkpointrestart or dynamicwire/grasptrial. Control/probe differONLYregistryqueries.',steps=2,dt_s=float(root.get('dt')),SDK='/home/ubuntu/SOFA/v26.06.00',memory_GiB=4,child_limit_s=60),indent=2));proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',str(d/'scene.scn')],d/'process',60);logs=''.join((d/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));rows=read(d/'states.csv') if (d/'states.csv').exists() else [];records.append(dict(probe=probe,process=proc,outputs=len(rows),Native_execution_valid=proc['exit_code']==0 and '[ERROR]'not in logs and len(rows)==2))
 error=0.
 for file,keys in [('states.csv',('rigid_q','rigid_v','object_impulse_Ns_Nms')),('surface.csv',('q','v'))]:
  x=read(out/'control'/file);y=read(out/'probe'/file);assert [r['time_s'] for r in x]==[r['time_s'] for r in y]
  for r,s in zip(x,y):
   for k in keys:error=max(error,float(abs(np.fromstring(r[k],sep=' ')-np.fromstring(s[k],sep=' ')).max()))
 registry=read(out/'probe/registry.csv');inventory={}
 for r in registry:
  key=r['class0']+' | '+r['class1'];inventory.setdefault(key,set()).add((r['supported'],r['intersector']))
 result=dict(status='PASS_READONLY_REGISTRY_AND_INITIAL_GEOMETRY_COUPON_ONLY' if all(r['Native_execution_valid'] for r in records) and error<=1e-12 and registry else 'FAIL_NATIVE_COUPON_OR_OBSERVER',records=records,maximum_observer_q_v_surface_impulse_error=error,actual_registered_pair_inventory={k:sorted(v) for k,v in inventory.items()},initial_source_frame_s=t,source_sha256=sha(Path(__file__)),scope='Actualregisteredpair availability andobserverpurityONLY. Initialpenetration deliberately inheritedforcapabilitydiagnosis,not acceptednormalinitialconditionforgrasp. Wholephysicalguide/wiremesh retained; rigid surrogate andassumedinertia doNOTvalidate elasticwire/tendon/mass/dynamics/100gHolding. RegistryNULLmaydeliberatelyignoredcompositepair;requireactualfeature/geometryresponse audit.');(out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result,indent=2))
if __name__=='__main__':main()
