"""Opposite-side tendon feasibility,not integrated four-cable hardware.

Replaces two closing eyelet routes by two backside routes for a controlled
single-finger no-object contrast. Original guide anchor/mass assumptions stay
fixed,not claimed physical COM/inertia of a redesigned support.
"""
import argparse,csv,json,math,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
from mechanism_candidates import world
from b3_contact_layer_native import flat
from native_bending_coupon import guarded

def segment_bound(a,b,tri,radius_mm,step_mm=.5):
 n=max(1,int(np.ceil(np.linalg.norm(b-a)/step_mm)));minimum=math.inf
 for p in np.linspace(a,b,n+1):
  near=trimesh.triangles.closest_point(tri,np.repeat(p[None],len(tri),axis=0));minimum=min(minimum,float(np.linalg.norm(near-p,axis=1).min()))
 return minimum-radius_mm-np.linalg.norm(b-a)/(2*n)
def geometry(root,c,mesh,reference=world):
 finger=root.find("Node[@name='finger0']");q=np.fromstring(finger.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)*1000;skin=finger.find("Node[@name='skinCollision']");ids=np.fromstring(skin.find('SubsetMapping').get('indices'),sep=' ',dtype=int);faces=ids[np.fromstring(skin.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3)];tri=q[faces];guide=root.find("Node[@name='guides0']");anchors=np.fromstring(guide.find("Node[@name='anchors']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)*1000;owner=np.fromstring(guide.find("Node[@name='anchors']/RigidMapping").get('rigidIndexPerPoint'),sep=' ',dtype=int);routes=[];records=[]
 for cable in range(2):
  node=guide.find(f"Node[@name='cable{cable}']");old=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)*1000;pull=np.fromstring(node.find('CableConstraint').get('pullPoint'),sep=' ')*1000;stations=c['tendon']['guide_stations'];normal=np.array([np.array(reference(c,[x,0,1],0))-reference(c,[x,0,0],0) for x in [0]+stations]);path=np.vstack([pull,old])-6*normal;route=path[1:];nodes=np.fromstring(node.find('RigidMapping').get('rigidIndexPerPoint'),sep=' ',dtype=int);support=[]
  for p,j in zip(route,nodes):
   foot=anchors[owner==j].mean(0);support.append(segment_bound(foot,p,tri,.25,.25))
  wire=[segment_bound(a,b,tri,.25) for a,b in zip(path[:-1],path[1:])];guidegap=[]
  for p in route:
   near=trimesh.triangles.closest_point(tri,np.repeat(p[None],len(tri),axis=0));guidegap.append(float(np.linalg.norm(near-p,axis=1).min()-math.hypot(1.5,1)))
  routes.append(dict(cable=cable,old_route_mm=old.tolist(),new_route_mm=route.tolist(),new_pull_point_mm=path[0].tolist(),normal_world=normal.tolist()));records.append(dict(cable=cable,minimum_wire_skin_lower_bound_mm=min(wire),minimum_guide_sphere_skin_gap_mm=min(guidegap),minimum_support_capsule_skin_lower_bound_mm=min(support)))
 return dict(status='PASS_INITIAL_OPPOSED_PROXY_SKIN_CLEARANCE' if all(min(r[k] for k in r if k!='cable')>0 for r in records) else 'REJECT_INITIAL_OPPOSED_PROXY_CLEARANCE',routes=routes,records=records,support_assumption='Finite0.5mmOD rod from3anchor centroid to3mmODx2mmeyelet;no measured strength/COM,inertia not redesigned',wire_radius_mm=.25,scope='Initial single-finger no-object wire capsule/guide sphere/support capsule vs actual Skin triangles. Not own-Rail bond clearance,fullassembly,swept/selfcollision or finite bored-eyelet wire bend certification.')
def nonuniform_reference(root,c,mesh):
 from contact_adaptation_profile import candidate
 f=root.find("Node[@name='finger0']");g=root.find("Node[@name='guides0']");local=np.array(mesh['local_positions_mm']);q=np.array([candidate(c,p,0) for p in local])*.001;pairs=np.fromstring(f.find('SubsetMultiMapping').get('indexPairs'),sep=' ',dtype=int).reshape(-1,2);anchors=np.empty((36,3));free=np.empty(((pairs[:,0]==0).sum(),3))
 for k,(owner,index) in enumerate(pairs):
  if owner==0:free[index]=q[k]
  else:anchors[index]=q[k]
 f.find('MechanicalObject').set('position',flat(q));f.find('MeshTopology').set('position',flat(q));root.find("Node[@name='free0']/MechanicalObject").set('position',flat(free));g.find("Node[@name='anchors']/MechanicalObject").set('position',flat(anchors));owners=np.fromstring(g.find("Node[@name='anchors']/RigidMapping").get('rigidIndexPerPoint'),sep=' ',dtype=int);frames=np.fromstring(g.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7);assert np.max(abs(frames[:,3:]-[0,0,0,1]))==0
 for j in range(len(frames)):frames[j,:3]=anchors[owners==j].mean(0)
 g.find('MechanicalObject').set('position',flat(frames))
 for name in ('skinCollision','railCollision'):
  n=f.find(f"Node[@name='{name}']");ids=np.fromstring(n.find('SubsetMapping').get('indices'),sep=' ',dtype=int);n.find('MechanicalObject').set('position',flat(q[ids]));n.find('MeshTopology').set('position',flat(q[ids]))
 for cable in range(2):
  node=g.find(f"Node[@name='cable{cable}']");old=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)*1000;points=np.array([candidate(c,[x,-p[1],3],0) for x,p in zip(c['tendon']['guide_stations'],old)])*.001;node.find('MechanicalObject').set('position',flat(points));pull=np.fromstring(node.find('CableConstraint').get('pullPoint'),sep=' ')*1000;node.find('CableConstraint').set('pullPoint',flat(np.array(candidate(c,[0,-pull[1],3],0))*.001))
 c['finger']['precurve']['profile']='phi(u)=40deg*(2u-u^2),new manufactured stress-free rest,not observed motion'
 return candidate
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--native',action='store_true');p.add_argument('--opposed',action='store_true');p.add_argument('--nonuniform-rest',action='store_true');p.add_argument('--release-cycle',action='store_true');p.add_argument('--zero-force',action='store_true');p.add_argument('--duration',type=float,choices=[.05,.6,1.2],default=.05);p.add_argument('--pilot');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_railback_grasp1001298';root=ET.parse(src/'scene.scn').getroot();c=json.loads((src/'config.json').read_text());mesh=json.loads((src/'mesh.json').read_text());reference=nonuniform_reference(root,c,mesh) if a.nonuniform_rest else world;geo=geometry(root,c,mesh,reference);(out/'geometry.json').write_text(json.dumps(geo,indent=2));(out/'config.json').write_text(json.dumps(c,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes())
 if not a.native:
  geo.update(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),input_hashes={f:sha(src/f) for f in ('scene.scn','config.json','mesh.json')},physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(geo,indent=2));print(json.dumps(dict(status=geo['status'],records=geo['records'])));return
 assert geo['status'].startswith('PASS')
 for control in root.iter('NativeCableSequence'):
  if a.zero_force:control.set('maximumForceN','0')
  if a.release_cycle:control.set('hold','.6');control.set('release','.9')
 for n in list(root):
  if n.tag=='Node' and n.get('name') not in ('finger0','guides0','free0'):root.remove(n)
  elif n.tag.startswith('Native'):root.remove(n)
 if a.opposed:
  guide=root.find("Node[@name='guides0']")
  for r in geo['routes']:
   node=guide.find(f"Node[@name='cable{r['cable']}']");node.find('MechanicalObject').set('position',flat(np.array(r['new_route_mm'])*.001));node.find('CableConstraint').set('pullPoint',flat(np.array(r['new_pull_point_mm'])*.001))
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'scene.scn');(out/'mesh.json').write_bytes((src/'mesh.json').read_bytes());dt=float(root.get('dt'));steps=round(a.duration/dt);forecast=10
 if a.duration>.05:
  assert a.pilot;pr=json.loads((BASE/'results'/a.pilot/'summary.json').read_text());pm=json.loads((BASE/'results'/a.pilot/'preflight.json').read_text());assert pr['status']=='BOUNDED_NO_OBJECT_ACTUATION_ONLY' and pm['opposed']==a.opposed and pm.get('nonuniform_rest',False)==a.nonuniform_rest and pm.get('zero_force',False)==a.zero_force and pm['duration_s']==.05;forecast=pr['process']['runtime_s']*(a.duration/.05)*5;assert forecast<120
 cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',str(out/'scene.scn')]
 pre=dict(command=cmd,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),scene_sha256=sha(out/'scene.scn'),baseline_scene_sha256=sha(src/'scene.scn'),binary_hashes={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')},duration_s=a.duration,dt_s=dt,opposed=a.opposed,nonuniform_rest=a.nonuniform_rest,forecast_s=forecast,child_limit_s=120,memory_GiB=4,input='Original NativeC2 force1.5N/cable,gravity9.81,noObject/otherFingers/support. Not Cableforce increase.',mass_inertia='Original guide mass/COM/inertia retained as controlled ideal-body assumption;NOT redesigned fabricated support property',classification='EXPLORATORY SINGLE_FINGER_NO_OBJECT')
 pre.update(zero_force=a.zero_force,release_cycle=a.release_cycle,force_N_per_cable=0 if a.zero_force else 1.5,hold_end_s=.6 if a.release_cycle else 2.,release_end_s=.9 if a.release_cycle else 2.5,pilot_note='.05s pilot control prefix identical;release schedule only changes future>=.6s,not a checkpoint transfer')
 pre['input']='NativeC2 force1.5N/cable,or zeroForce reference if force_N_per_cable=0;gravity9.81,noObject/otherFingers/support. No force increase.'
 (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',120);rows=list(csv.DictReader((out/'finger0.csv').open())) if (out/'finger0.csv').exists() else [];log=''.join((out/'process'/x).read_text() for x in ('stdout.log','stderr.log'));q0=np.fromstring(root.find("Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);t=np.array(mesh['tetrahedra']);det0=np.linalg.det((q0[t[:,1:]]-q0[t[:,0,None]]).transpose(0,2,1));minimum=1.;finite=True
 for r in rows:
  q=np.fromstring(r['q_m'],sep=' ').reshape(-1,3);finite&=bool(np.isfinite(q).all());minimum=min(minimum,float((np.linalg.det((q[t[:,1:]]-q[t[:,0,None]]).transpose(0,2,1))/det0).min()))
 valid=proc['exit_code']==0 and '[ERROR]'not in log and len(rows)==steps and finite and minimum>0;d=dict(status='BOUNDED_NO_OBJECT_ACTUATION_ONLY' if valid else 'FAIL_NATIVE_OR_ELEMENT',process=proc,outputs=len(rows),minimum_saved_core_volume_ratio=minimum,finite=finite,opening='NOT ASSESSED',physical_validation='NOT QUALIFIED',scope='Opposite route controlled idealjoint/mass contrast,not simultaneous fourtendon hardware,unsupportedHolding,fullsweptclearance or time/mesh/energy qualification.');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
